import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load Python results
py = np.load('python_ensemble.npy', allow_pickle=True).item()
py_years = py['years']

# Load MATLAB results - update path to where your CSVs were saved
matlab = pd.read_csv('/Users/dchen/Documents/GitHub/MOCAT-MC/matlab_ensemble_stats.csv',
                     header=None, names=['day', 'mean', 'std', 'p5', 'p95'])
matlab_years = 2020 + matlab['day'].values / 365.25

fig, axes = plt.subplots(2, 1, figsize=(12, 10))

# Top: overlay means and bands
ax = axes[0]
ax.plot(matlab_years, matlab['mean'], 'k-', linewidth=2, label='MATLAB mean')
ax.fill_between(matlab_years, matlab['p5'], matlab['p95'],
                color='gray', alpha=0.3, label='MATLAB 5-95%')
ax.plot(py_years, py['N_mean'], 'g-', linewidth=2, label='Python mean')
ax.fill_between(py_years, py['N_p5'], py['N_p95'],
                color='green', alpha=0.2, label='Python 5-95%')
ax.set_ylabel('Debris Count (shell-binned)')
ax.set_title('Python vs MATLAB Ensemble — Debris (N)')
ax.legend()
ax.grid(True)

# Bottom: percentage difference of means
ax = axes[1]
matlab_interp = np.interp(py_years, matlab_years, matlab['mean'].values)
pct_diff = 100 * (py['N_mean'] - matlab_interp) / matlab_interp
ax.plot(py_years, pct_diff, 'b-', linewidth=1.5)
ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.fill_between(py_years, -20, 20, color='green', alpha=0.1, label='±20% band')
ax.set_xlabel('Year')
ax.set_ylabel('% difference')
ax.set_title('Percentage Difference of Ensemble Means (Python - MATLAB) / MATLAB')
ax.legend()
ax.grid(True)
ax.set_ylim(-100, 100)

plt.tight_layout()
plt.savefig('python_vs_matlab_verification.png', dpi=150)
plt.show()

print('=== VERIFICATION SUMMARY ===')
print(f'Python mean debris at 2120: {py["N_mean"][-1]:.0f}')
print(f'MATLAB mean debris at 2120: {matlab_interp[-1]:.0f}')
print(f'% difference at 2120: {pct_diff[-1]:.1f}%')
print(f'Mean absolute % difference: {np.abs(pct_diff).mean():.1f}%')
print(f'Max % difference: {np.abs(pct_diff).max():.1f}%')
