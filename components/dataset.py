from pandas import IndexSlice as idx
from os.path import isfile

from components.panel import Panel
from components.sample_group import SampleGroup
from components.source import Source
from analyzers.smart_pca import SmartPCA
from analyzers.sklearn_pca import SklearnPCA
from analyzers.fst import Fst
from analyzers.admixture import Admixture
from helpers.plink import Plink


class Dataset:
    def __init__(self, source_label, samplegroup_label, panel_label):
        """
        - Gets genotypes from the source passing the panel as argument.
        - Filter the genotypes by the samples in the samplegroup.
        """
        self.source = Source(source_label)
        self.samplegroup = SampleGroup(source_label, samplegroup_label)

        self.panel = Panel(panel_label)
        self.panel_bedfile = self.source.bedfile_path('ALL.'+self.panel.label)

        self.label = '{}.{}'.format(self.samplegroup.label, self.panel.label)
        self.full_label = '{}.{}'.format(self.source.label, self.label)
        self.bedfile = self.source.bedfile_path(self.label)
        self.bimfile = self.bedfile + '.bim'
        self.pedfile = self.bedfile + '.ped'
        self._genotypes_mem = None

    def __repr__(self):
        template = '{{Dataset:\n  {}\n  {}\n  {}}}'
        return template.format(str(self.source), str(self.samplegroup),
                               str(self.panel))

    def genotypes(self):
        if self._genotypes_mem is None:
            all_genos = self.source.genotypes('ALL.'+self.panel.label)
            genos = all_genos.loc[idx[:, :, :, self.samplegroup.sample_ids], :]
            self._genotypes_mem = genos

        return self._genotypes_mem

    def pca(self, implementation='smartpca', overwrite=False,
            normalize=True, args={}):
        """
        Computes a Principal Components Analysis with the genotypes in this
        dataset. Returns a PCA object that responds to #results and #plot().
        """
        if implementation == 'smartpca':
            self.make_ped()
            pca = SmartPCA(dataset=self)
            pca.run(overwrite=overwrite, args=args)
            return pca
        elif implementation == 'sklearn':
            pca = SklearnPCA(self)
            pca.run(normalize=normalize)
            return pca

    def fst(self, level='region'):
        """
        Calls plink to compute the Fst for each marker in the dataset.
        Returns a DataFrame with said info.
        """
        self.samplegroup._write_clusters_files(level)
        self.make_bed()
        return Fst.run(self, level)

    def admixture(self, Ks, cores=4, infer_components=True, overwrite=False):
        """
        Run admixture for a list of K values. You may specify the number of
        CPU cores for admixture to use. Set 'overwrite=True' to make it ignore
        existing results files if it finds them; otherwise, it will read them
        instead of rerunning the analysis, to save time.
        Returns an admixture object that responds to #results and #plot().
        """
        self.make_bed()
        admixture = Admixture(self)
        admixture.run(Ks, cores, infer_components, overwrite)
        return admixture

    def extract_subdataset_from_panel(self, panel):
        new_label = '{}.{}'.format(self.samplegroup.label, panel.label)
        filename = Plink(self.bedfile).extract(panel.snps_file, out=new_label)
        print('Written -> ' + filename)
        msg = "You can now call Dataset('{}', '{}', '{}')"
        print(msg.format(self.source.label, self.samplegroup.label,
                         panel.label))

    def make_bed(self):
        bed_exists = isfile(self.bedfile + '.bed')
        bim_exists = isfile(self.bedfile + '.bim')
        fam_exists = isfile(self.bedfile + '.fam')
        if bed_exists and bim_exists and fam_exists:
            return self.bedfile
        plink = Plink(self.panel_bedfile)
        return plink.keep_fam(self.samplegroup.famfile, out=self.bedfile)

    def make_ped(self):
        if isfile(self.pedfile):
            return self.pedfile
        self.make_bed()
        return Plink(self.bedfile).ped()
