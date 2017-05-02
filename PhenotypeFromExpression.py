#! /usr/bin/env python

import logging
import numpy
import pandas

from utils import Logging
from utils import Utilities

def standardize(x):
    scale = numpy.std(x)
    if scale == 0:
        return numpy.repeat(numpy.nan,len(x))
    mean = numpy.mean(x)
    x = x - mean
    x = x / scale
    return x

def load_expression(expression):
    expression = pandas.read_table(expression)
    expression = expression.apply(standardize)
    expression = expression.dropna(axis=1)
    return expression

def run(args):
    logging.info("Reading samples")
    samples = pandas.read_table(args.selected_samples, sep="\s+")

    logging.info("Reading expression")
    expression = load_expression(args.expression)
    columns = expression.columns

    numpy.random.seed(1000)  # Introduce a seed, but have it be constant for reproducibility. We are not that interested in "truer" randomness at this time.
    effect_sizes = numpy.random.normal(size=len(columns))
    y = numpy.dot(expression, effect_sizes)
    samples["PHENO"] = y

    phenotype_path = args.output_prefix + ".pheno.txt"
    Utilities.ensure_requisite_folders(phenotype_path)
    samples.to_csv(phenotype_path, index=False, sep="\t")

    effect_sizes = {"gene":expression.columns.values, "effect_sizes":effect_sizes}
    effect_sizes = pandas.DataFrame(effect_sizes)
    effect_sizes_path = args.output_prefix + ".effect_sizes.txt"
    effect_sizes.to_csv(effect_sizes_path, index=False, sep="\t")

    logging.info("Ran")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build a synthetic phenotype from expression file')

    parser.add_argument("--selected_samples", help="File with people samples ('ID POP GROUP SEX' expected header)", default=None)
    parser.add_argument("--expression", help="File with expression to use", default=None)
    parser.add_argument("--output_prefix", help="Where to save the phenotype", default=None)
    parser.add_argument("--verbosity", help="Logging verbosity", default=10)

    args = parser.parse_args()

    Logging.configureLogging(int(args.verbosity))

    run(args)