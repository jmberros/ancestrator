import numpy as np

from plotters.base_plotter import BasePlotter
from helpers.helpers import hide_spines_and_ticks
from helpers.config import Config


class PCAPlotter(BasePlotter):
    """
    Expects a PCA object with 'results' and 'explained_variance' attributes.
    """

    def __init__(self, pca):
        self.colors = Config('colors')  # FIXME use super()__init__()!
        self.base_dir = Config('dirs')['plots']
        self.plot_settings = Config('plots')['PCA']
        self.explained_variance = pca.explained_variance

    def draw_ax(self, ax, eigenvalues):
        """
        Draws a scatterplot of the first two columns in eigenvalues
        """
        grouped_results = eigenvalues.groupby(level='population')
        components = eigenvalues.columns[:2]
        reference_population = self.plot_settings['reference_population']

        ylabel_prefix = ""
        xlabel_prefix = ""

        for population, values in grouped_results:
            kwargs = self._plot_kwargs(population)
            x, y = components
            values.plot(kind='scatter', x=x, y=y, ax=ax, **kwargs)

            # Keep the reference population in the upper left
            if population == reference_population:
                xaxis_mean = np.mean(ax.get_xlim())
                yaxis_mean = np.mean(ax.get_ylim())

                # The median determines in which quadrant most of the scatter
                # points of this population is located
                reference_in_the_left = np.median(values[x]) < xaxis_mean
                reference_in_the_top = np.median(values[y]) > yaxis_mean

                if not reference_in_the_left:
                    ax.invert_xaxis()
                    xlabel_prefix = "–"
                if not reference_in_the_top:
                    ax.invert_yaxis()
                    ylabel_prefix = "–"

        xvariance = self.explained_variance.ix[x]['percentage']
        xlabel = "{}{}: {}".format(xlabel_prefix, x, xvariance)
        ax.set_xlabel(xlabel)

        yvariance = self.explained_variance.ix[y]['percentage']
        ylabel = "{}{}: {}".format(ylabel_prefix, y, yvariance)
        ax.set_ylabel(ylabel)

        ax.tick_params(axis="x", bottom="off", top="off")
        ax.tick_params(axis="y", left="off", right="off")
        hide_spines_and_ticks(ax, 'all')

    def _plot_kwargs(self, population):
        kwargs = {
            'color': self.colors[population],
            'marker': self.plot_settings['primary_marker'],
            'lw': self.plot_settings['linewidth'],
            'alpha': self.plot_settings['alpha'],
            's': self.plot_settings['markersize'],
        }
        primary_population = population in self.plot_settings['primary_populations']
        if not primary_population:
            kwargs['marker'] = self.plot_settings['secondary_marker']
        return kwargs
