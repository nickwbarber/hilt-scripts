import os
from itertools import chain
import gatenlphiltlab
import explanatory_style as es

def get_sentence(key_annotation):
    if key_annotation.type.lower() == "sentence":
        return
    sentence = next(
        (
            annotation
            for annotation in tree.search(key_annotation)
            if annotation.type.lower() == "sentence"
        ),
        None
    )
    return sentence

def get_context(key_annotation, distance):
    center = get_sentence(key_annotation)
    previous = []
    following = []

    count = 0
    comparison_sentence = center
    while count < distance:
        previous.append(comparison_sentence.previous)
        count += 1
        comparison_sentence = comparison_sentence.previous

    count = 0
    comparison_sentence = center
    while count < distance:
        following.append(comparison_sentence.next)
        count += 1
        comparison_sentence = comparison_sentence.next

    return chain(
        list(reversed(previous)),
        [center],
        following,
    )

relators = [
    "because",
    "cuz",
    "since",
    "after",
    "when",
    "whenever",
    "once",
    "therefore",
    "so",
    "if",
    "soon",
    "result",
    "results",
    "resulted",
    "resulting",
    "cause",
    "causes",
    "caused",
    "causing",
    "starts",
    "start",
    "starts",
    "started",
    "starting",
    "make",
    "makes",
    "made",
    "making",
    "precipitate",
    "precipitates",
    "precipitated",
    "precipitating",
    "lead",
    "leads",
    "led",
    "produce",
    "produces",
    "produced",
    "producing",
    "provoke",
    "provokes",
    "provoked",
    "provoking",
    "breeds",
    "breeds",
    "bred",
    "breeding",
    "induce",
    "induces",
    "induced",
    "inducing",
    "create",
    "creates",
    "created",
    "creating",
    "effect",
    "effects",
    "effected",
    "effecting",
]

conversations_dir = "/home/nick/hilt/pes/conversations"

annotation_file_paths = [
    os.path.join(root, f)
    for root, dirs, files in os.walk(conversations_dir)
    for f in files
    if f.lower().endswith("pes_3_consensus.xml")
]

eau_count = 0

for annotation_file_path in annotation_file_paths:

    basename = os.path.basename(annotation_file_path)

    annotation_file = gatenlphiltlab.AnnotationFile(annotation_file_path)
    annotations = annotation_file.annotations
    annotations = [
        annotation
        for annotation in annotations
        if annotation.type.lower() in [
            "token",
            "sentence",
            "attribution",
            "event",
        ]
    ]
    tokens = [
        annotation
        for annotation in annotations
        if annotation.type.lower() == "token"
    ]
    sentences = [
        annotation
        for annotation in annotations
        if annotation.type.lower() == "sentence"
    ]
    gatenlphiltlab.dlink(sorted(sentences, key=lambda x: x.start_node))
    events = [
        es.Event(annotation)
        for annotation in annotations
        if (
            annotation.type.lower() == "event"
            and "consensus" in annotation.annotation_set_name.lower()
        )
    ]
    attributions = [
        es.Attribution(annotation)
        for annotation in annotations
        if (
            annotation.type.lower() == "attribution"
            and "consensus" in annotation.annotation_set_name.lower()
        )
    ]

    annotations = chain(
        tokens,
        sentences,
        attributions,
        events,
    )

    tree = annotation_file.interval_tree

    for annotation in annotations:
        tree.add(annotation)

    EAUs = es.get_event_attribution_units(events, attributions)

    print(basename)
    print()
    for EAU in EAUs:
        eau_count += 1
        event = EAU.event
        attribution = EAU.attribution

        intersecting_sentences = [
            annotation
            for annotation in tree.search(attribution)
            if annotation.type.lower() == "sentence"
        ]
        intersecting_token_strings = [
            annotation.text.lower()
            for intersecting_sentence in intersecting_sentences
            for annotation in tree.search(intersecting_sentence)
            if annotation.type.lower() == "token"
        ]
        relator_strings = [
            string
            for string in intersecting_token_strings
            if string in relators
        ]
        relator_string = ",".join(relator_strings)

        event_context = get_context(event,5)
        attribution_context = get_context(attribution,5)

        context = sorted(
            set(
                chain(event_context, attribution_context)
            ),
            key=lambda x: x.start_node,
        )
        print("Context:")
        for x in context:
            print(eau_count, x.id, x.text)
        print()
        print("Event:")
        print()
        print(event.get_concatenated_text())
        print()
        print("Attribution:")
        print()
        print(attribution.get_concatenated_text())
        print()
        print("relators = [{}]".format(relator_string))
        print()
        print()
    print()
    print()
    print()
