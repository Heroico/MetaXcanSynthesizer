__author__ = 'heroico'

import sqlite3

class WeightDBEntry:
    def __init__(self, rsid=None, gene=None, weight=None, ref_allele = None, eff_allele=None, pval=None, N=None, cis=None):
        self.rsid = rsid
        self.gene = gene
        self.weight = weight
        self.ref_allele = ref_allele
        self.eff_allele = eff_allele
        self.pval = pval
        self.N = N
        self.cis = cis

class WDBQF(object):
    "Weight DB Query Format"
    RSID=0
    GENE=1
    WEIGHT=2
    REF_ALLELE=3
    EFF_ALLELE=4
    PVAL=5
    N=6
    CIS=7

class WeightDB(object):
    def __init__(self,file_name):
        self.connection = None
        self.cursor = None
        self.file_name = file_name

    def __del__(self):
        self.closeDB()

    def openDBIfNecessary(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.file_name)
            self.cursor = self.connection.cursor()

    def closeDB(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def weightEntriesFromResults(self, results, result_callback=None):
        weights = []
        for result in results:
            weight = WeightDBEntry(result[WDBQF.RSID],
                                   result[WDBQF.GENE],
                                   result[WDBQF.WEIGHT],
                                   result[WDBQF.REF_ALLELE],
                                   result[WDBQF.EFF_ALLELE],
                                   result[WDBQF.PVAL],
                                   result[WDBQF.N],
                                   result[WDBQF.CIS])
            weights.append(weight)
            if result_callback:
                result_callback(weight)
        return weight

    def loadFromDBWithGeneName(self, gene_name, callback=None):
        self.openDBIfNecessary()
        results = self.cursor.execute("SELECT rsid, gene, weight, ref_allele, eff_allele, pval, N, cis FROM weights WHERE gene = ?;",(gene_name,))
        weights = self.weightEntriesFromResults(results, callback)
        return  weights

    def loadFromDB(self, callback=None):
        self.openDBIfNecessary()
        results = self.cursor.execute("SELECT rsid, gene, weight, ref_allele, eff_allele, pval, N, cis FROM weights;")
        weights = self.weightEntriesFromResults(results, callback)
        return  weights

    def loadGeneNamesFromDB(self):
        self.openDBIfNecessary()
        names = []

        results = self.cursor.execute("SELECT DISTINCT gene FROM weights;")

        for result in results:
            name = result[0]
            names.append(name)

        return names

class WeightDBEntryLogic(object):
    def __init__(self, db_file_name):
        self.weights_by_gene_name = {}
        self.genes_for_an_rsid = {}
        self._loadData(db_file_name)

    def anEntryWithRSID(self, rsid):
        entry = None
        if not rsid in self.genes_for_an_rsid:
            return entry

        genes = self.genes_for_an_rsid[rsid]
        gene = genes[0]
        weights = self.weights_by_gene_name[gene]
        entry = weights[rsid]
        return  entry

    def _loadData(self, db_file_name):
        weights_db = WeightDB(db_file_name)

        class ByNameCallback(object):
            """Helper class to group weights by gene name"""
            def __init__(self, weights_by_gene, genes_for_an_rsid):
                self.weights_by_gene = weights_by_gene
                self.genes_for_an_rsid = genes_for_an_rsid

            def __call__(self,weight):
                if weight.gene in self.weights_by_gene:
                    weights = self.weights_by_gene[weight.gene]
                else:
                    weights = {}
                    self.weights_by_gene[weight.gene] = weights
                weights[weight.rsid]= weight

                if not weight.rsid in self.genes_for_an_rsid:
                    self.genes_for_an_rsid[weight.rsid] = []
                genes = self.genes_for_an_rsid[weight.rsid]

                if not weight.gene in genes:
                    genes.append(weight.gene)

        callback = ByNameCallback(self.weights_by_gene_name, self.genes_for_an_rsid)
        weights_db.loadFromDB(callback)

