import pandas as pd
import numpy as np
import sqlite3

smk = snakemake  # noqa
master_catalogue = pd.read_csv(smk.input.region_tiling_catalogue).set_index("ID")

"""
ToDo
(SPV Feb 2024)

When the QC and data reduction process is mature, this section of code will need to be edited.
At the moment, it removes galaxies which have been observed. However, there are likely to be 
galaxies which will need to be re-observed because they fail QC. The logic below will have to account for this!

I would recommend making a new table in the database called something like "QC_checks". This table will have to have a column 
with three options:
     
* QC passed- this galaxy is done and shouldn't be re-tiled.
* QC failed- this galaxy needs to be tiled again
* QC pending- this galaxy hasn't been reduced/checked yet, in which case *it also shouldn't be re-tiled*.

The aim of the "pending" column is to avoid galaxies being reobserved just because the QC process 
is slow- in that case we'd end up with mutliple good observations of the same object.
"""
con = sqlite3.connect(smk.input.observed_galaxy_database)
observed_galaxies = pd.read_sql("select * from galaxies_observed", con)

# Find out how many times each galaxy has been observed
n_observations_per_galaxy = observed_galaxies["ID"].value_counts()
# Now reindex this to match the indexing of our master catalogue
n_reindexed = n_observations_per_galaxy.reindex(master_catalogue.index, fill_value=0)
# Now subtract this from the "N_observations_to_complete" category
master_catalogue["N_observations_to_complete"] -= n_reindexed

# Now check that we haven't made anything negative
negative_mask = master_catalogue["N_observations_to_complete"] < 0

if np.any(negative_mask):
    master_catalogue.loc[negative_mask, "N_observations_to_complete"] = 0


master_catalogue.to_csv(smk.output.output_catalogue)
