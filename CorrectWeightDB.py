#! /usr/bin/env python
__author__ = 'heroico'

import logging
import gzip
import math
import Logging
import sqlite3


class FixDB(object):
    def __init__(self, args):
        self.weight_db = args.weight_db
        self.var_path = args.variance_file

    def run(self):
        logging.info("Loading variance %s", self.var_path)
        variance = self.loadVariance(self.var_path)

        self.fixDBAtPath(self.weight_db, variance)

    def fixDBAtPath(self, path, variance):
        connection = sqlite3.connect(self.weight_db)
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
                self.deleteSnpFromDB(snp, cursor, connection)
                continue

            var = float(variance[snp])
            if var == 0:
                logging.log(9, "zero variance for snp %s", (snp,))
                self.deleteSnpFromDB(snp, cursor, connection)
                continue

            gene = result[2]

            sigma = math.sqrt(var)
            weight = float(result[1])
            corrected = str(weight/sigma)
            cursor.execute("UPDATE weights SET weight = :w WHERE rsid = :s and gene = :g", {"w":corrected, "s":snp, "g":gene})

        connection.commit()
        connection.close()

    def deleteSnpFromDB(self, snp, cursor, connection):
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
                        default="data/mod/DGN-WB_0.5.db")

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
