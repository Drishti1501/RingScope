import pandas as pd
import networkx as nx
from itertools import combinations
from pathlib import Path


# ===================================
# 1. Set project paths
# ===================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUTS_FOLDER = PROJECT_ROOT / "outputs"


# ===================================
# 2. Load validated cycles
# ===================================

print("Loading validated cycles...")

cycles_path = OUTPUTS_FOLDER / "validated_cycles.csv"

cycles = pd.read_csv(cycles_path)

print(f"Validated cycles: {len(cycles)}")


# ===================================
# 3. Validate cycle structure
# ===================================

required_columns = [
    "account_1",
    "account_2",
    "account_3"
]

for column in required_columns:
    cycles[column] = cycles[column].astype(int)


cycles = cycles[
    cycles.apply(
        lambda row: len({
            row["account_1"],
            row["account_2"],
            row["account_3"]
        }) == 3,
        axis=1
    )
].copy()

cycles = cycles.reset_index(drop=True)

print(f"Cycles after structure validation: {len(cycles)}")


# ===================================
# 4. Create account sets
# ===================================

cycles["account_set"] = cycles.apply(
    lambda row: {
        row["account_1"],
        row["account_2"],
        row["account_3"]
    },
    axis=1
)


# ===================================
# 5. Group overlapping cycles
# ===================================

print("Grouping cycles sharing at least two accounts...")

cycle_graph = nx.Graph()

cycle_graph.add_nodes_from(cycles.index)

for cycle_a, cycle_b in combinations(cycles.index, 2):

    accounts_a = cycles.loc[cycle_a, "account_set"]
    accounts_b = cycles.loc[cycle_b, "account_set"]

    shared_accounts = accounts_a.intersection(accounts_b)

    if len(shared_accounts) >= 2:

        cycle_graph.add_edge(cycle_a, cycle_b)


components = list(
    nx.connected_components(cycle_graph)
)

print(f"Candidate groups detected: {len(components)}")


# ===================================
# 6. Assign candidate IDs
# ===================================

cycle_to_candidate = {}

for candidate_id, component in enumerate(
    components,
    start=1
):

    for cycle_index in component:

        cycle_to_candidate[cycle_index] = candidate_id


cycles["candidate_id"] = cycles.index.map(
    cycle_to_candidate
)


# ===================================
# 7. Load fraud labels
# ===================================

nodes_path = (
    PROJECT_ROOT /
    "data" /
    "raw" /
    "aml_20k_combined" /
    "nodes.csv"
)

nodes = pd.read_csv(nodes_path)

fraud_labels = dict(
    zip(
        nodes["nodeid"],
        nodes["isFraud"]
    )
)


# ===================================
# 8. Create candidate summaries
# ===================================

print("Calculating candidate features...")

candidate_results = []

for candidate_id, group_data in cycles.groupby(
    "candidate_id"
):

    accounts = set()

    for account_set in group_data["account_set"]:

        accounts.update(account_set)

    fraud_accounts = sum(
        fraud_labels.get(account_id, 0) == 1
        for account_id in accounts
    )

    account_count = len(accounts)

    cycle_count = len(group_data)

    if cycle_count == 1:

        candidate_type = "Single-cycle candidate"

    else:

        candidate_type = "Multi-cycle candidate"

    candidate_results.append({

        "candidate_id": candidate_id,

        "account_count": account_count,

        "cycle_count": cycle_count,

        "candidate_type": candidate_type,

        "fraud_accounts": fraud_accounts,

        "fraud_rate": round(
            fraud_accounts / account_count * 100,
            2
        )

    })


candidate_summary = pd.DataFrame(candidate_results)


# ===================================
# 9. Save membership file
# ===================================

membership_output = cycles.drop(
    columns=["account_set"]
)

membership_path = (
    OUTPUTS_FOLDER /
    "ring_candidate_membership.csv"
)

membership_output.to_csv(
    membership_path,
    index=False
)


# ===================================
# 10. Save candidate summary
# ===================================

candidate_summary = candidate_summary.sort_values(
    by=["cycle_count", "account_count"],
    ascending=False
)

summary_path = (
    OUTPUTS_FOLDER /
    "ring_candidates.csv"
)

candidate_summary.to_csv(
    summary_path,
    index=False
)


# ===================================
# 11. Display results
# ===================================

print("\nCandidate group distribution:")

print(
    candidate_summary[
        ["account_count", "cycle_count"]
    ].describe()
)

print("\nCandidate type distribution:")

print(
    candidate_summary["candidate_type"]
    .value_counts()
)

print("\nTop 20 candidate groups:")

print(
    candidate_summary.head(20).to_string(
        index=False
    )
)

print("\nFiles saved:")

print(membership_path)

print(summary_path)