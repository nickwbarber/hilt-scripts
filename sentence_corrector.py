#!/usr/bin/env python3

import os
import gatenlp


#TODO: make this a CLI program

conversations_dirs = [
    "/home/nick/hilt/pes/consensus_files_cleaned",
    "/home/nick/hilt/pes/consensus_files_with_tags",
]
# conversations_dir = "/home/nick/test/gate/evita"

for conversations_dir in conversations_dirs:

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
                # gatenlp.unlink(current_sentence)

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
