import pandas as pd
import subprocess

from os.path import join, isfile, isdir, basename
from glob import glob
from helpers.config import Config


class Source:
    def __init__(self, source_label):
        """
        Expects to find:
            <base_dir>/<label>/samples.csv
            # with fields: sample, population, region[, gender]

            <base_dir>/<label>/populations.csv
            # with fields: population, description, region

            <base_dir>/<label>/datasets/<dataset_label>.bed
            (^ for any requested dataset)
            It will creat a .traw for dataset if it doesn't find one.
        """
        self.base_dir = join(Config('dirs')['sources'], source_label)
        if not isdir(self.base_dir):
            msg = ("I couldn't find a '{}' directory. "
                   "Is the name of the Source mispelled?'")
            raise Exception(msg.format(self.base_dir))
        self.datasets_dir = join(self.base_dir, 'datasets')
        self.plots_dir = join(self.base_dir, 'plots')
        self.label = source_label
        self.samples = self._read_samples()
        self.populations = self._read_populations()
        self.genotypes_cache = {}

    def __repr__(self):
        return '<Source {}>'.format(self.label)

    def genotypes(self, dataset_label):
        if self.genotypes_cache.get(dataset_label) is None:
            filepath = join(self.datasets_dir, dataset_label + '.traw')
            if not isfile(filepath):
                self._create_traw_from_bed(dataset_label)
            self.genotypes_cache[dataset_label] = self._read_traw(filepath)
        return self.genotypes_cache[dataset_label]

    def has_dataset(self, dataset_label):
        return dataset_label in self.available_datasets()

    def available_datasets(self):
        bedfiles = glob(join(self.datasets_dir, '*.bed'))
        return [basename(bfile).replace('.bed', '') for bfile in bedfiles]

    def bedfile_path(self, dataset_label):
        return join(self.datasets_dir, dataset_label)

    def _read_traw(self, filepath):
        df = pd.read_table(filepath, index_col='SNP')
        df.drop(['CHR', '(C)M', 'POS', 'COUNTED', 'ALT'], axis=1, inplace=True)
        # fids = [iid_fid.split('_')[0] for iid_fid in df.columns]
        iids = [iid_fid.split('_')[1] for iid_fid in df.columns]
        df.columns = iids  # Use individual IDs as columns!
        df.columns.name, df.index.name = 'sample', 'rs_id'
        df = self.samples.join(df.transpose())  # Adds region, pop, family info
        multi_index = ['region', 'population', 'family', 'sample']
        df = df.reset_index().set_index(multi_index)
        return df.sort_index()

    def _create_traw_from_bed(self, dataset_label):
        print('Calling plink to create a .traw for {}'.format(dataset_label))
        bedfile = join(self.datasets_dir, dataset_label)
        if not isfile(bedfile + '.bed'):
            raise OSError("Couldn't find {}.bed".format(bedfile))
        subprocess.run([
            'plink', '--bfile', bedfile,
            '--recode', 'A-transpose',
            '--out', bedfile
        ])

    def _read_samples(self):
        samples = pd.read_csv(join(self.base_dir, 'samples.csv'))
        if 'gender' in samples.columns:
            samples.drop('gender', axis=1, inplace=True)
        samples.set_index('sample', inplace=True)
        samples.rename(columns={'superpopulation': 'region'}, inplace=True)
        return samples

    def _read_populations(self):
        populations = pd.read_csv(join(self.base_dir, 'populations.csv'))
        populations.rename(columns={'superpopulation': 'region'}, inplace=True)
        populations.set_index('population', inplace=True)
        return populations

    #  def samples_from_pop_codes(self, pop_codes):
    #  # Assumes pop_code as a column.
    #  missing = setdiff1d(pop_codes, self.all_samples()["population"])
    #  if len(missing) > 0:
    #  raise ValueError("Couldn't find populations: {}".format(missing))

        #  # Turn population into index temporarily to get the desired samples
        #  # *in the order of the pop_codes*. Then set the original index back.
        #  filtered = self.all_samples().reset_index()\
        # .set_index("population").loc[pop_codes]
        #  return filtered.reset_index().set_index("sample").dropna()

    #  @classmethod
    #  def population_names(cls):
    #  if isfile(cls.POP_NAMES_FILE):
    #  return pd.read_csv(cls.POP_NAMES_FILE, index_col="population")

        #  df = cls._get_pop_names_from_url()
        #  keep_these_columns = ["Population Code", "Population Description",
        #  "Super Population Code"]
        #  df = df[keep_these_columns]
        #  df.columns = ["population", "description", "superpopulation"]
        #  df.set_index("population", inplace=True)

        #  df.to_csv(cls.POP_NAMES_FILE)
        #  return df
