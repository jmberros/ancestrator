import pandas as pd
import subprocess

from os.path import expanduser, join
from shutil import copyfile

from analyzers.base_pca import BasePCA
from helpers.helpers import percentage_fmt


class SmartPCA(BasePCA):
    _EXECUTABLE = expanduser('~/software/eigensoft6/src/eigensrc/smartpca')

    def __init__(self, dataset):
        self.dataset = dataset

    def run(self, args={}):
        self._evecfile = self._output_filepath('pca.evec')
        self._evalfile = self._output_filepath('pca.eval')
        self._logfile = self._output_filepath('pca.log')

        args = {**self.arguments(), **args}
        parfile_path = self._create_parameters_file(args)
        command = '{} -p {}'.format(self._EXECUTABLE, parfile_path)
        with open(self._output_filepath('pca.log'), 'w+') as logfile:
            subprocess.call(command.split(' '), stdout=logfile)

        result = pd.read_table(self._evecfile, sep="\s+", header=None,
                               skiprows=1)

        # TODO: read the interesting info in the log file
        self.explained_variance = self._read_eval_file(args['evaloutname'])
        self.result = self._parse_evec_file(result)
        self.extra_info = self._read_log()

    def arguments(self):
        # See ./POPGEN/README in the eigensoft package for a description
        # about each of these parameters and some extra ones.
        args = {
            'genotypename': self.dataset.pedfile,
            'snpname': self._create_pedsnp(),
            'indivname': self._create_pedind(),
            'numoutevec': 15,  # PCs to take
            'evecoutname': self._evecfile,
            'evaloutname': self._evalfile,
            'altnormstyle': 'NO',
            'numoutlieriter': 5,  # max outlier removal iterations
            'numoutlierevec': 10,  # PCs along which to remove outliers
            'outliersigmathresh': 6,  # min standard deviations of outliers
            'missingmode': 'NO',  # set to YES for 'informative missingness'
            'fastmode': 'NO',
            'outliermode': 1,
        }
        return args

    def _create_parameters_file(self, args):
        parfile_path = join(self.dataset.bedfile + '.pca.par')
        with open(parfile_path, 'w+') as parfile:
            for argname, argvalue in args.items():
                parfile.write('{}: {}\n'.format(argname, argvalue))
        return parfile_path

    def _create_pedsnp(self):
        # .pedsnp format is exactly the same as .bim, but smartpca needs
        # the file to have that extension.
        pedsnp_filepath = self.dataset.bedfile + '.pedsnp'
        copyfile(self.dataset.bimfile, pedsnp_filepath)
        return pedsnp_filepath

    def _create_pedind(self):
        ped = pd.read_table(self.dataset.pedfile, header=None, sep='\s+')
        pedind = ped.ix[:, :6]  # .pedind = the first 6 columns of .ped
        pedind_filepath = self.dataset.bedfile + '.pedind'
        pedind.to_csv(pedind_filepath, sep=' ', header=False, index=False)
        return pedind_filepath

    def _output_filepath(self, ext):
        return self.dataset.bedfile + '.' + ext

    def _parse_evec_file(self, df):
        df[0] = df[0].map(lambda s: s.split(':')[1])
        df = df.set_index(0)
        df = df.ix[:, df.columns[:-1]]  # Remove the '???' useless col
        df.columns = ['PC{}'.format(column) for column in df.columns]
        df.index.name = 'sample'
        df = df.join(self.dataset.samplegroup.samples).reset_index()
        df = df.set_index(['region', 'population', 'sample'])
        df = df.sort_index()
        return df

    def _read_eval_file(self, eval_filename):
        df = pd.read_table(eval_filename, header=None, names=['variance'])
        df.index = ['PC{}'.format(ix + 1) for ix in df.index]
        df['ratio'] = df['variance'] / df['variance'].sum()
        df['percentage'] = df['ratio'].map(percentage_fmt)
        return df

    def _read_log(self):
        self._logfile
        return 'Not implemented yet :('
        # TODO read the logfile!