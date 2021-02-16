The two files in this directory, `affected_population_medium.csv` and `affected_population_high.csv`, contain formatted results from interseceting the projected population with the Digital Coast SLR estimates.

In the medium scenario we assume 0.3m SLR at 2055, 0.6m at 2080 and 0.9m at 2100. In the high scenario we are assuming 0.3m SLR at 2042, 0.6m at 2059, 0.9m at 2071, 1.2m at 2082, 1.5m at 2091, and 1.8m at 2100.

The column headers are as follows:
- `County FIPS` - The county FIPS code (or GEOID in some places)
- `Total Population {YEAR}` - Projected population according to methodology we replicated from Hauer et al. 2016, "Millions projected to be at risk from sea-level rise in the continental United States" in Nature Climate Change.
- `Affected Population {YEAR}` - The amount of population per county that is estimated to be directly effected by SLR.