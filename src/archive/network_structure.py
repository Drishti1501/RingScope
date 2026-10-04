import pandas as pd
import networkx as nx
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

data_folder = (
    project_folder
    / "data"
    / "raw"
    / "aml_20k_combined"
)

nodes = pd.read_csv(data_folder / "nodes.csv")
transactions = pd.read_csv(data_folder / "transactions.csv")

# Create an undirected graph for group connectivity
graph = nx.Graph()

# Add all accounts
graph.add_nodes_from(nodes["nodeid"])

# Add transaction connections
graph.add_edges_from(
    transactions[
        ["sourceNodeId", "targetNodeId"]
    ].itertuples(index=False, name=None)
)

# Find connected components
components = list(nx.connected_components(graph))

component_data = []

for group_id, component in enumerate(components, start=1):
    group_accounts = nodes[
        nodes["nodeid"].isin(component)
    ]

    component_data.append({
        "group_id": group_id,
        "group_size": len(component),
        "fraud_labeled_accounts": group_accounts["isFraud"].sum(),
        "fraud_percentage": (
            group_accounts["isFraud"].mean() * 100
        )
    })

component_summary = pd.DataFrame(component_data)

component_summary = component_summary.sort_values(
    "group_size",
    ascending=False
)

print("========== NETWORK STRUCTURE ==========")

print("Total connected components:", len(components))

print("\nLargest connected groups:")
print(component_summary.head(15).to_string(index=False))

# Save results
output_folder = project_folder / "outputs"
output_folder.mkdir(exist_ok=True)

component_summary.to_csv(
    output_folder / "connected_components.csv",
    index=False
)

print("\nAnalysis saved successfully.")