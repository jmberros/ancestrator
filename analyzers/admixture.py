import subprocess
import pandas as pd
import matplotlib.pyplot as plt

from os import chdir, getcwd
from os.path import expanduser, isfile
from plotters.admixture_plotter import AdmixturePlotter
from helpers.config import Config


class Admixture:
    _EXECUTABLE = expanduser(Config('executables')['admixture'])

    def __init__(self, dataset):
        self.dataset = dataset
        self.Pfiles = {}
        self.Qfiles = {}
        self.logfiles = {}

    def run(self, Ks, cores, infer_components=False):
        if not hasattr(Ks, '__iter__'):
            Ks = [Ks]

        self.result = {}
        for K in Ks:
            self.logfiles[K] = self._output_filepath(K, 'log')
            self.Pfiles[K] = self._output_filepath(K, 'P')
            self.Qfiles[K] = self._output_filepath(K, 'Q')
            if not isfile(self.Pfiles[K]) or not isfile(self.Qfiles[K]):
                self._call_admixture(K, cores)
            self.result[K] = self._read_ancestry_file(K)

            regions = self.result[K].index.get_level_values('region').unique()
            if infer_components and len(regions) >= 3:
                self._assign_regions_to_clusters(self.result[K])

    def plot(self, K_to_plot, ax=None):
        self.plotter = AdmixturePlotter(self, self.dataset.source.plots_dir)

        if ax is None:
            _, ax = plt.subplots(figsize=(15, 5))
        self.plotter.draw_ax(ax, K_to_plot)
        return ax

    def savefig(self, filename=None):
        if filename is None:
            filename = '{}.{}'.format(self.dataset.label, type(self).__name__)
        self.plotter.savefig(filename)

    def _assign_regions_to_clusters(self, ancestries_df):
        means = ancestries_df.groupby(level='region').mean()
        max_region_per_component = means.idxmax(axis=0).to_dict()
        max_component_per_region = means.idxmax(axis=1).to_dict()

        # I accept an association of region-cluster if two conditions are met:
        # - The component must have the max avg. ancestry value for that
        #   region.
        # - For the region, that component must have the max avg. ancestry
        #   value.
        # I know it's kind of a tongue twister, but check the result DataFrames
        # to get what I'm saying. Max value column-wise must coincide with max
        # value row-wise, otherwise it would be a dubious guess.
        guesses = {}
        for region, guessed_component in max_component_per_region.items():
            if region == max_region_per_component[guessed_component]:
                guesses[guessed_component] = region

        ancestries_df.rename(columns=guesses, inplace=True)

    #  def _infer_ancestral_components_from_reference_pop(self, ancestries_df):
        #  # Last resort after #infer_ancestral_components_from_samples_region
        #  # With Peruvians' mean as reference, I can guess their known 3
        #  # ancestral components.
        #  reference_population = "PEL"
        #  reference_ancestries = ["AMR", "EUR", "AFR"]

        #  components_order = ancestries_df.groupby("population").mean()
        #  components_order = components_order.loc[reference_population]
        #  components_order = components_order.sort_values(ascending=False).index

        #  guess = {}
        #  for component, ancestry in zip(components_order, reference_ancestries):
            #  if type(component) != int:
                #  continue  # Don't re-guess already known ancestries

            #  ancestries_already_inferred = [col for col in ancestries_df.columns
                                           #  if type(col) != int]

            #  if ancestry not in ancestries_already_inferred:
                #  guess[component] = ancestry

        #  if len(guess) > 0:
            #  ancestries_df.rename(columns=guess, inplace=True)

    def _read_ancestry_file(self, K):
        result = pd.read_table(self.Qfiles[K], sep='\s+', header=None)
        result.columns = range(1, K+1)
        result.index = self.dataset.samplegroup.samples.index
        result = result.join(self.dataset.samplegroup.samples)
        multi_index = ['region', 'population', 'family', 'sample']
        result = result.reset_index().set_index(multi_index)
        return result

    def _call_admixture(self, K, cores):
        command = '{} --cv {}.bed {} -j{}'
        command = command.format(self._EXECUTABLE, self.dataset.bedfile, K,
                                 cores)
        working_dir = getcwd()
        chdir(self.dataset.source.datasets_dir)
        with open(self.logfiles[K], 'w+') as logfile:
            subprocess.call(command.split(' '), stdout=logfile)
        chdir(working_dir)

    def _output_filepath(self, K, output_label):
        return self.dataset.bedfile + '.{}.{}'.format(K, output_label)
