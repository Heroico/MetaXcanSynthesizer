#! /usr/bin/env python

__author__ = 'heroico'

import os
import logging
import numpy
from subprocess import call
import Person
import Logging
import Utilities


GWAS_FAM = "GWAS.fam"
GWAS_LIST = "GWAS.list"
GWAS_FILTER = "GWAS.filter"

class GenerateGWAS(object):
    def __init__(self, args):
        self.dosages_folder = args.dosages_folder
        self.selected_samples_file = args.selected_samples
        self.snp_list_file = args.snp_list

        self.output_folder = args.output_folder
        absolute_output_folder = os.path.join(os.getcwd(), self.output_folder)
        self.FAM_output_path = os.path.join(absolute_output_folder, GWAS_FAM)
        self.list_output_path = os.path.join(absolute_output_folder, GWAS_LIST)
        self.filter_output_path = os.path.join(absolute_output_folder, GWAS_FILTER)

        self.mean = float(args.mean)
        self.se = float(args.se)
        self.cutoff = float(args.cutoff)

    def run(self):
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)

        self.buildFAM()

        self.runPLINK()

    def buildFAM(self):

        numpy.random.seed(1000) #Introduce a seed, but have it be constant. We are not that interested in "truer" randomness at this time.
        all_samples_input_path = Utilities.samplesInputPath(self.dosages_folder)
        all_people = Person.Person.allPeople(all_samples_input_path, '\t', False)
        selected_people_by_id = Person.Person.peopleByIdFromFile(self.selected_samples_file)
        pheno = self.buildPheno(all_people)

        if os.path.exists(self.FAM_output_path):
            logging.info("%s already exists, delete it if you want it to be generated again", self.FAM_output_path)
        else:
            with open(self.FAM_output_path, "w") as file:
                for person in all_people:
                    fields = [person.id, person.id, "0", "0", "0", pheno[person.id]]
                    line = " ".join(fields)+"\n"
                    file.write(line)

        if os.path.exists(self.list_output_path):
            logging.info("%s already exists, delete it if you want it to be generated again", self.list_output_path)
        else:
            with open(self.list_output_path, "w") as file:
                for person in all_people:
                    fields = [person.id, person.id]
                    line = " ".join(fields)+"\n"
                    file.write(line)

        if os.path.exists(self.filter_output_path):
            logging.info("%s already exists, delete it if you want it to be generated again", self.filter_output_path)
        else:
            with open(self.filter_output_path, "w") as file:
                for person in all_people:
                    value = "0"
                    if person.id in selected_people_by_id:
                        value = "1"
                    fields = [person.id, person.id, value]
                    line = " ".join(fields)+"\n"
                    file.write(line)


    def buildPheno(self, all_people):
        pheno = {}
        for person in all_people:
            value = numpy.random.normal(self.mean, self.se)
            if self.cutoff > 0:
                if value < 0:
                    value = 0
                if value > self.cutoff:
                    value = self.cutoff
                value = str(value) if value > 0 else "0.0"
            else:
                value = str(value)
            pheno[person.id] =value
        return pheno

    def runPLINK(self):
        base_dir = os.getcwd()
        dosages_path = os.path.join(base_dir, self.dosages_folder)

        contents = Utilities.contentsWithPatternsFromFolder(self.dosages_folder, ["dosage.txt.gz"])
        os.chdir(self.output_folder)
        for content in contents:
            self.runPLINKForContent(dosages_path, content)

    def runPLINKForContent(self, dosages_path, content):
        #quick and dirty
        chr = content.split(".dosage")[0]

        command = "plink --fam GWAS.fam "
        command += "--dosage %s " % os.path.join(dosages_path, content)
        command += "noheader format=1 skip0=1 skip1=1 skip2=1 Zout "
        command += "--out %s " % chr
        command += "--allow-no-sex "
        command += "--filter GWAS.filter 1"
        call(command.split(" "))



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build a synthetic phenotype and run plink on it')

    parser.add_argument("--selected_samples",
                        help="File with people samples",
                        default="intermediate/IMPUTE/samples.sample")

    parser.add_argument("--dosages_folder",
                        help="Folder with files with people dosages",
                        default="data/dosagefiles-hapmap2")

    parser.add_argument("--snp_list",
                        help="file with selected snps",
                        default="data/hapmapSnpsCEU.list.gz")

    parser.add_argument("--output_folder",
                        help="higher level output folder",
                        default="intermediate/GWAS")

    parser.add_argument("--mean",
                        help="mean for simulated phenotype",
                        default="0.0")

    parser.add_argument("--se",
                        help="standard deviation for simulated phenotype",
                        default="1")

    parser.add_argument("--cutoff",
                        help="max upper bound for phenotype",
                        default="-1.0")

    args = parser.parse_args()

    Logging.configureLogging(7)

    work = GenerateGWAS(args)
    work.run()