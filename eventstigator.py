import os
from lxml import etree
import gatenlp


class EvitaFile:
    def __init__(self, filename):
        self._filename = filename
        self._tree = etree.parse(self.filename)
        self._root = self.tree.getroot()
        # self._nodes = None
        # self._text_with_nodes = None
        self._annotations = None
        self._events = None
        # self._interval_tree = None

    @property
    def filename(self):
        return self._filename

    @property
    def tree(self):
        return self._tree

    @property
    def root(self):
        return self._root

    @property
    def text(self):
        return self.root.find("./text").text

    @property
    def annotations(self):
        if not self._annotations:
            self._annotations = [
                Annotation(x)
                for x in self.iter_annotations()
            ]
        return self._annotations

    def iter_annotations(self):
        annotations = self.root.iterfind(
            ".//tarsqi_tags/"
        )
        for x in annotations:
            if "LINK" not in x.tag:
                yield x

    @property
    def events(self):
        if not self._events:
            self._events = [
                x for x in self.annotations
                if x.type == "EVENT"
            ]
        return self._events

class Annotation:
    def __init__(self, annotation_element):
        self._type = annotation_element.tag
        self._attrib = dict(annotation_element.attrib)
        self._start = int(self.attrib["begin"])
        del self.attrib["begin"]
        self._end = int(self.attrib["end"])
        del self.attrib["end"]

    @property
    def type(self):
        return self._type

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def attrib(self):
        return self._attrib


if __name__ == "__main__":

    import argparse


    parser = argparse.ArgumentParser(
        description="Writes the plain text used within "
        "a GATE document to a file"
    )
    parser.add_argument(
        "-g",
        "--gate-file",
        dest="gate_file_path",
        required="true",
        help="GATE annotation file"
    )
    parser.add_argument(
        "-e",
        "--evita-file",
        dest="evita_file_path",
        required="true",
        help="Evita annotation file"
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

    if args.verbose:
        print("gate_file_path == {}".format(repr(args.gate_file_path)))
        print("evita_file_path == {}".format(repr(args.evita_file_path)))

    gate_file = gatenlp.AnnotationFile(args.gate_file_path)
    evita_file = EvitaFile(args.evita_file_path)

    old_evita_set = gate_file.annotation_sets_dict["Evita"]
    if old_evita_set:
        old_evita_set.delete()

    if gate_file.text == evita_file.text:
        is_text_same = True
    else:
        is_text_same = False
        changes = gatenlp.diff.get_change_list_2(
            evita_file.text,
            gate_file.text,
        )
        new_annotations = []

    if args.verbose:
        print("is_text_same == {}".format(is_text_same))


    gate_evita_set = gate_file.create_annotation_set("Evita")

    for event in evita_file.events:
        new_annotation = gate_evita_set.create_annotation(
            annotation_type=event.type,
            start=event.start,
            end=event.end,
            feature_dict=event.attrib,
        )
        if not is_text_same:
            new_annotations.append(new_annotation)

    if not is_text_same:
        gatenlp.diff.align_annotations_2(new_annotations, changes)
        gatenlp.diff.assure_nodes(new_annotations, gate_file)

    gate_file.save_changes()

    if args.verbose:
        print()