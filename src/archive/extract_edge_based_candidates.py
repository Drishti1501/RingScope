import pandas as pd
from pathlib import Path


# -----------------------------------------
# 1. File paths
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CYCLE_FILE = (
    BASE_DIR
    / "outputs"
    / "validated_cycles.csv"
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
    / "edge_based_candidates.csv"
)


# -----------------------------------------
# 2. Load data
# -----------------------------------------

print("Loading validated cycles...")

cycles = pd.read_csv(CYCLE_FILE)

nodes = pd.read_csv(NODE_FILE)

print(f"Total cycles: {len(cycles)}")


# -----------------------------------------
# 3. Validate cycle structure
# -----------------------------------------

cycles = cycles[
    (cycles["account_1"] != cycles["account_2"])
    & (cycles["account_2"] != cycles["account_3"])
    & (cycles["account_1"] != cycles["account_3"])
].copy()

cycles = cycles.reset_index(drop=True)

print(f"Valid cycles: {len(cycles)}")


# -----------------------------------------
# 4. Create directed edges for each cycle
# -----------------------------------------

cycle_edges = []

for _, row in cycles.iterrows():

    first = int(row["account_1"])
    second = int(row["account_2"])
    third = int(row["account_3"])

    edges = {
        (first, second),
        (second, third),
        (third, first)
    }

    cycle_edges.append(edges)


# -----------------------------------------
# 5. Union-Find initialization
# -----------------------------------------

parent = list(range(len(cycle_edges)))


def find_parent(node):

    while parent[node] != node:

        parent[node] = parent[parent[node]]

        node = parent[node]

    return node


def merge_groups(first, second):

    first_root = find_parent(first)
    second_root = find_parent(second)

    if first_root != second_root:

        parent[second_root] = first_root


# -----------------------------------------
# 6. Build edge-to-cycle mapping
# -----------------------------------------

print("Finding shared directed edges...")

edge_to_cycles = {}

for cycle_index, edges in enumerate(cycle_edges):

    for edge in edges:

        if edge not in edge_to_cycles:

            edge_to_cycles[edge] = []

        edge_to_cycles[edge].append(cycle_index)


# -----------------------------------------
# 7. Group cycles sharing an edge
# -----------------------------------------

for edge, cycle_indexes in edge_to_cycles.items():

    if len(cycle_indexes) < 2:

        continue

    first_cycle = cycle_indexes[0]

    for other_cycle in cycle_indexes[1:]:

        merge_groups(
            first_cycle,
            other_cycle
        )


# -----------------------------------------
# 8. Assign candidate IDs
# -----------------------------------------

group_mapping = {}

next_candidate_id = 1

candidate_ids = []

for cycle_index in range(len(cycle_edges)):

    root = find_parent(cycle_index)

    if root not in group_mapping:

        group_mapping[root] = next_candidate_id

        next_candidate_id += 1

    candidate_ids.append(
        group_mapping[root]
    )


cycles["candidate_id"] = candidate_ids

print(
    f"Candidate groups detected: "
    f"{len(group_mapping)}"
)


# -----------------------------------------
# 9. Create fraud lookup
# -----------------------------------------

fraud_lookup = dict(
    zip(
        nodes["nodeid"].astype(int),
        nodes["isFraud"]
    )
)


# -----------------------------------------
# 10. Calculate candidate features
# -----------------------------------------

candidate_records = []

for candidate_id, group in cycles.groupby(
    "candidate_id"
):

    accounts = set()

    shared_edges = set()

    for _, row in group.iterrows():

        first = int(row["account_1"])
        second = int(row["account_2"])
        third = int(row["account_3"])

        accounts.update([
            first,
            second,
            third
        ])

        shared_edges.update([
            (first, second),
            (second, third),
            (third, first)
        ])


    fraud_accounts = sum(
        fraud_lookup.get(account, 0)
        for account in accounts
    )

    account_count = len(accounts)

    fraud_rate = (
        fraud_accounts / account_count * 100
        if account_count > 0
        else 0
    )


    candidate_records.append({

        "candidate_id": candidate_id,

        "account_count": account_count,

        "cycle_count": len(group),

        "edge_count": len(shared_edges),

        "fraud_accounts": fraud_accounts,

        "fraud_rate": fraud_rate,

        "accounts": ",".join(
            str(account)
            for account in sorted(accounts)
        )

    })


candidate_data = pd.DataFrame(candidate_records)


# -----------------------------------------
# 11. Classify candidate type
# -----------------------------------------

candidate_data["candidate_type"] = (
    candidate_data["cycle_count"]
    .apply(
        lambda count:
        "Multi-cycle candidate"
        if count >= 2
        else "Single-cycle candidate"
    )
)


# -----------------------------------------
# 12. Sort candidates
# -----------------------------------------

candidate_data = candidate_data.sort_values(
    by=[
        "cycle_count",
        "account_count"
    ],
    ascending=False
).reset_index(drop=True)


# -----------------------------------------
# 13. Display results
# -----------------------------------------

print("\nCandidate distribution:")

print(
    candidate_data[
        [
            "account_count",
            "cycle_count",
            "edge_count"
        ]
    ].describe()
)


print("\nCandidate type distribution:")

print(
    candidate_data["candidate_type"]
    .value_counts()
)


print("\nTop 20 candidates:")

print(
    candidate_data[
        [
            "candidate_id",
            "account_count",
            "cycle_count",
            "edge_count",
            "candidate_type",
            "fraud_accounts",
            "fraud_rate"
        ]
    ].head(20).to_string(index=False)
)


# -----------------------------------------
# 14. Save results
# -----------------------------------------

candidate_data.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\nResults saved to:\n"
    f"{OUTPUT_FILE}"
)