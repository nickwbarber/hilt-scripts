#!/usr/bin/env python3

import os
import gatenlp


conversations_dir = "/home/nick/hilt/pes/conversations"

annotation_file_paths = [
    os.path.join(root, f)
    for root, dirs, files in os.walk(conversations_dir)
    for f in files
    if f.lower().endswith("pes_3_consensus.xml")
]

for annotation_file_path in annotation_file_paths:

    annotation_file = gatenlp.AnnotationFile(annotation_file_path)
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

    gatenlp.dlink(sentences)

    current_sentence = sentences[0]
    while True:
        if len(current_sentence) <= 2:
            # gatenlp.unlink(current_sentence)
            current_sentence.delete()

            if current_sentence.previous:
                previous_sentence = current_sentence.previous
                previous_sentence.end_node = (
                    previous_sentence.end_node
                    + len(current_sentence)
                )
            elif current_sentence.next:
                next_sentence = current_sentence.next
                next_sentence.end_node = (
                    next_sentence.end_node
                    + len(current_sentence)
                )

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

    # continue
    annotation_file.save_changes()
