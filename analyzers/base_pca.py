from plotters.pca_plotter import PCAPlotter


class BasePCA:
    """
    Don't instantiate this class; use instead SmartPCA or SklearnPCA.
    """
    def plot(self, ax, components_to_plot):
        plotter = PCAPlotter(self)
        eigenvalues = self.result[components_to_plot]
        plotter.draw_ax(ax, eigenvalues)
