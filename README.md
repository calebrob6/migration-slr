# Migration patterns under different scenarios of sea level rise

By: [Caleb Robinson](http://calebrob.com/), [Bistra Dilkina](https://viterbi.usc.edu/directory/faculty/Dilkina/Bistra), and [Juan Moreno-Cruz](https://www.morenocruz.org/).

This reposoitory accompanies the manuscript, "Migration patterns under different scenarios of sea level rise", in submission to PLOS One. We study how the population distribution of the United States may change under different climate change scenarios by coupling human migration models with sea level rise models and population projections. As sea levels rise throughout the 21st century, large areas of previously habitable land will be directly innundated and/or exposed to more frequent extreme flooding events. This dynamic will displace vulnerable coastal populations, who will have to move to adapt to the climatic pressures. As we show, these migrants have the potential to signficantly shift the population landscape in the US by 2100.

Our work extends prior work by Hauer et al. [1,2], by formalizing the coupling of migration and sea level rise models into a generalized *joint model* of migration under sea level rise, studying the impact of choice of migration model on the final results, and modeling different migration dynamics for affected vs. unaffected migrants.

Using this repository, an user can entirely reproduce the Census block group level sea level rise aware population projections from Hauer 2010 ([


## Explanation of existing files

### Code

### Data

- `R11631788_SL050.txt` - Census 2000 download from Social Explorer, see Codebook at `data/raw/R11631788.txt`
- `R11632411_SL050.txt` - Census 2010 download from Social Explorer, see Codebook at `data/raw/R11633875.txt`
- `R11628343_SL150.txt` - ACS 2012 (5-Year Estimates) download from Social Explorer, see Codebook at `data/raw/R11628343.txt`


- `data/national_population_projections_census_2012.csv` is generated from here [here](https://www.census.gov/data/tables/2012/demo/popproj/2012-summary-tables.html). We concatenate the "Population" columns of the Low Series, Middle Series, and High Series of Table 1. Projections of the Population and Components of Change for the United States: 2015 to 2060.


- `co-est00int-tot.csv` is from https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/county/co-est00int-tot.csv, and includes the 2000-2010 intercensal population estimates per county
- `co-est2017-alldata.csv` is from https://www2.census.gov/programs-surveys/popest/datasets/2010-2017/counties/totals/co-est2017-alldata.csv and includes pre-censal population estimates based on the 2010 census
 

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


## Reproducing results

### Reproducing population/SLR projections (Hauer et al. 2016)

### Hurricane affected counties

### Migration models (Robinson and Dilkina 2018)

### Final results



## References

[1] Hauer, Mathew E., Jason M. Evans, and Deepak R. Mishra. "Millions projected to be at risk from sea-level rise in the continental United States." Nature Climate Change 6.7 (2016): 691.

[2] Hauer, Mathew E. "Migration induced by sea-level rise could reshape the US population landscape." Nature Climate Change 7.5 (2017): 321.

[3] Robinson, Caleb, and Bistra Dilkina. "A machine learning approach to modeling human migration." Proceedings of the 1st ACM SIGCAS Conference on Computing and Sustainable Societies. ACM, 2018.