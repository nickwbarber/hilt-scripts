#!/usr/bin/env python3

# calculates Cohen's Kappa scores from CompanionBot Importance annotations

import os
import sys
import re
import argparse
import gatenlp


# parses command line arguments
# sample command:
#   importanceKappa --csv-output --annotation-set event_spans file1.xml file2.xml

csv_format = 'file1,file2,annotation_type:attribute,kappa_score,kappa_length'

parser = argparse.ArgumentParser(
    description="calculates Cohen's Kappa scores from "
    "CompanionBot Importance annotations"
)
parser.add_argument(
    '--csv-header',
    action='store_true',
    dest='csv_header',
    help='''print the header line for stats in CSV format to terminal:
     ({})'''.format(csv_format)
)

# stop arg-parse configuration if csv-header is requested
if '--csv-header' in sys.argv:
    print(csv_format)
    quit()

parser.add_argument(
    '--csv-output',
    action='store_true',
    dest='csv_output_mode',
    help='''print stats in CSV format to terminal and exit:
     ({})'''.format(csv_format)
)
parser.add_argument(
    '--annotation-set',
    dest='annotation_set',
    type=str,
    help='specifies the annotation set from which to gather annotations'
)
parser.add_argument(
    '--schema',
    dest='schema',
    required=True,
    type=str,
    help='specifies the annotation schema used to create annotations'
)
parser.add_argument(
    '--annotation-type',
    type=str,
    required=True,
    help='the annotation type to gather'
)
parser.add_argument(
    'source1',
    type=str,
    help='the first source annotation file'
)
parser.add_argument(
    'source2',
    type=str,
    help='the second source annotation file'
)
parser.add_argument(
    '--weighting',
    type=str,
    default='none',
    help="the type of weighting used to calculate Kappa; "
    "can be 'linear', 'quadratic', or 'none'"
)

# parse command-line arguments
args = parser.parse_args()

csv_output_mode = args.csv_output_mode
source1 = gatenlp.Annotation(args.source1)
source2 = gatenlp.Annotation(args.source2)
schema = gatenlp.Schema(args.schema)
weighting = args.weighting
if weighting.lower() == 'none':
    weighting = None

test = gatenlp.pair_annotations(
    source1.get_annotations(
        annotation_type=args.annotation_type,
        annotation_set=args.annotation_set
    ),
    source2.get_annotations(
        annotation_type=args.annotation_type,
        annotation_set=args.annotation_set
    ),
    annotation_type=args.annotation_type,
    schema=schema
)

for x in test:
    # use linear weighting for importance
    # don't use weighting for categorical values like polarity
    # if no weighting, assign unique numbers for each annotation feature value

    kappa = gatenlp.kappa(x, weights=weighting)

    if csv_output_mode:
        print(
            '{},{},{}:{},{},{}'.format(
                os.path.basename(args.source1),
                os.path.basename(args.source2),
                args.annotation_type,
                x.attribute,
                kappa['score'],
                kappa['length']
            )
        )
    else:
        print(kappa)
