import numpy as np
import seaborn as sns

from plotters.base_plotter import BasePlotter
from helpers.helpers import hide_spines_and_ticks
from helpers.config import Config


class PCAPlotter(BasePlotter):
    def __init__(self, pca, plots_dir):
        """
        Expects a PCA object with 'results' and 'explained_variance'
        """
        self.colors = Config('colors')  # FIXME use super()__init__()!
        self.base_dir = plots_dir  # FIXME should be in super too
        self.plot_settings = Config('plots')['PCA']
        self.components = pca.result
        self.explained_variance = pca.explained_variance

    def draw_ax(self, ax, components_to_plot):
        """
        Draws a scatterplot of the first two columns in eigenvalues
        """
        if len(components_to_plot) != 2:
            error_msg = 'I only know how to plot exactly TWO components. '
            error_msg += 'I received: {}'.format(components_to_plot)
            raise ValueError(error_msg)
        selected_components = self.components[components_to_plot]
        reference_population = self.plot_settings['reference_population']

        ylabel_prefix = ""
        xlabel_prefix = ""

        grouped_results = selected_components.groupby(level='population')
        for population, values in grouped_results:
            kwargs = self._plot_kwargs(population)
            x, y = components_to_plot
            values.plot(kind='scatter', x=x, y=y, ax=ax, label=population,
                        **kwargs)

            # Decide whether to flip the axes to keep the reference population
            # in the upper left quadrant.
            if population == reference_population:
                xaxis_mean = np.mean(ax.get_xlim())
                yaxis_mean = np.mean(ax.get_ylim())

                # The median determines in which quadrant most of the scatter
                # points of this population are located
                reference_in_the_left = np.median(values[x]) < xaxis_mean
                reference_in_the_top = np.median(values[y]) > yaxis_mean

                if not reference_in_the_left:
                    ax.invert_xaxis()
                    xlabel_prefix = "–"
                if not reference_in_the_top:
                    ax.invert_yaxis()
                    ylabel_prefix = "–"

        # Set the axes labels
        xvariance = self.explained_variance.ix[x]['percentage']
        xlabel = "{}{}: {}".format(xlabel_prefix, x, xvariance)
        ax.set_xlabel(xlabel)
        yvariance = self.explained_variance.ix[y]['percentage']
        ylabel = "{}{}: {}".format(ylabel_prefix, y, yvariance)
        ax.set_ylabel(ylabel)

        # Remove non-data ink ;)
        ax.tick_params(axis="x", bottom="off", top="off")
        ax.tick_params(axis="y", left="off", right="off")
        hide_spines_and_ticks(ax, 'all')

        return ax

    def _plot_kwargs(self, population):
        primary = population in self.plot_settings['primary_populations']
        importance = 'primary' if primary else 'secondary'
        kwargs = {
            # Generate a new color for a population if there's no color defined
            # in the settings yml.
            'color': self.colors.get(population, self._new_color()),
            'marker': self.plot_settings[importance]['marker'],
            'lw': self.plot_settings[importance]['linewidth'],
            'alpha': self.plot_settings[importance]['alpha'],
            's': self.plot_settings[importance]['markersize'],
            'zorder': self.plot_settings[importance]['zorder'],
        }
        return kwargs

    def _new_color(self):
        if not hasattr(self, '_more_colors'):
            palette_name = self.colors['QualitativePalette']
            populations = self.components.index.get_level_values('population')
            number_of_populations = len(populations.unique())
            self._more_colors = sns.color_palette(palette_name,
                                                  number_of_populations)
        return self._more_colors.pop(0)
