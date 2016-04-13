# Add a new Source #
* Create a new dir with the source name under the sources directory
  (sources directory is defined in `settings/dirs.yml`).
* Put there a `samples.csv` with info about each sample. Fields are:
  `sample,population,region`
* Put there a `populations.csv` with descriptions for each population. Fields:
  `population,region,description` (it's ok if it has more fields)
* Create new dirs: `datasets`, `samplegroups` and `plots` in the source dir.
* Create an `samplegroups/ALL.samples` plain text file with one sample id per line. It should be just a list of all sample IDs of the project. You can do `tail -n +2 samples.csv | ruby -F, -lane 'puts $F.first' > samplegroups/ALL.samples`.
* The panels defined in the panels dir (check `settings/dirs.yml` for the location) will still be the same. Alternatively, you can define new panels as lists of rs IDs there (see next section). For every panel you want to use, you need to create the `ALL` bedfiles under the `datasets` dir --for instance, `ALL.MyPanel.{bed,bim,fam}`. That bedfile will be used as base and filtered when asking for different samplegroups within that panel.

# Create a new Panel of rs IDs #
Panels are defined independently of sources and can be used across multiple
sources, but nothing assures you that the list of SNPs will be found in every
source. (For instance, HGDP has a limited set of markers available.)

* Create a new `.bim` file in the panels dir (defined in `settings/dirs.yml`)
    with the info about each marker.
* You can also throw a `.csv` in there with extra info about the SNPs. Make
    sure you use the same filename (say, `MyPanel.bim` and `MyPanel.csv`).

# Create a new SampleGroup #
* Put a list of sample IDs in a new `.samples` file under the `samplegroups`
    directory of the desired source. The list should be subset of the samples
    found in `ALL.samples`.
