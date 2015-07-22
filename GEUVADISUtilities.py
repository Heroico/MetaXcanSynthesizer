__author__ = 'heroico'

import logging
import os
import gzip
import Utilities


class GDTF:
    """Format of GEUVADIS dosage"""
    CHR = 0
    RSID = 1
    POSITION = 2
    ALLELE_0 = 3
    ALLELE_1 = 4
    COLUMN_5 = 5
    FIRST_DATA_COLUMN = 6


class GEUVADISFilteredFilesBuilder(object):
    def __init__(self, input_file_path, output_path, name, all_people, selected_people_by_id, snps_dict, delimiter=" "):
        self.input_file_path = input_file_path
        self.output_path = output_path
        self.name = name
        self.all_people = all_people
        self.selected_people_by_id = selected_people_by_id
        self.snps_dict = snps_dict
        self.delimiter = delimiter

        self.legend_file = None
        self.dosage_file = None

    def run(self):
        dosage_path = self.dosagePath()
        legend_path = self.legendPath()
        if os.path.exists(dosage_path) or os.path.exists(legend_path):
            logging.info("%s and/or %s already exists, delete it if you want it done again", dosage_path, legend_path)
            return

        logging.info("building %s", dosage_path)
        with gzip.open(legend_path, 'wb') as legend_file:
            self.legend_file = legend_file
            legend_file.write("id position a0 a1 TYPE AFR AMR EAS EUR SAS ALL\n")
            with gzip.open(dosage_path, 'wb') as dosage_file:
                self.dosage_file = dosage_file

                iterator = Utilities.CSVFileIterator(self.input_file_path, compressed=True)
                callback = self
                iterator.iterate(callback)

        self.reset()

    def __call__(self, i, row):
        """Assumes -self.legend_file- and -self.dosage_file- to be defined as gzip files"""
        rsid = row[GDTF.RSID]

        if rsid not in self.snps_dict:
            logging.log(5, "rsid %s not in whitelist", rsid)
            return

        position = row[GDTF.POSITION]
        a0 = row[GDTF.ALLELE_0]
        a1 = row[GDTF.ALLELE_1]

        #legend
        first = "%s:%s:%s:%s" % (rsid, position, a0, a1)
        fields = [first, position, a0, a1, "Biallelic_SNP", "NA", "NA", "NA", "NA", "NA", "NA"]
        legend_line = " ".join(fields)+"\n"
        self.legend_file.write(legend_line)

        #dosages
        dosages = row[GDTF.FIRST_DATA_COLUMN:]
        if len(dosages) != len(self.all_people):
            logging.log(9,"rsid %s: not enough dosage: %d, %d", rsid, len(dosages), len(self.all_people))
            assert False
        selected_dosages = self.pickDosages(dosages)
        dosage_line = " ".join(selected_dosages)+"\n"
        self.dosage_file.write(dosage_line)

    def pickDosages(self, dosages):
        selected = []
        for i, person in enumerate(self.all_people):
            if not person.id in self.selected_people_by_id:
                continue
            selected.append(dosages[i])
        return selected

    def dosagePath(self):
        base_name = self.name.strip(".dosage.txt.gz")
        dosage_name = Utilities.dosageName(base_name)
        output_path = os.path.join(self.output_path, dosage_name)
        return output_path

    def legendPath(self):
        base_name = self.name.strip(".dosage.txt.gz")
        legend_name = Utilities.legendName(base_name)
        output_path = os.path.join(self.output_path, legend_name)
        return output_path

    def reset(self):
        self.legend_file = None
        self.dosage_file = None
