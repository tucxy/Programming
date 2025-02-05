from z3 import *
import networkx as nx

import sys
sys.path.append(r'C:\Users\Danny\Desktop\Git\Programming\tikzgrapher') #enter PATH of tikzgrapher.py
from tikzgrapher import viz
from itertools import combinations
import math


def sigmapm_graph_labeling(graph):
    s = Solver()
    m = graph.number_of_edges()

    # Variables: Each node gets a unique label in {0, ..., 2m-1}
    labels = {v: Int(f'label_{v}') for v in graph.nodes()}
    for v in graph.nodes():
        s.add(And(labels[v] >= 0, labels[v] <= 2 * m - 1))

    # Constraint 1: Unique labels
    for u in graph.nodes():
        for v in graph.nodes():
            if u != v:
                s.add(labels[u] != labels[v])

    # Constraint 2: Ordering constraint for bipartite edges
    components = list(nx.connected_components(graph))
    A, B = set(), set()
    for component in components:
        subgraph = graph.subgraph(component)
        try:
            A_sub, B_sub = nx.bipartite.sets(subgraph)
            A.update(A_sub)
            B.update(B_sub)
        except nx.NetworkXError:
            raise ValueError("Graph contains a non-bipartite component.")

    for a, b in graph.edges():
        if a in A:
            s.add(labels[a] < labels[b])
        else:
            s.add(labels[b] < labels[a])

    # Constraint 3: Edge lengths form a bijection with {1, ..., m}
    edge_lengths = {}
    for a, b in graph.edges():
        length = Int(f'len_{a}_{b}')
        s.add(length == Abs(labels[a] - labels[b]))
        s.add(And(length >= 1, length <= m))
        edge_lengths[(a, b)] = length

    # Ensure all edge lengths are unique
    for (a1, b1), len1 in edge_lengths.items():
        for (a2, b2), len2 in edge_lengths.items():
            if (a1, b1) != (a2, b2):
                s.add(len1 != len2)

    # Solve
    if s.check() == sat:
        model = s.model()
        labeled_graph = graph.copy()
        nx.set_node_attributes(labeled_graph, {v: model[labels[v]].as_long() for v in graph.nodes()}, "label")
        return labeled_graph
    else:
        return None  # No solution found

# Example usage
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])
labeled_graph = sigmapm_graph_labeling(G)
if labeled_graph:
    print("Labeled Graph:")
    for node, data in labeled_graph.nodes(data=True):
        print(f"Node {node}: Label {data['label']}")
else:
    print("No solution found.")

#123#

def construct_kG(G, k):
    """Constructs k disjoint isomorphic copies of G."""
    kG = nx.Graph()
    for i in range(k):
        mapping = {v: (v, i) for v in G.nodes()}  # (original node, copy index)
        Gi = nx.relabel_nodes(G, mapping)
        kG = nx.compose(kG, Gi)  # Merge each copy
    return kG

def solve_123_labeling(G):
    """Finds a (1-2-3-⋯-k)-labeling of kG where edge lengths form a bijection with {1, ..., k}."""
    m = G.number_of_edges()
    k = math.floor((3 * m) / 2) - m  # Calculate k

    if k <= 0:
        raise ValueError(f"Invalid k value: {k}. Ensure that m is large enough.")

    kG = construct_kG(G, k)  # Create k copies of G
    s = Solver()

    # Variables: Each node gets a unique label in {0, ..., 3m - 1}
    labels = {v: Int(f'label_{v}') for v in kG.nodes()}
    for v in kG.nodes():
        s.add(And(labels[v] >= 0, labels[v] <= 3 * m - 1))

    # Constraint 1: Unique labels within each connected component
    for i in range(k):
        component_nodes = [v for v in kG.nodes() if v[1] == i]  # Nodes in the i-th copy
        for u in component_nodes:
            for v in component_nodes:
                if u != v:
                    s.add(labels[u] != labels[v])

    # Constraint 2: Edge lengths modulo m form a bijection with {1, ..., k}
    edge_lengths = {}
    for (u, v) in kG.edges():
        length = Int(f'len_{u}_{v}')
        s.add(length == (labels[u] - labels[v]) % m)  # Length modulo m
        s.add(And(length >= 1, length <= k))  # Length must be in {1, ..., k}
        edge_lengths[(u, v)] = length

    # Ensure all edge lengths are unique
    for (u1, v1), len1 in edge_lengths.items():
        for (u2, v2), len2 in edge_lengths.items():
            if (u1, v1) != (u2, v2):
                s.add(len1 != len2)

    # Solve
    if s.check() == sat:
        model = s.model()
        labeled_kG = kG.copy()
        nx.set_node_attributes(labeled_kG, {v: model[labels[v]].as_long() for v in kG.nodes()}, "label")
        return labeled_kG
    else:
        return None  # No solution found