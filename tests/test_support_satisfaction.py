from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fieldforge import pipeline
from fieldforge.reconciliation import support_satisfaction_matches

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(('value', 'valid'), [
    ('1', True), ('5', True), ('2.0', True), ('', True), (None, True),
    ('5.9', False), ('3.5', False), ('0', False), ('6', False),
    ('-1', False), ('NaN', False), ('Infinity', False), ('bad', False),
    ('5.0000000000000001', False),
])
def test_source_rating_is_missing_or_whole_and_in_range(value, valid):
    row = pd.Series({'opened_at': '2025-09-01', 'resolved_at': '', 'csat': value})
    failures = pipeline._reasons('tickets', row, {})
    assert ('TICKET_CSAT_INVALID' in [code for code, _ in failures]) is not valid


@pytest.fixture
def satisfaction_case(tmp_path):
    # Constructed fixture: a rating without resolution still counts; resolution
    # without feedback does not. Keep an all-unrated group and both scale limits.
    rows = [
        {'opened_at': '2025-09-30 23:00:00', 'resolved_at': '2025-10-01 01:00:00', 'category': 'account', 'csat': '2.0'},
        {'opened_at': '2025-09-01 00:00:00', 'resolved_at': '', 'category': 'account', 'csat': '5'},
        {'opened_at': '2025-09-02 00:00:00', 'resolved_at': '2025-09-03 00:00:00', 'category': 'account', 'csat': ''},
        {'opened_at': '2025-09-03 00:00:00', 'resolved_at': None, 'category': 'account', 'csat': None},
        {'opened_at': '2025-10-01 00:00:00', 'resolved_at': None, 'category': 'billing', 'csat': None},
        {'opened_at': '2025-10-01 00:00:00', 'resolved_at': None, 'category': 'product', 'csat': '1'},
    ]
    for index, row in enumerate(rows):
        row.update(ticket_id=f'fixture-{index}', normalized_email='fixture@example.test')
    path = tmp_path / 'tickets.parquet'
    pq.write_table(pa.Table.from_pylist(rows), path)
    with duckdb.connect() as con:
        con.read_parquet(str(path)).create_view('silver_tickets')
        staging = (ROOT / 'dbt/models/staging/stg_tickets.sql').read_text()
        con.execute('create view stg_tickets as ' + staging.replace("{{ source('silver', 'tickets') }}", 'silver_tickets'))
        model = (ROOT / 'dbt/models/marts/mart_support_health.sql').read_text()
        con.execute('create table mart_support_health as ' + model.replace("{{ ref('stg_tickets') }}", 'stg_tickets'))
        sql = (ROOT / 'dbt/tests/assert_support_satisfaction_reconciles.sql').read_text().replace("{{ source('silver', 'tickets') }}", 'silver_tickets').replace("{{ ref('mart_support_health') }}", 'mart_support_health')
        yield con, path, sql


def test_model_and_controls_preserve_rating_population(satisfaction_case):
    con, path, sql = satisfaction_case
    assert con.execute('select ticket_count, rated_ticket_count, avg_csat from mart_support_health order by 1 desc, category').fetchall() == [(4, 2, 3.5), (1, 0, None), (1, 1, 1.0)]
    assert support_satisfaction_matches(con, path)
    assert con.execute(sql).fetchall() == []


@pytest.mark.parametrize('mutation', [
    "update mart_support_health set avg_csat=1.75 where category='account'",
    "update mart_support_health set rated_ticket_count=4 where category='account'",
    "update mart_support_health set avg_csat=0 where category='billing'",
    "update mart_support_health set avg_csat='NaN'::double where category='account'",
    "update mart_support_health set avg_csat=null where category='account'",
    "delete from mart_support_health where category='billing'",
])
def test_both_controls_reject_corrupted_groups(satisfaction_case, mutation):
    con, path, sql = satisfaction_case
    con.execute(mutation)
    assert not support_satisfaction_matches(con, path)
    assert con.execute(sql).fetchall()


def test_python_control_rejects_duplicate_groups(satisfaction_case):
    con, path, _ = satisfaction_case
    con.execute('insert into mart_support_health select * from mart_support_health')
    assert not support_satisfaction_matches(con, path)


@pytest.mark.parametrize('invalid', ['5.9', 'bad', 'NaN'])
def test_controls_reject_invalid_accepted_source(satisfaction_case, invalid):
    con, path, sql = satisfaction_case
    rows = pq.read_table(path).to_pylist()
    rows[0]['csat'] = invalid
    pq.write_table(pa.Table.from_pylist(rows), path)
    assert not support_satisfaction_matches(con, path)
    assert con.execute(sql).fetchall()


def test_validation_preserves_invalid_raw_feedback_in_quarantine(tmp_path, monkeypatch):
    monkeypatch.setenv('FIELDFORGE_DATA_ROOT', str(tmp_path / 'data'))
    monkeypatch.setenv('FIELDFORGE_ARTIFACTS_ROOT', str(tmp_path / 'artifacts'))
    monkeypatch.setattr(pipeline, 'SOURCES', ('customers', 'orders', 'tickets'))
    pipeline.ensure_directories()
    pd.DataFrame(columns=['crm_customer_id']).to_parquet(pipeline.bronze_dir() / 'customers.parquet')
    pd.DataFrame(columns=['order_id']).to_parquet(pipeline.bronze_dir() / 'orders.parquet')
    ratings = ['5.9', 'bad', '3.5', 'NaN', '5.0', '']
    rows = [dict(ticket_id=f'fixture-{i}', opened_at='2025-09-01', resolved_at='', csat=value, _source_file='fixture.csv', _source_row_number=i+2, _run_id='fixture-run') for i, value in enumerate(ratings)]
    pd.DataFrame(rows).to_parquet(pipeline.bronze_dir() / 'tickets.parquet')
    summary = pipeline.validate_silver()['tickets']
    assert summary == {'bronze': 6, 'accepted': 2, 'quarantined': 4, 'reconciled': True}
    rejected = pq.read_table(pipeline.quarantine_dir() / 'tickets.parquet').to_pylist()
    assert [row['csat'] for row in rejected] == ratings[:4]
    assert all(row['_rule_codes'] == 'TICKET_CSAT_INVALID' and row['_run_id'] == 'fixture-run' and row['_source_file'] == 'fixture.csv' for row in rejected)
