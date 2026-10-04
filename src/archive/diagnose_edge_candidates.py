import pandas as pd
from pathlib import Path
from collections import defaultdict


# -----------------------------------------
# 1. File paths
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CYCLE_FILE = (
    BASE_DIR
    / "outputs"
    / "validated_cycles.csv"
)

CANDIDATE_FILE = (
    BASE_DIR
    / "outputs"
    / "edge_based_candidates.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "shared_edge_analysis.csv"
)


# -----------------------------------------
# 2. Load data
# -----------------------------------------

print("Loading data...")

cycles = pd.read_csv(CYCLE_FILE)

candidates = pd.read_csv(CANDIDATE_FILE)

print(f"Total cycles: {len(cycles)}")


# -----------------------------------------
# 3. Create edge-to-cycle mapping
# -----------------------------------------

print("Analyzing shared directed edges...")

edge_to_cycles = defaultdict(list)

for cycle_index, row in cycles.iterrows():

    first = int(row["account_1"])
    second = int(row["account_2"])
    third = int(row["account_3"])

    edges = [
        (first, second),
        (second, third),
        (third, first)
    ]

    for edge in edges:

        if cycle_index not in edge_to_cycles[edge]:

            edge_to_cycles[edge].append(
                cycle_index
            )


# -----------------------------------------
# 4. Create shared-edge records
# -----------------------------------------

shared_edge_records = []

for edge, cycle_indexes in edge_to_cycles.items():

    if len(cycle_indexes) < 2:

        continue

    source, target = edge

    shared_edge_records.append({

        "source_account": source,

        "target_account": target,

        "cycle_count": len(cycle_indexes),

        "cycle_indexes": ",".join(
            str(index)
            for index in cycle_indexes
        )

    })


shared_edges = pd.DataFrame(
    shared_edge_records
)


# -----------------------------------------
# 5. Display shared-edge results
# -----------------------------------------

if len(shared_edges) > 0:

    shared_edges = shared_edges.sort_values(
        by="cycle_count",
        ascending=False
    )

    print("\nTop shared directed edges:")
    print("-" * 60)

    print(
        shared_edges.head(20).to_string(
            index=False
        )
    )

else:

    print("No shared directed edges found.")


# -----------------------------------------
# 6. Analyze candidate size distribution
# -----------------------------------------

print("\nCandidate size distribution:")
print("-" * 60)

print(
    candidates[
        [
            "account_count",
            "cycle_count",
            "edge_count"
        ]
    ].describe()
)


# -----------------------------------------
# 7. Display large candidate groups
# -----------------------------------------

large_candidates = candidates[
    candidates["cycle_count"] >= 10
].sort_values(
    by="cycle_count",
    ascending=False
)


print("\nLarge candidate groups:")
print("-" * 60)

if len(large_candidates) > 0:

    print(
        large_candidates[
            [
                "candidate_id",
                "account_count",
                "cycle_count",
                "edge_count",
                "fraud_accounts",
                "fraud_rate"
            ]
        ].to_string(index=False)
    )

else:

    print("No candidate groups with 10 or more cycles.")


# -----------------------------------------
# 8. Save shared-edge analysis
# -----------------------------------------

shared_edges.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\nShared-edge analysis saved to:\n"
    f"{OUTPUT_FILE}"
)