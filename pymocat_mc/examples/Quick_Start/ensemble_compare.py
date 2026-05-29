from multiprocessing import Pool
from pymocat_mc import MOCATMC
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

IC_FILE = '/Users/dchen/Documents/GitHub/PyMOCAT-MC/pymocat_mc/supporting_data/TLEhistoric/2020.mat'
N_SEEDS = 100

def run_seed(seed):
    mocat = MOCATMC()
    cfg = mocat.setup_mc_config(seed, IC_FILE)
    nS, nD, nN, nB, _, history = mocat.main_mc(cfg, seed)
    return history

if __name__ == '__main__':
    print(f'Running {N_SEEDS} seeds...')
    with Pool(processes=13) as pool:
        results = pool.map(run_seed, range(1, N_SEEDS + 1))
    print('Done. Saving results...')

    years = results[0]['years']
    keys = ['S', 'D', 'N', 'B']

    # Save ensemble statistics
    stats = {'years': years}
    for key in keys:
        vals = np.array([r[key] for r in results])
        stats[f'{key}_mean'] = np.mean(vals, axis=0)
        stats[f'{key}_std'] = np.std(vals, axis=0)
        stats[f'{key}_p5'] = np.percentile(vals, 5, axis=0)
        stats[f'{key}_p95'] = np.percentile(vals, 95, axis=0)
        stats[f'{key}_all'] = vals

    np.save('python_ensemble.npy', stats)
    print('Saved python_ensemble.npy')

    # Plot
    labels = ['Active Satellites (S)', 'Derelicts (D)', 'Debris (N)', 'Rocket Bodies (B)']
    colors = ['blue', 'orange', 'green', 'red']

    fig, axes = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
    for ax, key, label, color in zip(axes, keys, labels, colors):
        vals = np.array([r[key] for r in results])
        for i in range(len(results)):
            ax.plot(years, vals[i], color=color, alpha=0.1, linewidth=0.5)
        ax.plot(years, stats[f'{key}_mean'], color=color, linewidth=2, label='Mean')
        ax.fill_between(years, stats[f'{key}_p5'], stats[f'{key}_p95'],
                        color=color, alpha=0.2, label='5-95%')
        ax.set_ylabel('Count')
        ax.set_title(label)
        ax.legend()
        ax.grid(True)

    axes[-1].set_xlabel('Year')
    fig.suptitle('LEO Population 2020 — Python 100-seed Ensemble', fontsize=14)
    plt.tight_layout()
    plt.savefig('python_ensemble_100seeds.png', dpi=150)
    print('Saved python_ensemble_100seeds.png')
