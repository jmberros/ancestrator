import pandas as pd
import subprocess

from os.path import expanduser, join
from shutil import copyfile


class SmartPCA:
    # PATH_TO_EXECUTABLE = expanduser('~/software/eigensoft6/bin/smartpca.perl')
    EXECUTABLE = expanduser('~/software/eigensoft6/src/eigensrc/smartpca')

    def __init__(self, dataset):
        self.dataset = dataset

    def run(self, args={}):
        self.evecfile = self.output_filepath('pca.evec')
        self.evalfile = self.output_filepath('pca.eval')
        self.logfile = self.output_filepath('pca.log')

        args = {**self.arguments(), **args}
        parfile_path = self.create_parameters_file(args)
        command = '{} -p {}'.format(self.EXECUTABLE, parfile_path)
        print(command)
        with open(self.output_filepath('pca.log'), 'w+') as logfile:
            subprocess.call(command.split(' '), stdout=logfile)

        result = pd.read_table(self.evecfile, sep="\s+",
                               header=None, skiprows=1)
        explained_variance = self._read_eval_file(args['evaloutname'])

        # TODO: read the interesting info in the log file!!!!
        # TODO: merge the result df with the samples index
        return self._parse_evec_file(result), explained_variance

    def arguments(self):
        # See ./POPGEN/README in the eigensoft package for a description
        # about each of these parameters and some extra ones.
        args = {
            'genotypename': self.dataset.pedfile,
            'snpname': self.create_pedsnp(),
            'indivname': self.create_pedind(),
            'numoutevec': 15,  # PCs to take
            'evecoutname': self.evecfile,
            'evaloutname': self.evalfile,
            'altnormstyle': 'NO',
            'numoutlieriter': 5,  # max outlier removal iterations
            'numoutlierevec': 10,  # PCs along which to remove outliers
            'outliersigmathresh': 6,  # min standard deviations of outliers
            'missingmode': 'NO',  # set to YES for 'informative missingness'
            'fastmode': 'NO',
            'outliermode': 1,
        }
        return args

    def create_parameters_file(self, args):
        parfile_path = join(self.dataset.bedfile + '.pca.par')
        with open(parfile_path, 'w+') as parfile:
            for argname, argvalue in args.items():
                parfile.write('{}: {}\n'.format(argname, argvalue))
        return parfile_path

    def create_pedsnp(self):
        # .pedsnp format is exactly the same as .bim, but smartpca needs
        # the file to have that extension.
        pedsnp_filepath = self.dataset.bedfile + '.pedsnp'
        copyfile(self.dataset.bimfile, pedsnp_filepath)
        return pedsnp_filepath

    def create_pedind(self):
        ped = pd.read_table(self.dataset.pedfile, header=None, sep='\s+')
        pedind = ped.ix[:, :6]  # .pedind = the first 6 columns of .ped
        pedind_filepath = self.dataset.bedfile + '.pedind'
        pedind.to_csv(pedind_filepath, sep=' ', header=False, index=False)
        return pedind_filepath

    def output_filepath(self, ext):
        return self.dataset.bedfile + '.' + ext

    def _parse_evec_file(self, df):
        df = df.ix[:, df.columns[:-1]]  # Remove the '???' useless col
        df[0] = df[0].map(lambda s: s.split(':')[1])
        df = df.set_index(0)
        df.index.name = 'sample'
        df.columns = ['PC{}'.format(column) for column in df.columns]
        return df

    def _read_eval_file(self, eval_filename):
        df = pd.read_table(eval_filename, header=None, names=['variance'])
        df.index = ['PC{}'.format(ix + 1) for ix in df.index]
        df['ratio'] = df['variance'] / df['variance'].sum()
        pretty_percentage = lambda r: '{0:.1f}%'.format(100*r)
        df['percentage'] = df['ratio'].map(pretty_percentage)
        return df


