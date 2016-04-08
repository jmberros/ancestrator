import numpy as np
import pandas as pd

from glob import glob
from os.path import join, isfile, basename
from components.source import Source
from helpers.config import Config


class Panel:
    def __init__(self, panel_label):
        """
        - Reads an rs_id list from a <label>.bim file. Will also look for a
        <label>.csv info file about the SNPs in the panel.
        - To get genotypes from a given Source, put a <label>.traw of the panel
        in the Source dir!
        """
        bim_file = join(self.base_dir(), panel_label + '.bim')
        self.snps = self.read_bim(bim_file)

        info_file = join(self.base_dir(), panel_label + '.csv')
        if isfile(info_file):
            self.extra_info = self.read_info(info_file)

        self.rs_ids = self.snps.index.values  # Redundant, but handy shortcut
        self.label = panel_label
        self.name = self._generate_name()
        self.parent = None
        if "_from_" in self.label:
            parent_label = self.label.split("_from_")[1]
            self.parent = Panel(parent_label)

        self.genotypes_cache = {}

    def __repr__(self):
        return '<Panel {}>'.format(self.name)

    def genotypes(self, source_label, dataset=None):
        if self.genotypes_cache.get(source_label) is None:
            data = Source(source_label).genotypes(self.label)
            self.genotypes_cache[source_label] = data

        if dataset is None:
            return self.genotypes_cache[source_label]

        # Assmes a MultiIndex with levels: superpopulation, population, sample
        slicer = pd.IndexSlice[:, :, dataset.sample_ids]
        return self.genotypes_cache.loc[slicer, :]

    #  def allele_freqs(self, level="population"):
        #  genotypes = self.genotypes_1000G()
        #  # allele_freqs = genotypes.groupby(level=level).sum()
        #  total_obs = genotypes.count() * 2
        #  return total_obs

    def _generate_name(self):
        # TODO: think about the Subpanel subclass
        #  if "_from_" in self.label:  # Subpanel
            #  name = self.label.replace("_", " ")
        #  else:

        #  is_AIMs_panel = ("GAL" in self.label)
        #  if is_AIMs_panel:
            #  name = name.replace("SNPs", "AIMs")

        name = "{0} · {1:,} SNPs".format(self.label, len(self.rs_ids))
        return name

    def generate_subset_SNP_list(self, length, sort_key="LSBL(Fst)"):
        """
        This generates a .snps file with one rs_id per line.
        The extraction of SNPs from the original .bed should be run in plink.
        Afterwards, you can just read the new subpanel with Panel(label).
        """
        new_label = '{}_SNPs_from_{}'.format(length, self.label)
        rs_ids_with_genotypes = self.genotypes_1000G().columns
        snps_with_genotype = self.extra_info.loc[rs_ids_with_genotypes]
        snps_with_genotype.sort_values(sort_key, ascending=False, inplace=True)
        subpanel = snps_with_genotype.ix[:length, :]
        filename = join(self.PANEL_INFO_DIR, new_label)
        subpanel.to_csv(filename + ".csv",
                        index_label=self.extra_info.index.name)
        np.savetxt(filename + ".snps", subpanel.index.values, fmt="%s")

        return filename

    @staticmethod
    def base_dir():
        return Config('dirs')['panels']

    @staticmethod
    def read_bim(filename):
        bim_fields = ["chr", "rs_id", "morgans", "position", "A1", "A2"]
        df = pd.read_table(filename, names=bim_fields, index_col="rs_id",
                           usecols=["chr", "rs_id", "position", "A1", "A2"])
        return df

    @staticmethod
    def read_info(filename):
        return pd.read_csv(filename, index_col="rs_id")

    @classmethod
    def available_panels(cls):
        bim_files = glob(join(cls.base_dir(), '*.bim'))
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
