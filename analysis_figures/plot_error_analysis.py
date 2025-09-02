#!/usr/bin/env python3
"""
Create Error Analysis plots: Box plots and heatmap for Python vs MATLAB accuracy
"""

import numpy as np
import matplotlib.pyplot as plt
import json

def load_error_data():
    """Load the calculated error data"""
    with open('../comparison_tests/accuracy_error_data.json', 'r') as f:
        return json.load(f)

def create_error_box_plots():
    """Create box plots showing relative error distributions"""
    
    error_data = load_error_data()
    
    # Relative errors (%)
    satellite_rel_errors = [d['satellite_rel_error'] for d in error_data]
    derelict_rel_errors = [d['derelict_rel_error'] for d in error_data]
    debris_rel_errors = [d['debris_rel_error'] for d in error_data]
    rb_rel_errors = [d['rocket_body_rel_error'] for d in error_data]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Box plot: Relative errors
    rel_data = [satellite_rel_errors, derelict_rel_errors, debris_rel_errors, rb_rel_errors]
    rel_labels = ['Active Satellites', 'Derelicts', 'Debris', 'Rocket\nBodies']
    
    bp = ax.boxplot(rel_data, tick_labels=rel_labels, patch_artist=True,
                    #0173B2', alpha=0.7),  # Colorblind-friendly blue
                    boxprops=dict(facecolor='
                    #DE8F05', linewidth=2))  # Colorblind-friendly orange
                    medianprops=dict(color='
    
    ax.set_title('Relative Error Distribution', fontsize=24, fontweight='bold')
    ax.set_ylabel('Relative Error (%)', fontsize=20)
    ax.tick_params(axis='x', labelsize=18)  # Increase x-axis label font size
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0, top=2.6)
    
    # Add value annotations
    for i, data in enumerate(rel_data):
        max_val = max(data)
        mean_val = np.mean(data)
        
        # Position Mean annotation above the maximum whisker/outlier
        ax.text(i+1, max_val + 0.1, f'Mean: {mean_val:.2f}%', ha='center', va='bottom', 
                fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(
        '../paper/figures/error_box_plots.png',
        dpi=300,
        bbox_inches='tight')
    plt.show()
    
    print("Error box plots created: ../paper/figures/error_box_plots.png")


if __name__ == "__main__":
    print("Creating relative error box plot...")
    create_error_box_plots()
    print("Error analysis complete!")