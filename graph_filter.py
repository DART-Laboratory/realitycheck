import networkx as nx
import time

def do_bfs(G, nodes):
    stack = list(nodes)
    visited = []
    while len(stack) > 0:
        node = stack.pop()
        visited.append(node)
        for neighbor in nx.all_neighbors(G, node):
            if neighbor not in visited:
                visited.append(neighbor)
                stack.append(neighbor)
    return visited

def filter_graph(pid, tid, G):
    start_time = time.time()
    filtered_nodes = set()
    comparison_function = get_comparison_function(G, pid, tid)
    for node in G.nodes:
        if comparison_function(node):
                filtered_nodes.add(node)
    nodes_to_keep = do_bfs(G, filtered_nodes)
    nodes_to_remove = set(G.nodes).difference(nodes_to_keep)
    G.remove_nodes_from(nodes_to_remove)
    end_time = time.time()
    print("Graph filtration took: ", end_time-start_time, "s.")

def get_comparison_function(graph, pid, tid):
    if not pid and not tid:
        return lambda node: True
    if pid and not tid:
        return lambda node: 'pid' in graph.nodes[node] and graph.nodes[node]['pid'] == pid
    if not pid and tid:
        return lambda node: 'tid' in graph.nodes[node] and graph.nodes[node]['tid'] == tid
    if pid and tid:
        return lambda node: 'tid' in graph.nodes[node] and 'pid' in graph.nodes[node] and graph.nodes[node]['tid'] == tid and graph.nodes[node]['pid']