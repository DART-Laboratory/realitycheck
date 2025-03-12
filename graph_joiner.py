import re
import networkx as nx
from datetime import datetime

# import modules for NLP log processing
import customNER_POS_tagging as ml
import extended_nlp_edge_recovery as ner

def joinGraph(hmd_entries, sysmon_entries, perfetto_edges, oculus_entries):

    #initialising a DAG Graph using networkx
    G = nx.DiGraph()

    #generating a list of unique hmd_pids in the logs to make sure we generate graph for all
    unique_pid_list = list({entry.pid for entry in hmd_entries})

    # get NLP model from customNER_POS_tagging to process entities
    nlp = ml.train_model()

    #traversing for all the hmd_pids to generate graphs for the processes one by one
    for element in unique_pid_list:
        current_edge = None # the current edge for the process, should be none until the first process with a valid pid
        thread_mappings = dict() #mappings of thread ids to edges
        resolved_mappings = dict() #mappings of thread ids to whether it needs to be resolved
        new_threads = False
        found_parent = False

        #iterating through hmd log entries
        for entry in hmd_entries:
            #checking hmd_pids to form edges between hmd_nodes
            if entry.pid == element:
                #checking if this is not thread (pid == tid)
                if entry.tid == element:
                    to_edge = str(entry.timestamp) + " " + str(entry.data)
                    #if this is the first parent node
                    if not found_parent:
                        found_parent = True
                        if current_edge == None:
                            current_edge = str(entry.timestamp) + " " + str(entry.data)
                            G.add_node(current_edge)
                            G.nodes[current_edge]['pid'] = entry.pid
                            G.nodes[current_edge]['tid'] = entry.tid
                            G.nodes[current_edge]['source'] = 'hmd'
                        #add edge from current to new
                        else:
                            if add_new_edge(G, current_edge, to_edge, nlp):
                                current_edge = to_edge
                                G.nodes[to_edge]['pid'] = entry.pid
                                G.nodes[to_edge]['tid'] = entry.tid
                    #checking if there are currently threads that need to be resolved to original process
                    if new_threads:
                        # resolve all threads to original process
                        for tid in thread_mappings.keys():
                            if not G.has_edge (to_edge, thread_mappings[tid]) and resolved_mappings[tid]:
                                add_new_edge(G, thread_mappings[tid], to_edge, nlp)
                                current_edge = to_edge
                                resolved_mappings[tid] = False
                        new_threads = False
                    # simply create new edge from process to process
                    else:
                        if current_edge == None:
                            current_edge = str(entry.timestamp) + " " + str(entry.data)
                            G.add_node(current_edge)
                            G.nodes[current_edge]['pid'] = entry.pid
                            G.nodes[current_edge]['tid'] = entry.tid
                            G.nodes[current_edge]['source'] = 'hmd'
                        else:
                            if to_edge != current_edge: #check that edge hasn't already been added
                                if add_new_edge(G, current_edge, to_edge, nlp):
                                    current_edge = to_edge
                                    G.nodes[to_edge]['pid'] = entry.pid
                                    G.nodes[to_edge]['tid'] = entry.tid
                # if not original process (tid != pid)
                else:
                    to_edge = str(entry.timestamp) + " " + str(entry.data)
                    #if new thread and parent hasn't be found yet with no current_edge
                    if not found_parent and not current_edge:
                        #treat the current edge as a regular process node
                        current_edge = to_edge
                        G.add_node(current_edge)
                        G.nodes[current_edge]['pid'] = entry.pid
                        G.nodes[current_edge]['tid'] = entry.tid
                        G.nodes[current_edge]['source'] = 'hmd'
                    elif not found_parent and current_edge:
                        #add edge from current to new
                        if add_new_edge(G, current_edge, to_edge, nlp):
                            G.nodes[to_edge]['pid'] = entry.pid
                            G.nodes[to_edge]['tid'] = entry.tid
                            current_edge = to_edge
                    # if thread already exists
                    elif entry.tid in thread_mappings:
                        from_edge = thread_mappings[entry.tid]
                        if add_new_edge(G, from_edge, to_edge, nlp):
                            G.nodes[to_edge]['pid'] = entry.pid
                            G.nodes[to_edge]['tid'] = entry.tid
                            thread_mappings[entry.tid] = to_edge
                    # if new thread and process node exists which is parent
                    else:
                        # say that we have unresolved ("open") threads
                        new_threads = True
                        resolved_mappings[entry.tid] = True
                        if add_new_edge(G, current_edge, to_edge, nlp):
                            G.nodes[to_edge]['pid'] = entry.pid
                            G.nodes[to_edge]['tid'] = entry.tid
                            thread_mappings[entry.tid] = to_edge # put new thread in dictionary

        #Uncomment the statements below to verify that no. of edges are same every time you run the program.
        #Please note that since we are using sets to extrat uniqe hmd_pids, the hmd_pids might not be in a certain order,
        #but the edges will always be the same and so will the graph.
        #if edges != []:
        #    print("PID " + str(element) + " has " + str(len(edges)) + " edges.")

    for i in range (0,len(perfetto_edges)):
        this_relation = perfetto_edges[i].split(",")
        if int(this_relation[0]) > 0 and int(this_relation[1]) > 0:
            pids_int = [eval(entry.pid) for entry in hmd_entries]
            tids_int = [eval(entry.tid) for entry in hmd_entries]

            if int(this_relation[0]) in pids_int:
                from_pid = pids_int.index(int(this_relation[0]))
            elif int(this_relation[0]) in tids_int:
                from_pid = tids_int.index(int(this_relation[0]))

            if int(this_relation[1]) in pids_int:
                to_pid = pids_int.index(int(this_relation[1]))
            elif int(this_relation[1]) in tids_int:
                to_pid = tids_int.index(int(this_relation[1]))
        try:
            from_edge = str(hmd_entries[from_pid].timestamp) + " " + str(hmd_entries[from_pid].data)
            to_edge = str(hmd_entries[to_pid].timestamp) + " " + str(hmd_entries[to_pid].data)
            if G.has_edge (to_edge, from_edge) == False:
                #G.add_edge(from_edge[:95],to_edge[:95])
                G.add_edge(from_edge, to_edge)
        except:
            pass


    sysmon_edge_list = []
    exists = False
    for i in range(0,len(sysmon_entries)):

        if sysmon_entries[i].event_id == 1:
            for j in reversed(range(i)):
                if sysmon_entries[i].ppid == sysmon_entries[j].pid:
                    exists = True
                    from_edge = str(sysmon_entries[j].timestamp) + " " + str(sysmon_entries[j].process_name)
                    to_edge = str(sysmon_entries[i].timestamp) + " " + str(sysmon_entries[i].process_name)
                    this_sysmon_edge = (from_edge, to_edge)
            if exists and this_sysmon_edge not in sysmon_edge_list:
                sysmon_edge_list.append(this_sysmon_edge)
                #G.add_edge(from_edge[:95], to_edge[:95])



        elif sysmon_entries[i].event_id in (3, 11):
            from_edge = str(sysmon_entries[i].timestamp) + " " + str(sysmon_entries[i].process_name)
            to_edge = str(sysmon_entries[i].data)
            this_sysmon_edge = (from_edge, to_edge)
            sysmon_edge_list.append(this_sysmon_edge)
            #G.add_edge(from_edge[:95], to_edge[:95])
    
    made_sysmon_hmd_edge = False

    for i in range(0,len(sysmon_entries)):
        #print(sysmon_entries[i].data)
        for this_node in list(G.nodes()):
                from_edge = str(sysmon_entries[i].timestamp) + " " + str(sysmon_entries[i].process_name)

                check_this_data = sysmon_entries[i].data.split(" ").pop()

                if made_sysmon_hmd_edge:
                    break

                #compare_data = re.sub(r'[^a-zA-Z]', '', check_this_data)
                #this_node_data = re.sub(r'[^a-zA-Z]', '', this_node)
                compare_data = re.findall(r"[\w']+", check_this_data)
                #print(this_node)
                this_node_data = re.split('[^a-zA-Z]', this_node)


                compare_data = [re.sub(r'[^a-zA-Z]', '', i) for i in compare_data]
                this_node_data = [re.sub(r'[^a-zA-Z]', '', i) for i in this_node_data]

                common = list(set(this_node_data).intersection(compare_data))
                while("apk" in common):
                    common.remove("apk")

                #if len(common)>0 and common[0]!='':
                #    print (compare_data, "and ", this_node_data, "and ", common)

                from_timestamp = sysmon_entries[i].timestamp
                numeric_from_timestamp = re.sub("[^0-9]", "", from_timestamp)
                to_timestamp = this_node[:13]
                numeric_to_timestamp = re.sub("[^0-9]", "", to_timestamp)
                difference = int(numeric_to_timestamp) - int(numeric_from_timestamp)

                if (len(common)>0 and common[0]!='') and abs(difference) < 200 and G.has_edge (this_node,from_edge) == False:
                    print ("YES")
                    G.add_edge(from_edge, this_node)
                    made_sysmon_hmd_edge = True
                    break
        if made_sysmon_hmd_edge:
            break

    G.add_edges_from(sysmon_edge_list)

    edges = [(edge[0], edge[1]) for edge in G.edges()]

    #cycle through oculus log entries
    for entry in oculus_entries:
        # check all edges already in the graph to account for every edge
        for edge in edges:
            # only check edges that have a timestamp
            try:
                time1 = datetime.strptime(edge[0].split()[0], "%H:%M:%S.%f").time()
                time2 = datetime.strptime(edge[1].split()[0], "%H:%M:%S.%f").time()
            except ValueError:
                continue
            # get the time of the oculus entry
            oculus_time = datetime.strptime(entry.timestamp, "%H:%M:%S.%f").time()
            # if oculus entry takes place between 1st entry and 2nd entry
            if oculus_time > time1 and oculus_time < time2:
                # insert oculus entry between the edges
                G.remove_edge(edge[0], edge[1])
                G.add_edge(edge[0], str(oculus_time) + " " + entry.data)
                G.add_edge(str(oculus_time) + " " + entry.data, edge[1])
                continue

    substrings_to_remove = ["xrPollEvent", "onResume", "onPause", "OnApplicationPause", "OnApplicationFocus", "OnApplicationQuit", "ApplicationWillEnterBackgroundDelegate", "ApplicationHasEnteredForegroundDelegate", "ApplicationWillTerminateDelegate"]

    fix_dependencies(G, substrings_to_remove)

    nodes = [str(node) for node in G.nodes]

    # extract entities from hmd nodes
    for node in nodes:
        if 'source' in G.nodes[node] and G.nodes[node]['source'] == 'hmd':
            process_entity_edge(G, node, nlp)

    return(G)

# method for adding edges between two log entry nodes
def add_new_edge(G, current_edge, to_edge, nlp):
    if not G.has_edge (to_edge, current_edge):
        # separate log entries into everything before and after colon followed by space
        # extract entities
        # current_application = process_entity_edge(G, current_edge, nlp)
        # to_application = process_entity_edge(G, to_edge, nlp)
        G.add_edge(current_edge, to_edge)
        G.nodes[current_edge]['type'] = 'process'
        G.nodes[current_edge]['source'] = 'hmd'
        G.nodes[to_edge]['type'] = 'process'
        G.nodes[to_edge]['source'] = 'hmd'
        return True
    return False

def fix_dependencies(G, substrings_to_remove):
    nodes = [str(node) for node in G.nodes]
    for node in nodes:
        for substring in substrings_to_remove:
            if substring.strip().lower() in node.lower():
                G.remove_node(node)
                break

# add here a function that, if in some node, it finds 'xrPollEvent' --> remove that node

def remove_quotes(string):
    while True:
        if string[0] == "'" and string[-1] == "'":
            string = string[1:-1]
        elif string[0] == '"' and string[-1] == '"':
            string = string[1:-1]
        else:
            return string

# method for processing if log entry nodes have entities and adding an edge if necessary, returns the application name for later processing
def process_entity_edge(G, edge, nlp):
    [application, data] = edge.split(": ", 1)
    if len(data) <= 50: return #visualizable edge
    else: 
        text = ml.preprocess(data)
        ents = nlp(text).ents
        timestamp = application.split()[0]
        if len(ents) > 0 and not G.has_edge(application, str(ents[0])) and ents[0].label_ in ("URL", "FILEPATH_OR_URL", "FILEPATH"):
            entity = timestamp + " " + remove_quotes(str(ents[0]))
            direction = ner.get_edge_direction(text)
            if direction == "outgoing":
                G.add_edge(application, entity)
            elif direction == "incoming":
                G.add_edge(entity, application)
            else:
                G.add_edge(entity, application)
                G.add_edge(application, entity)
            G.nodes[entity]['type'] = 'entity'
        nx.relabel_nodes(G, {edge: application}, copy=False)