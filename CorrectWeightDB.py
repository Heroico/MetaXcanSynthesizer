#! /usr/bin/env python
__author__ = 'heroico'

import os
import logging
import gzip
import math
import re
import Logging
import sqlite3
import Utilities

class FixDB(object):
    def __init__(self, args):
        self.weight_db = args.weight_db
        self.weight_db_folder = args.weight_db_folder
        self.weight_db_regexp = None
        if args.weight_db_pattern:
            self.weight_db_regexp = re.compile(args.weight_db_pattern)
        else:
            self.weight_db_regexp = re.compile(".*")
        self.var_path = args.variance_file

    def run(self):
        logging.info("Loading variance %s", self.var_path)
        variance = self.loadVariance(self.var_path)

        if self.weight_db_folder:
            self.fixDBSAtFolder(self.weight_db_folder, variance)
        elif self.weight_db:
            self.fixDBAtPath(self.weight_db, variance)

    def fixDBSAtFolder(self, folder, variance):
        contents = Utilities.contentsWithRegexpFromFolder(folder, self.weight_db_regexp)
        for content in contents:
            path = os.path.join(folder, content)
            size = os.path.getsize(path)
            if size==0:
                logging.info("Skipping %s, zero size", path)
                continue
            self.fixDBAtPath(path, variance)

    def fixDBAtPath(self, path, variance):
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        logging.info("Loading db %s", path)
        query_results = cursor.execute("SELECT rsid, weight, gene FROM weights;")
        results = []
        for i,result in enumerate(query_results):
            results.append(result)

        for i,result in enumerate(results):
            snp = result[0]
            if not snp in variance:
                logging.log(9, "snp %s not in variance", snp)
                self.deleteSnpFromDB(snp, cursor)
                continue

            var = float(variance[snp])
            if var == 0:
                logging.log(9, "zero variance for snp %s", (snp,))
                self.deleteSnpFromDB(snp, cursor)
                continue

            gene = result[2]

            sigma = math.sqrt(var)
            weight = float(result[1])
            corrected = str(weight/sigma)
            cursor.execute("UPDATE weights SET weight = :w WHERE rsid = :s and gene = :g", {"w":corrected, "s":snp, "g":gene})

        connection.commit()
        connection.close()

    def deleteSnpFromDB(self, snp, cursor):
        cursor.execute("DELETE FROM weights where rsid = ?", (snp,))

    def loadVariance(self, path):
        variance = {}
        with gzip.open(path, 'rb') as variance_file:
            for line in variance_file:
                comps = line.strip().split(",")
                snp = comps[0]
                if snp in variance:
                    logging.info("Snp %s already in variance", snp)
                variance[comps[0]] = comps[1]
        return variance


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build a synthetic phenotype and run plink on it')

    parser.add_argument("--weight_db",
                        help="Database with transcriptome model",
                        default=None)

    parser.add_argument("--weight_db_folder",
                        help="Folder with databases with transcriptome model",
                        default=None)

    parser.add_argument("--weight_db_pattern",
                        help="Regexp pattern of dbs to process",
                        default=None)

    parser.add_argument("--variance_file",
                        help="File with dosage variance",
                        default="data/var.txt.gz")

    parser.add_argument("--verbosity",
                        help="Log verbosity level. 1 is everything being logged. 10 is only high level messages, above 10 will hardly log anything",
                        default = "10")


    args = parser.parse_args()

    Logging.configureLogging(int(args.verbosity))

    work = FixDB(args)
    work.run()
