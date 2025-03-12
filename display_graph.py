import networkx as nx
import matplotlib.pyplot as plt

def displayGraph(G):
    #using networkx and matplotlib to generate the graph
    plt.tight_layout()
    nx.draw_networkx(G, arrows=True, node_size=250, font_size=6, width = 1)

    # save fig
    # plt.savefig("Graph.png", format="PNG")
    # nx.write_gexf(G, "graph.gexf")

    #display the graph to screen
    plt.show()