import pandas as pd
from pathlib import Path


# -----------------------------------------
# 1. Define file paths
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CYCLE_FILE = (
    BASE_DIR
    / "outputs"
    / "validated_cycles.csv"
)

TRANSACTION_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "aml_20k_combined"
    / "transactions.csv"
)

NODE_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "aml_20k_combined"
    / "nodes.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "cycle_investigation_table.csv"
)


# -----------------------------------------
# 2. Load data
# -----------------------------------------

print("Loading data...")

cycles = pd.read_csv(CYCLE_FILE)

transactions = pd.read_csv(TRANSACTION_FILE)

nodes = pd.read_csv(NODE_FILE)

print(f"Cycles loaded: {len(cycles)}")
print(f"Transactions loaded: {len(transactions)}")


# -----------------------------------------
# 3. Create fraud-label lookup
# -----------------------------------------

fraud_lookup = dict(
    zip(
        nodes["nodeid"].astype(int),
        nodes["isFraud"].astype(int)
    )
)


# -----------------------------------------
# 4. Create transaction lookup
# -----------------------------------------

print("Creating transaction lookup...")

transaction_lookup = {}

for _, row in transactions.iterrows():

    source = int(row["sourceNodeId"])

    target = int(row["targetNodeId"])

    value = float(row["value"])

    key = (source, target)

    if key not in transaction_lookup:

        transaction_lookup[key] = []

    transaction_lookup[key].append(value)


# -----------------------------------------
# 5. Analyze each cycle
# -----------------------------------------

print("Analyzing cycles...")

investigation_records = []


for cycle_id, row in cycles.iterrows():

    account_1 = int(row["account_1"])

    account_2 = int(row["account_2"])

    account_3 = int(row["account_3"])


    # Directed edges forming the cycle

    edges = [
        (account_1, account_2),
        (account_2, account_3),
        (account_3, account_1)
    ]


    cycle_values = []

    edge_transaction_counts = []


    for source, target in edges:

        values = transaction_lookup.get(
            (source, target),
            []
        )

        cycle_values.extend(values)

        edge_transaction_counts.append(
            len(values)
        )


    transaction_count = len(cycle_values)


    if transaction_count > 0:

        total_value = sum(cycle_values)

        average_value = (
            total_value / transaction_count
        )

    else:

        total_value = 0

        average_value = 0


    accounts = [
        account_1,
        account_2,
        account_3
    ]


    fraud_account_count = sum(
        fraud_lookup.get(account, 0)
        for account in accounts
    )


    contains_fraud_label = (
        fraud_account_count > 0
    )


    investigation_records.append({

        "cycle_id": cycle_id + 1,

        "account_1": account_1,

        "account_2": account_2,

        "account_3": account_3,

        "transaction_count": transaction_count,

        "total_value": round(
            total_value,
            2
        ),

        "average_value": round(
            average_value,
            2
        ),

        "max_edge_transaction_count": max(
            edge_transaction_counts
        ),

        "fraud_account_count": (
            fraud_account_count
        ),

        "contains_fraud_label": (
            contains_fraud_label
        )

    })


# -----------------------------------------
# 6. Create final table
# -----------------------------------------

investigation_table = pd.DataFrame(
    investigation_records
)


# -----------------------------------------
# 7. Sort by total transaction value
# -----------------------------------------

investigation_table = investigation_table.sort_values(
    by="total_value",
    ascending=False
).reset_index(drop=True)


# -----------------------------------------
# 8. Display results
# -----------------------------------------

print("\nInvestigation table preview:")
print("-" * 70)

print(
    investigation_table.head(10).to_string(
        index=False
    )
)


print("\nInvestigation table summary:")
print("-" * 70)

print(
    investigation_table[
        [
            "transaction_count",
            "total_value",
            "average_value",
            "fraud_account_count"
        ]
    ].describe()
)


print("\nCycles containing fraud labels:")

print(
    investigation_table[
        "contains_fraud_label"
    ].value_counts()
)


# -----------------------------------------
# 9. Save table
# -----------------------------------------

investigation_table.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\nInvestigation table saved to:\n"
    f"{OUTPUT_FILE}"
)