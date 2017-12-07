#!/usr/bin/env python3

from collections import Counter
from pprint import PrettyPrinter
import pandas


record_file_path = "/home/nick/temp/causal_relator_stats_2017-10-25/sentence_cause_count.csv"
with open(record_file_path) as record_file:
    sentences_df = pandas.read_csv(record_file, index_col=0)

def analyze_records(records):

    relator_mention_counts_dict = {
        name : series.sum()
        for name, series in records.items()
        if name.lower() not in [
            "participant_id",
            "conversation_id",
            "annotation_id",
            "attribution_present",
        ]
    }

    sum_relator_mentions = sum(
        count for count in relator_mention_counts_dict.values()
    )

    relator_mention_proportions_dict = {
        relator : ( count / sum_relator_mentions )
        for relator, count in relator_mention_counts_dict.items()
    }

    relator_mentions_per_annotation = Counter(
        [
            sum(
                value
                for name, value in row.items()
                if name.lower() not in [
                    "participant_id",
                    "conversation_id",
                    "annotation_id",
                    "attribution_present",
                ]
            )
            for _, row in records.iterrows()
        ]
    )

    sum_sentences_with_attributions = sum(
        1
        for _, row in records.iterrows()
        if row.get_value("attribution_present")
    )

    return (
        sum_relator_mentions,
        relator_mention_counts_dict,
        relator_mention_proportions_dict,
        relator_mentions_per_annotation,
    )

def summarize_analysis(analysis,
                       total_mentions=False,
                       mention_tallies=False,
                       mention_proportions=False,
                       per_annotation=False):
    (
        sum_mentions,
        mention_counts_dict,
        mention_proportions_dict,
        mentions_per_annotation,
    ) = analysis


    if mention_tallies:
        print("relator tallies:")
        PrettyPrinter().pprint(mention_counts_dict)
        print()

    if mention_proportions:
        print("relator tally / total relator mentions :")
        PrettyPrinter().pprint(mention_proportions_dict)
        print()

    num_annotations = sum(
        count for count in mentions_per_annotation.values()
    )
    print(
        (
            "Number of annotations".ljust(40, ".")
        ),
        " = ",
        (
            "{:,}"
            .format(num_annotations)
            .rjust(6)
        ),
    )

    if total_mentions:
        print(
            (
                "Number of mentions".ljust(40, ".")
            ),
            " = ",
            (
                "{:,}"
                .format(sum_mentions)
                .rjust(6)
            ),
        )

    if per_annotation:
        for num_mentions, attribution_count in sorted(
            mentions_per_annotation.items()
        ):
            summed_annotations = sum(
                _attribution_count
                for _num_mentions, _attribution_count
                in mentions_per_annotation.items()
                if _num_mentions >= num_mentions
            )

            if not num_mentions > 0:
                description = "Annotations with {} mentions"
                print(
                    (
                        description
                        .format(num_mentions)
                        .ljust(40, ".")
                    ),
                    " = ",
                    (
                        "{:,}"
                        .format(mentions_per_annotation[0])
                        .rjust(6)
                    ),
                    (
                        " ({:.2%})"
                        .format(
                            mentions_per_annotation[0] / num_annotations
                        )
                        .rjust(9)
                    ),
                )

            else:
                if num_mentions == 1:
                    description = "Annotations with at least {} mention"
                if num_mentions > 1:
                    description = "Annotations with at least {} mentions"
                print(
                    (
                        description
                        .format(num_mentions)
                        .ljust(40, ".")
                    ),
                    " = ",
                    (
                        "{:,}"
                        .format(summed_annotations)
                        .rjust(6)
                    ),
                    (
                        " ({:.2%})"
                        .format(
                            summed_annotations / num_annotations
                        )
                        .rjust(9)
                    ),
                )



if __name__ == "__main__":

    print("overall:")
    print()
    summarize_analysis(
        analyze_records(sentences_df),
        # mention_tallies=True,
        # mention_proportions=True,
        total_mentions=True,
        per_annotation=True,
    )
    print()
    print()

    for attribution_present, group in sentences_df.groupby("attribution_present"):
        print("attribution_present == " + str(attribution_present))
        print()
        summarize_analysis(
            analyze_records(group),
            # mention_tallies=True,
            # mention_proportions=True,
            total_mentions=True,
            per_annotation=True,
        )
        print()
        print()
