#! /usr/bin/env python


from ancestrator import *

#  panels = ["GAL_Affy", "GAL_Completo", "CPx100", "100_SNPs_from_GAL_Affy",
          #  "50_SNPs_from_GAL_Affy", "25_SNPs_from_GAL_Affy",
          #  "20_SNPs_from_GAL_Affy", "15_SNPs_from_GAL_Affy"]
panels = ["CPx10", "CPx1"]
samplegroups = ["LEAC", "LEACI"]
source = "1000Genomes"

for panel in panels:
    for samplegroup in samplegroups:
        dataset = Dataset(source, samplegroup, panel)
        print(dataset)
        pca = dataset.pca('smartpca')
