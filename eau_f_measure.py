#!/usr/bin/env python3

import os
import itertools
import argparse
import gatenlp
import hiltnlp
import f_measure as fm


def is_eau_relevant(type_list):
    event_present = "Event" in type_list
    attribution_present = "Attribution" in type_list
    return (event_present or attribution_present)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculates effectiveness of EAU heuristics in terms of an F1 score"
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
        "-t",
        "--type",
        dest="heuristic_type",
        required="true",
        help="which annotation type to analyze"
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

        eau_heuristic_annotations = [
            annotation
            for annotation in annotation_file.annotations
            if annotation.type == args.heuristic_type
        ]
        consensus_attributions_set = annotation_file.annotation_sets_dict["consensus_attributions"]
        consensus_events_set = annotation_file.annotation_sets_dict["consensus_events"]

        sentences = [
            annotation
            for annotation in annotation_file.annotations
            if annotation.type.lower() == "sentence"
        ]
        gatenlp.dlink(sentences)

        turns = hiltnlp.get_turns(sentences)

        num_true_positives = 0
        num_false_positives = 0
        num_false_negatives = 0

        tree = gatenlp.GateIntervalTree()
        for annotation in itertools.chain(
            eau_heuristic_annotations,
            consensus_events_set,
            consensus_attributions_set,
        ):
            tree.add(annotation)
        
        for turn in turns:
            intersecting_annotation_types = set(
                annotation.type
                for sentence in turn
                for annotation in tree.search(sentence)
            )

            heuristic_present = args.heuristic_type in intersecting_annotation_types
            eau_relevant = is_eau_relevant(intersecting_annotation_types)
            
            if heuristic_present and eau_relevant:
                num_true_positives += 1
            if heuristic_present and not eau_relevant:
                num_false_positives += 1
            if not heuristic_present and eau_relevant:
                num_false_negatives += 1

        f_measure = fm.calc_f_measure(
            num_true_positives=num_true_positives,
            num_false_positives=num_false_positives,
            num_false_negatives=num_false_negatives,
        )

        print(f_measure)
