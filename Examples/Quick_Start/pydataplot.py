import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

data_dir = '/Users/dchen/Documents/GitHub/MOCAT-MC/200 year sim'
ts_files = sorted(glob.glob(os.path.join(data_dir, 'timeseries_seed*.csv')))
print(f"Found {len(ts_files)} files")

fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
species = [('active', 'Active satellites', 'b'),
           ('derelict', 'Derelicts', 'r'),
           ('debris', 'Debris', 'k')]

for f in ts_files:
    seed = int(f.split('seed')[1].split('.')[0])
    df = pd.read_csv(f)
    t_years = df['day'] / 365.25+2020
    for ax, (col, label, color) in zip(axes, species):
        ax.plot(t_years, df[col], color=color, alpha=0.5, linewidth=0.8)

for ax, (col, label, color) in zip(axes, species):
    ax.set_ylabel('Count')
    ax.set_title(label)
    ax.legend(fontsize=7, ncol=5)

axes[-1].set_xlabel('Year')
plt.suptitle('LEO population 2020 — individual seeds', y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(data_dir, 'mocat_individual_seeds.png'), dpi=150, bbox_inches='tight')
plt.show()