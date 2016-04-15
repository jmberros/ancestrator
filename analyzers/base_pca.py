from plotters.pca_plotter import PCAPlotter


class BasePCA:
    """
    Don't instantiate this class; use instead SmartPCA or SklearnPCA.
    """
    def plot(self, ax, components_to_plot=['PC1', 'PC2']):
        self.plotter = PCAPlotter(self, self.dataset.source.plots_dir)
        self.plotter.draw_ax(ax, components_to_plot)
        return ax

    def savefig(self, filename=None):
        if filename is None:
            filename = '{}.{}'.format(self.dataset.label, type(self).__name__)
        self.plotter.savefig(filename)

    def _write_result_csvs(self):
        self.result.to_csv(self._output_filepath('eigenvals') + '.csv')
        self.explained_variance.to_csv(self._output_filepath('eigenvecs') + '.csv')

    def _output_filepath(self, ext):
        return self.dataset.bedfile + '.' + ext
