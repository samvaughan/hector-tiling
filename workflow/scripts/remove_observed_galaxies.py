import pandas as pd
import numpy as np
import sqlite3

smk = snakemake  # noqa
master_catalogue = pd.read_csv(smk.input.region_tiling_catalogue).set_index("ID")

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
