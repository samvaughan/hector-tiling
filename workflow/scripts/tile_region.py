"""
Take the catalogues of galaxies, guide stars and standard stars for a region and run the tiling algorithm to create Hector tiles ready for the configuration pipeline.
"""

from hop import pipeline
from pathlib import Path
import hop.misc.misc_tools as misc_tools
import shutil
import sqlite3
import pandas as pd
import numpy as np

smk = snakemake  # noqa

# Load out config file
config_dictionary = misc_tools._load_config(smk.input.config_file)

# Edit some of the things in the config filename
config_dictionary["final_catalogue_name"] = smk.input.region_target_catalogue
config_dictionary["guide_star_filename"] = smk.input.region_guide_star_catalogue
config_dictionary["standard_star_filename"] = smk.input.region_standard_star_catalogue

# Some more parameters
config_dictionary["output_filename_stem"] = smk.params.output_filename_stem
config_dictionary["output_folder"] = smk.params.output_folder
config_dictionary["SourceCat"] = smk.params.output_filename_stem

# This isn't needed for the tiling run
skyfiles_location = (
    ""  # Path(config_dictionary['profit_skymasks_location']) / smk.params.region
)
try:
    print(f"Tiling the {smk.wildcards.master_region} field {smk.wildcards.region_name}")
except AttributeError:
    pass
print(f"\tProximity is {config_dictionary['proximity']} arcseconds")

HP = pipeline.HectorPipe(
    config_dictionary=config_dictionary, Profit_files_location=skyfiles_location
)
HP.load_input_catalogue()

# Add a type column which we'll use later
HP.df_targets["type"] = 1

# Add zeros for the star-specific values
HP.df_targets[
    [
        "y_mag",
        "GAIA_g_mag",
        "GAIA_bp_mag",
        "GAIA_rp_mag",
        "pmRA",
        "pmDEC",
    ]
] = 0.0

HP.df_standard_stars.loc[:, ["y_mag", "Mstar", "Re", "z", "GAL_MU_E_R"]] = 0.0

# Get the largest tile ID we already have in the database
con = sqlite3.connect(smk.input.observed_galaxy_database)
tile_database = pd.read_sql("select * from tiles", con)

starting_tile_number = int(
    tile_database.loc[
        tile_database["region"] == smk.wildcards.region_name, "tile_number"
    ].max()
    + 1
)

print(f"Field: {smk.wildcards.region_name}")
print(f"\tTotal Targets: {len(HP.df_targets)}")
print(f"\tRemaining Targets: {np.sum(HP.df_targets['N_observations_to_complete'] > 0)}")
print(f"\tStarting the tiling from tile number {starting_tile_number}")

HP.tile_field(
    configure_tiles=False,
    apply_distortion_correction=False,
    check_sky_fibres=False,
    use_galaxy_priorities=True,
    date="2023 06 15",
    plot=True,
    label=f"{smk.wildcards.region_name}",
    starting_tile_number=starting_tile_number,
)

# Clean up our output folders
folders_to_remove = [
    "Allocation",
    "DistortionCorrected",
    "FinalOutputs",
    "Configuration",
    "Fibres",
    "Logs",
]
base_output_folder = Path(smk.output.tiling_complete_flag).parent
for folder in folders_to_remove:
    path = base_output_folder / folder
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass

Path(smk.output.tiling_complete_flag).touch()
