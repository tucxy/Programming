import networkx as nx
import sys
sys.path.append('C:\\Users\\baneg\\OneDrive\\Desktop\\Git\\research\\tikzgrapher\\tikzgrapher.py') #enter PATH of tikzgrapher.py
from tikzgrapher import viz
from itertools import combinations
import math

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

#notebook
if __name__ == "__main__":
    #Define a custom edge length function
    def custom_edge_length(node1, node2):
        if isinstance(node1, str) or isinstance(node2, str):
            return ";)"
        return abs(node1 - node2)

    #Define a custom edge sublabel function
    def custom_edge_sublabel(node1, node2):
        if isinstance(node1, str) or isinstance(node2, str):
            return None
        return (node1 + node2) % 5

    #Define a custom vertex sublabel function
    def custom_vertex_sublabel(node):
        if isinstance(node, str):
            return None
        return node % 18
    
    #using standard Networkx methods for example. Graphs are induced by edges here.
    G1 = merge(star(6,[0,1,2,3]),path([8,0,7]),path([5,3,4]))
    G2 = merge(star(0,[6,7,8]),path([1,6,2]),star(9,[10,11,12]))
    
    # Pass custom functions or leave as None for default behavior
        #opt. means optional and #req means required

    viz(
        [G1, G2], #must pass a list, [G1] or [G1,G2] ... 
        mod=14, #opt.
        edge_length_func=custom_edge_length, #opt.
        edge_sublabel_func=custom_edge_sublabel, #opt.
        vertex_sublabel_func=custom_vertex_sublabel, #opt.
        save_info=['graph test', 'C:\\Users\\baneg\\OneDrive\\Desktop\\Git\\research\\pygtikz test files'] #opt.
    ) #under save_info enter the PATH where you wish to save the .tex file in
