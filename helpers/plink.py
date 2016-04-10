import subprocess
from os.path import dirname, join


class Plink:
    def __init__(self, bfile_path):
        self.label = bfile_path.replace('.bed', '')
        self.workdir = dirname(bfile_path)

    def __repr__(self):
        return '<Plink for "{}">'.format(self.label)

    def make_ped(self):
        self.run('--recode')

    def extract(self, snps_filename, out):
        self.run('--extract {}'.format(snps_filename), out=out)

    def keep_fam(self, samples_filepath, out):
        return self.run('--keep-fam {}'.format(samples_filepath), out=out)

    def fst(self, clusters_file, out=None):
        return self.run('--within {} --fst'.format(clusters_file), out=out,
                        make_bed=False)

    def run(self, options, out=None, make_bed=True):
        out = join(self.workdir, out)
        if out is None:
            out = self.label
        command_template = 'plink --bfile {} {}'
        if make_bed:
            command_template += ' --make-bed'
        command_template += ' --out {}'
        command = command_template.format(self.label, options, out)
        subprocess.run(command.split(' '))

        return out
