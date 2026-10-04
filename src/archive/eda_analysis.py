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

print("========== DATASET OVERVIEW ==========")

print("Total accounts:", len(nodes))
print("Total transactions:", len(transactions))

print("\nAccount columns:")
print(nodes.columns.tolist())

print("\nTransaction columns:")
print(transactions.columns.tolist())

print("\nFraud label distribution:")
print(nodes["isFraud"].value_counts())

print("\nMissing values in accounts:")
print(nodes.isnull().sum())

print("\nMissing values in transactions:")
print(transactions.isnull().sum())

print("\nTransaction amount statistics:")
print(transactions["value"].describe())


import matplotlib.pyplot as plt

# ==============================
# FRAUD LABEL DISTRIBUTION
# ==============================

fraud_counts = nodes["isFraud"].value_counts().sort_index()

plt.figure(figsize=(7, 5))

plt.bar(
    ["Non-Fraud Labeled", "Fraud Labeled"],
    fraud_counts.values
)

plt.title("Fraud Label Distribution")
plt.xlabel("Account Type")
plt.ylabel("Number of Accounts")

plt.tight_layout()
plt.show()

# ==============================
# TRANSACTION AMOUNT DISTRIBUTION
# ==============================

plt.figure(figsize=(8, 5))

plt.hist(
    transactions["value"],
    bins=30,
    edgecolor="black"
)

plt.title("Transaction Amount Distribution")
plt.xlabel("Transaction Amount")
plt.ylabel("Number of Transactions")

plt.tight_layout()
plt.show()

# ==============================
# TRANSACTION VOLUME OVER TIME
# ==============================

time_activity = transactions.groupby("time").size()

plt.figure(figsize=(10, 5))

plt.plot(
    time_activity.index,
    time_activity.values
)

plt.title("Transaction Volume Over Time")
plt.xlabel("Time")
plt.ylabel("Number of Transactions")

plt.tight_layout()
plt.show()

# ==============================
# TOTAL TRANSACTION VALUE OVER TIME
# ==============================

value_over_time = transactions.groupby("time")["value"].sum()

plt.figure(figsize=(10, 5))

plt.plot(
    value_over_time.index,
    value_over_time.values
)

plt.title("Total Transaction Value Over Time")
plt.xlabel("Time")
plt.ylabel("Total Transaction Value")

plt.tight_layout()
plt.show()

# ==============================
# ACCOUNT-LEVEL ACTIVITY ANALYSIS
# ==============================

outgoing = transactions.groupby("sourceNodeId").agg(
    outgoing_amount=("value", "sum")
).reset_index()

outgoing.rename(
    columns={"sourceNodeId": "nodeid"},
    inplace=True
)

incoming = transactions.groupby("targetNodeId").agg(
    incoming_amount=("value", "sum")
).reset_index()

incoming.rename(
    columns={"targetNodeId": "nodeid"},
    inplace=True
)

account_activity = nodes.merge(
    outgoing,
    on="nodeid",
    how="left"
).merge(
    incoming,
    on="nodeid",
    how="left"
)

account_activity[
    ["outgoing_amount", "incoming_amount"]
] = account_activity[
    ["outgoing_amount", "incoming_amount"]
].fillna(0)

activity_summary = account_activity.groupby("isFraud")[
    ["outgoing_amount", "incoming_amount"]
].mean()

print("\n========== ACCOUNT ACTIVITY SUMMARY ==========")
print(activity_summary)

# ==============================
# VISUALIZE ACCOUNT ACTIVITY
# ==============================

activity_summary.index = [
    "Non-Fraud Labeled",
    "Fraud Labeled"
]

activity_summary.plot(
    kind="bar",
    figsize=(8, 5)
)

plt.title("Average Account Transaction Activity")
plt.xlabel("Account Type")
plt.ylabel("Average Transaction Amount")
plt.xticks(rotation=0)
plt.legend(["Outgoing Amount", "Incoming Amount"])

plt.tight_layout()
plt.show()

# ==============================
# NETWORK CONNECTIVITY ANALYSIS
# ==============================

network_metrics = nodes[["nodeid", "isFraud"]].copy()

outgoing_connections = transactions.groupby("sourceNodeId").agg(
    unique_receivers=("targetNodeId", "nunique"),
    outgoing_transactions=("targetNodeId", "count")
).reset_index()

outgoing_connections.rename(
    columns={"sourceNodeId": "nodeid"},
    inplace=True
)

incoming_connections = transactions.groupby("targetNodeId").agg(
    unique_senders=("sourceNodeId", "nunique"),
    incoming_transactions=("sourceNodeId", "count")
).reset_index()

incoming_connections.rename(
    columns={"targetNodeId": "nodeid"},
    inplace=True
)

network_metrics = network_metrics.merge(
    outgoing_connections,
    on="nodeid",
    how="left"
).merge(
    incoming_connections,
    on="nodeid",
    how="left"
)

network_metrics = network_metrics.fillna(0)

print("\n========== NETWORK CONNECTIVITY ==========")

print("\nTop accounts by unique receivers:")
print(
    network_metrics.sort_values(
        "unique_receivers",
        ascending=False
    ).head(15)
)

print("\nTop accounts by unique senders:")
print(
    network_metrics.sort_values(
        "unique_senders",
        ascending=False
    ).head(15)
)

# ==============================
# AVERAGE NETWORK CONNECTIVITY
# ==============================

connectivity_summary = network_metrics.groupby("isFraud")[
    ["unique_receivers", "unique_senders"]
].mean()

print("\n========== AVERAGE CONNECTIVITY ==========")
print(connectivity_summary)

connectivity_summary.index = [
    "Non-Fraud Labeled",
    "Fraud Labeled"
]

connectivity_summary.plot(
    kind="bar",
    figsize=(8, 5)
)

plt.title("Average Account Connectivity")
plt.xlabel("Account Type")
plt.ylabel("Average Number of Connections")
plt.xticks(rotation=0)
plt.legend(["Unique Receivers", "Unique Senders"])

plt.tight_layout()
plt.show()