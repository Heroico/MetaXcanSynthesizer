#! /usr/bin/env python

__author__ = 'heroico'

import os
import logging
import numpy
import Person
import Logging


GWAS_FAM = "GWAS.fam"

class GenerateGWAS(object):
    def __init__(self, args):
        self.samples_file = args.samples
        self.snp_list_file = args.snp_list
        self.output_folder = args.output_folder

        self.mean = float(args.mean)
        self.se = float(args.se)
        self.cutoff = float(args.cutoff)

    def run(self):
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)

        self.buildFAM()

    def buildFAM(self):
        output_path = os.path.join(self.output_folder, GWAS_FAM)
        if os.path.exists(output_path):
            logging.info("%s already exists, delete it if you want it to be generated again", output_path)
            return

        numpy.random.seed(1000) #Introduce a seed, but have it be constant. We are not that interested in "truer" randomness at this time.
        people = Person.Person.allPeople(self.samples_file)

        with open(output_path, "wb") as file:
            for person in people:
                value = numpy.random.normal(self.mean, self.se)
                if value < 0:
                    value = 0
                if value > self.cutoff:
                    value = self.cutoff
                value = str(value) if value > 0 else "0.0"
                fields = [person.id, person.id, "0", "0", "0", value]
                line = " ".join(fields)+"\n"
                file.write(line)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Transform GEUVADIS-formatted data into IMPUTE-formatted. Will ')

    parser.add_argument("--samples",
                        help="File with people samples",
                        default="intermediate/IMPUTE/samples.sample")

    parser.add_argument("--snp_list",
                        help="file with selected snps",
                        default="data/hapmapSnpsCEU.list.gz")

    parser.add_argument("--output_folder",
                        help="higher level output folder",
                        default="intermediate/GWAS")

    parser.add_argument("--mean",
                        help="mean for simulated phenotype",
                        default="0.5")

    parser.add_argument("--se",
                        help="standard deviation for simulated phenotype",
                        default="0.2")

    parser.add_argument("--cutoff",
                        help="max upper bound for phenotype",
                        default="1.0")

    args = parser.parse_args()

    Logging.configureLogging(7)

    work = GenerateGWAS(args)
    work.run()