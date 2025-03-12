# Import the spaCy library
import spacy

# Load the English language model for spaCy
nlp = spacy.load("en_core_web_sm")

# Determine the direction of the provenance graph edge using this function
def get_edge_direction(log_entry):
    # Parse the log entry using the spaCy NLP pipeline
    doc = nlp(log_entry)

    # Find the first verb in the sentence
    verb = None
    for token in doc:
        if token.pos_ == "VERB":
            verb = token
            break
    
    # If there is no verb, return None
    if not verb:
        return None
    
    # Check whether any of the verb's children are object nouns or prepositional object nouns
    if any(child.dep_ in ("dobj", "pobj") for child in verb.children):
        return "incoming"
    
    # Check whether any of the verb's children are subject nouns or subject passive nouns
    elif any(child.dep_ in ("nsubj", "nsubjpass") for child in verb.children):
        return "outgoing"
    
    # If neither condition is met, return None
    else:
        return None

if __name__ == 'main':
    # Test the function with two example log entries
    log_entry = "process reads file"
    edge_direction = get_edge_direction(log_entry)
    print(edge_direction) # "incoming"

    log_entry = "process writes to a file"
    edge_direction = get_edge_direction(log_entry)
    print(edge_direction) # "outgoing"

    log_entry = "process loads a URL"
    edge_direction = get_edge_direction(log_entry)
    print(edge_direction) # "outgoing"