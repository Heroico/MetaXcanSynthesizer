#! /usr/bin/env python
"""
Dosages in predixcan format are assumed for now.
"""
import os
import re
import logging
import pandas
import numpy
from subprocess import call

from utils import Logging

def _get_pheno(input_pheno, samples):
    if input_pheno:
        pheno = pandas.read_table(input_pheno, sep="\s+")
        pheno = pheno[["ID", "PHENO"]]
        return pheno

    p = numpy.random.normal(size=len(samples))
    p = pandas.DataFrame(data = {"ID":samples.ID, "PHENO":p})
    return p

#This method is the most rigid thing of this script.
def process_pheno(dosage_folder, input_pheno, output_folder):
    names = os.listdir(dosage_folder)

    samples = [x for x in names if ".sample" in x][0]
    samples = os.path.join(dosage_folder, samples)
    samples = pandas.read_table(samples, sep="\s+")

    if list(samples.columns.values) != ["ID", "POP", "GROUP", "SEX"]:
        raise RuntimeError("Unexpected samples file")

    pheno = _get_pheno(input_pheno, samples)
    merged = pandas.merge(samples, pheno, how="left", on="ID")

    valid = ~merged.PHENO.isnull()
    merged["FILTER"] = 0
    merged.loc[valid, "FILTER"] = 1
    merged = merged.fillna("NA")

    fam = merged[["ID", "SEX","PHENO"]]
    fam["FAMILY_ID"] = fam.ID
    fam["FATHER_ID"] = 0
    fam["MOTHER_ID"] = 0
    fam = fam[["FAMILY_ID", "ID", "FATHER_ID", "MOTHER_ID", "SEX", "PHENO"]]
    fam_path = os.path.join(output_folder, "GWAS.fam")
    fam.to_csv(fam_path, index=False, header=False, sep= " ")

    filter = merged[["ID", "FILTER"]]
    filter["FAMILY_ID"] = filter.ID
    filter = filter[["FAMILY_ID", "ID", "FILTER"]]
    filter_path = os.path.join(output_folder, "GWAS.filter")
    filter.to_csv(filter_path, index=False, header=False, sep= " ")


regexp = re.compile(".*chr(\d+).*")
def _run_plink_for_file(dosage_folder, dosage_file, output_folder, output_prefix):
    # quick and dirty
    if not output_prefix:
        chr = dosage_file.split(".dosage")[0]
        out = os.path.join(output_folder, chr)
    else:
        number = regexp.match(dosage_file).group(1)
        out = "_".join([output_prefix,"chr"+number])
        out = os.path.join(output_folder, out)

    command = "plink --fam %s " % os.path.join(output_folder, "GWAS.fam")
    command += "--dosage %s " % os.path.join(dosage_folder, dosage_file)
    command += "noheader format=1 skip0=1 skip1=1 skip2=1 Zout "
    command += "--out %s " % out
    command += "--allow-no-sex "
    command += "--filter %s 1" % os.path.join(output_folder, "GWAS.filter")
    call(command.split())

def run_plink(dosage_folder, output_folder, output_prefix):
    names = [x for x in os.listdir(dosage_folder) if "gz" in x]
    for name in names:
        _run_plink_for_file(dosage_folder, name, output_folder, output_prefix)

def run(args):
    if os.path.exists(args.output_folder):
        logging.info("Output already exists, delete/move it if you want it done again.")
        return

    #set seed for reproducibility
    numpy.random.seed(1000)

    os.makedirs(args.output_folder)
    process_pheno(args.dosage_folder, args.input_pheno, args.output_folder)
    run_plink(args.dosage_folder, args.output_folder, args.output_prefix)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Ran a GWAS against a syntethic phenotype. Supports individual filtering')

    parser.add_argument("--dosage_folder", help="Folder with dosage, predixcan format", default=None)
    parser.add_argument("--input_pheno", help="Folder with files with people dosages", default=None)
    parser.add_argument("--output_folder", help="higher level output folder", default=None)
    parser.add_argument("--output_prefix", help="Optional: name to use", default=None)
    parser.add_argument("--verbosity", help="Logging verbosity", default=10)

    args = parser.parse_args()

    Logging.configureLogging(int(args.verbosity))

    run(args)