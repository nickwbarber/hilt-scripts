#!/usr/bin/env python3

from os.path import *
from collections import namedtuple
import re
import argparse
import gatenlp


Regex = namedtuple(
    "Regex",
    [
        "name",
        "expression",
        "replacement",
    ]
)

regexes = (
    Regex(
        name="file_names",
        expression=re.compile(".*\.\w\w+.*?"),
        replacement="",
    ),
    Regex(
        name="speaker_tag",
        expression=re.compile("^.*?:", re.MULTILINE),
        replacement="",
    ),
    Regex(
        name="extralinguistic_tags",
        expression=re.compile("{.+?}"),
        replacement="",
    ),
    Regex(
        name="round_braces",
        expression=re.compile("[\(\)]"),
        replacement="",
    ),
    Regex(
        name="square_braces",
        expression=re.compile("[\[\]]"),
        replacement="",
    ),
    Regex(
        name="curly_braces",
        expression=re.compile("[{}]"),
        replacement="",
    ),
    Regex(
        name="tilde",
        expression=re.compile("~"),
        replacement="",
    ),
    Regex(
        name="backslash",
        expression=re.compile(r"\\"),
        replacement="",
    ),
    Regex(
        name="forward_slash",
        expression=re.compile("/"),
        replacement="",
    ),
    Regex(
        name="asterisk",
        expression=re.compile("\*"),
        replacement="",
    ),
    Regex(
        name="misc_characters",
        expression=re.compile("[\$\^\+@#`_=]|<>;"),
        replacement="",
    ),
    Regex(
        name="leading_spaces",
        expression=re.compile("^\s+?", re.MULTILINE),
        replacement="",
    ),
    Regex(
        name="trailing_spaces",
        expression=re.compile("\s+?$", re.MULTILINE),
        replacement="",
    ),
    Regex(
        name="extra_spaces",
        expression=re.compile("\s\s+?"),
        replacement=" ",
    ),
    Regex(
        name="crlf_newlines",
        expression=re.compile(r"\r\n"),
        replacement="\n",
    ),
    Regex(
        name="cr_newlines",
        expression=re.compile(r"\r"),
        replacement="\n",
    ),
    Regex(
        name="extra_newlines",
        expression=re.compile(r"\n\n+?"),
        replacement="\n",
    ),
)

def clean(text,
          verbose=False):
    matches = set()
    cleaned_text = text
    for regex in regexes:
        cleaned_text = regex.expression.sub(regex.replacement, cleaned_text)
        if verbose:
            matches.add(regex.name)
    if verbose:
        print(matches)
    return cleaned_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Writes the plain text used within "
        "a GATE document to a file"
    )
    parser.add_argument(
        "-i",
        "--input-file",
        dest="input_file",
        required="true",
        help="GATE annotation file"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        dest="output_file",
        help="destination file for text output. "
        "Default is '<filename>.textraction'."
    )
    parser.add_argument(
        "-c",
        "--clean",
        dest="clean",
        action="store_true",
        default=False,
        help="cleans transcript of any speaker tags, extralinguistic features, "
        "etc.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="displays which patterns were replaced in the text"
    )
    args = parser.parse_args()

    annotation_file = gatenlp.AnnotationFile(args.input_file)

    if args.clean:
        text = clean(
            annotation_file.text,
            verbose=args.verbose,
        )
    else:
        text = annotation_file.text

    if args.output_file: output_file = abspath(args.output_file)
    else: output_file = (
        splitext(
            abspath(args.input_file)
        )[0] + ".textraction"
    )

    if isfile(output_file):
        while True:
            response = input(
                "Overwrite file '{}'? y/N --> ".format(output_file)
            ).lower()
            if response == "y":
                break
            elif (response == "n") or (response == ""):
                print("Skipping file '{}'".format(output_file))
                quit()
            else: print("Error: '{}' not recognized.".format(response))

    with open(output_file, "w") as destination:
        destination.write(text)

    print("File written: '{}'".format(output_file))
