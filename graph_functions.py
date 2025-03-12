import networkx as nx

def find_ancestors(G, timestamp, entity_name):
    node = find_node(G, timestamp, entity_name)
    return nx.ancestors(G, node)

def find_successors(G, timestamp, entity_name):
    node = find_node(G, timestamp, entity_name)
    return nx.descendants(G, node)

def backward_query(G, timestamp, entity_name):
    node = find_node(G, timestamp, entity_name)
    subgraph_nodes = find_ancestors(G, timestamp, entity_name)
    subgraph_nodes.add(node)
    return G.subgraph(subgraph_nodes)

def forward_query(G, timestamp, entity_name):
    node = find_node(G, timestamp, entity_name)
    subgraph_nodes = find_successors(G, timestamp, entity_name)
    subgraph_nodes.add(node)
    return G.subgraph(subgraph_nodes)

def find_node(G, timestamp, entity_name):
    for node in G.nodes:
        if timestamp.strip() in node and entity_name.lower().strip() in node.lower():
            return node
    return None