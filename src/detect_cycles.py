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

print("========== 3-CYCLE DETECTION ==========")
print(f"Total transactions: {len(transactions)}")


# ==========================================
# 3. BUILD DIRECTED ADJACENCY LIST
# ==========================================

neighbors = {}

for row in transactions.itertuples(index=False):

    source = int(row.sourceNodeId)
    target = int(row.targetNodeId)

    # Ignore self-transactions
    if source == target:
        continue

    if source not in neighbors:
        neighbors[source] = set()

    neighbors[source].add(target)


print(f"Accounts with outgoing transactions: {len(neighbors)}")


# ==========================================
# 4. DETECT VALID DIRECTED 3-CYCLES
# ==========================================

cycles = set()

for first, second_targets in neighbors.items():

    # First transaction: first -> second
    for second in second_targets:

        if second == first:
            continue

        # Second transaction: second -> third
        for third in neighbors.get(second, set()):

            if third == first or third == second:
                continue

            # Third transaction: third -> first
            if first in neighbors.get(third, set()):

                # Store each group only once
                cycle = tuple(sorted([first, second, third]))

                cycles.add(cycle)


# ==========================================
# 5. DISPLAY RESULTS
# ==========================================

print(f"Unique valid 3-account cycles: {len(cycles)}")

print("\nFirst 20 cycles:")

for cycle in list(cycles)[:20]:
    print(cycle)


# ==========================================
# 6. SAVE CYCLES
# ==========================================

cycle_data = []

for cycle in cycles:

    first, second, third = cycle

    cycle_data.append({
        "account_1": first,
        "account_2": second,
        "account_3": third
    })


cycle_summary = pd.DataFrame(cycle_data)

output_file = output_folder / "three_account_cycles.csv"

cycle_summary.to_csv(output_file, index=False)


# ==========================================
# 7. ANALYSE FRAUD LABELS
# ==========================================

fraud_labels = nodes.set_index("nodeid")["isFraud"].to_dict()

if not cycle_summary.empty:

    cycle_summary["fraud_accounts"] = cycle_summary.apply(
        lambda row: sum(
            fraud_labels.get(account, 0)
            for account in [
                row["account_1"],
                row["account_2"],
                row["account_3"]
            ]
        ),
        axis=1
    )

    cycle_summary["fraud_percentage"] = (
        cycle_summary["fraud_accounts"] / 3 * 100
    )

    cycle_summary["contains_fraud"] = (
        cycle_summary["fraud_accounts"] > 0
    )

    # Save enhanced cycle analysis
    analysis_file = output_folder / "three_account_cycles_analysis.csv"

    cycle_summary.to_csv(analysis_file, index=False)

    print("\n========== FRAUD LABEL ANALYSIS ==========")

    print(
        "Cycles containing at least one fraud-labeled account:",
        cycle_summary["contains_fraud"].sum()
    )

    print(
        "Cycles containing no fraud-labeled accounts:",
        (~cycle_summary["contains_fraud"]).sum()
    )

    print("\nFraud-account distribution per cycle:")

    print(
        cycle_summary["fraud_accounts"].value_counts().sort_index()
    )

else:

    print("\nNo valid 3-account cycles found.")


# ==========================================
# 8. FINAL MESSAGE
# ==========================================

print("\nCycle analysis saved successfully.")
print(f"Saved file: {output_file}")