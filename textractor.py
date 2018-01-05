#!/usr/bin/env python3

from os.path import abspath
from os.path import splitext
from os.path import isfile
import argparse
import gatenlp
import Levenshtein


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
    parser.add_argument(
        "-r",
        "--regexes",
        nargs="*",
        dest="regex_restrictions",
        required=False,
        help="specific regex patterns desired. If not specified, all will be"
        " run")
    args = parser.parse_args()

    regexes = gatenlp.regex_patterns.regexes

    annotation_file = gatenlp.AnnotationFile(args.input_file)
    if args.regex_restrictions:
        regex_restrictions = [
            regex.name
            for regex in regexes
            if regex.name in args.regex_restrictions
        ]
        if len(args.regex_restrictions) != len(regex_restrictions):
            for desired_regex in args.regex_restrictions:
                if desired_regex not in [ regex.name for regex in regexes ]:
                    not_recognized_string = "'{}' is not a recognized regex pattern.".format(
                        desired_regex
                    )
                    match_ratios = {
                        regex.name : Levenshtein.ratio(
                            regex.name,
                            desired_regex
                        )
                        for regex in regexes
                    }
                    highest_ratio = max(match_ratios.values())
                    if highest_ratio <= 0.5:
                        raise Exception(not_recognized_string)
                    elif highest_ratio >= 0.85:
                        target_ratio = highest_ratio
                    else:
                        target_ratio = 0.5
                    close_matches = [
                        regex_name
                        for regex_name, ratio in match_ratios.items()
                        if ratio >= target_ratio
                    ]
                    if len(close_matches) == 1:
                        suggestion_string = "Did you mean '{}'?".format(
                            close_matches[0],
                        )
                    elif len(close_matches) == 2:
                        suggestion_string = "Did you mean '{}' or '{}'?".format(
                            close_matches[0],
                            close_matches[1],
                        )
                    else:
                        suggestion_string = "Did you mean one of these?: {}".format(
                            ", ".join(close_matches)
                        )
                    if suggestion_string:
                        error_string = "{} {}".format(
                            not_recognized_string,
                            suggestion_string,
                        )
                    else:
                        error_string = not_recognized_string
                    raise Exception(error_string)
            quit()


    else:
        regex_restrictions = False

    if args.clean:
        text = gatenlp.normalize(
            annotation_file.text,
            regex_restrictions=regex_restrictions,
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
