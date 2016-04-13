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
        self.path_label = join(self.base_dir(), self.label)

        bim_file = self.path_label + '.bim'
        self.snps = self.read_bim(bim_file)

        info_file = self.path_label + '.csv'
        if isfile(info_file):
            self.extra_info = self.read_info(info_file)

        self.rs_ids = self.snps.index.values  # Redundant, but handy shortcut
        self.parent = None
        if "_from_" in self.label:
            parent_label = self.label.split("_from_")[1]
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

    def generate_subpanel(self, length, sort_key="LSBL(Fst)", source_label=None):
        """
        This generates .snps, .csv and .bim files with a subset of markers.
        The extraction of SNPs from the .bed files should be run in plink;
        you can use the .snps file for that purpose.
        Afterwards, you can just read the new subpanel with Panel(label).
        """
        subpanel_label = '{}_SNPs_from_{}'.format(length, self.label)
        filepath = join(self.base_dir(), subpanel_label)

        # .csv file
        subpanel = self.extra_info.sort_values(sort_key, ascending=False)
        subpanel = subpanel.ix[:length, :]
        subpanel.to_csv(filepath + ".csv",
                        index_label=self.extra_info.index.name)

        # .bim file
        bim_df = subpanel.copy().reset_index()
        bim_df['morgans'] = 0
        bim_df = bim_df[self.bim_fields()]
        bim_df.to_csv(filepath + '.bim', index=False)

        # .snps file
        bim_df['rs_id'].to_csv(filepath + '.snps', index=False)

        # .bed file
        if source_label is not None:
            source = Source(source_label)
            bfile_in = join(source.panels_dir, self.label)
            out = join(source.panels_dir, subpanel_label)
            Plink(bfile_in).extract(filepath + '.snps', out=out)

        return filepath

    @staticmethod
    def base_dir():
        return Config('dirs')['panels']

    @staticmethod
    def read_bim(filename):
        df = pd.read_table(filename, names=Panel.bim_fields(), index_col="rs_id",
                           usecols=["chr", "rs_id", "position", "A1", "A2"])
        return df

    @classmethod
    def write_bim(cls, bim_df, label):
        """
        Use this to create a new Panel from a bim-info DataFrame
        """
        bim_df['morgans'] = 0
        bim_df = bim_df.reset_index()
        bim_df = bim_df[cls.bim_fields()]
        filepath = join(cls.base_dir(), label + '.bim')
        bim_df.to_csv(filepath, header=False, index=False, sep='\t')
        print('Written -> ' + filepath)

        filepath = join(cls.base_dir(), label + '.snps')
        bim_df['rs_id'].to_csv(filepath, index=False, header=False)
        print('Written -> ' + filepath)

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
        return [basename(f).replace('.bim', '') for f in bim_files]

    #  @classmethod
    #  def panel_groups(cls):
        #  return {
            #  "panels": cls.all_panels(),
            #  "control_panels": cls.all_control_panels(),
            #  "subpanels": cls.all_subpanels()
        #  }

    #  @classmethod
    #  def all_panels_and_subpanels(cls):
        #  glob_expr = join(cls.THOUSAND_GENOMES_DIR, "*.bim")
        #  bim_files = [basename(path) for path in glob(glob_expr)]
        #  labels = sorted([fn.replace(".bim", "") for fn in bim_files])

        #  gal_panels = [label for label in labels if "GAL" in label]
        #  control_panels = [label for label in labels if "CPx" in label]
        #  subpanels = [label for label in labels if "_from_" in label and
                     #  label not in gal_panels + control_panels]

        #  return [cls(label) for label in gal_panels + control_panels + subpanels]

    #  @classmethod
    #  def all_panels(cls):
        #  return [panel for panel in cls.all_panels_and_subpanels()
                #  if "GAL" in panel.label and "_from_" not in panel.label]

    #  @classmethod
    #  def all_subpanels(cls, label=None):
        #  all_panels = cls.all_panels_and_subpanels()
        #  subpanels = [p for p in all_panels if "_from_" in p.label]
        #  if label is not None:
            #  subpanels = [sp for sp in subpanels if label in sp.label]
        #  subpanels.sort(key=lambda p: len(p.rs_ids), reverse=True)
        #  return subpanels

    #  @classmethod
    #  def all_control_panels(cls):
        #  return [panel for panel in cls.all_panels_and_subpanels()
                #  if "CPx" in panel.label and "_from_" not in panel.label]
