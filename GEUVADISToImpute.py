#! /usr/bin/env python

__author__ = 'heroico'

import logging
import os
import Logging
import Utilities
import Person

class GenerateMasterList(object):
    def __init__(self, args):
        self.input_path = args.input_folder

        self.intermediate_path = args.intermediate_folder
        self.output_folder = args.output_folder
        self.output_path = os.path.join(self.intermediate_path, self.output_folder)

    def run(self):
        if not os.path.exists(self.intermediate_path):
            os.mkdir(self.intermediate_path)

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

        self.filterPeople()

    def filterPeople(self):
        samples_file = Utilities.contentsWithPatternsFromFolder(self.input_path, ["samples"])[0]
        samples_path = os.path.join(self.input_path, samples_file)
        filtered_samples_path = os.path.join(self.output_path, "samples.sample")

        Person.Person.filterSamples(samples_path, filtered_samples_path, "\t")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Transform GEUVADIS-formatted data into IMPUTE-formatted. Will ')

    parser.add_argument("--input_folder",
                        help="Folder with GEUVADIS data",
                        default="data/dosagefiles-hapmap2")

    parser.add_argument("--intermediate_folder",
                        help="higher level output folder",
                        default="intermediate")

    parser.add_argument("--output_folder",
                        help="higher level output folder",
                        default="IMPUTE")

    parser.add_argument("--filter",
                        help="kind of population filter.",
                        default="EUR")


    args = parser.parse_args()

    Logging.configureLogging(7)

    work = GenerateMasterList(args)
    work.run()