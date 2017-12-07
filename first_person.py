#!/usr/bin/env python3

import os
from itertools import chain
from collections import Counter
import pandas
import matplotlib
import matplotlib.pyplot as plt
import gatenlp
import explanatory_style as es
import turn_parser as tp


def get_sentence(key_annotation):
    if key_annotation.type.lower() == "sentence":
        return
    sentence = next(
        (
            annotation
            for annotation in tree.search(key_annotation)
            if annotation.type.lower() == "sentence"
        ),
        None
    )
    return sentence

def get_sentence_offset(tree,
                        start_annotation,
                        end_annotation):
    start_sentence = get_sentence(start_annotation)
    end_sentence = get_sentence(end_annotation)

    offset = 0
    comparison_sentence = start_sentence
    while True:
        if comparison_sentence == end_sentence:
            return offset
        else:
            if start_sentence.start_node < end_sentence.start_node:
                offset += 1
                comparison_sentence = comparison_sentence.next
            else:
                offset -= 1
                comparison_sentence = comparison_sentence.previous

def get_turn_offset(tree,
                    start_annotation,
                    end_annotation):
    start_sentence = get_sentence(start_annotation)
    end_sentence = get_sentence(end_annotation)

    offset = 0
    comparison_turn = start_sentence.turn
    while True:
        # if comparison_sentence == end_sentence:
        if comparison_turn == end_sentence.turn:
            return offset
        else:
            if start_sentence.turn.start_node < end_sentence.turn.start_node:
                offset += 1
                comparison_turn = comparison_turn.next
            else:
                offset -= 1
                comparison_turn = comparison_turn.previous

participant_tags = [
    "Participant",
    "Paricipant",
    "Particpant",
    "Partcipant",
]
therapist_tags = [
    "Therapist",
    "Thearpist",
]
second_reference_words = [
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
]
first_reference_words = [
    "i",
    "me",
    "my",
    "mine",
    "myself",
    "we",
    "us",
    "our",
    "ours",
    "ourselves",
]
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

offset_counter = Counter()

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
            "event",
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
    turns = tp.segment_turns(sentences)
    gatenlp.dlink(turns)
    gatenlp.dlink(sentences)
    assert turns[0].start_node == turns[1].previous.start_node
    assert turns[-1].start_node == turns[-2].next.start_node
    # # filter sentences to truly uttered sentences
    # sentences = [
    #     sentence for sentence in sentences
    #     if (
    #         sentence.features["Speaker"].value
    #         in chain(participant_tags, therapist_tags)
    #     )
    # ]
    events = [
        es.Event(annotation)
        for annotation in annotations
        if (
            annotation.type.lower() == "event"
            and "consensus" in annotation.annotation_set_name.lower()
        )
    ]
    attributions = [
        es.Attribution(annotation)
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
        events,
    )

    tree = annotation_file.interval_tree

    for annotation in annotations:
        tree.add(annotation)

    EAUs = es.get_event_attribution_units(events, attributions)

    for EAU in EAUs:
        event = EAU.event
        attribution = EAU.attribution
        attribution_record = {
            "participant_id" : participant_name,
            "conversation_id" : basename,
            "annotation_id" : attribution.id,
            "has_first_person" : False,
        }
        # offset = get_sentence_offset(tree, attribution, event)
        offset = get_turn_offset(tree, attribution, event)
        # print(offset)
        # print(get_sentence(attribution).turn)
        # print()
        # print(get_sentence(attribution).turn.previous.previous)
        # print()
        # print(event)
        # print(attribution)
        offset_counter[offset] += 1
        attribution_record.update(
            { "offset" : offset }
        )
        continue
        # intersecting_sentences = [
        #     annotation
        #     for annotation in tree.search(attribution)
        #     if annotation.type.lower() == "sentence"
        # ]
        # previous_sentence = None
        # for sentence in intersecting_sentences:
        #     if sentence != previous_sentence:
        #         previous_sentence = sentence
        #         intersecting_tokens = [
        #             annotation
        #             for annotation
        #             in tree.search(sentence)
        #             if annotation.type.lower() == "token"
        #         ]
        #         for token in intersecting_tokens:
        #             token_string = token.get_concatenated_text()
        #             if token_string.lower() in relators:
        #                 relator = token_string.lower()
        #     else:
        #         continue


        intersecting_sentences = [
            annotation
            for annotation in tree.search(event)
            if annotation.type.lower() == "sentence"
        ]
        previous_sentence = None
        for sentence in intersecting_sentences:
            if sentence != previous_sentence:
                previous_sentence = sentence
                speaker_tag = sentence.features["Speaker"].value
                intersecting_tokens = [
                    annotation
                    for annotation
                    in tree.search(sentence)
                    if annotation.type.lower() == "token"
                ]
                for token in intersecting_tokens:
                    token_string = token.get_concatenated_text()
                    if speaker_tag in participant_tags:
                        if token_string.lower() in first_reference_words:
                            attribution_record["has_first_person"] = True
                    elif speaker_tag in therapist_tags:
                        if token_string.lower() in second_reference_words:
                            attribution_record["has_first_person"] = True
            else:
                continue

        attribution_records.append(attribution_record)

    continue

    for sentence in sentences:

        speaker_tag = sentence.features["Speaker"].value

        sentence_relator_tallies = Counter()

        intersecting_annotations = tree.search(sentence)

        attribution_present = any(
            "attribution" in annotation.type.lower()
            for annotation in intersecting_annotations
        )

        sentence_record = {
            "participant_id" : participant_name,
            "conversation_id" : basename,
            "annotation_id" : sentence.id,
            "attribution_present" : attribution_present,
            "has_first_person" : False,
        }

        intersecting_tokens = [
            annotation
            for annotation in intersecting_annotations
            if annotation.type.lower() == "token"
        ]
        for token in intersecting_tokens:
            token_string = token.get_concatenated_text()
            # if token_string.lower() in relators:
                # relator = token_string.lower()
                # sentence_relator_tallies[relator] += 1
            if speaker_tag in participant_tags:
                if token_string.lower() in first_reference_words:
                    sentence_record["has_first_person"] = True
            elif speaker_tag in therapist_tags:
                if token_string.lower() in second_reference_words:
                    sentence_record["has_first_person"] = True

        # for relator in relators:
            # sentence_record.update(
                # { relator : sentence_relator_tallies[relator] }
            # )
        sentence_records.append(sentence_record)

## sentence offsets
# offset_dict = {
#     offset : offset_counter[offset]
#     for offset in range(min(offset_counter.keys()),max(offset_counter.keys())+1)
# }
# print(offset_dict)
# offset_series = pandas.Series(offset_dict)
# offset_series.plot(kind="bar")
# plt.xlabel("event sentence offset from attribution sentence")
# plt.ylabel("number of EAUs")
# plt.savefig("/home/nick/temp/eau_sentence_offsets")

## turn offsets
offset_dict = {
    offset : offset_counter[offset]
    for offset in range(min(offset_counter.keys()),max(offset_counter.keys())+1)
}
print(offset_dict)
offset_series = pandas.Series(offset_dict)
offset_series.plot(kind="bar")
plt.xlabel("event turn offset from attribution turn")
plt.ylabel("number of EAUs")
plt.savefig("/home/nick/temp/eau_turn_offsets")
quit()

record_dfs = []
for records in [ attribution_records, sentence_records ]:
    df = pandas.DataFrame.from_records(records)
    record_dfs.append(df)

attributions_df, sentences_df = record_dfs

attribution_records_file_path = "/home/nick/temp/first_person_stats/attributions.csv"
with open(attribution_records_file_path, "w") as records_file:
    attributions_df.to_csv(records_file)
sentence_records_file_path = "/home/nick/temp/first_person_stats/sentences.csv"
with open(sentence_records_file_path, "w") as records_file:
    sentences_df.to_csv(records_file)
