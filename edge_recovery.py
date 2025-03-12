import re

def edgeRecovery():

    with open('Logs/perfetto.systrace', 'r', encoding='utf-8', errors='ignore') as f3:
        perfetto_lines = f3.readlines()
        del perfetto_lines [0:11]
    
    perfetto_relations = [''] * len(perfetto_lines)

    pos = 0
    
    for i in perfetto_lines:

        split_condition = "prev_pid="
        index_for_split= i.find(split_condition)+len(split_condition)
        prev_pid=i[index_for_split:index_for_split+5]
        prev_pid = re.sub("[^0-9]", "", prev_pid)
        
        split_condition = "next_pid="
        index_for_split= i.find(split_condition)+len(split_condition)
        #print(index_for_split)

        next_pid=i[index_for_split:index_for_split+5]
        next_pid = re.sub("[^0-9]", "", next_pid)

        this_interaction = prev_pid + "," + next_pid
    
        perfetto_relations[pos] = this_interaction
        pos = pos + 1


    return perfetto_relations