__author__ = 'heroico'

import logging
import os
import Logging


class GenerateMasterList(object):
    def __init__(self, args):
        self.results_folder = args.results_folder
        self.list = args.list
        self.path = os.path.join(self.results_folder, self.list)

    def run(self):
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build correlations and/or covariances from PHASE3 data and weights database.')

    parser.add_argument("--results_folder",
                        help="higher level output folder",
                        default="results")

    parser.add_argument("--list",
                        help="name of weight db in data folder",
                        default="master_list.txt")


    args = parser.parse_args()

    Logging.configureLogging(7)

    work = GenerateMasterList(args)
    work.run()