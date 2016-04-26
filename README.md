# General use #
## The dataset instance: fst(), pca(), and associated objects.
```python
dataset = Dataset('1000Genomes', 'LEA', 'GAL_Completo')  # Source, SampleGroup, Panel
dataset.genotypes()  # => DataFrame with allele dosages per sample/marker

dataset.panel  # => <Panel GAL_Completo · 445 SNPs>
dataset.panel.snps  # => DataFrame with info per SNP

dataset.samplegroup  # => <SampleGroup LEA · 3 regions · 8 populations · 752 samples>
dataset.samplegroup.samples  # => DataFrame with population info per sample

dataset.source  # => <Source 1000Genomes>
dataset.source.populations  # => DataFrame with info per population

dataset.fst()  # => DataFrame of fst values per marker

pca = dataset.pca('smartpca')  # 'sklearn' is the other option
pca.result  # => DataFrame with values of each sample in the PC space

fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(1, 1, 1)
pca.plot(ax=ax, components_to_plot=['PC2', 'PC3'])
plt.show()
# ^ plots the passed components in the passed ax
# omit the ax argument and a new fig will be created
# components_to_plot can be omitted, it has the obvs default of PC1 vs. PC2

dataset.admixture(K=3)
dataste.admixture(K=[2, 3, 4], infer_components=True)
# => DataFrame of cluster pertenence proportions for each sample
```

# Add a new Source #
* Create a new dir with the source name under the sources directory (sources directory is defined in `settings/dirs.yml`).
* Put there a `samples.csv` with info about each sample. Fields are: `sample,family,population,region` (include a header!)
* Put there a `populations.csv` with descriptions for each population. Fields: `population,region,description` (it's ok if it has more fields; include a header)
* Create new dirs: `datasets`, `samplegroups` and `plots` in the source dir. * Create a `samplegroups/ALL.fam` famfile with `family ID, sample ID, father, mother, sexcode, phenotype` and all the samples available for the new source.
* For every SNPs panel you want to use with this source, create `ALL.MyPanel.{bed,bim,fam}` bedfiles in the `datasets` directory and copy the `.bim` also to the panels directory but dropping the `ALL` bit (e.g. `MyPanel.bim`). The bedfiles under `datasets` will be used as base and filtered when asking for different samplegroups within that panel. The `.bim` will be used for reference across sources/samplegroups.

# Create a new Panel of rs IDs #
Panels are defined independently of sources and can be used across multiple sources, but nothing assures you that the list of SNPs will be found in every source. (For instance, HGDP has a limited set of markers available.)

To add a new panel:

* Put the list of marker IDs that constitute the new panel in a `.snps` file. The `Panel.write_bim()` method might be of use for this if you're subsetting an existing panel or creating it via IPython, it will also create a `.snps`.

* Extract the genotypes for ALL samples at those _loci_. This means creating the `ALL` bedfiles `ALL.MyPanel.{bed,bim,fam}` for the new panel under the `datasets` dir in the desired Source directory. Use plink for this with the `.snps` you just created and the project/source original genotypes file (it might be a `.vcf`, in that case use `plink --vcf <SourceFile.vcf>`): `plink --bfile <SourceFile> --extract MyPanel.snps --make-bed --out ALL.MyPanel`. 

    Alternatively, you can do it with `ancestrator`, it the SourceFile that serves as base is a set of bedfiles:
    `Plink(<Path to Source bedfile>).extract(<filepath to .snps of new panel>, out='ALL.MyPanel')`

* Copy the `.bim` and `.snps` files (already created in the previous steps) to the panels directory (defined in `settings/dirs.yml`).

* You can also throw a `.csv` in there with extra info about the SNPs. Make sure you use the same filename (say, `MyPanel.bim` and `MyPanel.csv`).

# Create a new SampleGroup #
* Filter the `ALL.fam` file in the `samplegroups` directory picking the samples you want. You can use the `SampleGroup.write_fam(samples_df, source_label, new_samplegroup_label)` method if you're filtering from a pandas DataFrame. E.g. `samples_df = SampleGroup('1000Genomes', 'ALL').samples; samples_df = samples_df[samples_df.region == 'AMR']; SampleGroup.write_fam(samples_df, '1000Genomes', 'AMR')`.
