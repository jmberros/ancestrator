import pandas as pd

from pandas import IndexSlice as idx
from glob import glob
from os.path import join, basename

from components.source import Source
from components.panel import Panel
from helpers.config import Config
from helpers.plink import Plink


class Dataset:
    def __init__(self, source_label, dataset_label, panel_label=None):
        """
        Looks for samples in <source_dir>/datasets/<dataset>.samples
        """
        self.label = dataset_label
        self.name = Config('names')[self.label]
        self.source = Source(source_label)
        self.base_dir = join(self.source.base_dir, 'datasets')
        self.samples = self._read_samples()
        self.genotypes_cache = {}
        self.panel_label = None
        if panel_label:
            self.set_panel(panel_label)

        # handy shortcuts
        self.sample_ids = self.samples.index.values
        self.populations = self.samples['population'].unique()

    def __repr__(self):
        template = '<[{}][{}] Dataset {}, {} populations, {} samples>'
        panel_label = 'No Panel'
        if hasattr(self, 'panel'):
            panel_label = self.panel.label
        return template.format(self.source.label, panel_label, self.label,
                               len(self.populations), len(self.samples))

    def genotypes(self, panel_label):
        if panel_label not in self.genotypes_cache:
            all_genos = Panel(panel_label).genotypes(self.source.label)
            genos = all_genos.loc[idx[:, :, self.sample_ids], :]
            self.genotypes_cache[panel_label] = genos

        return self.genotypes_cache[panel_label]

    def pca(self):
        # Assumes a panel defined
        # TODO:
        # if not isfile()
        # Check if a .ped file exists, otherwise create it
        # -- creation should be done via a Plink class
        # call a PCA class that uses eigensoft with thhe new .ped
        # try plotting with their service? or matplotlib, w/e
        pass

    def run_fst(self, level='region'):
        clusters_file = self._write_clusters_files(level)
        bed_filepath = self._make_bed()  # .bed file to compute Fst from
        plink = Plink(bed_filepath)
        out_label = '{}.{}.{}'.format(self.label, self.panel.label, level)
        fst_file = plink.fst(clusters_file, out=out_label) + '.fst'
        fst_file_fields = ['chr', 'rs_id', 'position', 'NMISS', 'Fst']
        df = pd.read_table(fst_file, index_col='rs_id', skiprows=1,
                           names=fst_file_fields)
        return df

    def _make_bed(self):
        new_label = '{}.{}'.format(self.label, self.panel.label)
        plink = Plink(join(self.source.panels_dir, self.panel.label))
        plink_out = plink.keep_fam(self.samples_file, out=new_label)
        return plink_out

    def set_panel(self, panel_label):
        self.panel = Panel(panel_label)

    def _read_samples(self):
        self.samples_file = join(self.base_dir, self.label + '.samples')
        with open(self.samples_file, 'r') as f:
            samples = [line.strip() for line in f.readlines()]
        return self.source.samples.ix[samples]

    def _write_clusters_files(self, level='population'):
        """
        Write a file with three columns: FID, IID, and cluster (pop or region).
        FID and IID are usually the same, the clusters field is what matters
        for later use with plink --fst.
        """
        # Family ID (FID), Within-family ID (IID), Cluster ID
        clusters = self.samples.reset_index()
        clusters["FID"] = clusters["sample"]
        clusters = clusters[["FID", "sample", level]]
        filename = "{}.{}.clusters".format(self.label, level)
        filepath = join(self.base_dir, filename)
        clusters.to_csv(filepath, sep="\t", header=None, index=False)

        return filepath

    @staticmethod
    def available_datasets(source_label):
        datasets_dir = join(Source(source_label).base_dir, 'datasets')
        samples_files = glob(join(datasets_dir, '*.samples'))
        labels = [basename(f).replace('.samples', '') for f in samples_files]
        return sorted(labels)
