"""Generate the two Assignment 3 datasets.

The Duka generator is reproduced exactly as supplied. The agent generator is
a deterministic reconstruction from the assignment specifications because
the original practical source could not be located.
"""
import numpy as np
import pandas as pd

# Duka Electronics generator — supplied practical code; kept unchanged.
rng = np.random.default_rng(2026)
n = 1000
products = {"Phone": 15000, "Laptop": 65000, "Headphones": 2500,
            "Tablet": 28000, "Charger": 1200}
sales = pd.DataFrame({
    "order_id": range(1001, 1001 + n),
    "order_date": pd.to_datetime("2026-01-01")
                  + pd.to_timedelta(rng.integers(0, 180, n), unit="D"),
    "branch": rng.choice(["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"], n,
                         p=[0.4, 0.2, 0.15, 0.15, 0.1]),
    "product": rng.choice(list(products), n),
    "quantity": rng.integers(1, 6, n),
    "channel": rng.choice(["In-store", "Online", "Phone order"], n,
                          p=[0.55, 0.35, 0.10]),
})
sales["unit_price"] = sales["product"].map(products)
sales.to_csv("duka_sales.csv", index=False)

# Agent-network generator — reconstructed from the assignment specifications.
agent_rng = np.random.default_rng(44)
agent_ids = [f"AG{i:03d}" for i in range(1, 21)]
counties = ["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Kisumu"]
agents = pd.DataFrame({
    "agent_id": agent_ids,
    "agent_name": [f"Agent {i:02d}" for i in range(1, 21)],
    "county": agent_rng.choice(counties, 20),
    "onboarded_date": pd.date_range("2024-01-01", periods=20, freq="MS").strftime("%Y-%m-%d"),
})
n_txns = 600
base_dates = pd.Timestamp("2026-03-01") + pd.to_timedelta(agent_rng.integers(0, 60, n_txns), unit="D")
txns = pd.DataFrame({
    "txn_id": [f"TX{i:04d}" for i in range(1, n_txns + 1)],
    "agent_id": agent_rng.choice(agent_ids, n_txns),
    "txn_type": agent_rng.choice(["Deposit", "withdrawal", "DEPOSIT ", "Withdrawal", "deposit"], n_txns),
    "amount": np.round(agent_rng.lognormal(mean=7.5, sigma=0.8, size=n_txns), 2).astype(object),
    "txn_date": pd.Series(base_dates).dt.strftime("%Y-%m-%d").to_numpy(),
})
missing_idx = agent_rng.choice(txns.index, 15, replace=False)
for i in missing_idx:
    txns.loc[i, "amount"] = np.nan
remaining = np.array([i for i in txns.index if i not in set(missing_idx)])
na_idx = agent_rng.choice(remaining, 5, replace=False)
for i in na_idx:
    txns.loc[i, "amount"] = "N/A"
remaining = np.array([i for i in txns.index if i not in set(missing_idx) and i not in set(na_idx)])
high_idx = agent_rng.choice(remaining, 5, replace=False)
for i in high_idx:
    txns.loc[i, "amount"] = "250000"
slash_idx = agent_rng.choice(txns.index, 5, replace=False)
for i in slash_idx:
    txns.loc[i, "txn_date"] = pd.to_datetime(txns.loc[i, "txn_date"]).strftime("%d/%m/%Y")
unknown_idx = agent_rng.choice(txns.index, 8, replace=False)
for i in unknown_idx:
    txns.loc[i, "agent_id"] = "AG099"
txns = pd.concat([txns, txns.sample(n=12, random_state=44)], ignore_index=True)
agents.to_csv("agents.csv", index=False)
txns.to_csv("agent_transactions.csv", index=False)
