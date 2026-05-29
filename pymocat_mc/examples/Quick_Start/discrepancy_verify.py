from multiprocessing import Pool
from pymocat_mc import MOCATMC
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def run_seed(seed):
    mocat = MOCATMC()
    cfg = mocat.setup_mc_config(seed, '2020.mat')
    nS, nD, nN, nB, _, history = mocat.main_mc(cfg, seed)
    return history

if __name__ == '__main__':
    n_seeds = 10  # start with 10, increase later

    with Pool(processes=10) as pool:
        results = pool.map(run_seed, range(1, n_seeds + 1))

    fig, axes = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
    labels = ['Active Satellites (S)', 'Derelicts (D)', 'Debris (N)', 'Rocket Bodies (B)']
    keys = ['S', 'D', 'N', 'B']
    colors = ['blue', 'orange', 'green', 'red']

    for ax, key, label, color in zip(axes, keys, labels, colors):
        all_values = np.array([r[key] for r in results])
        years = results[0]['years']

        for i in range(len(results)):
            ax.plot(years, all_values[i], color=color, alpha=0.2, linewidth=0.8)

        mean = np.mean(all_values, axis=0)
        std = np.std(all_values, axis=0)
        ax.plot(years, mean, color=color, linewidth=2, label='Mean')
        ax.fill_between(years, mean - std, mean + std, color=color, alpha=0.3, label='±1σ')

        ax.set_ylabel('Count')
        ax.set_title(label)
        ax.legend()
        ax.grid(True)

    axes[-1].set_xlabel('Year')
    fig.suptitle('LEO Population 2020 — Individual Seeds', fontsize=14)
    plt.tight_layout()
    plt.savefig('ensemble.png')
    plt.show()