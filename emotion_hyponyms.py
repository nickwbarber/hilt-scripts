#!/usr/bin/env python3

from nltk.corpus import wordnet as wn


def hypo(synset):
    return synset.hyponyms()

def hyper(synset):
    return synset.hypernyms()

touchy_feely_synsets = [
    wn.synset("feeling.n.01"),
    wn.synset("condition.n.01"),
    wn.synset("psychological_state.n.01"),
]

def is_hyponym_of(synset_a, synset_b):
    return any(
        hypernym == synset_b
        for hypernym in synset_a.closure(hyper)
    )

def is_hyponym_of_emotion(lemma):
    return any(
        is_hyponym_of(lemma.synset(), target_synset)
        for target_synset in touchy_feely_synsets
    )

def is_related_to_emotion(word):
    lemmas = [
        lemma
        for synset in wn.synsets(word)
        for lemma in synset.lemmas()
    ]
    lemmas += [
        derived_lemma
        for lemma in lemmas
        for derived_lemma in lemma.derivationally_related_forms()
    ]
    return any(
        is_hyponym_of_emotion(lemma)
        for lemma in lemmas
    )

print(
    is_related_to_emotion("bothered")
)
