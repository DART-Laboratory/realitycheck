import graph_joiner
import extract_data
import display_graph
import edge_recovery
import perf_query
import graph_simplifier
from pyvis.network import Network
import webbrowser
import argparse
import graph_filter

def main():
    parser = argparse.ArgumentParser(
        prog='RealityCheck',
        description='Construct provenance graph from logs')

    parser.add_argument('-t', '--tid')
    parser.add_argument('-p', '--pid')
    args = parser.parse_args()

    hmd_entries, sysmon_entries, oculus_entries = extract_data.extractData()

    #print(logcat_pids, logcat_tids, logcat_nodes, logcat_timestamps, sysmon_timestamps, sysmon_pids, sysmon_ppids, sysmon_process_name, sysmon_data)
    perfetto_edges = edge_recovery.edgeRecovery()
    G = graph_joiner.joinGraph(hmd_entries, sysmon_entries, perfetto_edges, oculus_entries)
    graph_simplifier.collect_garbage(G)
    graph_filter.filter_graph(args.pid, args.tid, G)

    display_graph.displayGraph(G)
    
    net = Network(directed=True)
    net.from_nx(G)

    net.save_graph("networkx-pyvis.html")
    #ucomment to check query performance
    #perf_query.perfPlot(G)

if __name__ == "__main__":
    main()