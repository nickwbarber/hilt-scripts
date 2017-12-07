#!/usr/bin/env python3

import gatenlp


annotation_file_path = "/home/nick/test/gate/pers_ment/test.xml"

annotation_file = gatenlp.AnnotationFile(annotation_file_path)

tree = annotation_file.interval_tree

annotations = annotation_file.annotations

for annotation in annotations:
    tree.add(annotation)

persons = [
    annotation
    for annotation in annotations
    if annotation.type.lower() == "person"
]

tokens = [
    annotation
    for annotation in annotations
    if annotation.type.lower() == "token"
]

for person in persons:
    intersecting_tokens = sorted(
        [
            annotation
            for annotation in tree.search(person)
            if annotation.type.lower() == "token"
        ],
        key=lambda x: x.start_node
    )

    if not len(intersecting_tokens) > 0:
        continue

    if "person_B" not in intersecting_tokens[0].features:
        intersecting_tokens[0].add_feature("person_B", "0", overwrite=True)
    for intersecting_token in intersecting_tokens[1:]:
        if "person_I" not in intersecting_token.features:
            intersecting_token.add_feature("person_I", "0", overwrite=True)

    intersecting_tokens[0].features["person_B"].tally()
    for intersecting_token in intersecting_tokens[1:]:
        intersecting_token.features["person_I"].tally()

continue
# annotation_file.save_changes()
