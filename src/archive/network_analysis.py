import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

data_folder = (
    project_folder
    / "data"
    / "raw"
    / "aml_20k_combined"
)

nodes = pd.read_csv(data_folder / "nodes.csv")
transactions = pd.read_csv(data_folder / "transactions.csv")

# ==============================
# OUTGOING ACCOUNT ANALYSIS
# ==============================

outgoing = transactions.groupby("sourceNodeId").agg(
    outgoing_transactions=("targetNodeId", "count"),
    outgoing_amount=("value", "sum"),
    unique_receivers=("targetNodeId", "nunique")
).reset_index()

outgoing.rename(
    columns={"sourceNodeId": "nodeid"},
    inplace=True
)

# ==============================
# INCOMING ACCOUNT ANALYSIS
# ==============================

incoming = transactions.groupby("targetNodeId").agg(
    incoming_transactions=("sourceNodeId", "count"),
    incoming_amount=("value", "sum"),
    unique_senders=("sourceNodeId", "nunique")
).reset_index()

incoming.rename(
    columns={"targetNodeId": "nodeid"},
    inplace=True
)

# ==============================
# COMBINE ACCOUNT METRICS
# ==============================

risk_data = nodes.merge(
    outgoing,
    on="nodeid",
    how="left"
)

risk_data = risk_data.merge(
    incoming,
    on="nodeid",
    how="left"
)

# Replace missing values with zero
numeric_columns = [
    "outgoing_transactions",
    "outgoing_amount",
    "unique_receivers",
    "incoming_transactions",
    "incoming_amount",
    "unique_senders"
]

risk_data[numeric_columns] = risk_data[numeric_columns].fillna(0)

# ==============================
# DISPLAY RESULTS
# ==============================

print("========== NETWORK RISK ANALYSIS ==========")

print("\nTop 10 accounts by outgoing amount:")
print(
    risk_data[
        ["nodeid", "outgoing_amount", "outgoing_transactions"]
    ]
    .sort_values("outgoing_amount", ascending=False)
    .head(10)
)

print("\nTop 10 accounts by number of receivers:")
print(
    risk_data[
        ["nodeid", "unique_receivers", "outgoing_amount"]
    ]
    .sort_values("unique_receivers", ascending=False)
    .head(10)
)

print("\nTop 10 accounts by incoming amount:")
print(
    risk_data[
        ["nodeid", "incoming_amount", "incoming_transactions"]
    ]
    .sort_values("incoming_amount", ascending=False)
    .head(10)
)

# Save results
output_folder = project_folder / "outputs"
output_folder.mkdir(exist_ok=True)

risk_data.to_csv(
    output_folder / "account_network_metrics.csv",
    index=False
)

print("\nAnalysis saved successfully.")