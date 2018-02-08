#!/usr/bin/env python3

import hiltnlp
import pdb


eau_heuristic_types = [
    "evita_event",
    "nonneutral_sentence",
    "participant_reference",
    "possible_causal_connective",
]

def get_intersecting_sentence(annotation,
                              annotation_tree):
    return next(
        iter(hiltnlp.get_intersecting_of_type(
            annotation,
            "Sentence",
            annotation_tree=annotation_tree,
        )),
        None,
    )

def has_nonneutral_sentiment(annotation,
                             annotation_tree):
    intersecting_sentence = get_intersecting_sentence(
        annotation,
        annotation_tree=annotation_tree,
    )
    assert intersecting_sentence
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
    assert intersecting_sentence
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
    assert intersecting_sentence
    return any(
        intersecting_annotation.type.lower() == "participant_reference"
        for intersecting_annotation in annotation_tree.search(intersecting_sentence)
    )

def is_probable_eau(evita_event,
                    eau_heuristic_tree):
    intersecting_sentence = next(
        iter([x for x in hiltnlp.get_intersecting_of_type(evita_event, "Sentence", annotation_tree=eau_heuristic_tree)]),
        None,
    )
    print(type(intersecting_sentence))
    # intersecting_sentence = get_intersecting_sentence(
        # evita_event,
        # annotation_tree=eau_heuristic_tree,
    # )
    assert intersecting_sentence
    return bool(
        has_participant_reference(evita_event, annotation_tree=eau_heuristic_tree)
        and has_possible_causal_connective(evita_event, annotation_tree=eau_heuristic_tree)
        and has_nonneutral_sentiment(evita_event, annotation_tree=eau_heuristic_tree)
    )

def create_heuristic_annotations(annotation_file,
                                 label):
    eau_heuristic_tree = gatenlp.GateIntervalTree()

    # add sentence annotations to tree
    for sentence in hiltnlp.get_sentences(annotation_file):
        eau_heuristic_tree.add(sentence)

    # add heuristic annotations to tree
    eau_heuristic_annotation_set = annotation_file.annotation_sets_dict["EAU_heuristics"]
    for annotation in eau_heuristic_annotation_set:
        if annotation.type in eau_heuristic_types:
            eau_heuristic_tree.add(annotation)

    for annotation in eau_heuristic_tree:
        if annotation.type.lower() == "evita_event":
            evita_event = annotation
            if is_probable_eau(evita_event, eau_heuristic_tree):
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
    import gatenlp


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
        # eau_heuristic_annotation_set = annotation_file.annotation_sets_dict["EAU_heuristics"]
        # sentences = [
        #     annotation
        #     for annotation in annotation_file.annotations
        #     if annotation.type.lower() == "sentence"
        # ]
        # gatenlp.dlink(sentences)
        # eau_heuristic_tree = gatenlp.GateIntervalTree()
        # for annotation in eau_heuristic_annotation_set:
        #     if annotation.type in eau_heuristic_types:
        #         eau_heuristic_tree.add(annotation)
        # for sentence in sentences:
        #     eau_heuristic_tree.add(sentence)

        # for annotation in eau_heuristic_tree:
        #     if annotation.type.lower() == "sentence":
        #         sentence = annotation

        #         eau_heuristic_annotations = get_eau_heuristics(
        #             eau_heuristic_tree.search(
        #                 sentence
        #             )
        #         )
        #         key_heuristic_annotation = next(
        #             (
        #                 annotation
        #                 for annotation in eau_heuristic_annotations
        #                 if annotation.type == "evita_event"
        #             ),
        #             None
        #         )
        #         intersecting_heuristic_types = [
        #             annotation.type
        #             for annotation in eau_heuristic_annotations
        #         ]
        #         intersecting_heuristic_type_set = set(intersecting_heuristic_types)
        #         if len(intersecting_heuristic_type_set) == len(eau_heuristic_types):
        #             eau_heuristic_annotation_set.create_annotation(
        #                 args.label,
        #                 key_heuristic_annotation.start_node,
        #                 key_heuristic_annotation.end_node,
        #             )
        #             continue

        #         intersecting_heuristic_type_set.add("possible_causal_connective")
        #         if len(intersecting_heuristic_type_set) == len(eau_heuristic_types):
        #             near_sentences = get_near_sentences(sentence, distance=3)
        #             for near_sentence in near_sentences:
        #                 intersecting_heuristic_types = [
        #                     annotation.type
        #                     for annotation in get_eau_heuristics(
        #                         eau_heuristic_tree.search(
        #                             near_sentence
        #                         )
        #                     )
        #                 ]
        #                 if "possible_causal_connective" in intersecting_heuristic_types:
        #                     eau_heuristic_annotation_set.create_annotation(
        #                         args.label,
        #                         key_heuristic_annotation.start_node,
        #                         key_heuristic_annotation.end_node,
        #                     )
        #                     break

        annotation_file.save_changes()
