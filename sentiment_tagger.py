#!/usr/bin/env python3

import os
from collections import namedtuple
from collections import Counter
import json
import gatenlp
import explanatory_style as es
import textractor
from pycorenlp import StanfordCoreNLP

scnlp = StanfordCoreNLP("http://localhost:9000")

conversations_dir = "/home/nick/hilt/pes/consensus_files_cleaned"

gate_file_paths = [
    os.path.join(root, f)
    for root, dirs, files in os.walk(conversations_dir)
    for f in files
    if f.lower().endswith("consensus.xml")
]

# gate_file_path = "/home/nick/test/gate/sentiment/gate.xml"

polarity_pair = namedtuple(
    "Pairing",
    [
        "event",
        "sentence",
    ]
)

sentence_sentiments = Counter()
sentence_sentiment_values = Counter()
event_and_sentence_polarities = Counter()
for gate_file_path in gate_file_paths:
    gate_file = gatenlp.AnnotationFile(gate_file_path)


    # events
    for name in gate_file.annotation_set_names:
        if (
            "event" in name.lower()
            and "cons" in name.lower()
        ):
            consensus_events_set = gate_file.annotation_sets_dict[name]

    events = [
        es.Event(event)
        for event in consensus_events_set
    ]

    # sentences
    sentences = [
        annotation
        for annotation in gate_file.annotations
        if (
            annotation.type.lower() == "sentence"
            and annotation.features["Speaker"].value != "None"
        )
    ]
    for sentence in sentences:
        sentence_text = textractor.clean(sentence.text)
        if sentence_text == "":
            continue

        result = scnlp.annotate(
            # sentence.text,
            sentence_text,
            properties={
                "annotators" : "sentiment",
                "outputFormat" : "json",
                "timeout" : "10000",
            }
        )

        sentence_sentiment = int(result["sentences"][0]["sentimentValue"])
        sentence_sentiment_value = result["sentences"][0]["sentiment"]

        sentence_sentiments.update([sentence_sentiment])
        sentence_sentiment_values.update([sentence_sentiment_value])

        for event in events:
            if gatenlp.is_overlapping(
                [
                    sentence,
                    event,
                ]
            ):
                this_polarity_pair = polarity_pair(
                    event=event.polarity,
                    sentence=sentence_sentiment,
                )
                event_and_sentence_polarities.update(
                    [this_polarity_pair]
                )

print(sentence_sentiment_values)
print(repr(event_and_sentence_polarities))
