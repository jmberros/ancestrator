# Add a new Source #
* Create a new dir with the source name under the sources directory
  (sources directory is defined in `settings/dirs.yml`).
* Put there a `samples.csv` with info about each sample. Fields are:
  `sample,family,population,region` (include a header!)
* Put there a `populations.csv` with descriptions for each population. Fields:
  `population,region,description` (it's ok if it has more fields; include a
  header)
* Create new dirs: `datasets`, `samplegroups` and `plots` in the source dir.
* Create an `samplegroups/ALL.fam` famfile with `family ID, sample ID, father, mother, sexcode, phenotype`.
* The panels defined in the panels dir (check `settings/dirs.yml` for the location) will still be the same. Alternatively, you can define new panels as lists of rs IDs there (see next section). For every panel you want to use, you need to create the `ALL` bedfiles under the `datasets` dir --for instance, `ALL.MyPanel.{bed,bim,fam}`. Make sure you also copy the `.bim` of that panel to the panels directory, dropping the `ALL.` bit. The bedfile will be used as base and filtered when asking for different samplegroups within that panel.

# Create a new Panel of rs IDs #
Panels are defined independently of sources and can be used across multiple
sources, but nothing assures you that the list of SNPs will be found in every
source. (For instance, HGDP has a limited set of markers available.)

To add a new panel:

* Create a new `.bim` file in the panels dir (defined in `settings/dirs.yml`) with the info about each marker. The `Panel.write_bim()` method might be of use for this if you're subsetting an existing panel or creating it via IPython. The method will also write a `.snps` helper file that is needed.

* You can also throw a `.csv` in there with extra info about the SNPs. Make sure you use the same filename (say, `MyPanel.bim` and `MyPanel.csv`).

* Create the `ALL` bedfiles `ALL.MyPanel.{bed,bim,fam}` for the new panel under the `datasets` dir. This bedfile will be used as a base to filter different samplegroups later. To create the new bedfiles use plink with the `.snps` you just created: `plink --bfile <ALL.base> --extract MyPanel.snps --make-bed --out ALL.MyPanel`. 

    Alternatively, you can do it with `ancestrator`:
    `Plink(BasePanel.bedfile).extract(<filepath to .snps just created>, out='ALL.MyPanel')`

# Create a new SampleGroup #
* Put a list of sample IDs in a new `.samples` file under the `samplegroups`
    directory of the desired source. The list should be subset of the samples
    found in `ALL.samples`.
