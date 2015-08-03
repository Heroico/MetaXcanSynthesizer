library(dplyr)

print("reading pheno")
fam = read.table("intermediate/GWAS/GWAS.fam")
fam_colnames <- c("FAMILY","INDIVIDUAL", "PATERNAL", "MATERNAL", "SEX","PHENOTYPE")
colnames(fam) <- fam_colnames

print("reading filter")
filter = read.table("intermediate/GWAS/GWAS.filter")
colnames(filter) <- c("FAMILY", "INDIVIDUAL", "FILTER")

print("reading predicted")
predicted = read.delim("data/output-DGN-WB.txt")
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
write.table(OUT,"intermediate/predixcan_s_wb.txt",col.names=T,row.names=F,quote=F)