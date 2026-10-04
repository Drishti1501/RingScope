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

fraud_accounts = set(
    nodes.loc[nodes["isFraud"] == 1, "nodeid"]
)

source_fraud = transactions["sourceNodeId"].isin(fraud_accounts)
target_fraud = transactions["targetNodeId"].isin(fraud_accounts)

print("========== FRAUD ACCOUNT VALIDATION ==========")

print("Fraud accounts:", len(fraud_accounts))

print("Fraud accounts with fraudStep = -1:")
print(
    nodes[
        (nodes["isFraud"] == 1) &
        (nodes["fraudStep"] == -1)
    ].shape[0]
)

print("\n========== TRANSACTION CONNECTIONS ==========")

print("Transactions sent by fraud-labeled accounts:",
      source_fraud.sum())

print("Transactions received by fraud-labeled accounts:",
      target_fraud.sum())

print("Transactions connected to at least one fraud-labeled account:",
      (source_fraud | target_fraud).sum())

print("\n========== FRAUD STEP ==========")

print(
    nodes[nodes["isFraud"] == 1]["fraudStep"].describe()
)