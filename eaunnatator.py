#!/usr/bin/env python3

import gatenlp
import hiltnlp


eau_heuristic_types = [
    "evita_event",
    "nonneutral_sentence",
    "participant_reference",
    "possible_causal_connective",
]

def get_intersecting_sentence(annotation):
    return annotation.get_intersecting_of_type("Sentence")[0]

def has_nonneutral_sentiment(annotation):
    intersecting_sentence = get_intersecting_sentence(annotation)
    return bool(
        intersecting_sentence.get_intersecting_of_type("nonneutral_sentence")
    )

def has_possible_causal_connective(annotation):
    intersecting_sentence = get_intersecting_sentence(annotation)
    return any(
        bool(
            sentence.get_intersecting_of_type("possible_causal_connective")
        )
        for sentence in hiltnlp.get_near_sentences(intersecting_sentence, distance=3) + [intersecting_sentence]
    )

def has_participant_reference(annotation):
    intersecting_sentence = get_intersecting_sentence(annotation)
    result = bool(
        intersecting_sentence.get_intersecting_of_type("participant_reference")
    )
    return result

def is_probable_eau(evita_event):
    try:
        return bool(
            has_participant_reference(evita_event)
            and has_possible_causal_connective(evita_event)
            and has_nonneutral_sentiment(evita_event)
        )
    except:
        print(evita_event)
        return False

def create_heuristic_annotations(annotation_file,
                                 label):
    num_new_annotations = 0

    eau_heuristic_annotation_set = annotation_file.annotation_sets_dict["EAU_heuristics"]
    for annotation in annotation_file.annotations:
        if annotation.type.lower() == "evita_event":
            evita_event = annotation
            if is_probable_eau(evita_event):
                new_annotation = eau_heuristic_annotation_set.create_annotation(
                    args.label,
                    evita_event.start_node,
                    evita_event.end_node,
                )
                num_new_annotations += 1

    return num_new_annotations


def get_eau_heuristics(annotations):
    return [
        annotation
        for annotation in annotations
        if annotation.type in eau_heuristic_types
    ]


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
        print("annotating:", annotation_file.filename)
        num_new_annotations = 0

        for annotation in annotation_file.annotations:
            if annotation.type == args.label:
                annotation.delete()

        sentences = [ x for x in annotation_file.annotations if x.type == "Sentence" ]
        gatenlp.dlink(sentences)

        num_new_annotations += create_heuristic_annotations(annotation_file, label=args.label)

        annotation_file.save_changes()
        print("finished:", annotation_file.filename)
        print("num_new_annotations:", num_new_annotations)
        print("-"*20)
        ###
        quit()
