#!/usr/bin/env python3

import os
from itertools import chain
from collections import Counter
import argparse
import gatenlphiltlab


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

parser = argparse.ArgumentParser(
    description="Annotates causal connectives within GATE annotation files"
)
parser.add_argument(
    "-i",
    "--annotation-file",
    dest="annotation_files",
    nargs="+",
    required="true",
    help="GATE annotation files"
)
args = parser.parse_args()

for annotation_file_path in args.annotation_files:
    annotation_file = gatenlphiltlab.AnnotationFile(annotation_file_path)
    EAU_heuristics_set = annotation_file.create_annotation_set("EAU_heuristics")
    tokens = [
        annotation
        for annotation in annotation_file.annotations
        if annotation.type.lower() == "token"
    ]
    for token in tokens:
        # if token.text.lower() in relators:
        if token.text.lower() == "because":
            EAU_heuristics_set.create_annotation(
                annotation_type="possible_causal_connective",
                start=token.start_node,
                end=token.end_node,
            )
    annotation_file.save_changes()
