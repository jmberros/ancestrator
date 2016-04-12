#  import matplotlib.pyplot as plt
#  import seaborn as sns

from helpers.config import Config


class BasePlotter:
    """
    Abstract class. Use PCAPlotter and the like, not this one.
    """
    def __init__(self):
        self.colors = Config('colors')
