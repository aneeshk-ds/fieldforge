from __future__ import annotations

import random
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from fieldforge.settings import ARTIFACTS, DEFAULT_SEED, SOURCE, ensure_directories
from fieldforge.utils import write_json


def _plant(df: pd.DataFrame, indices: list[int], code: str, mutate) -> None:
    for idx in indices:
        mutate(df, idx)
        current = df.at[idx, "_planted_error"]
        df.at[idx, "_planted_error"] = code if not current else f"{current}|{code}"


def generate(seed: int = DEFAULT_SEED, customers: int = 500) -> dict[str, int]:
    ensure_directories()
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    fake = Faker("en_US")
    Faker.seed(seed)
    end = date(2026, 8, 31)
    countries = ["US", "CA", "GB"]
    currencies = {"US": "USD", "CA": "CAD", "GB": "GBP"}

    people = []
    for i in range(customers):
        country = rng.choices(countries, [0.65, 0.2, 0.15])[0]
        first, last = fake.first_name(), fake.last_name()
        email = f"{first}.{last}.{i}@northstar.example".lower().replace("'", "")
        people.append(
            {
                "crm_customer_id": f"CRM-{i + 1:06d}",
                "first_name": first,
                "last_name": last,
                "email": email,
                "phone": f"+1-555-{i // 10000:03d}-{i % 10000:04d}",
                "country": country,
                "created_at": datetime(2025, 1, 1) + timedelta(days=rng.randrange(600)),
                "_planted_error": "",
            }
        )
    customers_df = pd.DataFrame(people)
    _plant(customers_df, [3, 53, 103], "malformed_email", lambda d, i: d.__setitem__("email", d["email"].mask(d.index == i, "not-an-email")))
    _plant(customers_df, [151, 152], "duplicate_primary_key", lambda d, i: d.__setitem__("crm_customer_id", d["crm_customer_id"].mask(d.index == i, "CRM-DUPLICATE")))
    _plant(customers_df, [201, 251], "missing_country", lambda d, i: d.__setitem__("country", d["country"].mask(d.index == i, None)))

    plans = {"ESSENTIALS": 2900, "PLUS": 4900, "PREMIUM": 7900}
    subs = []
    invoices = []
    for i, person in customers_df.iterrows():
        if rng.random() > 0.83:
            continue
        start = date(2025, 1, 1) + timedelta(days=rng.randrange(560))
        cancelled = start + timedelta(days=rng.randrange(45, 450)) if rng.random() < 0.22 else None
        if cancelled and cancelled > end:
            cancelled = None
        plan = rng.choice(list(plans))
        sid = f"SUB-{i + 1:06d}"
        billing_id = f"BILL-{i + 1:06d}"
        subs.append({"subscription_id": sid, "billing_customer_id": billing_id, "customer_email": str(person.email).upper() if i % 9 == 0 else person.email, "plan_code": plan, "status": "cancelled" if cancelled else "active", "start_date": start, "cancelled_at": cancelled, "monthly_price_cents": plans[plan], "currency": currencies.get(person.country, "USD"), "_planted_error": ""})
        bill_day = start
        n = 0
        while bill_day <= end and (not cancelled or bill_day <= cancelled):
            n += 1
            refund = plans[plan] if rng.random() < 0.035 else 0
            invoices.append({"invoice_id": f"INV-{i + 1:06d}-{n:02d}", "subscription_id": sid, "billing_customer_id": billing_id, "paid_at": bill_day, "refunded_at": bill_day + timedelta(days=7) if refund else None, "gross_amount_cents": plans[plan], "refund_amount_cents": refund, "currency": currencies.get(person.country, "USD"), "_planted_error": ""})
            bill_day += timedelta(days=30)
    subs_df, invoices_df = pd.DataFrame(subs), pd.DataFrame(invoices)
    _plant(subs_df, [5, 15], "invalid_date_order", lambda d, i: d.__setitem__("cancelled_at", d["cancelled_at"].mask(d.index == i, date(2024, 1, 1))))
    _plant(subs_df, [25, 35], "unknown_plan", lambda d, i: d.__setitem__("plan_code", d["plan_code"].mask(d.index == i, "ULTRA")))
    _plant(invoices_df, [10, 20], "negative_gross_amount", lambda d, i: d.__setitem__("gross_amount_cents", d["gross_amount_cents"].mask(d.index == i, -100)))
    _plant(invoices_df, [30, 40], "refund_exceeds_gross", lambda d, i: d.__setitem__("refund_amount_cents", d["refund_amount_cents"].mask(d.index == i, 999999)))

    orders, items = [], []
    product_prices = {f"PROD-{i:03d}": 500 + i * 125 for i in range(1, 25)}
    for oid in range(customers * 3):
        pidx = rng.randrange(customers)
        person = customers_df.iloc[pidx]
        ordered = datetime(2025, 9, 1) + timedelta(minutes=rng.randrange(365 * 24 * 60))
        status = rng.choices(["delivered", "refunded", "cancelled"], [0.88, 0.07, 0.05])[0]
        line_count = rng.randint(1, 3)
        total = 0
        order_id = f"ORD-{oid + 1:07d}"
        for line in range(1, line_count + 1):
            product = rng.choice(list(product_prices))
            qty = rng.randint(1, 3)
            price = product_prices[product]
            total += qty * price
            items.append({"order_id": order_id, "line_number": line, "product_id": product, "quantity": qty, "unit_price_cents": price, "_planted_error": ""})
        orders.append({"order_id": order_id, "storefront_customer_id": f"SHOP-{pidx + 1:06d}", "customer_email": person.email if oid % 7 else f" {str(person.email).upper()} ", "ordered_at": ordered, "delivered_at": ordered + timedelta(days=rng.randrange(2, 10)) if status in {"delivered", "refunded"} else None, "status": status, "order_amount_cents": total, "refund_amount_cents": total if status == "refunded" else 0, "currency": currencies.get(person.country, "USD"), "_planted_error": ""})
    orders_df, items_df = pd.DataFrame(orders), pd.DataFrame(items)
    _plant(orders_df, [7, 17], "unsupported_currency", lambda d, i: d.__setitem__("currency", d["currency"].mask(d.index == i, "XYZ")))
    _plant(orders_df, [27, 37], "delivered_before_ordered", lambda d, i: d.__setitem__("delivered_at", d["delivered_at"].mask(d.index == i, d.at[i, "ordered_at"] - timedelta(days=1))))
    _plant(orders_df, [47, 57], "missing_customer_identity", lambda d, i: (d.__setitem__("customer_email", d["customer_email"].mask(d.index == i, None)), d.__setitem__("storefront_customer_id", d["storefront_customer_id"].mask(d.index == i, None))))
    _plant(items_df, [11, 21], "nonpositive_quantity", lambda d, i: d.__setitem__("quantity", d["quantity"].mask(d.index == i, 0)))
    _plant(items_df, [31, 41], "orphan_order", lambda d, i: d.__setitem__("order_id", d["order_id"].mask(d.index == i, "ORD-MISSING")))

    tickets = []
    for tid in range(customers):
        pidx = rng.randrange(customers)
        opened = datetime(2025, 9, 1) + timedelta(minutes=rng.randrange(365 * 24 * 60))
        resolved = opened + timedelta(hours=rng.randrange(1, 120)) if rng.random() < 0.92 else None
        tickets.append({"ticket_id": f"TKT-{tid + 1:06d}", "requester_email": customers_df.iloc[pidx].email, "opened_at": opened, "resolved_at": resolved, "category": rng.choice(["billing", "delivery", "product", "account"]), "csat": int(np_rng.integers(1, 6)) if resolved else None, "_planted_error": ""})
    tickets_df = pd.DataFrame(tickets)
    _plant(tickets_df, [12, 22], "resolved_before_opened", lambda d, i: d.__setitem__("resolved_at", d["resolved_at"].mask(d.index == i, d.at[i, "opened_at"] - timedelta(hours=1))))
    _plant(tickets_df, [32, 42], "invalid_csat", lambda d, i: d.__setitem__("csat", d["csat"].mask(d.index == i, 9)))

    frames = {"customers": customers_df, "subscriptions": subs_df, "invoices": invoices_df, "orders": orders_df, "order_items": items_df, "tickets": tickets_df}
    for name, frame in frames.items():
        frame.to_csv(SOURCE / f"{name}.csv", index=False, date_format="%Y-%m-%dT%H:%M:%S")
    manifest = {"banner": "SYNTHETIC DATA — NOT REAL CUSTOMERS", "seed": seed, "customers_requested": customers, "row_counts": {k: len(v) for k, v in frames.items()}, "planted_counts": {k: int(v["_planted_error"].ne("").sum()) for k, v in frames.items()}}
    write_json(ARTIFACTS / "synthetic_manifest.json", manifest)
    return manifest["row_counts"]
