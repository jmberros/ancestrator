import seaborn as sns
from helpers.config import Config
from helpers.helpers import hide_spines_and_ticks


class AdmixturePlotter:
    def __init__(self, admixture, plots_dir=None):
        """
        Expects an admixture object that responds to #result
        """
        self.admixture = admixture
        self.colors = Config('colors')  # FIXME use super()__init__()!
        self.base_dir = plots_dir  # FIXME should be in super too
        if plots_dir is None:
            self.base_dir = self.admixture.dataset.source.plots_dir
        self.plot_settings = Config('plots')['admixture']

    def draw_ax(self, ax, K_to_plot):
        ancestries = self.admixture.result[K_to_plot]
        ancestries = self._reorder_samples_and_parse(ancestries)

        plot_title = self._make_title(K_to_plot)
        colors = self._generate_palette(ancestries.columns)
        ancestries.plot(ax=ax, kind="bar", stacked=True, linewidth=0, width=1,
                        color=colors)

        self._plot_aesthetics(ax, plot_title, ancestries)
        ax.legend_.set_visible(False)
        return ax

    def _reorder_samples_and_parse(self, ancestries):
        ancestries = ancestries.reset_index()
        # Use the same sample order through plots once defined.
        if not hasattr(self, 'plot_samples_order'):
            if 'AMR' in ancestries.columns:
                ancestries = ancestries.sort_values(['population', 'AMR'],
                                                    ascending=False)
            self.plot_samples_order = ancestries['sample']
        ancestries = ancestries.set_index('sample')
        ancestries = ancestries.loc[self.plot_samples_order]
        ancestries = ancestries.reset_index()
        ancestries = ancestries.drop(['region', 'family', 'sample'], axis=1)
        ancestries = ancestries.set_index("population")
        population_order = self.plot_settings['population_order']
        ancestries = ancestries.loc[population_order].dropna()
        return ancestries

    def _generate_palette(self, ancestry_labels):
        defined_colors = Config('colors')
        palette = []
        for ancestry in ancestry_labels:
            if ancestry in defined_colors:
                palette.append(defined_colors[ancestry])
        remaining = len(ancestry_labels) - len(palette)
        quali_palette = Config('colors')['QualitativePalette']
        palette += sns.color_palette(quali_palette, remaining)
        return palette

    def _plot_aesthetics(self, ax, plot_title, ancestries):
        ax.set_title(plot_title, y=1.08)

        # Place the population labels in the middle of the range of its samples
        population_order = ancestries.index.unique()
        N_by_population = ancestries.index.value_counts()[population_order]
        xlabels = N_by_population.cumsum() - N_by_population / 2
        ax.set_xticklabels(xlabels.index)
        ax.set_xticks(xlabels.values)

        ax.set_xlabel("")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.set_ylabel("Ancestría")
        ax.set_ylim([0, 1])
        ax.set_yticks([0, 1])
        #  ax.set_yticklabels([0, 1])
        #  hide_spines_and_ticks(ax, spines='all')

    def _new_color(self):
        if not hasattr(self, '_more_colors'):
            palette_name = self.colors['QualitativePalette']
            regions = self.admixture.result.index.get_level_values('region')
            number_of_regions = len(regions.unique())
            self._more_colors = sns.color_palette(palette_name,
                                                  number_of_regions)
        return self._more_colors.pop(0)

    def _make_title(self, K):
        dataset = self.admixture.dataset
        return "{} - {} (K = {})".format(dataset.label, dataset.panel.name, K)
