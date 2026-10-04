import pandas as pd
from pathlib import Path
from itertools import permutations


# -----------------------------------------
# 1. File paths
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CYCLE_FILE = (
    BASE_DIR
    / "outputs"
    / "three_account_cycles.csv"
)

TRANSACTION_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "aml_20k_combined"
    / "transactions.csv"
)


# -----------------------------------------
# 2. Load data
# -----------------------------------------

print("Loading data...")

cycles = pd.read_csv(CYCLE_FILE)
transactions = pd.read_csv(TRANSACTION_FILE)

print(f"Total cycle records: {len(cycles)}")
print(f"Total transactions: {len(transactions)}")


# -----------------------------------------
# 3. Create transaction edge lookup
# -----------------------------------------

transaction_edges = set(
    zip(
        transactions["sourceNodeId"].astype(int),
        transactions["targetNodeId"].astype(int)
    )
)


# -----------------------------------------
# 4. Validate cycles
# -----------------------------------------

valid_cycles = []
invalid_cycles = []

seen_cycles = set()

for _, row in cycles.iterrows():

    accounts = [
        int(row["account_1"]),
        int(row["account_2"]),
        int(row["account_3"])
    ]

    # Check for repeated accounts
    if len(set(accounts)) != 3:

        invalid_cycles.append({
            "accounts": accounts,
            "reason": "Repeated account"
        })

        continue

    cycle_found = False
    valid_order = None

    # Check every possible ordering
    for order in permutations(accounts):

        first, second, third = order

        edges = [
            (first, second),
            (second, third),
            (third, first)
        ]

        if all(
            edge in transaction_edges
            for edge in edges
        ):

            cycle_found = True
            valid_order = order
            break

    if cycle_found:

        # Canonical representation prevents duplicates
        canonical_cycle = tuple(sorted(accounts))

        if canonical_cycle not in seen_cycles:

            seen_cycles.add(canonical_cycle)

            valid_cycles.append({
                "account_1": valid_order[0],
                "account_2": valid_order[1],
                "account_3": valid_order[2]
            })

    else:

        invalid_cycles.append({
            "accounts": accounts,
            "reason": "No valid directed ordering"
        })


# -----------------------------------------
# 5. Display results
# -----------------------------------------

print("\nValidation Results")
print("-------------------------")

print(f"Original cycles: {len(cycles)}")

print(
    f"Valid directed cycles: "
    f"{len(valid_cycles)}"
)

print(
    f"Invalid cycles: "
    f"{len(invalid_cycles)}"
)


# -----------------------------------------
# 6. Display invalid examples
# -----------------------------------------

if invalid_cycles:

    print("\nExamples of invalid cycles:")

    for example in invalid_cycles[:10]:

        print(example)


# -----------------------------------------
# 7. Save validated cycles
# -----------------------------------------

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "validated_cycles.csv"
)

validated_data = pd.DataFrame(valid_cycles)

validated_data.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\nValidated cycles saved to:\n"
    f"{OUTPUT_FILE}"
)