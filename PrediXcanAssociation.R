library(dplyr)
library(argparse)

parser <- ArgumentParser(description='Generate PrediXcan association')
parser$add_argument('--predicted',
                    help='predicted gene expression',
                    default='data/output-DGN-WB.txt')

parser$add_argument('--pheno',
                    help='Path of pheno file, without extension',
                    default='intermediate/GWAS/GWAS.fam')

parser$add_argument('--filter',
                    help='fam file filter',
                    default='intermediate/GWAS/GWAS.filter')

parser$add_argument('--output',
                    help='output',
                    default='intermediate/predixcan_s_wb.txt')

arguments <- parser$parse_args(commandArgs(TRUE))

print("reading pheno")
fam = read.table(arguments$pheno)
fam_colnames <- c("FAMILY","INDIVIDUAL", "PATERNAL", "MATERNAL", "SEX","PHENOTYPE")
colnames(fam) <- fam_colnames

print("reading filter")
filter = read.table(arguments$filter)
colnames(filter) <- c("FAMILY", "INDIVIDUAL", "FILTER")

print("reading predicted")
predicted = read.delim(arguments$predicted)
genes =  colnames(predicted)

print("Preparing data")
merged_people = merge(fam, filter)
merged <- cbind(predicted, merged_people)
filtered <- merged %>% filter(FILTER==1)

pheno <- filtered$PHENO
filtered <- subset(filtered, select = genes)

print("running correlation")
OUT<-NULL
for (gene in genes) {
    data <- filtered[[gene]]
    results = coef(summary(lm(pheno ~ data)))[c(2,6,8,4)]
    line = c(gene,results)
    OUT<-rbind(OUT,line)
}
colnames(OUT)<-c("gene","beta","z-stat","p-val", "se(beta)")
write.table(OUT,arguments$output,col.names=T,row.names=F,quote=F)