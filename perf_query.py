import networkx as nx
import matplotlib.pyplot as plt
import time
import numpy as np
import queue

# Generates a performance plot for a given provenance graph
def perfPlot(G, num_iterations=200, num_pairs=2000):

    # Find the root nodes in the graph
    root_nodes = [node for node in G.nodes() if len(list(G.predecessors(node))) == 0]

    # Performs breadth-first search on the graph starting from a given node
    def bfs(G, start_node):
        visited = set()
        q = queue.Queue()
        q.put(start_node)
        visited.add(start_node)
        while not q.empty():
            node = q.get()
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    q.put(neighbor)
        return visited
    
    # Measures the response time of BFS from a given start node to an end node for a given number of iterations
    def response_time(G, start_node, end_node, num_iterations):
        times = []
        for i in range(num_iterations):
            start_time = time.time()
            bfs(G, start_node)
            end_time = time.time()
            times.append(end_time - start_time)
        return np.mean(times)

    # Choose num_pairs random end nodes and the root node as the start node
    end_nodes = np.random.choice(G.nodes(), num_pairs, replace=True)
    start_node = root_nodes[0]

    # Measure the response time for all possible start-end node pairs and store them in an array
    response_times = []
    for end_node in end_nodes:
        response_times.append(response_time(G, start_node, end_node, num_iterations))
    response_times = np.array(response_times)

    # Sort the response times and calculate the cumulative density for each value
    response_times = np.sort(response_times)
    cumulative_density = np.arange(len(response_times)) / (float(len(response_times)) - 1)

    # Calculate the average query time and print it
    avg_query_time = np.mean(response_times)
    print('Average query time:', avg_query_time)

    # Write the output data to a file
    # with open('output.txt', 'w') as f:
    #     f.write('1.0 0.0\n')
    #     for i in range(len(response_times)):
    #         f.write(str(response_times[i]) + ' ' + str(cumulative_density[i]) + '\n')

    # Plot the performance plot with response time on the x-axis and cumulative density on the y-axis
    plt.plot(response_times, cumulative_density)
    plt.xlabel('Response Time (seconds)')
    plt.ylabel('Cumulative Density')
    plt.show()
    
    # Save fig: uncomment the below statement and comment plt.show() above
    #plt.savefig("QueryPerformance.png", format="PNG")
    #plt.savefig('QueryPerformance.pdf')