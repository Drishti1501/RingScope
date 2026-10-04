import pandas as pd
from pathlib import Path


# -----------------------------------------
# 1. File paths
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CANDIDATE_FILE = (
    BASE_DIR
    / "outputs"
    / "ring_candidates.csv"
)


# -----------------------------------------
# 2. Load candidates
# -----------------------------------------

candidates = pd.read_csv(CANDIDATE_FILE)


# -----------------------------------------
# 3. Display largest candidate groups
# -----------------------------------------

large_groups = candidates[
    candidates["cycle_count"] >= 3
].sort_values(
    by="cycle_count",
    ascending=False
)


print("\nCandidate groups with at least 3 cycles:")
print("-" * 60)

print(
    large_groups[
        [
            "candidate_id",
            "account_count",
            "cycle_count",
            "fraud_accounts",
            "fraud_rate"
        ]
    ].to_string(index=False)
)


# -----------------------------------------
# 4. Inspect account composition
# -----------------------------------------

print("\n\nDetailed account composition:")
print("-" * 60)

for _, row in large_groups.head(10).iterrows():

    print(
        f"\nCandidate ID: {row['candidate_id']}"
    )

    print(
        f"Accounts: {row['account_count']}"
    )

    print(
        f"Cycles: {row['cycle_count']}"
    )

    print(
        f"Fraud-labeled accounts: "
        f"{row['fraud_accounts']}"
    )

    print(
        f"Fraud rate: "
        f"{row['fraud_rate']:.2f}%"
    )

    print(
        f"Account IDs: {row['accounts']}"
    )