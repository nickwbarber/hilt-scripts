import gatenlphiltlab
import explanatory_style as es
import argparse
import os
import io
import csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="extracts eaus in HiLT PES GATE annotation documents to a"
        " csv formatted representation"
    )
    parser.add_argument(
        "-i",
        "--annotation-file",
        dest="annotation_files",
        nargs="+",
        required="true",
        help="GATE annotation files"
    )
    parser.add_argument(
        "-o",
        "--csv-file",
        dest="csv_file",
        required="true",
        help="destination csv file"
    )
    args = parser.parse_args()

    fieldnames = [
        "filename",
        "event_id",
        "event_text",
        "attribution_id",
        "attribution_text",
    ]

    with open(args.csv_file, "w") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for annotation_file_path in args.annotation_files:
            gate_file = gatenlphiltlab.AnnotationFile(annotation_file_path)
            EAU_sets = [
                annotation_set
                for annotation_set in gate_file.annotation_sets
                if (
                    "consensus" in annotation_set.name
                    and (
                        "event" in annotation_set.name
                        or "attribution" in annotation_set.name
                    )
                )
            ]
            EAU_annotations = [
                EAU_annotation
                for EAU_set in EAU_sets
                for EAU_annotation in EAU_set
            ]

            EAUs = es.get_event_attribution_units_from_annotations(
                EAU_annotations
            )

            for EAU in EAUs:
                writer.writerow(
                    {
                        "filename" : os.path.basename(gate_file.filename),
                        "event_id" : EAU.event.annotation.id,
                        "event_text" : repr(EAU.event.annotation.get_concatenated_text(separator=" ## ")),
                        "attribution_id" : EAU.attribution.annotation.id,
                        "attribution_text" : repr(EAU.attribution.annotation.get_concatenated_text(separator=" ## ")),
                    }
                )
