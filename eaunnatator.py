#!/usr/bin/env python3

import gatenlp
import hiltnlp


eau_heuristic_types = [
    "evita_event",
    "nonneutral_sentence",
    "participant_reference",
    "possible_causal_connective",
]

def has_nonneutral_sentiment(annotation,
                             annotation_tree):
    intersecting_sentence = get_intersecting_sentence(
        annotation,
        annotation_tree=annotation_tree,
    )
    return any(
        intersecting_annotation.type.lower() == "nonneutral_sentence"
        for intersecting_annotation in annotation_tree.search(intersecting_sentence)
    )

def has_possible_causal_connective(annotation,
                                   annotation_tree):
    intersecting_sentence = get_intersecting_sentence(
        annotation,
        annotation_tree=annotation_tree,
    )
    return any(
        any(
            intersecting_annotation.type.lower() == "possible_causal_connective"
            for intersecting_annotation in annotation_tree.search(sentence)
        )
        for sentence in get_near_sentences(intersecting_sentence, distance=3)
    )

def has_participant_reference(annotation,
                              annotation_tree):
    intersecting_sentence = get_intersecting_sentence(
        annotation,
        annotation_tree=annotation_tree,
    )
    return any(
        intersecting_annotation.type.lower() == "participant_reference"
        for intersecting_annotation in annotation_tree.search(intersecting_sentence)
    )

def is_probable_eau(evita_event):
    intersecting_sentence = evita_event.get_intersecting_of_type(
        "Sentence"
    )[0]
    return bool(
        has_participant_reference(evita_event, annotation_tree=eau_heuristic_tree)
        and has_possible_causal_connective(evita_event, annotation_tree=eau_heuristic_tree)
        and has_nonneutral_sentiment(evita_event, annotation_tree=eau_heuristic_tree)
    )

def create_heuristic_annotations(annotation_file,
                                 label):
    eau_heuristic_annotation_set = annotation_file.annotation_sets_dict["EAU_heuristics"]
    for annotation in annotation_file.annotations:
        if annotation.type.lower() == "evita_event":
            evita_event = annotation
            if is_probable_eau(evita_event):
                eau_heuristic_annotation_set.create_annotation(
                    args.label,
                    evita_event.start_node,
                    evita_event.end_node,
                )

def get_eau_heuristics(annotations):
    return [
        annotation
        for annotation in annotations
        if annotation.type in eau_heuristic_types
    ]

def get_near_sentences(sentence,
                       distance=1,
                       before=True,
                       after=True):
    if not (before or after):
        return

    desired_distance = distance

    before_sentences = []
    current_distance = 0
    current_sentence = sentence
    while current_distance < desired_distance:
        previous_sentence = current_sentence.previous
        if not previous_sentence:
            break
        before_sentences.append(previous_sentence)
        current_distance += 1
        current_sentence = previous_sentence

    after_sentences = []
    current_distance = 0
    current_sentence = sentence
    while current_distance < desired_distance:
        next_sentence = current_sentence.next
        if not next_sentence:
            break
        after_sentences.append(next_sentence)
        current_distance += 1
        current_sentence = next_sentence

    near_sentences = []
    if before:
        for x in before_sentences:
            near_sentences.append(x)
    if after:
        for x in after_sentences:
            near_sentences.append(x)

    return near_sentences


if __name__ == "__main__":
    import os
    import argparse


    parser = argparse.ArgumentParser(
        description="Adds more abstract annotations to a PES pre-annotated GATE"
        " file"
    )
    parser.add_argument(
        "-i",
        "--annotation-file",
        dest="annotation_files",
        nargs="+",
        required="true",
        help="GATE annotation files"
    )
    parser.add_argument(
        "-l",
        "--label",
        dest="label",
        required="true",
        help="GATE annotation files"
    )
    args = parser.parse_args()

    for annotation_file_path in args.annotation_files:
        if not os.path.isfile(annotation_file_path):
            print(
                "{} is not a valid file!".format(
                    repr(annotation_file_path)
                )
            )
            continue
        annotation_file = gatenlp.AnnotationFile(annotation_file_path)

        for annotation in annotation_file.annotations:
            if annotation.type == args.label:
                annotation.delete()

        create_heuristic_annotations(annotation_file, label=args.label)

        annotation_file.save_changes()
