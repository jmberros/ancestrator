import pandas as pd

from os.path import join
from pandas import IndexSlice as idx

from components.panel import Panel
from components.sample_group import SampleGroup
from components.source import Source
from analyzers.smart_pca import SmartPCA
from helpers.plink import Plink


class Dataset:
    def __init__(self, source_label, samplegroup_label, panel_label):
        """
        - Gets genotypes from the source passing the panel as argument.
        - Filter the genotypes by the samples in the samplegroup.
        """
        self.source = Source(source_label)
        self.samplegroup = SampleGroup(samplegroup_label, source_label)
        self.set_panel(panel_label)

    def __repr__(self):
        template = '{{Dataset:\n  {}\n  {}\n  {}}}'
        return template.format(str(self.source), str(self.samplegroup),
                               str(self.panel))

    def genotypes(self):
        all_genos = self.source.genotypes(self.panel.label)
        return all_genos.loc[idx[:, :, self.samplegroup.sample_ids], :]

    def pca(self):
        SmartPCA.run(self)
        # TODO finish this ^

    def run_fst(self, level='region'):
        clusters_file = self.samplegroup._write_clusters_files(level)
        bed_filepath = self._make_bed()  # .bed file to compute Fst from
        plink = Plink(bed_filepath)
        out_label = '{}.{}.{}'.format(self.samplegroup.label, self.panel.label,
                                      level)
        fst_file = plink.fst(clusters_file, out=out_label) + '.fst'
        fst_file_fields = ['chr', 'rs_id', 'position', 'NMISS', 'Fst']
        df = pd.read_table(fst_file, index_col='rs_id', skiprows=1,
                           names=fst_file_fields)
        return df

    def set_panel(self, panel_label):
        self.panel = Panel(panel_label)

    def _make_bed(self):
        new_label = '{}.{}'.format(self.samplegroup.label, self.panel.label)
        plink = Plink(join(self.source.panels_dir, self.panel.label))
        plink_out = plink.keep_fam(self.samplegroup.samples_file,
                                   out=new_label)
        return plink_out
