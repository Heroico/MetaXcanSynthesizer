#! /usr/bin/env python

import logging
import pandas
import re
import numpy

import PhenotypeFromExpression
from utils import Logging
from utils import Utilities

def _sanity_check(expressions, samples):
    shapes = sorted({e.shape[0] for e in expressions.values()})
    assert(len(shapes) == 1)
    assert(samples.shape[0] == shapes[0])

_regexp = re.compile(".*TW_(.*)_0.5.expr.txt$")
def _tissue_name(expression):
    return _regexp.match(expression).group(1)

def _effect_sizes(expressions, genes):
    tissues = expressions.keys()
    e = [(x,y) for x in tissues for y in genes]
    e = zip(*e)
    columns = ["tissue", "gene"]
    e = {columns[i]:e[i] for i in xrange(0,len(columns))}
    e = pandas.DataFrame(data=e)
    e["effect_size"] = numpy.random.uniform(0, 2, size=e.shape[0]) * numpy.random.choice([1.0, -1.0], size=e.shape[0])
    return e

def _pheno(expressions, effect_sizes):
    p = None
    for  e in effect_sizes.itertuples():
        t = expressions[e.tissue]
        g = t[e.gene] * e.effect_size
        p = g if p is None else p+g
    e = numpy.random.normal(size=len(p))
    p = p+e
    return p,e

def _build_pheno(samples, expressions, effect_sizes):
    pheno = pandas.DataFrame(samples)
    _p, _noise = _pheno(expressions, effect_sizes)
    pheno["PHENO"] = _p
    pheno["NOISE"] = _noise
    return  pheno

def load_expressions(expressions):
    expressions = {_tissue_name(e):PhenotypeFromExpression.load_expression(e) for e in expressions}
    return expressions

def build_pheno(samples, expressions, selected_genes):
    effect_sizes = _effect_sizes(expressions, selected_genes)
    pheno = _build_pheno(samples, expressions, effect_sizes)
    return pheno, effect_sizes


def run(args):
    logging.info("Reading samples")
    samples = pandas.read_table(args.selected_samples, sep="\s+")

    logging.info("Reading expression")
    expressions = load_expressions(args.expressions)
    _sanity_check(expressions, samples)

    # Introduce a seed, but have it be constant for reproducibility. We are not that interested in "truer" randomness at this time.
    numpy.random.seed(1000)

    pheno, effect_sizes = build_pheno(samples, expressions, args.genes)

    Utilities.ensure_requisite_folders(args.output_prefix)
    pheno.to_csv(args.output_prefix + ".full_pheno.txt", index=False, sep="\t")

    effect_sizes_path = args.output_prefix + ".effect_sizes.txt"
    effect_sizes.to_csv(effect_sizes_path, index=False, sep="\t")

    logging.info("Ran")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build a synthetic phenotype from expression file')

    parser.add_argument("--selected_samples", help="File with people samples ('ID POP GROUP SEX' expected header)", default=None)
    parser.add_argument("--expressions", help="File with expression to use", default=[], type=str, nargs="+")
    parser.add_argument("--genes", help="File with expression to use", default=[], type=str, nargs="+")
    parser.add_argument("--output_prefix", help="Where to save the phenotype", default=None)
    parser.add_argument("--verbosity", help="Logging verbosity", default=10)

    args = parser.parse_args()

    Logging.configureLogging(int(args.verbosity))

    run(args)