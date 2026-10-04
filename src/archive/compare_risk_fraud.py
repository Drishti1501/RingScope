import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

data_folder = (
    project_folder
    / "data"
    / "raw"
    / "aml_20k_combined"
)

output_folder = project_folder / "outputs"

risk_data = pd.read_csv(
    output_folder / "account_network_metrics.csv"
)

# ==============================
# FRAUD LABEL COMPARISON
# ==============================

print("========== FRAUD VS NON-FRAUD ==========")

summary = risk_data.groupby("isFraud")[
    [
        "outgoing_transactions",
        "outgoing_amount",
        "unique_receivers",
        "incoming_transactions",
        "incoming_amount",
        "unique_senders"
    ]
].mean()

print(summary)

# ==============================
# TOP ACCOUNTS AND FRAUD LABEL
# ==============================

print("\n========== TOP OUTGOING ACCOUNTS ==========")

top_accounts = risk_data.sort_values(
    "outgoing_amount",
    ascending=False
).head(20)

print(
    top_accounts[
        [
            "nodeid",
            "isFraud",
            "fraudStep",
            "outgoing_amount",
            "outgoing_transactions",
            "unique_receivers"
        ]
    ]
)

# ==============================
# FRAUD RATE AMONG HIGH-ACTIVITY ACCOUNTS
# ==============================

threshold = risk_data["outgoing_amount"].quantile(0.95)

high_activity = risk_data[
    risk_data["outgoing_amount"] >= threshold
]

print("\n========== HIGH-ACTIVITY ACCOUNTS ==========")

print("Threshold:", threshold)
print("Number of accounts:", len(high_activity))
print("Fraud-labeled accounts:", high_activity["isFraud"].sum())
print(
    "Fraud percentage:",
    high_activity["isFraud"].mean() * 100
)