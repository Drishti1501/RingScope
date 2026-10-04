import pandas as pd
import networkx as nx
from itertools import combinations


# -----------------------------------
# 1. Load validated cycles
# -----------------------------------

print("Loading validated cycles...")

cycles = pd.read_csv("outputs/validated_cycles.csv")

print(f"Total cycles loaded: {len(cycles)}")


# -----------------------------------
# 2. Prepare account sets
# -----------------------------------

print("Preparing cycle account sets...")

cycles["account_set"] = cycles.apply(
    lambda row: {
        int(row["account_1"]),
        int(row["account_2"]),
        int(row["account_3"])
    },
    axis=1
)


# -----------------------------------
# 3. Create a graph of cycles
# -----------------------------------

print("Finding overlapping cycles...")

cycle_graph = nx.Graph()

# Add every cycle as a graph node
for cycle_id in cycles.index:
    cycle_graph.add_node(cycle_id)


# Compare every pair of cycles
for cycle_a, cycle_b in combinations(cycles.index, 2):

    accounts_a = cycles.loc[cycle_a, "account_set"]
    accounts_b = cycles.loc[cycle_b, "account_set"]

    shared_accounts = accounts_a.intersection(accounts_b)

    # Connect cycles if they share at least 2 accounts
    if len(shared_accounts) >= 2:
        cycle_graph.add_edge(
            cycle_a,
            cycle_b,
            shared_accounts=len(shared_accounts)
        )


# -----------------------------------
# 4. Identify candidate groups
# -----------------------------------

print("Creating candidate groups...")

components = list(nx.connected_components(cycle_graph))

cycle_to_group = {}

for group_id, component in enumerate(components, start=1):

    for cycle_id in component:
        cycle_to_group[cycle_id] = group_id


cycles["candidate_group_id"] = cycles.index.map(cycle_to_group)


# -----------------------------------
# 5. Load account labels
# -----------------------------------

print("Loading account labels...")

nodes = pd.read_csv("data/raw/aml_20k_combined/nodes.csv")

fraud_labels = dict(
    zip(
        nodes["nodeid"],
        nodes["isFraud"]
    )
)


# -----------------------------------
# 6. Create group-level summary
# -----------------------------------

print("Creating group-level summary...")

group_rows = []

for group_id, group_data in cycles.groupby("candidate_group_id"):

    unique_accounts = set()

    for account_set in group_data["account_set"]:
        unique_accounts.update(account_set)

    fraud_account_count = sum(
        fraud_labels.get(account_id, 0) == 1
        for account_id in unique_accounts
    )

    group_rows.append({
        "candidate_group_id": group_id,
        "cycle_count": len(group_data),
        "unique_account_count": len(unique_accounts),
        "fraud_account_count": fraud_account_count,
        "contains_fraud_label": fraud_account_count > 0
    })


group_summary = pd.DataFrame(group_rows)


# -----------------------------------
# 7. Add group size category
# -----------------------------------

def classify_group(cycle_count):

    if cycle_count == 1:
        return "Single cycle"

    elif cycle_count <= 3:
        return "Small group"

    elif cycle_count <= 10:
        return "Medium group"

    else:
        return "Large group"


group_summary["group_size_category"] = (
    group_summary["cycle_count"]
    .apply(classify_group)
)


# -----------------------------------
# 8. Save outputs
# -----------------------------------

cycles_output = cycles.drop(columns=["account_set"])

cycles_output.to_csv(
    "outputs/ring_candidate_membership.csv",
    index=False
)

group_summary.to_csv(
    "outputs/ring_candidates.csv",
    index=False
)


# -----------------------------------
# 9. Print results
# -----------------------------------

print("\nCandidate Group Summary")
print("-" * 50)

print(f"Total candidate groups: {len(group_summary)}")

print(
    f"Groups containing fraud labels: "
    f"{group_summary['contains_fraud_label'].sum()}"
)

print("\nGroup size distribution:")
print(
    group_summary["group_size_category"]
    .value_counts()
)

print("\nLargest candidate groups:")

print(
    group_summary
    .sort_values(
        by=["cycle_count", "unique_account_count"],
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)


print("\nFiles saved:")
print("outputs/ring_candidate_membership.csv")
print("outputs/ring_candidates.csv")