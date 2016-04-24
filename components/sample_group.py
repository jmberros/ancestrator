import pandas as pd

from glob import glob
from os.path import join, basename, isfile

from components.source import Source
from helpers.config import Config


class SampleGroup:
    def __init__(self, source_label, samplegroup_label):
        """
        Looks for samples in <source_dir>/samplegroups/<samplegroup>.fam
        """
        self.label = samplegroup_label
        self.name = Config('names').get(self.label, self.label)
        self.source = Source(source_label)
        self.base_dir = join(self.source.base_dir, 'samplegroups')

        self.famfile = join(self.base_dir, self.label + '.fam')
        self.samples = self._read_fam()

        # handy shortcuts
        self.sample_ids = self.samples.index.values
        self.populations = self.samples['population'].unique()
        self.regions = self.samples['region'].unique()

    def __repr__(self):
        tmpl = '<SampleGroup {} · {} regions · {} populations · {} samples>'
        return tmpl.format(self.label, len(self.regions),
                           len(self.populations), len(self.samples))

    def _read_fam(self):
        all_samples = self.source.samples
        samples = pd.read_table(self.famfile, names=self._fam_fields(),
                                index_col="sample", sep='\s+')
        return all_samples.loc[samples.index]

    @classmethod
    def new_samplegroup(cls, source_label, codes, new_samplegroup_label):
        """
        Create a new SampleGroup filtering all the available samples in a given
        source with the provided sample, population and/or region codes
        (you can mix them). It will write the new .fam file needed to later use
        SampleGroup('NewLabel').
        """
        all_samples = SampleGroup(source_label, 'ALL').samples.reset_index()
        pop_mask = all_samples['population'].isin(codes)
        region_mask = all_samples['region'].isin(codes)
        sample_mask = all_samples['sample'].isin(codes)
        samples_df = pd.concat([all_samples[pop_mask],
                                all_samples[sample_mask],
                                all_samples[region_mask]])
        samples_df = samples_df.set_index('sample')
        cls.write_fam(samples_df, source_label, new_samplegroup_label)

        msg = "You can now call SampleGroup('{}', '{}')"
        print(msg.format(source_label, new_samplegroup_label))

    @staticmethod
    def _fam_fields():
        return ['family', 'sample', 'father', 'mother', 'sexcode', 'pheno']

    @classmethod
    def write_fam(cls, samples_df, source_label, new_samplegroup_label):
        """
        Writes a .fam file from a dataframe of samples. Useful if you're
        subsetting an existing SampleGroup. The dataframe should have the
        sample IDs as index.
        """
        if len(new_samplegroup_label) == 0:
            raise NameError('Please choose a non-empty SampleGroup name.')
        dest_dir = join(Source(source_label).base_dir, 'samplegroups')
        filepath = join(dest_dir, new_samplegroup_label + '.fam')
        if isfile(filepath):
            msg = 'Label "{}" is already in use.'.format(new_samplegroup_label)
            raise NameError(msg)
        fam_df = samples_df.reset_index()
        fam_df['father'] = fam_df['mother'] = fam_df['sexcode'] = 0
        fam_df['pheno'] = -9
        fam_df = fam_df[cls._fam_fields()]
        fam_df.to_csv(filepath, index=False, header=False, sep=' ')
        print('Written -> ' + filepath)
        return filepath

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

    def clusters_filepath(self, level):
        filename = '{}.{}.clusters'.format(self.label, level)
        return join(self.base_dir, filename)

    @staticmethod
    def available_samplegroups(source_label):
        samplegroups_dir = join(Source(source_label).base_dir, 'samplegroups')
        samples_files = glob(join(samplegroups_dir, '*.samples'))
        labels = [basename(f).replace('.samples', '') for f in samples_files]
        return sorted(labels)
