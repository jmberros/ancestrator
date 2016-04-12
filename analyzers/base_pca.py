from plotters.pca_plotter import PCAPlotter


class BasePCA:
    """
    Don't instantiate this class; use instead SmartPCA or SklearnPCA.
    """
    def plot(self, component_pairs_to_plot=[('PC1', 'PC2')]):
       plotter = PCAPlotter(self)
       # TODO keep working on this
