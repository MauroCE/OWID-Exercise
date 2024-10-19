import pandas as pd
import numpy as np

# South American Countries according to OWID.
# According to Wikipedia, South Sandwich Islands are uninhabited, and South Georgia island has a very small,
# non-permanent population. Additionally, this country does not appear in the WHO data, so I will exclude it.
data = pd.read_csv("data/continents_owid.csv")
codes = data[data.Continent == "South America"].Code.values
countries = data[data.Continent == "South America"].Entity.values
countries = countries[countries != "South Georgia and the South Sandwich Islands"]

# WHO Population Data
cols = [
    "Region, subregion, country or area *",
    "Female Population, as of 1 July (thousands)",
    "Year",
    "Female Deaths (thousands)"
]
populations = pd.read_excel(
    io="data/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx",
    sheet_name="Estimates",
    skiprows=16)
populations = populations[cols]
populations.rename(
    columns={"Region, subregion, country or area *": "Region",
             "Female Population, as of 1 July (thousands)": "FemalePopulation",
             "Female Deaths (thousands)": "FemaleDeathsPer1000"},
    inplace=True
)

# One can easily check that most South American countries (according to OWID) are also in the WHO data, except
# "South Georgia and the South Sandwich Islands". A few countries have slightly different names, for instance
#     - "Venezuela" -> "Venezuela (Bolivarian Republic of)"
#     - "Bolivia" -> "Bolivia (Plurinational State of)"
#     - "Falkland Islands" -> "Falkland Islands (Malvinas)"
differently_named_countries = {
    'Venezuela (Bolivarian Republic of)',
    'Falkland Islands (Malvinas)',
    'Bolivia (Plurinational State of)'}
all_south_american_countries = set(countries).union(differently_named_countries)
pop_south_america = populations[populations.Region.isin(all_south_american_countries)]
# Rename Venezuela, Falkland Islands, and Bolivia
pop_south_america.loc[pop_south_america.Region == "Venezuela (Bolivarian Republic of)", "Region"] = "Venezuela"
pop_south_america.loc[pop_south_america.Region == "Falkland Islands (Malvinas)", "Region"] = "Falkland Islands"
pop_south_america.loc[pop_south_america.Region == "Bolivia (Plurinational State of)", "Region"] = "Bolivia"
# Compute population by year
fem_pop_by_year = pop_south_america.groupby("Year")["FemalePopulation"].sum() * 1000  # it was in thousands
fem_deaths_by_year = pop_south_america.groupby("Year")["FemaleDeathsPer1000"].sum()*1000
# Equivalent, but done by WHO
who_fem_pop_sa = populations[populations.Region == "South America"].groupby("Year")["FemalePopulation"].sum()*1000
# One can easily check that the two populations are roughly equivalent and indeed the largest difference in any 1 year
# was of about 4 people, so we are indeed working with the same countries, roughly
# just try this: np.max(abs((who_fem_pop_sa - fem_pop_by_year).values.astype(np.float64)))

# Grab WHO mortality data
mortality = pd.read_csv(
    "data/WHOMortalityDatabase_Map_Maternal conditions_28th March 2024 17_52.csv", skiprows=6,
    index_col=False
)
# Notice that in the WHO mortality data we are missing three countries
# 1. Bolivia
# 2. Falkland Islands
# 3. South Georgia and the South Sandwich Islands (which has no population anyway)
# I want to check if there is ever a year when the population of the rest of the countries does not make up at least
# 80% of the total population of South America.
sa_countries_mortality = set(mortality['Country Name'].unique()).intersection(all_south_american_countries)
fem_pop_with_mortality_data = populations[populations.Region.isin(sa_countries_mortality)].groupby("Year")["FemalePopulation"].sum()*1000
# A simple check ((fem_pop_with_mortality_data / fem_pop_by_year) > 0.8).all() shows that we do reach 80% of the total
# (as one would expect since these countries are a small population compared to the rest of South America combined)

# Grab data only for South America
mortality_sa = mortality[mortality["Country Name"].isin(all_south_american_countries)]
mortality_sa_fem = mortality_sa[mortality_sa.Sex == "Female"]


fem_mortality_all_ages = mortality.query("Sex == 'Female' & `Age Group` == '[All]'")
fem_mortality_all_ages = fem_mortality_all_ages[fem_mortality_all_ages["Country Name"].isin(all_south_american_countries)]
fem_mortality_all_ages = fem_mortality_all_ages[
    ["Country Name", "Year", 'Death rate per 100 000 population']
]

# change type of column year to int


