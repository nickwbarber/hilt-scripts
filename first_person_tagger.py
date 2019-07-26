#!/usr/bin/env python3

import os
import argparse
import gatenlphiltlab
import hiltnlp
import Levenshtein

#TODO : integrate this into hiltnlp/reorganize


def is_participant_speech(turn):
    ratio = Levenshtein.ratio(turn.speaker, "Participant")
    return ratio > 0.75

def is_therapist_speech(turn):
    ratio = Levenshtein.ratio(turn.speaker, "Therapist")
    return ratio > 0.75

def is_participant_reference(person_token,
                             turn):
    grammatical_person = hiltnlp.get_grammatical_person(person_token)
    if is_participant_speech(turn):
        if grammatical_person == 1:
            return True
    elif is_therapist_speech(turn):
        if grammatical_person == 2:
            return True

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="(temp)"
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
        sentences = hiltnlp.get_sentences(annotation_file)
        turns = hiltnlp.get_turns(sentences)

        participant_ref_set = annotation_file.create_annotation_set("EAU_heuristics")

        for turn in turns:
            for sentence in turn:
                tokens = hiltnlp.get_tokens(sentence)
                for token in tokens:
                    if hiltnlp.is_explicit_person_reference(token):
                        if is_participant_reference(token, turn):
                            participant_ref_set.create_annotation(
                                annotation_type="participant_reference",
                                start=token.start_node,
                                end=token.end_node,
                            )

        annotation_file.save_changes()
