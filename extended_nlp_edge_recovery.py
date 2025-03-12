import spacy
from customNER_POS_tagging import find_verb_phrase, find_verb

nlp = spacy.load('en_core_web_sm')

incoming = ['read', 'receive', 'import', 'fetch', 'download', 'load', 'extract']
outgoing = ['write', 'send', 'export', 'upload', 'post', 'output']

incoming = ['read', 'receive', 'import', 'fetch', 'download', 'load', 'extract']
outgoing = ['write', 'send', 'export', 'upload', 'post', 'output']

def get_edge_direction(log_entry):
    verb_phrase = find_verb_phrase(log_entry)
    string = "process " + verb_phrase + " entity"
    verb = find_verb(string)
    if verb == None:
        return None

    # Check the lemma (base form) of the verb against the "incoming" and "outgoing" verb lists
    if verb.lemma_ in incoming:
        for child in verb.children:
            if child.dep_ in ["dobj", "pobj"]:
                return "incoming"
            # If the child is a preposition (e.g., "from" in "reads from a file"), check its objects
            elif child.dep_ == "prep":
                for grandchild in child.children:
                    if grandchild.dep_ == "pobj":
                        return "incoming"
    elif verb.lemma_ in outgoing:
        for child in verb.children:
            if child.dep_ == "dobj":
                return "outgoing"
            # If the child is a preposition (e.g., "to" in "writes to a file"), check its objects
            elif child.dep_ == "prep":
                for grandchild in child.children:
                    if grandchild.dep_ == "pobj":
                        return "outgoing"

    return None

# log_entry = "process reads from a file/url"
# print(get_edge_direction(log_entry)) # "incoming"

# log_entry = "process writes to a file/url"
# print(get_edge_direction(log_entry)) # "outgoing"
