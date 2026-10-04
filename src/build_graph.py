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

# Create a directed graph
graph = nx.DiGraph()

# Add all accounts as nodes
for _, row in nodes.iterrows():
    graph.add_node(
        int(row["nodeid"]),
        isFraud=int(row["isFraud"]),
        init_balance=float(row["init_balance"])
    )

# Add transactions as directed edges
for _, row in transactions.iterrows():
    source = int(row["sourceNodeId"])
    target = int(row["targetNodeId"])
    amount = float(row["value"])

    if graph.has_edge(source, target):
        graph[source][target]["transaction_count"] += 1
        graph[source][target]["total_value"] += amount
    else:
        graph.add_edge(
            source,
            target,
            transaction_count=1,
            total_value=amount
        )

print("========== GRAPH SUMMARY ==========")

print("Total nodes:", graph.number_of_nodes())
print("Total edges:", graph.number_of_edges())

print("Self-loops:", nx.number_of_selfloops(graph))

print("Weakly connected components:",
      nx.number_weakly_connected_components(graph))

print("Average degree:",
      sum(dict(graph.degree()).values()) / graph.number_of_nodes())