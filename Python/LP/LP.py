from z3 import Solver, Int, Abs, And, Not, sat, Distinct, Or, If
import networkx as nx
import sys
print(sys.path)
from itertools import combinations
import math


def sigmapm(graph):
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
'''
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])
labeled_graph = sigmapm(G)
if labeled_graph:
    print("Labeled Graph:")
    for node, data in labeled_graph.nodes(data=True):
        print(f"Node {node}: Label {data['label']}")
else:
    print("No solution found.")
'''
#123##############################################################################################################################################################################################################################################################################

def construct_kG(G, k):
    """Returns a list of k identical copies of G."""
    return [G.copy() for _ in range(k)]


def labeling_1_to_k(G, r):
    """
    Builds a (1-2-...-k)-labeling for k copies of G, with node labels assigned correctly.
    - Each vertex label is unique within its copy.
    - Vertex labels can repeat across different copies.
    - ℓ(u, v) = |label_i[u] - label_i[v]| is in [1, k] for each copy.
    - ℓ^*(u, v) = (label_i[u] + label_i[v]) mod m for each edge.
    - (ℓ, ℓ^*) pairs must be disjoint across copies.
    """
    m = G.number_of_edges()
    k = r // 2 if r % 2 == 0 else (r - 1) // 2
    if k <= 0:
        print("k <= 0, no labeling possible.")
        return None

    # Create k identical copies of G
    k_copies = construct_kG(G, k)

    s = Solver()
    label = {i: {v: Int(f'label_{i}_{v}') for v in G.nodes()} for i in range(k)}

    # Set label bounds and enforce uniqueness within each copy
    for i in range(k):
        for v in G.nodes():
            s.add(label[i][v] >= 0, label[i][v] <= 2 * m + r - 1)

        # Ensure unique labels within each copy
        unique_labels = [label[i][v] for v in G.nodes()]
        s.add(Distinct(*unique_labels))  # Enforces no duplicate labels within the same copy

    edge_list = list(G.edges())
    length = [{} for _ in range(k)]
    length_star = [{} for _ in range(k)]

    for i in range(k):
        for (u, v) in edge_list:
            len_var = Int(f'len_{i}_{u}_{v}')
            s.add(len_var == Abs(label[i][u] - label[i][v]))
            s.add(And(len_var >= 1, len_var <= k))
            length[i][(u, v)] = len_var

            len_star_var = Int(f'len_star_{i}_{u}_{v}')
            q = Int(f'q_{i}_{u}_{v}')
            s.add(len_star_var >= 0, len_star_var < m)
            s.add(len_star_var == (label[i][u] + label[i][v]) - m * q)
            s.add(q >= 0)
            length_star[i][(u, v)] = len_star_var

    # Enforce (ℓ, ℓ^*)-disjointness across copies
    for i in range(k):
        for j in range(i + 1, k):
            for e1 in edge_list:
                for e2 in edge_list:
                    same_ell = (length[i][e1] == length[j][e2])
                    same_ell_s = (length_star[i][e1] == length_star[j][e2])
                    s.add(Not(And(same_ell, same_ell_s)))

    #checking all pairs exist...
    for ell in range(1, k + 1):
        for ell_star in range(m):
            pair_exists = []
            for i in range(k):
                for (u, v) in edge_list:
                    pair_exists.append(And(length[i][(u, v)] == ell, length_star[i][(u, v)] == ell_star))
            s.add(Or(*pair_exists))

    # Solve
    print("Solving...")
    if s.check() == sat:
        print("Solver found a solution.")
        model = s.model()
        labeled_copies = []
        for i in range(k):
            Gi = k_copies[i]
            labels = {v: model[label[i][v]].as_long() for v in Gi.nodes()}
            nx.set_node_attributes(Gi, labels, "label")
            labeled_copies.append(Gi)

            # Print labels for debugging
            print(f"\nGraph {i}:")
            for v in Gi.nodes(data=True):
                print(f"  Node {v[0]}: Label {v[1]['label']}")

        return labeled_copies
    else:
        print("No solution found.")
        return None


