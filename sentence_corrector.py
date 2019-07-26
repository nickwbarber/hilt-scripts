#!/usr/bin/env python3

import os
import argparse
import gatenlphiltlab


parser = argparse.ArgumentParser(
    description="Merges absurdly short sentences into its nearest likely"
    " sentence for HiLT GATE annotation files."
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
    annotations = annotation_file.annotations
    sentences = (
        annotation
        for annotation in annotations
        if annotation.type.lower() == "sentence"
    )
    sentences = sorted(
        sentences,
        key=lambda x: x.start_node
    )

    gatenlphiltlab.dlink(sentences)

    current_sentence = sentences[0]
    while True:
        if len(current_sentence) <= 2:

            if current_sentence.previous:
                previous_sentence = current_sentence.previous
                previous_sentence.end_node = current_sentence.end_node
                # previous_sentence.end_node = (
                    # previous_sentence.end_node
                    # + len(current_sentence)
                # )
            elif current_sentence.next:
                next_sentence = current_sentence.next
                previous_sentence.start_node = current_sentence.start_node
                # next_sentence.end_node = (
                    # next_sentence.end_node
                    # + len(current_sentence)
                # )
            current_sentence.delete()
            # gatenlphiltlab.unlink(current_sentence)

        current_sentence = current_sentence.next
        if not current_sentence:
            break

    chars = set()
    current_sentence = sentences[0]
    while True:
        if len(current_sentence) <= 2:
            # print(sentence)
            chars.add(current_sentence.text)
        current_sentence = current_sentence.next
        if not current_sentence:
            break

    annotation_file.save_changes()
