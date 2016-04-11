from glob import glob
from os.path import join, basename

from components.source import Source
from helpers.config import Config


class SampleGroup:
    def __init__(self, samplegroup_label, source_label):
        """
        Looks for samples in <source_dir>/samplegroups/<samplegroup>.samples
        """
        self.label = samplegroup_label
        self.name = Config('names')[self.label]
        self.source = Source(source_label)
        self.base_dir = join(self.source.base_dir, 'samplegroups')
        self.samples = self._read_samples()

        # handy shortcuts
        self.sample_ids = self.samples.index.values
        self.populations = self.samples['population'].unique()
        self.regions = self.samples['region'].unique()

    def __repr__(self):
        tmpl = '<SampleGroup {} · {} regions · {} populations · {} samples>'
        return tmpl.format(self.label, len(self.populations),
                           len(self.regions), len(self.samples))

    def _read_samples(self):
        self.samples_file = join(self.base_dir, self.label + '.samples')
        with open(self.samples_file, 'r') as f:
            samples = [line.strip() for line in f.readlines()]
        return self.source.samples.ix[samples]

    def _write_clusters_files(self, level='population'):
        """
        Write a file with three columns: FID, IID, and cluster (pop or region).
        FID and IID are usually the same, the clusters field is what matters
        for later use with plink --fst.
        """
        # Family ID (FID), Within-family ID (IID), Cluster ID
        clusters = self.samples.reset_index()
        clusters["FID"] = clusters["sample"]
        clusters = clusters[["FID", "sample", level]]
        filename = "{}.{}.clusters".format(self.label, level)
        filepath = join(self.base_dir, filename)
        clusters.to_csv(filepath, sep="\t", header=None, index=False)

        return filepath

    @staticmethod
    def available_samplegroups(source_label):
        samplegroups_dir = join(Source(source_label).base_dir, 'samplegroups')
        samples_files = glob(join(samplegroups_dir, '*.samples'))
        labels = [basename(f).replace('.samples', '') for f in samples_files]
        return sorted(labels)
