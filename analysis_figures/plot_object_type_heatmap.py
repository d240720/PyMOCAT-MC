#!/usr/bin/env python3
"""
Create Object Type Percentage Difference Heatmap
"""

import numpy as np
import matplotlib.pyplot as plt
import json

def plot_object_type_heatmap():
    """Create heatmap showing percentage differences by object type"""
    
    # Read actual error data from the updated files
    with open('../comparison_tests/accuracy_error_data.json', 'r') as f:
        error_data = json.load(f)
    
    # Create percentage difference matrix from the actual error data
    scenarios = [item['scenario'] for item in error_data]
    scenario_names = scenarios
    scenarios_short = ['Basic\nProp', 'Collision\nTest', 'Atm\nDrag', \
        'Full\nDefault', 'Realistic Ops\nNo Launch']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Use actual error data from the JSON file
    object_types = ['satellite', 'derelict', 'debris', 'rocket_body']
    object_labels = ['Active Satellites', 'Derelicts', 'Debris', 'Rocket Bodies']
    pct_diff_matrix = []
    
    for obj_type in object_types:
        row = []
        for item in error_data:
            error_key = f'{obj_type}_rel_error'
            pct_error = item[error_key]
            row.append(pct_error)
        pct_diff_matrix.append(row)
    
    pct_diff_matrix = np.array(pct_diff_matrix)
    
    # Create heatmap (use Reds colormap for absolute values)
    im = ax.imshow(pct_diff_matrix, cmap='Reds', aspect='auto', vmin=0, vmax=3)
    
    # Set ticks and labels
    ax.set_xticks(range(len(scenario_names)))
    ax.set_xticklabels(scenarios_short, fontsize=18)
    ax.set_yticks(range(len(object_types)))
    ax.set_yticklabels(object_labels, fontsize=18)
    ax.set_xlabel('Test Scenarios', fontsize=20)
    ax.set_ylabel('Object Types', fontsize=20)
    ax.set_title('Object Type Percentage Difference Heatmap', 
                fontsize=24, fontweight='bold', pad=20)
    
    # Add text annotations  
    for i in range(len(object_types)):
        for j in range(len(scenario_names)):
            text_color = 'white' if pct_diff_matrix[i, j] > 1.5 else 'black'
            ax.text(j, i, f'{pct_diff_matrix[i, j]:.2f}%',
                   ha="center", va="center", color=text_color, 
                   fontweight='bold', fontsize=16)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, label='Absolute Percentage Difference (%)')
    cbar.ax.tick_params(labelsize=16)
    cbar.set_label('Absolute Percentage Difference (%)', fontsize=18)
    
    # Add grid for better readability
    ax.set_xticks(np.arange(len(scenario_names)+1)-.5, minor=True)
    ax.set_yticks(np.arange(len(object_types)+1)-.5, minor=True)
    ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", size=0)
    
    plt.tight_layout()
    plt.savefig(
        '../paper/figures/object_type_percentage_heatmap.png',
        dpi=300,
        bbox_inches='tight')
    plt.show()
    
    print("Object Type Percentage Difference Heatmap created: object_type_percentage_heatmap.png")

if __name__ == "__main__":
    plot_object_type_heatmap()