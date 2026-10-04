from pathlib import Path
import pandas as pd


# 1. Set paths
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_FOLDER
    / "outputs"
    / "final_candidate_features.csv"
)


# 2. Load data
data = pd.read_csv(INPUT_FILE)

print("Feature table loaded successfully.")
print("Total rows:", len(data))


# 3. Check duplicate candidate IDs
print("\nDuplicate candidate IDs:")

duplicates = data[
    data["candidate_id"].duplicated()
]

print(len(duplicates))


# 4. Check missing values
print("\nMissing values:")

print(data.isnull().sum())


# 5. Check negative transaction values
value_columns = [
    "internal_transaction_value",
    "incoming_transaction_value",
    "outgoing_transaction_value"
]

print("\nNegative values:")

for column in value_columns:

    negative_count = (
        data[column] < 0
    ).sum()

    print(column, ":", negative_count)


# 6. Check fraud-label consistency
invalid_fraud_counts = data[
    data["fraud_label_count"]
    > data["account_count"]
]

print("\nInvalid fraud-label counts:")
print(len(invalid_fraud_counts))


# 7. Check impossible account and cycle counts
invalid_structure = data[
    (data["account_count"] <= 0)
    | (data["cycle_count"] <= 0)
]

print("\nInvalid account or cycle counts:")
print(len(invalid_structure))


# 8. Display summary statistics
print("\nSummary statistics:")

print(
    data[
        [
            "account_count",
            "cycle_count",
            "internal_transaction_count",
            "internal_transaction_value",
            "incoming_transaction_value",
            "outgoing_transaction_value"
        ]
    ].describe()
)


print("\nValidation completed.")