#!/usr/bin/env python3

import os
from itertools import chain
from collections import Counter
import gatenlp


relators = [
    "because",
    "cuz",
    "since",
    "after",
    "when",
    "whenever",
    "once",
    "therefore",
    "so",
    "if",
    "soon",
    "result",
    "results",
    "resulted",
    "resulting",
    "cause",
    "causes",
    "caused",
    "causing",
    "starts",
    "start",
    "starts",
    "started",
    "starting",
    "make",
    "makes",
    "made",
    "making",
    "precipitate",
    "precipitates",
    "precipitated",
    "precipitating",
    "lead",
    "leads",
    "led",
    "produce",
    "produces",
    "produced",
    "producing",
    "provoke",
    "provokes",
    "provoked",
    "provoking",
    "breeds",
    "breeds",
    "bred",
    "breeding",
    "induce",
    "induces",
    "induced",
    "inducing",
    "create",
    "creates",
    "created",
    "creating",
    "effect",
    "effects",
    "effected",
    "effecting",
]

# TODO: args
# annotation_file_path = args.annotation_file
annotation_file_path = "/home/nick/test/cause/test_file.xml"
annotation_file = gatenlp.AnnotationFile(annotation_file_path)
EAU_heuristics_set = annotation_file.create_annotation_set("EAU_heuristics")
tokens = [
    annotation
    for annotation in annotation_file.annotations
    if annotation.type.lower() == "token"
]
for token in tokens:
    if token.text.lower() in relators:
        EAU_heuristics_set.create_annotation(
            annotation_type="possible_causal_connective",
            start=token.start_node,
            end=token.end_node,
        )
annotation_file.save_changes()
