The two files in this directory, `output_high_scenario.xlsx` and `output_medium_scenario.xlsx`, contain formatted results from the neural network model.

The column headers are as follows:
- `county_fips` - The county FIPS code (or GEOID in some places)
- `projected population {YEAR}` - Projected population according to methodology we replicated from Hauer et al. 2016, "Millions projected to be at risk from sea-level rise in the continental United States" in Nature Climate Change.
- `incoming baseline migration {YEAR}` - Modeled incoming migration per county assuming no SLR
- `incoming slr migration {YEAR}` - Modeled incoming migration per county with SLR effects
- `migration difference {YEAR}` - Difference of the previous two (for convenience)
- `migration difference proportion {YEAR}` - Difference / Population