def string_match(string, expression):
    return expression in string

def list_match(string, list):
    for element in list:
        if string_match(string, element):
            return True
    return False

def is_entity(G, node):
    if 'type' not in G.nodes[node].keys():
        return False
    return G.nodes[node]["type"] == 'entity'

def split_entity_processes(G, list):
    entities = []
    processes = []
    for element in list:
        if is_entity(G, element[0]) or is_entity(G, element[1]):
            entities.append(element)
        else:
            processes.append(element)
    return entities, processes

def remove_node(G, node):
    outgoing = G.out_edges(node)
    incoming = G.in_edges(node)
    outgoing_entities, outgoing_processes = split_entity_processes(G, outgoing)
    incoming_entities, incoming_processes = split_entity_processes(G, incoming)
    for element in incoming_entities:
        G.remove_edge(element[0], element[1])
        if len(G[element[0]]) == 0:
            G.remove_node(element[0])
    for element in outgoing_entities:
        G.remove_edge(element[0], element[1])
        if len(G[element[1]]) == 0:
            G.remove_node(element[1])
    for outgoing_edge in outgoing_processes:
        for incoming_edge in incoming_processes:
            G.add_edge(incoming_edge[0], outgoing_edge[1])
    G.remove_node(node)

def collect_garbage_from_list_of_nodes(G, L):
    nodes = [str(node) for node in G.nodes()]
    for node in nodes:
        if list_match(node, L) and ('type' not in G.nodes[node].keys() or G.nodes[node]['type'] == 'process'):
            remove_node(G, node)

def collect_garbage(G):
    L = ['T2']
    collect_garbage_from_list_of_nodes(G, L)