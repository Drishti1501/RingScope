import pandas as pd
from pathlib import Path


# ==========================================
# 1. SET PROJECT PATHS
# ==========================================

project_folder = Path(__file__).resolve().parent.parent

data_folder = project_folder / "data" / "raw" / "aml_20k_combined"
output_folder = project_folder / "outputs"

output_folder.mkdir(exist_ok=True)


# ==========================================
# 2. LOAD DATA
# ==========================================

nodes = pd.read_csv(data_folder / "nodes.csv")

transactions = pd.read_csv(
    data_folder / "transactions.csv"
)

cycles = pd.read_csv(
    output_folder / "three_account_cycles_analysis.csv"
)


# ==========================================
# 3. CREATE FRAUD LABEL LOOKUP
# ==========================================

fraud_labels = nodes.set_index("nodeid")["isFraud"].to_dict()


# ==========================================
# 4. CREATE TRANSACTION LOOKUP
# ==========================================

transaction_lookup = {}

for row in transactions.itertuples(index=False):

    source = int(row.sourceNodeId)
    target = int(row.targetNodeId)
    value = float(row.value)

    key = (source, target)

    if key not in transaction_lookup:
        transaction_lookup[key] = []

    transaction_lookup[key].append(value)


# ==========================================
# 5. ANALYZE EACH CYCLE
# ==========================================

cycle_results = []

for row in cycles.itertuples(index=False):

    accounts = [
        int(row.account_1),
        int(row.account_2),
        int(row.account_3)
    ]

    first, second, third = accounts

    # Possible directed cycle arrangements
    possible_cycles = [
        (first, second, third),
        (first, third, second),
        (second, first, third),
        (second, third, first),
        (third, first, second),
        (third, second, first)
    ]

    selected_cycle = None

    for a, b, c in possible_cycles:

        edge_1 = (a, b)
        edge_2 = (b, c)
        edge_3 = (c, a)

        if (
            edge_1 in transaction_lookup
            and edge_2 in transaction_lookup
            and edge_3 in transaction_lookup
        ):
            selected_cycle = (a, b, c)
            break

    # Skip if a valid directed arrangement is not found
    if selected_cycle is None:
        continue

    a, b, c = selected_cycle

    values_1 = transaction_lookup[(a, b)]
    values_2 = transaction_lookup[(b, c)]
    values_3 = transaction_lookup[(c, a)]

    total_value = (
        sum(values_1)
        + sum(values_2)
        + sum(values_3)
    )

    transaction_count = (
        len(values_1)
        + len(values_2)
        + len(values_3)
    )

    fraud_count = sum(
        fraud_labels.get(account, 0)
        for account in accounts
    )

    cycle_results.append({

        "account_1": a,
        "account_2": b,
        "account_3": c,

        "transaction_count": transaction_count,

        "total_transaction_value": round(
            total_value, 2
        ),

        "average_transaction_value": round(
            total_value / transaction_count, 2
        ),

        "fraud_accounts": fraud_count,

        "fraud_percentage": round(
            fraud_count / 3 * 100, 2
        ),

        "contains_fraud": fraud_count > 0

    })


# ==========================================
# 6. SAVE RESULTS
# ==========================================

results = pd.DataFrame(cycle_results)

output_file = (
    output_folder / "cycle_transaction_analysis.csv"
)

results.to_csv(output_file, index=False)


# ==========================================
# 7. DISPLAY SUMMARY
# ==========================================

print("========== CYCLE TRANSACTION ANALYSIS ==========")

print(f"Analyzed cycles: {len(results)}")

if not results.empty:

    print("\nTotal transaction value summary:")

    print(
        results["total_transaction_value"].describe()
    )

    print("\nTransaction count summary:")

    print(
        results["transaction_count"].describe()
    )

    print("\nTop 10 cycles by transaction value:")

    print(
        results.sort_values(
            "total_transaction_value",
            ascending=False
        ).head(10)
    )

    print("\nCycles by fraud-account count:")

    print(
        results["fraud_accounts"].value_counts().sort_index()
    )

else:

    print("No cycles could be analyzed.")


print("\nAnalysis saved successfully.")

print(f"Saved file: {output_file}")