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
        "event_polarity",
        "event_sentiment",
    ]
)

string_sentiments = Counter()
string_sentiment_values = Counter()
event_sentiments_and_polarities = Counter()
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

    for event in events:
        event_text = textractor.clean(event.text)
        if event_text == "":
            continue

        result = scnlp.annotate(
            # event.text,
            event_text,
            properties={
                "annotators" : "sentiment",
                "outputFormat" : "json",
                "timeout" : "10000",
            }
        )

        string_sentiment = int(result["sentences"][0]["sentimentValue"])
        string_sentiment_value = result["sentences"][0]["sentiment"]

        string_sentiments.update([string_sentiment])
        string_sentiment_values.update([string_sentiment_value])

        this_polarity_pair = polarity_pair(
            event_polarity=event.polarity,
            event_sentiment=string_sentiment,
        )
        event_sentiments_and_polarities.update(
            [this_polarity_pair]
        )

print(string_sentiment_values)
print(repr(event_sentiments_and_polarities))
