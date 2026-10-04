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

print("========== NODE ANALYSIS ==========")

print("Total accounts:", len(nodes))
print("Fraud label distribution:")
print(nodes["isFraud"].value_counts())

print("\nFraud percentage:")
print(nodes["isFraud"].mean() * 100)

print("\nFraudStep distribution:")
print(nodes["fraudStep"].value_counts().head(10))


print("\n========== TRANSACTION ANALYSIS ==========")

print("Total transactions:", len(transactions))

print("\nTransaction time range:")
print(transactions["time"].min(), "to", transactions["time"].max())

print("\nTransaction amount statistics:")
print(transactions["value"].describe())


print("\n========== NETWORK QUALITY CHECK ==========")

print("Unique source accounts:",
      transactions["sourceNodeId"].nunique())

print("Unique target accounts:",
      transactions["targetNodeId"].nunique())

print("Self-transactions:",
      (transactions["sourceNodeId"] == transactions["targetNodeId"]).sum())

print("Duplicate transactions:",
      transactions.duplicated().sum())