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

    speaker_tag = "None"
    for sentence in sentences:
        text = sentence.text
        if ".wav" in text:
            sentence.add_feature("Speaker", "None", overwrite=True)
            continue
        if ":" in text:
            speaker_tag = text.split(":")[0]
        sentence.add_feature("Speaker", speaker_tag, overwrite=True)

    continue
    # annotation_file.save_changes()
