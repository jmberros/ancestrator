from plotters.pca_plotter import PCAPlotter


class BasePCA:
    """
    Don't instantiate this class; use instead SmartPCA or SklearnPCA.
    """
    def plot(self, ax, components_to_plot=['PC1', 'PC2']):
        selected_components = self.result[components_to_plot]
        PCAPlotter(self).draw_ax(ax, selected_components)

        return ax
