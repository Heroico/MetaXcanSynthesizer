#! /usr/bin/env python

__author__ = 'heroico'

import logging
import os
import Logging
import Utilities
import Person
import DataSet
import GEUVADISUtilities
import WeightDBUtilities


class GenerateMasterList(object):
    def __init__(self, args):
        self.input_path = args.input_folder
        self.snp_input_path = args.snp_list
        self.db_path = args.model_database

        self.intermediate_path = args.intermediate_folder
        self.output_folder = args.output_folder
        self.output_path = os.path.join(self.intermediate_path, self.output_folder)

    def run(self):
        if not os.path.exists(self.intermediate_path):
            os.mkdir(self.intermediate_path)

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

        self.filterPeople()
        self.buildFiles()

    def filterPeople(self):
        samples_path = Utilities.samplesInputPath(self.input_path)
        filtered_samples_path = self.filteredSamplesPath()
        if os.path.exists(filtered_samples_path):
            logging.info("%s already exists, delete it if you want it to be done again", filtered_samples_path)
        else:
            logging.info("Filtering people")
            Person.Person.filterSamples(samples_path, filtered_samples_path, "\t", False)

    def filteredSamplesPath(self):
        filtered_samples_path = os.path.join(self.output_path, "samples.sample")
        return filtered_samples_path

    def buildFiles(self):
        logging.info("Loading people")
        samples_input_path = Utilities.samplesInputPath(self.input_path)
        all_people = Person.Person.allPeople(samples_input_path, '\t', False)
        selected_people_by_id = Person.Person.peopleByIdFromFile(self.filteredSamplesPath())
        logging.info("%d total people, %d selected", len(all_people), len(selected_people_by_id))

        logging.info("Loading model database")
        weight_db_logic = WeightDBUtilities.WeightDBEntryLogic(self.db_path)

        logging.info("Loading snps")
        snp_data_set = DataSet.DataSetFileUtilities.loadFromCompressedFile(self.snp_input_path)
        snp_dict = {}
        for snp in snp_data_set.data:
            if snp in weight_db_logic.genes_for_an_rsid:
                snp_dict[snp] = True

        contents = Utilities.contentsWithPatternsFromFolder(self.input_path, ["dosage.txt.gz"])
        for content_name in contents:
            self.buildContentFile(content_name, all_people, selected_people_by_id, snp_dict)

    def buildContentFile(self, content_name, all_people, selected_people_by_id, snp_dict):
        input_path = os.path.join(self.input_path, content_name)
        fileBuilder = GEUVADISUtilities.GEUVADISFilteredFilesBuilder(input_path, self.output_path, content_name, all_people, selected_people_by_id, snp_dict)
        fileBuilder.run()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Transform GEUVADIS-formatted data into IMPUTE-formatted.')

    parser.add_argument("--input_folder",
                        help="Folder with GEUVADIS data",
                        default="data/dosagefiles-hapmap2")

    parser.add_argument("--snp_list",
                        help="file with selected snps",
                        default="data/hapmapSnpsCEU.list.gz")

    parser.add_argument("--model_database",
                        help="Model database",
                        default="data/DGN-WB_0.5.db")

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