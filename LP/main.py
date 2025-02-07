import networkx as nx
import os
import sys
from itertools import combinations
import math

from LP import sigmapm,construct_kG,labeling_1_to_k
home_path = r'C:\Users\baneg\OneDrive\Desktop\Git\Programming\tikzgrapher'
office_path = r'C:\Users\Danny\Desktop\Git\Programming\tikzgrapher'

hpath = r'C:\Users\baneg\OneDrive\Desktop\Git\Programming\graph_visualization'
sys.path.append(home_path)
sys.path.append(hpath)


from tikzgrapher import *

from graph_visualization import *
#* graph creation tools *#

# how to merge two graphs:
'''
# Create two graphs
G1 = nx.Graph()
G1.add_edges_from([('a', 'b'), ('b', 'c')])

G2 = nx.Graph()
G2.add_edges_from([('c', 'd'), ('d', 'e')])

# Merge the graphs
G_merged = nx.compose(G1, G2)
'''
#how to merge multiple graphs
'''
# Create multiple graphs
G1 = nx.Graph()
G1.add_edges_from([('a', 'b'), ('b', 'c')])

G2 = nx.Graph()
G2.add_edges_from([('c', 'd'), ('d', 'e')])

G3 = nx.Graph()
G3.add_edges_from([('e', 'f'), ('f', 'g')])

# Merge the graphs
G_merged = nx.compose_all([G1, G2, G3])
'''
#custom functions to build graphs more intuitively
def inspect(G):
    nodes = list(G.nodes)
    edges = list(G.edges)
    
    Ginfo = {
        "Nodes": nodes,
        "Edges": edges
    }
    
    return Ginfo

def build(vertices, edges):
    """
    Create a graph using NetworkX from a list of vertices and edges.
    build([u,v,w,...], [(u, v), (w, v), ...])
    """
    G = nx.Graph()
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)
    return G

def merge(*graphs):
    """
    Merge multiple NetworkX graphs into a single graph.
    """
    G = nx.Graph()
    
    for graph in graphs:
        G.add_nodes_from(graph.nodes())
        G.add_edges_from(graph.edges())
    
    return G

def path(cycle):

    C = list(cycle)
    G = nx.Graph()
    G.add_nodes_from(C)
    for i in range(len(C) - 1):
        G.add_edge(C[i], C[i + 1])
    return G

def cycle(cycle):

    C = list(cycle)
    G = nx.Graph()
    G.add_nodes_from(C)
    for i in range(len(C)):
        G.add_edge(C[i], C[(i + 1) % len(C)])
    return G

def star(hub, neighbors):

    leaves = list(neighbors)
    G = nx.Graph()
    G.add_node(hub)
    for node in leaves:
        G.add_node(node)
        G.add_edge(hub, node)
    return G

def K(n):
    G = nx.Graph()
    G.add_nodes_from(range(0,n))
    for node in range(0,n):
        for neighbor in range(0,n):
            if node != neighbor:
                G.add_edge(node,neighbor)
    return G

def trees(n):
    def is_isomorphic_to_any(graph, graph_list):
        for g in graph_list:
            if nx.is_isomorphic(graph, g):
                return True
        return False

    all_trees = []
    nodes = list(range(n + 1))  # A tree with n edges has n+1 nodes

    for edges in combinations(combinations(nodes, 2), n):
        G = nx.Graph()
        G.add_edges_from(edges)
        if nx.is_tree(G) and not is_isomorphic_to_any(G, all_trees):
            all_trees.append(G)

    return all_trees

'''-----------------------------------------------------------------------------------'''

# Create a bipartite test graph
G = merge(star(0,[1,2,3,4,5]),path([6,7,8]))

#viz([construct_kG(G, 3)])
t = 2
# Solve for a valid labeling
labeled_list = labeling_1_to_k(G,7)
print(labeled_list)
viz(labeled_list)

def rename_nodes_by_labels(graph):
    """Rename nodes based on their assigned labels."""
    mapping = {node: graph.nodes[node].get("label", node) for node in graph.nodes()}  # Handles missing labels
    return nx.relabel_nodes(graph, mapping)

labeled_list = [rename_nodes_by_labels(g) for g in labeled_list]


visualize(21, labeled_list,  '123list',  'C:\\Users\\baneg\\OneDrive\\Desktop\\Git\\Python\\Research\\7 (mod 14)\\texgraph')