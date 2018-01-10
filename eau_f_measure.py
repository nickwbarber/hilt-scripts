#!/usr/bin/env python3

import os
import itertools
import argparse
import gatenlp
import hiltnlp
import f_measure as fm


def get_near_turns(turn,
                   distance=1,
                   before=True,
                   after=True):
    if not (before or after):
        return

    desired_distance = distance

    before_turns = []
    current_distance = 0
    current_turn = turn
    while current_distance < desired_distance:
        previous_turn = current_turn.previous
        if not previous_turn:
            break
        before_turns.append(previous_turn)
        current_distance += 1
        current_turn = previous_turn

    after_turns = []
    current_distance = 0
    current_turn = turn
    while current_distance < desired_distance:
        next_turn = current_turn.next
        if not next_turn:
            break
        after_turns.append(next_turn)
        current_distance += 1
        current_turn = next_turn

    near_turns = []
    if before:
        for x in before_turns:
            near_turns.append(x)
    if after:
        for x in after_turns:
            near_turns.append(x)

    return near_turns

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

    num_true_positives = 0
    num_false_positives = 0
    num_false_negatives = 0
    total_text_length = 0
    total_heuristic_length = 0
    total_heuristics = 0
    total_eaus = 0

    for annotation_file_path in args.annotation_files:
        if not os.path.isfile(annotation_file_path):
            print(
                "{} is not a valid file!".format(
                    repr(annotation_file_path)
                )
            )
            continue

        annotation_file = gatenlp.AnnotationFile(annotation_file_path)
        total_text_length += len(annotation_file.text)

        eau_heuristic_annotations = [
            annotation
            for annotation in annotation_file.annotations
            if annotation.type == args.heuristic_type
        ]
        consensus_attributions_set = annotation_file.annotation_sets_dict["consensus_attributions"]
        consensus_events_set = annotation_file.annotation_sets_dict["consensus_events"]
        assert len(consensus_events_set) > 0
        assert len(consensus_attributions_set) > 0
        total_eaus += len(consensus_attributions_set)

        sentences = [
            annotation
            for annotation in annotation_file.annotations
            if annotation.type.lower() == "sentence"
        ]
        gatenlp.dlink(sentences)

        turns = hiltnlp.get_turns(sentences)

        tree = gatenlp.GateIntervalTree()
        for annotation in itertools.chain(
            eau_heuristic_annotations,
            consensus_events_set,
            consensus_attributions_set,
        ):
            tree.add(annotation)
        
        for turn in turns:
            # search_turns = [turn] + get_near_turns(turn, distance=1, after=False)
            search_turns = [turn]
            search_sentences = list( 
                itertools.chain.from_iterable(
                    search_turn.sentences
                    for search_turn in search_turns
                )
            )
            intersecting_annotation_types = set(
                annotation.type
                # for sentence in turn
                for sentence in search_sentences
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

            if heuristic_present:
                total_heuristic_length += sum(
                    len(str(search_turn))
                    for search_turn in search_turns
                )
                total_heuristics += 1

    precision = fm.calc_precision(
        num_true_positives=num_true_positives,
        num_false_positives=num_false_positives,
    )
    recall = fm.calc_recall(
        num_true_positives=num_true_positives,
        num_false_negatives=num_false_negatives,
    )
    f_measure = fm.calc_f_measure(
        num_true_positives=num_true_positives,
        num_false_positives=num_false_positives,
        num_false_negatives=num_false_negatives,
    )
    percentage_of_text = (total_heuristic_length / total_text_length)
    projected_annotation_speed = ( recall / percentage_of_text )

    results = [
        (
            "precision",
            precision,
        ),
        (
            "recall",
            recall,
        ),
        (
            "f-measure",
            f_measure,
        ),
        (
            "percentage_of_text",
            percentage_of_text,
        ),
        (
            "projected_annotation_speed",
            projected_annotation_speed,
        )
    ]

    longest_label=max(
        len(label)
        for label,_ in results
    )
    for label, value in results:
        print(
            "{label:.<{longest_label}} = {value}".format(
                label=label,
                value=round(value,2),
                longest_label=longest_label,
            )
        )
