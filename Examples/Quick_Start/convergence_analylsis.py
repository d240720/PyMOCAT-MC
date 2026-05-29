import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

data_dir = '/Users/dchen/Documents/GitHub/MOCAT-MC'
ts_files = sorted(glob.glob(os.path.join(data_dir, 'timeseries_seed*.csv')))

dfs = []
for f in ts_files:
    seed = int(f.split('seed')[1].split('.')[0])
    df = pd.read_csv(f)
    df['seed'] = seed
    dfs.append(df)
ts = pd.concat(dfs, ignore_index=True)

# Use cumulative collisions and peak debris instead of final timestep
seeds_sorted = sorted(ts['seed'].unique())

metrics = {
    'final_debris':     lambda df: df.loc[df['day']==df['day'].max(), 'debris'].values[0],
    'peak_debris':      lambda df: df['debris'].max(),
    'total_collisions': lambda df: df['collisions'].sum(),
    'final_derelict':   lambda df: df.loc[df['day']==df['day'].max(), 'derelict'].values[0],
}

fig, axes = plt.subplots(len(metrics), 2, figsize=(12, 10), sharex=True)
ns = range(2, len(seeds_sorted)+1)

for row, (name, fn) in enumerate(metrics.items()):
    vals = [fn(ts[ts['seed']==s]) for s in seeds_sorted]
    
    running_mean = [np.mean(vals[:n]) for n in ns]
    running_std  = [np.std(vals[:n])  for n in ns]
    running_sem  = [np.std(vals[:n]) / np.sqrt(n) for n in ns]

    axes[row,0].plot(list(ns), running_mean, 'b')
    axes[row,0].fill_between(list(ns),
                              np.array(running_mean) - np.array(running_sem),
                              np.array(running_mean) + np.array(running_sem),
                              alpha=0.3)
    axes[row,0].set_ylabel(name)
    if row == 0:
        axes[row,0].set_title('Mean ± SEM')

    axes[row,1].plot(list(ns), running_std, 'r')
    axes[row,1].set_ylabel(name)
    if row == 0:
        axes[row,1].set_title('Standard deviation')

axes[-1,0].set_xlabel('Number of seeds')
axes[-1,1].set_xlabel('Number of seeds')
plt.suptitle('Convergence analysis — improved metrics', y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(data_dir, 'convergence_v2.png'), dpi=150, bbox_inches='tight')
plt.show()

# Print convergence table
print(f"\n{'Metric':<20} {'N=10 mean':>12} {'N=20 mean':>12} {'N=20 std':>12} {'N=20 CoV':>12}")
for name, fn in metrics.items():
    vals = [fn(ts[ts['seed']==s]) for s in seeds_sorted]
    m10 = np.mean(vals[:10])
    m20 = np.mean(vals[:20])
    s20 = np.std(vals[:20])
    cov = s20/m20 if m20 != 0 else float('nan')
    print(f"{name:<20} {m10:>12.1f} {m20:>12.1f} {s20:>12.1f} {cov:>12.3f}")