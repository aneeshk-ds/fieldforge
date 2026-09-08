# Northstar Commerce customer brief

Northstar Commerce is a fictional direct-to-consumer subscription retailer operating in the United States, Canada, and the United Kingdom. It sells monthly Essentials, Plus, and Premium boxes plus one-off add-ons.

## Business situation

Growth has outpaced the reporting process. CRM contacts, billing subscriptions/invoices, storefront orders, and support tickets arrive as independent extracts. Email casing, phone formatting, duplicated contacts, late status changes, refunds, and currency representation make executive reporting inconsistent.

## Stakeholder questions

- How many active subscribers do we have at month end?
- What are gross revenue, refunds, and net revenue by month, plan, and market?
- How many customers churn and what is logo churn?
- Do delayed orders correlate with support demand?
- Which records cannot safely enter reporting, and why?

## Delivery constraints

The proof of value must run locally, use synthetic data, cost nothing beyond a laptop, expose its assumptions, and be transferable to an internal engineering team.

## Discovery assumptions to validate in a real engagement

Invoice `paid_at` is the revenue recognition event; refunds reduce net revenue on refund date; active subscribers are snapshotted at calendar month end; email exact match is permitted only after normalization; phone match requires a country-aware normalized value; manual review owns ambiguous collisions.
