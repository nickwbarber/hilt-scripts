import os
from pprint import PrettyPrinter
import gatenlp

conversations_dirs = [
    "/home/nick/hilt/pes/consensus_files_with_tags",
    "/home/nick/hilt/pes/consensus_files_cleaned",
]

for conversations_dir in conversations_dirs:
    print(conversations_dir)

    gate_file_paths = [
        os.path.join(root, f)
        for root, dirs, files in os.walk(conversations_dir)
        for f in files
        if f.lower().endswith("consensus.xml")
    ]

    num_intersecting_events = 0
    num_human_events = 0
    num_evita_events = 0
    num_sentences = 0
    num_sentences_with_events = 0
    for gate_file_path in gate_file_paths:

        gate_file = gatenlp.AnnotationFile(gate_file_path)

        try:
            evita_set = gate_file.annotation_sets_dict["Evita"]
        except KeyError:
            continue
        consensus_event_set = gate_file.annotation_sets_dict["consensus_events"]

        local_num_human_events = 0
        for human_event in consensus_event_set:
            num_human_events += 1
            local_num_human_events += 1
            for evita_event in evita_set:
                overlapping = gatenlp.is_overlapping(
                    [
                        human_event,
                        evita_event,
                    ]
                )
                if overlapping:
                    num_intersecting_events += 1
                    break
        assert local_num_human_events == len(consensus_event_set)
        num_evita_events += len(evita_set)

        sentences = [
            annotation
            for annotation in gate_file.annotations
            if (
                annotation.type.lower() == "sentence"
                and annotation.features["Speaker"].value != "None"
            )
        ]
        num_sentences += len(sentences)
        for sentence in sentences:
            for evita_event in evita_set:
                overlapping = gatenlp.is_overlapping(
                    [
                        sentence,
                        evita_event,
                    ]
                )
                if overlapping:
                    num_sentences_with_events += 1
                    break

    results = {
        "num_human_events_with_evita_events" : num_intersecting_events,
        "num_human_events" : num_human_events,
        "num_evita_events" : num_evita_events,
        "num_sentences_with_events" : num_sentences_with_events,
        "num_sentences" : num_sentences,
    }
    pp = PrettyPrinter()
    pp.pprint(results)
    print()
