#!/usr/bin/env python3

media_file_extensions = [
    ".mp3",
    ".mp4",
    ".aiff",
    ".raw",
    ".wav",
    ".flac",
]

#TODO make a file validation function for GATE files
if __name__ == "__main__":
    import os
    import argparse
    import gatenlp


    parser = argparse.ArgumentParser(
        description="Adds speaker tags to sentences within a HiLT GATE annotation"
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

        sentences = (
            annotation
            for annotation in annotation_file.annotations
            if annotation.type.lower() == "sentence"
        )
        sentences = sorted(
            sentences,
            key=lambda x: x.start_node
        )

        speaker_tag = "None"
        for sentence in sentences:
            text = sentence.text
            if any(
                extension in text.lower()
                for extension in media_file_extensions
            ):
                sentence.add_feature("Speaker", "None", overwrite=True)
                continue
            if ":" in text:
                speaker_tag = text.split(":")[0]
            sentence.add_feature("Speaker", speaker_tag, overwrite=True)

        annotation_file.save_changes()
