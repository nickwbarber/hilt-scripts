#!/usr/bin/env python3

import itertools
import gatenlphiltlab


# annotation_file_path = "/path/to/annotation_file.xml"
annotation_file_path = "/home/nick/hilt/pes/conversations/16/4-MG-2014-06-02_PES_3_consensus.xml"

annotation_file = gatenlphiltlab.AnnotationFile(annotation_file_path)

# Automatically links any annotation continuations to their continued annotations.
annotations = annotation_file.annotations

sentences = [
    annotation
    for annotation in annotations
    # The type is just a string pulled from the XML
    if annotation.type == "Sentence"
]

# doubly links each annotation
gatenlphiltlab.dlink(sentences)

for sentence in sentences[1:5]:
    print(
        sentence.previous.id,
        sentence.id,
        sentence.next.id,
    )
print()

# interval tree structure for querying overlaps
tree = annotation_file.interval_tree
for annotation in annotations:
    tree.add(annotation)

tokens = [
    annotation
    for annotation in annotations
    if annotation.type == "Token"
]

# An example of querying the interval tree
for token in sorted(tokens, key=lambda x: x.start_node)[20:50]:
    print(
        str(token.id).ljust(5),
        str(token.start_node).ljust(5),
        str(token.end_node).ljust(5),
        token.type.ljust(10),
        token.text, 
    )
    for intersection in tree.search(token):
        if intersection != token:
            print(
                str(intersection.start_node).ljust(5),
                str(intersection.end_node).ljust(5),
                str(intersection.id).ljust(5),
                intersection.type.ljust(10),
                intersection.text,
            )
    print()
