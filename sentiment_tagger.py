#!/usr/bin/env python3

import os
import argparse
import gatenlphiltlab
import hiltnlp
from pycorenlp import StanfordCoreNLP


def get_sentiment(annotation,
                  server,
                  verbose=False,
                  normalize=True):
    if normalize:
        annotation_text = gatenlphiltlab.normalize(annotation.text)
    else:
        annotation_text = annotation.text
    if annotation_text == "":
        return

    result = server.annotate(
        annotation_text,
        properties={
            "annotators" : "tokenize,ssplit,pos,parse,sentiment",
            "outputFormat" : "json",
            "timeout" : "15000",
        }
    )
    annotation_sentiment = int(result["sentences"][0]["sentimentValue"])
    annotation_sentiment_value = result["sentences"][0]["sentiment"]

    if verbose:
        return annotation_sentiment_value
    else:
        return annotation_sentiment


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Adds sentiment annotations over sentences within a HiLT GATE annotation"
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

    # Remember to start the StanfordCoreNLPServer before running!
    scnlp = StanfordCoreNLP("http://localhost:9000")

    for annotation_file_path in args.annotation_files:

        gate_file = gatenlphiltlab.AnnotationFile(annotation_file_path)
        sentences = [
            annotation
            for annotation in gate_file.annotations
            if annotation.type.lower() == "sentence"
        ]
        hiltnlp.tag_speakers(sentences)
        sentiment_annotation_set = gate_file.create_annotation_set(
            "EAU_heuristics",
        )

        for sentence in sentences:
            sentiment_value = get_sentiment(
                sentence,
                server=scnlp,
                verbose=True,
            )
            if not sentiment_value:
                continue
            if sentiment_value != "Neutral":
                sentiment_annotation = sentiment_annotation_set.create_annotation(
                    "nonneutral_sentence",
                    sentence.start_node,
                    sentence.end_node,
                    overwrite=True,
                )
                sentiment_annotation.add_feature("Sentiment", sentiment_value)

        gate_file.save_changes()
