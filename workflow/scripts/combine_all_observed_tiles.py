import pandas as pd
from pathlib import Path

smk = snakemake  # noqa
tiles_observed = smk.input.completed_tiles

observed_galaxies = pd.DataFrame()

for tile in tiles_observed:
    tmp_df = pd.read_csv(tile, comment="#")
    # Only keep galaxies
    tmp_df = tmp_df.loc[tmp_df["type"] == 1]
    tile = Path(tile)
    tmp_df["tile_name"] = tile.stem
    tmp_df["region"] = tile.stem.split("_")[0]
    tmp_df["tile_number"] = int(tile.stem.split("_")[1].strip("T"))
    observed_galaxies = pd.concat((observed_galaxies, tmp_df))

print(
    f"Combining {len(tiles_observed)} tiles gives {len(observed_galaxies)} observed to date"
)
observed_galaxies.to_csv(smk.output.observed_galaxy_catalogue)
