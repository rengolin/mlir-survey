#!/usr/bin/env python3
import sys
from pathlib import Path
import fileinput
import networkx as nx

# Reads CSV files and creates a graph of the co-occurrences and sorts by most common patterns

### Functions

# Read one CSV line into a list
# Remove quotes and newlines
def readLine (line : str):
    # Remove quotes
    line = line.replace("'", "")
    line = line.replace('"', '')
    # Swallow newline
    line = line.replace('\n', '')
    return line.split(',')

# Read file from stdin
# Return two lists: labels and nx.Graph
def readCSV(filename):
    G = nx.Graph()
    labels = None

    with open(filename, "r") as file:
        for line in file.readlines():
            fields = readLine(line)

            # Assume first row is labels
            if not labels:
                labels = fields
                continue

            # Either this is not a data line, or the label list is wrong
            if (len(labels) != len(fields)):
                continue

            # List of previous indices in the fields list
            occurrences = []
            # Current index in the fields list
            current = 0

            # For each field, associate it with all previous indices in the list
            for field in fields:
                if field:
                    # Associate previous occurrences with this one
                    for prev in occurrences:
                        # If previous links exist (from previous lines), increment weight
                        weight = 0
                        if G.has_edge(labels[prev], labels[current]):
                            weight = G.edges[labels[prev], labels[current]]['weight']
                        G.add_weighted_edges_from([(labels[prev], labels[current], weight+1)])
                    # Add index of this occurrence to the list
                    occurrences.append(current)
                # Increment index
                current += 1
    return labels, G

# Sort by value
def sortByVal(list, reverse=False):
    return sorted(list.items(), key=lambda item: item[1], reverse=reverse)

# Reverse sort by value
def revSortByVal(list):
    return sortByVal(list, reverse=True)

# Get the other node in the edge with a filter.
# Input format: ((from, to), {'weight': W})
# Output format: either from or to
def getOther(edge, filter):
    (entry, w) = edge
    (A, B) = entry
    if A == filter:
        return B
    if B == filter:
        return A
    return None

# Filter graph edges by label, into a new dictionary
# Output format: { (filter, *): weight, ... }
def filterByLabel(graph, filter):
    newList = {}
    # edge = ((from, to), {'weight': W})
    for edge in graph.edges().items():
        other = getOther(edge, filter)
        if other:
            newList[other] = edge[1]['weight']
    return newList

# Return total weight for each node as a dictionary
# Output format: { node: weight, ... }
def nodeConnectivity(graph):
    weights = {}
    for node in labels:
        nodes = filterByLabel(graph, node)
        weight = 0
        for e, w in nodes.items():
            weight += w
        weights[node] = weight
    return weights

# These should be used instead of hand parsing, but I'm not quite sure how yet
# Clsutering
#print(nx.clustering(G))

# Connectivity
#print(nx.node_connectivity(G))

if __name__ == '__main__':
    # Command line parsing
    inputFileName = sys.argv[1]
    path = Path(inputFileName)
    assert(path.is_file())
    label = None
    if len(sys.argv) > 2:
        label = sys.argv[2]

    # Read CSV file
    labels, graph = readCSV(inputFileName)
    assert(len(labels) > 0)

    # If label requested on command line, show a complete dump for that label
    if label:
        filtered = filterByLabel(graph, label)
        print(f"\nStats for label '{label}':")
        print(revSortByVal(filtered))

        # Rpint in a tabulated form, for spreadsheets
        print(f"\nTabulated form for '{label}':")
        print(f"label,weight")
        for other in sortByVal(filtered):
            (n, w) = other
            print(f"{n},{w}")

    # Find most heavily connected nodes
    heavyLabels = revSortByVal(nodeConnectivity(graph))
    print("\nMost connected labels:")
    print(heavyLabels)

    # Print top 10 with a sorted list of their most connected nodes
    print("\nTop 10 connectivity:")
    for d, w in heavyLabels[:10]:
        weightList = ""
        for other in revSortByVal(filterByLabel(graph, d)):
            weightList += other[0] + " "
        print(f" * '{d}': {weightList}")

    # DOT graph
    nx.nx_agraph.write_dot(graph, inputFileName+".dot")

