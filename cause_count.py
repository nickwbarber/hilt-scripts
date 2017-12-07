#!/usr/bin/env python3

import os
from itertools import chain
from collections import Counter
import intervaltree
import pandas
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

conversations_dir = "/home/nick/hilt/pes/conversations"

annotation_file_paths = [
    os.path.join(root, f)
    for root, dirs, files in os.walk(conversations_dir)
    for f in files
    if f.lower().endswith("pes_3_consensus.xml")
]

attribution_records = []
sentence_records = []

for annotation_file_path in annotation_file_paths:

    basename = os.path.basename(annotation_file_path)
    participant_name = "-".join(basename.split("-")[0:2])

    annotation_file = gatenlp.AnnotationFile(annotation_file_path)
    annotations = annotation_file.annotations
    annotations = [
        annotation
        for annotation in annotations
        if annotation.type.lower() in [
            "token",
            "sentence",
            "attribution",
        ]
    ]
    tokens = [
        annotation
        for annotation in annotations
        if annotation.type.lower() == "token"
    ]
    sentences = [
        annotation
        for annotation in annotations
        if annotation.type.lower() == "sentence"
    ]
    # filter sentences to Participant-uttered sentences
    sentences = [
        sentence for sentence in sentences
        if (
            sentence.features["Speaker"].value in [
                "Participant",
                "Paricipant",
                "Particpant",
                "Partcipant",
            ]
        )
    ]
    attributions = [
        annotation
        for annotation in annotations
        if (
            annotation.type.lower() == "attribution"
            and "consensus" in annotation.annotation_set_name.lower()
        )
    ]

    annotations = chain(
        tokens,
        sentences,
        attributions,
    )

    tree = annotation_file.interval_tree

    for annotation in annotations:
        tree.add(annotation)

    for attribution in attributions:
        attribution_record = {
            "participant_id" : participant_name,
            "conversation_id" : basename,
            "annotation_id" : attribution.id,
        }
        attribution_relator_tallies = Counter()
        intersecting_sentences = [
            annotation
            for annotation in tree.search(attribution)
            if annotation.type.lower() == "sentence"
        ]
        previous_sentence = None
        for sentence in intersecting_sentences:
            if sentence != previous_sentence:
                previous_sentence = sentence
                intersecting_tokens = [
                    annotation
                    for annotation
                    in tree.search(sentence)
                    if annotation.type.lower() == "token"
                ]
                for token in intersecting_tokens:
                    token_string = token.text
                    if token_string.lower() in relators:
                        relator = token_string.lower()
                        attribution_relator_tallies[relator] += 1
            else:
                continue

        for relator in relators:
            attribution_record.update(
                { relator : attribution_relator_tallies[relator] }
            )
        attribution_records.append(attribution_record)

    for sentence in sentences:
        sentence_relator_tallies = Counter()

        intersecting_annotations = tree.search(sentence)

        attribution_present = any(
            "attribution" in annotation.type.lower()
            for annotation in intersecting_annotations
        )

        intersecting_tokens = [
            annotation
            for annotation in intersecting_annotations
            if annotation.type.lower() == "token"
        ]
        for token in intersecting_tokens:
            token_string = token.text
            if token_string.lower() in relators:
                relator = token_string.lower()
                sentence_relator_tallies[relator] += 1

        sentence_record = {
            "participant_id" : participant_name,
            "conversation_id" : basename,
            "annotation_id" : sentence.id,
            "attribution_present" : attribution_present,
        }
        for relator in relators:
            sentence_record.update(
                { relator : sentence_relator_tallies[relator] }
            )
        sentence_records.append(sentence_record)

record_dfs = []
for records in [ attribution_records, sentence_records ]:
    df = pandas.DataFrame.from_records(records)
    record_dfs.append(df)

attributions_df, sentences_df = record_dfs

attribution_records_file_path = "/home/nick/temp/causal_relator_stats_2017-10-25/attribution_cause_count.csv"
with open(attribution_records_file_path, "w") as records_file:
    attributions_df.to_csv(records_file)
sentence_records_file_path = "/home/nick/temp/causal_relator_stats_2017-10-25/sentence_cause_count.csv"
with open(sentence_records_file_path, "w") as records_file:
    sentences_df.to_csv(records_file)
