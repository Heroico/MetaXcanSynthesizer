#!/usr/bin/bash

# run from the root folder

./PhenotypeFromExpression2.py \
--selected_samples data/TGF_EUR/1000GP_Phase3.sample \
--expressions data/expression/TW_Liver_0.5.expr.txt data/expression/TW_Whole_Blood_0.5.expr.txt \
--genes ENSG00000001460.13 ENSG00000001561.6 \
--output_prefix intermediate/phenotype/linear_pheno_mix
