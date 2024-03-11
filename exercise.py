
import numpy as np
from utils import read_table_from_notion, read_UN_population_data
import matplotlib.pyplot as plt
from matplotlib import rc


WHO_STD_POP = np.array([
    8.86, 8.69, 8.60, 8.47, 8.22, 7.93, 7.61, 7.15, 6.59, 6.04, 5.37, 4.55, 3.72, 2.96, 2.21, 1.52, 0.91, 0.63
])

# Read data
who_std_pop = WHO_STD_POP / WHO_STD_POP.sum()  # proportions (sum up to 1)
death_rates = read_table_from_notion()  # death rates by age group for the USA and Uganda
usa_pop_props, uganda_pop_props = read_UN_population_data()  # population proportions for the USA and Uganda

# Compute crude death rates (rounded to one decimal place)
print("Crude Death Rates")
print("\tUSA:    ", round(np.sum(death_rates['usa'].values * usa_pop_props), 1))
print("\tUganda: ", round(np.sum(death_rates['uganda'].values * uganda_pop_props), 1))

# Compute age-standardized death rates (rounded to one decimal place)
print("Age-Standardized Death Rates")
print("\tUSA:    ", round(np.sum(death_rates['usa'].values * who_std_pop), 1))
print("\tUganda: ", round(np.sum(death_rates['uganda'].values * who_std_pop), 1))

# Show the difference in age distribution between the USA, Uganda and WHO standard
rc('font', **{'family': 'STIXGeneral'})
fig, ax = plt.subplots(ncols=3, figsize=(16, 4), sharex=True, sharey=True)
x = np.linspace(0, 85, 18)
ax[0].bar(x, usa_pop_props, width=5, alpha=0.5, label="USA", color='indianred', edgecolor='firebrick', lw=1.3, zorder=10)
ax[1].bar(x, uganda_pop_props, width=5, alpha=0.5, label="Uganda", color='turquoise', edgecolor='teal', lw=1.3, zorder=10)
ax[2].bar(x, who_std_pop, width=5, alpha=0.5, label="WHO", color='gold', edgecolor='darkgoldenrod', lw=1.3, zorder=10)
ax[0].set_ylabel(r"Proportion of Population", fontsize=20)
for i in range(3):
    ax[i].grid(True, color='gainsboro')
    ax[i].set_xlabel(r"Age Groups", fontsize=20)
    ax[i].legend(fontsize=18)
plt.tight_layout()
plt.savefig("populations.png", dpi=300)
plt.show()
