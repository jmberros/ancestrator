from os.path import join
from components.source import Source
from helpers.config import Config


class Dataset:
    def __init__(self, source_label, dataset_label):
        """
        Looks for samples in <source_dir>/datasets/<dataset>.samples
        """
        self.label = dataset_label
        self.name = Config('names')[self.label]
        self.source = Source(source_label)
        self.file = join(self.source.base_dir, 'datasets',
                         self.label + '.samples')
        self.samples = self._read_samples()

        # handy shortcuts
        self.sample_ids = self.samples.index.values
        self.populations = self.samples['population'].unique()

    def __repr__(self):
        template = "<Dataset {}, {} populations, {} samples>"
        return template.format(self.label, len(self.populations),
                               len(self.samples))

    def _read_samples(self):
        with open(self.file, 'r') as f:
            samples = [line.strip() for line in f.readlines()]
        return self.source.samples.ix[samples]
