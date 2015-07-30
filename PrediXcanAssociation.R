
print("reading pheno")
fam = read.table("intermediate/GWAS/GWAS.fam")
pheno = fam$V6
print("reading predicted")
predicted = read.delim("data/output-DGN-WB.txt")
genes =  colnames(predicted)

print("running correlation")
OUT<-NULL
for (gene in genes) {
    data <- predicted[[gene]]
    results = coef(summary(lm(pheno ~ data)))[c(2,6,8,4)]
    line = tmp<-c(gene,results)
    OUT<-rbind(OUT,line)
}
colnames(OUT)<-c("gene","beta","z-stat","p-val", "se(beta)")
write.table(OUT,"intermediate/predixcan_s_wb.txt",col.names=T,row.names=F,quote=F)