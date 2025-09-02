#!/usr/bin/env python3
"""
Create Execution Time comparison plot
"""

import numpy as np
import matplotlib.pyplot as plt

def plot_execution_time():
    """Create bar chart comparing execution times between Python and MATLAB"""
    
    # Data - Real benchmark results
    scenarios = ['Basic\nPropagation', 'Collision\nTest', \
        'Atmospheric\nDrag', 'Full\nDefault', 'Realistic Ops\nNo Launch']
    python_times = [1.67, 0.10, 0.09, 1.02, 29.95]  # Python results
    # MATLAB results from actual benchmarks
    matlab_times = [1.09, 0.41, 0.25, 2.16, 75.0]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Bar chart setup
    x = np.arange(len(scenarios))
    width = 0.35
    
    # Colorblind-friendly colors: blue and orange
    bars1 = ax.bar(x - width/2, python_times, width, label='Python', color='#0173B2', alpha=0.8)
    bars2 = ax.bar(x + width/2, matlab_times, width, label='MATLAB', color='#DE8F05', alpha=0.8)
    
    # Formatting
    ax.set_title(
        'Execution Time Comparison',
        fontsize=24,
        fontweight='bold',
        pad=20)
    ax.set_ylabel('Time (seconds, log scale)', fontsize=20)
    ax.set_xlabel('Test Scenarios', fontsize=20)
    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=18)
    ax.legend(fontsize=18)
    ax.grid(True, alpha=0.3)
    
    # Set y-axis limits
    ax.set_ylim(bottom=0.01, top=350)
    
    # Add time values on bars
    for i, (py, mat) in enumerate(zip(python_times, matlab_times)):
        # Python bars
        ax.text(i - width/2, py * 1.1, f'{py:.2f}s', ha='center', va='bottom',
                fontsize=16, color='#004B87')  # Darker blue
        # MATLAB bars
        ax.text(i + width/2, mat * 1.1, f'{mat:.1f}s', ha='center', va='bottom',
                fontsize=16, color='#B07C0A')  # Darker orange
    
    # Add speedup factors
    for i, (py, mat) in enumerate(zip(python_times, matlab_times)):
        speedup = mat / py
        y_pos = max(py, mat) * 2
        
        # Color box orange if MATLAB is faster (speedup < 1), blue if Python is faster
        if speedup < 1:
            color = '#B07C0A'  # Darker orange
            facecolor = '#FDBF6F'  # Light orange
        else:
            color = '#004B87'  # Darker blue
            facecolor = '#A1C8E9'  # Light blue
            
        ax.annotate(f'{speedup:.1f}x', xy=(i, y_pos), ha='center', va='bottom',
                   color=color, fontweight='bold', fontsize=18,
                   bbox=dict(
                       boxstyle="round,pad=0.3",
                       facecolor=facecolor,
                       alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(
        '../paper/figures/execution_time_comparison.png',
        dpi=300,
        bbox_inches='tight')
    plt.close()
    
    print("Execution Time Comparison plot created: ../paper/figures/execution_time_comparison.png")

if __name__ == "__main__":
    plot_execution_time()