from plotters.base_plotter import BasePlotter
from helpers.config import Config


class PCAPlotter(BasePlotter):
    """
    Expects a PCA object with 'results' and 'explained_variance' attributes.
    """

    def __init__(self, pca):
        self.base_dir = Config('dirs')['plots']
        self.plot_settings = Config('plots')['PCA']
        self.eigenvalues = pca.result
        self.explained_variance = pca.explained_variance

    #  def plot(self, component_pairs=[('PC1', 'PC2')], reference_population):

    def draw_ax(self, ax, eigenvalues):
        #  grouped_results = eigenvalues.groupby(level='population')
        #  for population, eigenvalues in grouped_results:
            #  primary_population = population in self.primary_populations
            #  marker = self.plot_settings['marker']
        pass
