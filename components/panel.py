import pandas as pd

from glob import glob
from os.path import join, isfile, basename
from components.source import Source
from helpers.config import Config
from helpers.plink import Plink


class Panel:
    def __init__(self, panel_label):
        """
        - Reads an rs_id list from a <label>.bim file. Will also look for a
        <label>.csv info file about the SNPs in the panel.
        """
        self.label = panel_label
        self.info_path = join(self.base_dir(), self.label)

        bim_file = self.info_path + '.bim'
        self.snps = self.read_bim(bim_file)
        self.snps_file = self.info_path + '.snps'

        info_file = self.info_path + '.csv'
        if isfile(info_file):
            self.extra_info = self.read_info(info_file)

        self.rs_ids = self.snps.index.values  # Redundant, but handy shortcut
        self.parent = None
        if "SubPanel" in self.label:
            parent_label = self.label.split("_SubPanel_")[0]
            self.parent = Panel(parent_label)
        self.name = self._generate_name()

    def __repr__(self):
        return '<Panel {}>'.format(self.name)

    def __len__(self):
        return len(self.snps)

    #  def allele_freqs(self, level="population"):
        #  genotypes = self.genotypes_1000G()
        #  # allele_freqs = genotypes.groupby(level=level).sum()
        #  total_obs = genotypes.count() * 2
        #  return total_obs

    def _generate_name(self):
        name = '{0} · {1:,} SNPs'.format(self.label, len(self.rs_ids))
        if self.parent:
            name = '{} · SubPanel_{}'.format(self.parent.label, len(self.rs_ids))
        return name

    #  def generate_subpanel(self, length, sort_key="LSBL(Fst)", source_label=None):
        #  """
        #  This generates .snps, .csv and .bim files with a subset of markers.
        #  The extraction of SNPs from the .bed files should be run in plink;
        #  you can use the .snps file for that purpose.
        #  Afterwards, you can just read the new subpanel with Panel(label).
        #  """
        #  subpanel_label = '{}_SNPs_from_{}'.format(length, self.label)
        #  filepath = join(self.base_dir(), subpanel_label)

        #  # .csv file
        #  subpanel = self.extra_info.sort_values(sort_key, ascending=False)
        #  subpanel = subpanel.ix[:length, :]
        #  subpanel.to_csv(filepath + ".csv",
                        #  index_label=self.extra_info.index.name)

        #  # .bim file
        #  bim_df = subpanel.copy().reset_index()
        #  bim_df['morgans'] = 0
        #  bim_df = bim_df[self.bim_fields()]
        #  bim_df.to_csv(filepath + '.bim', index=False)

        #  # .snps file
        #  bim_df['rs_id'].to_csv(filepath + '.snps', index=False)

        #  # .bed file
        #  if source_label is not None:
            #  source = Source(source_label)
            #  bfile_in = join(source.panels_dir, self.label)
            #  out = join(source.panels_dir, subpanel_label)
            #  Plink(bfile_in).extract(filepath + '.snps', out=out)

        #  return filepath

    @staticmethod
    def base_dir():
        return Config('dirs')['panels']

    @staticmethod
    def read_bim(filename):
        df = pd.read_table(filename, names=Panel.bim_fields(), index_col="rs_id",
                           usecols=["chr", "rs_id", "position", "A1", "A2"])
        df.index.name = 'rs_id'
        return df

    def create_subpanel(self, snps_list, source_label):
        """
        Create a subpanel with the SNPs provided (must be a subset of my SNPs).
        """
        snps_subset_df = self.snps.loc[snps_list].dropna()
        if len(snps_subset_df) != len(snps_list):
            raise Exception("I don't have all of those SNPs.")
        snps_subset_df.index.name = 'rs_id'  # ^ .loc removes the index name :/
        new_label = '{}_SubPanel_{}'.format(self.label, len(snps_subset_df))
        snps_filepath = self.write_bim(snps_subset_df, new_label)

        # Create a base bedfile with genotypes for all the samples
        out_label = 'ALL.{}'.format(new_label)
        bedfile_path = self.bedfile_path(source_label)
        Plink(bedfile_path).extract(snps_filepath, out=out_label)
        msg = "You can now call Dataset('{}', '{}', '{}') with any SampleGroup"
        print(msg.format(source_label, 'ALL', new_label))

        return Panel(new_label)

    def bedfile_path(self, source_label):
        return join(Source(source_label).datasets_dir, 'ALL.' + self.label)

    @classmethod
    def write_bim(cls, snps_df, label):
        """
        Create a new Panel from a snps DataFrame.
        """
        snps_df['morgans'] = 0
        snps_df = snps_df.reset_index()
        snps_df = snps_df[cls.bim_fields()]
        bim_filepath = join(cls.base_dir(), label + '.bim')
        snps_df.to_csv(bim_filepath, header=False, index=False, sep='\t')
        print('Written -> ' + bim_filepath)

        snps_filepath = join(cls.base_dir(), label + '.snps')
        snps_df['rs_id'].to_csv(snps_filepath, index=False, header=False)
        print('Written -> ' + snps_filepath)
        print("You can now call Panel('{}')".format(label))

        return snps_filepath

    @staticmethod
    def bim_fields():
        return ["chr", "rs_id", "morgans", "position", "A1", "A2"]

    @staticmethod
    def read_info(filename):
        return pd.read_csv(filename, index_col="rs_id")

    @classmethod
    def available_panels(cls, source_label=None):
        bim_files = glob(join(cls.base_dir(), '*.bim'))
        if source_label is not None:
            glob_expr = join(Source(source_label).panels_dir, '*.bim')
            bim_files = glob(glob_expr)
        panel_labels = [basename(f).replace('.bim', '') for f in bim_files]
        return sorted(panel_labels)
