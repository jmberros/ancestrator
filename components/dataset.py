from pandas import IndexSlice as idx
from glob import glob
from os.path import join, basename
from components.source import Source
from components.panel import Panel
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
        self.genotypes_cache = {}

        # handy shortcuts
        self.sample_ids = self.samples.index.values
        self.populations = self.samples['population'].unique()

    def __repr__(self):
        template = "<Dataset {}, {} populations, {} samples>"
        return template.format(self.label, len(self.populations),
                               len(self.samples))

    def genotypes(self, panel_label):
        if panel_label not in self.genotypes_cache:
            all_genos = Panel(panel_label).genotypes(self.source.label)
            genos = all_genos.loc[idx[:, :, self.sample_ids], :]
            self.genotypes_cache[panel_label] = genos

        return self.genotypes_cache[panel_label]

    def _read_samples(self):
        with open(self.file, 'r') as f:
            samples = [line.strip() for line in f.readlines()]
        return self.source.samples.ix[samples]

    def write_clusters_files(self, dest_dir):
        """
        Will write a file with three columns: FID, IID, and cluster info, for
        use with plink (cluster info is used for Fst).
        """
        samples_info = self._thousand_genomes.all_samples().ix[self.sample_ids]
        # Family ID (FID), Within-family ID (IID), Cluster ID
        filenames = []
        for level in ["population", "superpopulation"]:
            df = samples_info.reset_index()
            df["FID"] = df["sample"]
            df = df[["FID", "sample", level]]
            filename = "{}.{}.clusters".format(self.label, level)
            df.to_csv(join(dest_dir, filename), sep="\t", header=None,
                      index=False)
            filenames.append(filename)

        return filenames

    @staticmethod
    def available_datasets(source_label):
        datasets_dir = join(Source(source_label).base_dir, 'datasets')
        samples_files = glob(join(datasets_dir, '*.samples'))
        labels = [basename(f).replace('.samples', '') for f in samples_files]
        return sorted(labels)
