import subprocess


class Plink:
    def __init__(self, bfile_path):
        self.label = bfile_path.replace('.bed', '')

    def __repr__(self):
        return '<Plink for "{}">'.format(self.label)

    def make_ped(self):
        self.run('--recode')

    def extract(self, snps_filename, out=None):
        self.run('--extract {}'.format(snps_filename), out=out)

    def run(self, options, out=None):
        if out is None:
            out = self.label
        command_template = 'plink --bfile {} {} --make-bed --out {}'
        command = command_template.format(self.label, options, out)
        subprocess.run(command.split(' '))
