# Running the Code

To start a new iteration of the tiling, taking into account the galaxies which have already been observed during the survey, follow the steps under [Running the Tiling](#running-the-tiling). This will create the necessary `.fld` files for the targets in each of the Hector Regions (G12, G15, etc).

If you want to tile a _new_ region of the sky, go to [Adding a new region](#adding-a-new-region)


## Running the Tiling

1. Create a new config file named `YYYMMDD.yaml` in the `config` folder. This should contain a single entry which is the date you're conducting the tiling. This is used to make the output folder in `results`. The format for this line should be `date: YYYYMMDD`.
2. Ensure that the most up-to-date versions of the Master Region catalogues are in the `resources/MasterRegionCatalogues` folder. These are the files which contain _all_ the Hector targets in a given region (including galaxies which have been observed already). Note that we need three catalogues to tile a region of sky- a galaxy catalogue, a guide star catalogue and a standard star catalogue.
3. Ensure that the up-to-date Hector Observing Database is sym-linked in the `resources/HectorDB/hector.db`. The script `workflow/scripts/remove_observed_galaxies.py` uses the `galaxies_observed` table to see which targets from the Master Region catalogue have already been targeted. Anything in this table will have its value of `N_observations_to_complete` reduced by 1. Anything with `N_observations_to_complete` equal to 0 will be ignored by the Tiling code.
4. Now run `snakemake -npr --configfile config/YYYMMDD.yaml`, giving it the name of the config file you made earlier. This will print out the steps the pipeline will undertake. Note that this command will tile _all_ of the different regions Hector will observe. _I highly recommend that you always retile all of the regions together_. It is possible to only make new tiles for, say, H01 on its own. However you'd then need to remember that the most recent tiles for H01 were in a different folder than all of the others and it would be easy to make a mistake when preparing for a run~
5. If all that looks acceptable, run `snakemake --configfile config/YYYMMDD.yaml` to actually run the code.
6. You should end up with a new folder in `results/YYYMMDD`. This should contain two folders: `MasterRegionCatalogues` and `Tiling`. The `MasterRegionCatalogues` folder contains all of the targets for a given region with all the targets we've already completed removed. This is the catalogue which has actually been tiled by the code. The `Tiling` folder contains the `.fld` files which you'll need for the Observing Pipeline, as well as plots of each of the tiles the code has made.

## Adding a new Region

To add a new region to the tiling, you'll have to make adjustments in three places:

1. Add the required galaxy, standard star and guide star catalogues to the correct subdirectory in the `resources/MasterRegionCatalogues/` folder.
2. Add a line to the `resources/RegionInformation/all_regions.csv` file. Each row sets out a square patch of sky to define the area each "region" covers.
3. Add the name of the new region to line 21 of `workflow/Snakefile`. This line sets out which regions the code will run on.

And that should be it!
