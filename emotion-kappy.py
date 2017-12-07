#!/usr/bin/env python3

import csv
from collections import deque
import os
import re
import argparse
import time


"""Annotators have been unknowingly annotating over existing annotation
documents, and without editing the code of the underlying tool, this
will most likely persist."""


# container for annotations lines from CSVs
annotations = {
        'annotator1':[],
        'annotator2':[]
        }

# all possible labels
labelBank = (
    'Anger',
    'Boredom',
    'Confusion',
    'Disgust',
    'Fear',
    'Happiness',
    'Sadness',
    'Surprise',
    'Neutral'
    )

# set starting values for each annotation pair
kappa = {}
for label in labelBank:
    kappa[label] = {x: 0.0 for x in labelBank}

# prep positions for queueing
prevPosition1 = 0
prevPosition2 = 0
currPosition1 = 0
currPosition2 = 0
prevLabel1 = ''
prevLabel2 = ''
currLabel1 = ''
currLabel2 = ''
queue1 = deque()
queue2 = deque()

def insertAnnotations(annotator, fileName):
    global annotations
    reader = csv.reader(fileName)
    rows = deque()
    for row in reader:
        rows.append([float(row[1]), row[2]])

    first = rows.popleft()
    lines = [first]
    for row in range(len(rows)):
        line = rows.popleft()
        if line[0] >= lines[-1][0]: lines.append(line)
        # if the previous annotation's timestamp is greater than
        # the current, reset the annotations to be calculated
        else: lines = [line]

    annotations[annotator] = lines

def compareAnnotations():
    global prevPosition1
    global prevPosition2
    global currPosition1
    global currPosition2
    global prevLabel1
    global prevLabel2
    global currLabel1
    global currLabel2
    global queue1
    global queue2
    global annotations
    global kappa

    queue1 = deque(annotations['annotator1'])
    queue2 = deque(annotations['annotator2'])

    temp1 = queue1.popleft()
    prevPosition1 = temp1[0]
    prevLabel1 = temp1[1].replace('Possible ', '')

    temp2 = queue2.popleft()
    prevPosition2 = temp2[0]
    prevLabel2 = temp2[1].replace('Possible ', '')

    temp1 = queue1.popleft()
    currPosition1 = temp1[0]
    currLabel1 = temp1[1].replace('Possible ', '')

    temp2 = queue2.popleft()
    currPosition2 = temp2[0]
    currLabel2 = temp2[1].replace('Possible ', '')

    recursiveFunc()

def recursiveFunc():
    global prevPosition1
    global prevPosition2
    global currPosition1
    global currPosition2
    global prevLabel1
    global prevLabel2
    global currLabel1
    global currLabel2
    global queue1
    global queue2
    global annotations
    global kappa

    if currPosition1 < currPosition2:
        kappa[prevLabel1][prevLabel2] += currPosition1 - prevPosition1
        if len(queue1) > 0:
            prevPosition1 = currPosition1
            prevPosition2 = currPosition1
            prevLabel1 = currLabel1
            temp1 = queue1.popleft()
            currPosition1 = temp1[0]
            currLabel1 = temp1[1]
            currLabel1 = currLabel1.replace('Possible ', '')
        elif len(queue2) > 0:
            pass
        else:
            return
    elif currPosition1 > currPosition2:
        kappa[prevLabel1][prevLabel2] += currPosition2 - prevPosition2
        if len(queue2) > 0:
            prevPosition1 = currPosition2
            prevPosition2 = currPosition2
            prevLabel2 = currLabel2
            temp2 = queue2.popleft()
            currPosition2 = temp2[0]
            currLabel2 = temp2[1]
            currLabel2 = currLabel2.replace('Possible ', '')
        elif len(queue2) > 0:
            pass
        else:
            return
    else:
        kappa[prevLabel1][prevLabel2] += currPosition2 - prevPosition2
        if len(queue1) > 0:
            prevPosition1 = currPosition1
            prevPosition2 = currPosition1
            prevLabel1 = currLabel1
            temp1 = queue1.popleft()
            currPosition1 = temp1[0]
            currLabel1 = temp1[1]
            currLabel1 = currLabel1.replace('Possible ', '')
        elif len(queue2) > 0:
            pass
        else:
            return
        if len(queue2) > 0:
            prevPosition1 = currPosition2
            prevPosition2 = currPosition2
            prevLabel2 = currLabel2
            temp2 = queue2.popleft()
            currPosition2 = temp2[0]
            currLabel2 = temp2[1]
            currLabel2 = currLabel2.replace('Possible ', '')
        elif len(queue2) > 0:
            pass
        else:
            return
    recursiveFunc()


def calculateKappa():

    # TODO: shorten this section more. It's redundant as it is.

    # amount of seconds with same labels
    agreement = sum(
        [kappa[label][label] for label in labelBank]
        )

    # amount of seconds the first annotator labeled 'Anger'
    anger1 = sum(
        [kappa['Anger'][label] for label in labelBank]
        )
    boredom1 = sum(
        [kappa['Boredom'][label] for label in labelBank]
        )
    confusion1 = sum(
        [kappa['Confusion'][label] for label in labelBank]
        )
    disgust1 = sum(
        [kappa['Disgust'][label] for label in labelBank]
        )
    fear1 = sum(
        [kappa['Fear'][label] for label in labelBank]
        )
    happiness1 = sum(
        [kappa['Happiness'][label] for label in labelBank]
        )
    sadness1 = sum(
        [kappa['Sadness'][label] for label in labelBank]
        )
    surprise1 = sum(
        [kappa['Surprise'][label] for label in labelBank]
        )
    neutral1 = sum(
        [kappa['Neutral'][label] for label in labelBank]
        )

    # amount of seconds the second annotator labeled 'Anger'
    anger2 = sum(
        [kappa[label]['Anger'] for label in labelBank]
        )
    boredom2 = sum(
        [kappa[label]['Boredom'] for label in labelBank]
        )
    confusion2 = sum(
        [kappa[label]['Confusion'] for label in labelBank]
        )
    disgust2 = sum(
        [kappa[label]['Disgust'] for label in labelBank]
        )
    fear2 = sum(
        [kappa[label]['Fear'] for label in labelBank]
        )
    happiness2 = sum(
        [kappa[label]['Happiness'] for label in labelBank]
        )
    sadness2 = sum(
        [kappa[label]['Sadness'] for label in labelBank]
        )
    surprise2 = sum(
        [kappa[label]['Surprise'] for label in labelBank]
        )
    neutral2 = sum(
        [kappa[label]['Neutral'] for label in labelBank]
        )

    # count total from one perspective
    total = sum(
        [anger1,
            boredom1,
            confusion1,
            disgust1,
            fear1,
            happiness1,
            sadness1,
            surprise1,
            neutral1
            ]
        )

    agreement = (agreement
        /total)

    anger3 = ((anger1 * anger2)
        /total)

    boredom3 = ((boredom1 * boredom2)
        /total)

    confusion3 = ((confusion1 * confusion2)
        /total)

    disgust3 = ((disgust1 * disgust2)
        /total)

    fear3 = ((fear1 * fear2)
        /total)

    happiness3 = ((happiness1 * happiness2)
        /total)

    sadness3 = ((sadness1 * sadness2)
        /total)

    surprise3 = ((surprise1 * surprise2)
        /total)

    neutral3 = ((neutral1 * neutral2)
        /total)

    chance = (sum(
        [anger3,
            boredom3,
            confusion3,
            disgust3,
            fear3,
            happiness3,
            sadness3,
            surprise3,
            neutral3
            ]
        )
        /total)

    kappa_score = (agreement - chance) / (1 - chance)

    return {
        'total':total,
        'agreement':agreement,
        'chance':chance,
        'kappa_score':kappa_score
        }


def timespanToSeconds(timespan):
    h, m, s = timespan.split(':')
    h = float(h)
    m = float(m)
    s = float(s)
    return (h*60*60 + m*60 + s)

if __name__ == '__main__':
    parser= argparse.ArgumentParser(
        description=("calculates Cohen's Kappa scores from CompanionBot "
            "Emotion Detection annotation files"
            )
        )
    #TODO: finish csv header output
    parser.add_argument(
        '-H',
        '--csv-header',
        action='store_true',
        dest='csv_header',
        help=("print the header line for stats in CSV format to terminal: "
            "(file1,file2,total,agreement,chance,kappa_score)"
            )
        )
    parser.add_argument(
        '-c',
        '--csv-output',
        action='store_true',
        dest='csv_output_mode',
        help=("print stats in CSV format to terminal: "
            "(file1,file2,total,agreement,chance,kappa_score)"
            )
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

    args = parser.parse_args()
    csv_output_mode = args.csv_output_mode
    sources = (
        os.path.abspath(args.source1),
        os.path.abspath(args.source2)
        )
    for source in sources:
        if not os.path.isfile(source):
            print("'{}' not a valid file path!".format(source))
    for source in sources:
        if not os.path.isfile(source): quit()

    CSV_files = []
    for source in sources:
        source = os.path.abspath(source)
        if source.endswith('.txt'):
            readFile = open(source)
            outputFile = (
                os.path.join(
                    os.path.dirname(source),
                    re.sub('.txt$', '.csv', os.path.basename(source))
                    )
                )
            with open(outputFile, 'w', newline='') as csvFile:
                lines = []
                for line in readFile.readlines():
                    line = re.sub(', ', ',', line)
                    line = re.sub('file:///', '', line)
                    tokens = line.split(',')
                    if ':' in tokens[1]:
                        tokens[1] = timespanToSeconds(tokens[1])
                    for x in range(len(tokens)):
                        tokens[x] = str(tokens[x]).rstrip()
                    lines.append(tokens)
                for line in lines:
                    csv.writer(csvFile).writerow(line)
            for x in range(3):
                if os.path.isfile(outputFile): break
                else: time.sleep(1)
            CSV_files.append(outputFile)
        elif source.endswith('.csv'):
            CSV_files.append(source)
        else: print('{} not recognized'.format(source))

    # If the label is not recognized, use previous.
    # If no previous, use 'neutral'.
    count = 0
    for f in CSV_files:
        count =+ 1
        lines = []
        for line in open(f).readlines():
            lines.append(line.rstrip('\n').split(','))
        with open(f, 'w', newline='\n') as csvFile:
            for line in range(len(lines)):
                # elements: 0=file, 1=duration, 2=label, 3=time
                if lines[line][2] not in labelBank:
                    if line - 2 >= 0:
                        if lines[line][2].lower() == 'No'.lower():
                            lines[line - 1][2] = lines[line - 2][2]
                            lines[line][2] = lines[line - 2][2]
                        else: lines[line][2] = lines[line - 1][2]
                    else: lines[line][2] = 'Neutral'
            for line in lines:
                csv.writer(csvFile).writerow(line)

        '''
        with open(f, 'r', newline='') as csvFile:
            annotators.update(
                    ('annotator_{}'.format(str(count),
                    insertAnnotations('annotator1', csvFile)
                        )
                    )
        '''


    with open(CSV_files[0], 'r', newline='') as csvFile:
        insertAnnotations('annotator1', csvFile)

    with open(CSV_files[1], 'r', newline='') as csvFile:
        insertAnnotations('annotator2', csvFile)

    compareAnnotations()

    stats = calculateKappa()

    '''
    if csv_header:
        print(
            '{},{},{},{},{},{}'.format(
                'file1',
                'file2',
                'length',
                'agreement',
                'chance',
                'kappa_score'
                )
            )
    '''

    if csv_output_mode:
        #TODO: create csv-header output
        #file1,file2,total,agreement,chance,kappa_score
        print(
            '{},{},{},{},{},{}'.format(
                os.path.basename(CSV_files[0]),
                os.path.basename(CSV_files[1]),
                round(stats['total'],2),
                round(stats['agreement'],2),
                round(stats['chance'],2),
                round(stats['kappa_score'],2)
                )
            )

    else:
        seconds = stats['total']
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        print(
            'File length'.ljust(20, '.')
            + ' {}h{}m{}s'.format(
                int(hours), int(minutes), int(seconds)
                )
            )
        print(
            'Total agreement'.ljust(20, '.')
            + ' {}%'.format(
                float(round(stats['agreement'],2) * 100)
                )
            )
        print(
            'Chance agreement'.ljust(20, '.')
            + ' {}%'.format(
                float(round(stats['chance'],2) * 100)
                )
            )
        print(
            'Kappa score'.ljust(20, '.')
            + ' {}'.format(
                round(stats['kappa_score'],2)
                )
            )
