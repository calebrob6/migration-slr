# migration-slr

# Data

## Raw
- `R11631788_SL050.txt` - Census 2000 download from Social Explorer, see Codebook at `data/raw/R11631788.txt`
- `R11632411_SL050.txt` - Census 2010 download from Social Explorer, see Codebook at `data/raw/R11633875.txt`
- `R11628343_SL150.txt` - ACS 2012 (5-Year Estimates) download from Social Explorer, see Codebook at `data/raw/R11628343.txt`


- `data/national_population_projections_census_2012.csv` is generated from here [here](https://www.census.gov/data/tables/2012/demo/popproj/2012-summary-tables.html). We concatenate the "Population" columns of the Low Series, Middle Series, and High Series of Table 1. Projections of the Population and Components of Change for the United States: 2015 to 2060.


### Digital Coast processing

(NEED GDAL)

- Download and unzip all "Sea Level Rise" data from (here)[https://coast.noaa.gov/slrdata/] into `data/raw/digital_coast/`. For convinience, see `data/raw/digital_coast/url_list.txt` for a list of files to download. Unzipped, this data will be ~110GB on disk.



- Merge all rasterized polygons with `gdal_merge.py -o 2ft.tif -n -1 -a_nodata -1 -co COMPRESS=DEFLATE -co PREDICTOR=1 -co TILED=NO -co NUM_THREADS=ALL_CPUS /home/caleb/Dropbox/code/migration_slr/data/digital_coast/slr_2ft/*.tif`
- We have three rasters for each level of sea level rise:
  1. `{0-6}ft.tif`
  2. `{0-6}ft_masked.tif`
  3. `{0-6}ft_masked_union.tif`


TODO
- Explain what `data/raw/cph-2-1-1.pdf` is and how we go from that to `data/intermediate/Population and Housing Units: 1940 to 1990.txt`
  - `data/raw/cph-2-1-1.pdf` comes from [here](https://www.census.gov/data/tables/1993/dec/cph-2-1-1.html).
  - We use this data based on Hauer et al. 2016 [1] supplementary information, "The second piece of data is the actual historic count of housing units (HU) and population for each county. This data is available as digitized records from the Census Bureau’s website. For 1940 to 1990, data can be found at http://www.census.gov/prod/cen1990/cph2/cph-2-1-1.pdf."

- Need to explain how we get from `data/intermediate/Population and Housing Units: 1940 to 1990__intermediate.csv` to `data/processed/Population and Housing Units: 1940 to 1990.csv`



## Citations

[1] Hauer, Mathew E., Jason M. Evans, and Deepak R. Mishra. "Millions projected to be at risk from sea-level rise in the continental United States." Nature Climate Change 6.7 (2016): 691.

[2] Hauer, Mathew E. "Migration induced by sea-level rise could reshape the US population landscape." Nature Climate Change 7.5 (2017): 321.