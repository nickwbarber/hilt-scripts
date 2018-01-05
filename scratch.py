from nltk import Tree
from pprint import PrettyPrinter

def get_parsed_sentence(sentence_text):
    parse_annotation = scnlp.annotate(
        sentence_text,
        properties={
            "annotators" : "parse",
            "outputFormat" : "json",
        }
    )
    parsed_sentence = parse_annotation["sentences"][0]["parse"]

    # return parsed_sentence
    return parse_annotation

def get_subtrees(parsed_sentence):
    tree = Tree.fromstring(parsed_sentence)
    subtexts = []
    for subtree in tree.subtrees():
        # if subtree.label() == "S" or subtree.label() == "SBAR":
        if subtree.label() == "S":
            # print(subtree.leaves())
            subtexts.append(
                " ".join(subtree.leaves())
            )
    return subtexts
