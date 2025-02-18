import pandas as pd
import numpy as np
import os
import argparse
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

# Style definitions
STYLES = {
    'bw': {
        'toroid': {'facecolor': '#E0E0E0', 'edgecolor': 'black', 'alpha': 0.3},
        'wire': {'facecolor': 'white', 'edgecolor': 'black', 'linewidth': 1.0},
        'effective': {'color': '#808080', 'alpha': 0.2, 'linestyle': '--'},
        'text': {
            'outer_diameter': {
                'fontsize': 12,
                'color': 'black',
                'fontweight': 'normal',
                'horizontalalignment': 'center',
                'verticalalignment': 'bottom',
                'offset': 0.1
            },
            'inner_diameter': {
                'fontsize': 12,
                'color': 'black',
                'fontweight': 'normal',
                'horizontalalignment': 'center',
                'verticalalignment': 'top',
                'offset': -0.15
            },
            'turns_count': {
                'fontsize': 14,
                'color': 'black',
                'fontweight': 'bold',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
                'offset': 0
            },
            'title': {
                'fontsize': 14,
                'color': 'black', 
                'fontweight': 'bold',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
                'offset': 0.2
            }
        }
    },
    'color': {
        'toroid': {'facecolor': '#E6E6FA', 'edgecolor': '#4B0082', 'alpha': 0.3},
        'wire': {'facecolor': '#4682B4', 'edgecolor': '#27408B', 'linewidth': 0.5},
        'effective': {'color': '#8B4513', 'alpha': 0.2, 'linestyle': '--'},
        'text': {
            'outer_diameter': {
                'fontsize': 12,
                'color': '#4B0082',
                'fontweight': 'normal',
                'horizontalalignment': 'center',
                'verticalalignment': 'bottom',
                'offset': 0.1
            },
            'inner_diameter': {
                'fontsize': 12,
                'color': '#4B0082',
                'fontweight': 'normal',
                'horizontalalignment': 'center',
                'verticalalignment': 'top',
                'offset': -0.15
            },
            'turns_count': {
                'fontsize': 14,
                'color': '#27408B',
                'fontweight': 'bold',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
                'offset': 0
            },
            'title': {
                'fontsize': 14,
                'color': '#27408B',
                'fontweight': 'bold',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
                'offset': 0.1
            }
        }
    },
    'creative': {
        'toroid': {'facecolor': '#FFB6C1', 'edgecolor': '#FF69B4', 'alpha': 0.5},
        'wire': {'facecolor': '#98FB98', 'edgecolor': '#32CD32', 'linewidth': 0.8},
        'effective': {'color': '#87CEEB', 'alpha': 0.3, 'linestyle': '-.'},
        'text': {
            'outer_diameter': {
                'fontsize': 12,
                'color': 'black',
                'fontweight': 'normal',
                'horizontalalignment': 'center',
                'verticalalignment': 'bottom',
                'offset': 0.1
            },
            'inner_diameter': {
                'fontsize': 12,
                'color': 'black',
                'fontweight': 'normal',
                'horizontalalignment': 'center',
                'verticalalignment': 'top',
                'offset': -0.15
            },
            'turns_count': {
                'fontsize': 14,
                'color': 'black',
                'fontweight': 'bold',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
                'offset': 0
            },
            'title': {
                'fontsize': 14,
                'color': 'black',
                'fontweight': 'bold',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
                'offset': 0.1
            }
        }
    }
}

def load_wire_data(wire_file):
    try:
        if Path(wire_file).suffix == '.ods':
            wire_data = pd.read_excel(wire_file, engine='odf')
        else:
            wire_data = pd.read_csv(wire_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The wire data file '{wire_file}' was not found.")
    except Exception as e:
        raise ValueError(f"Error reading wire file '{wire_file}': {str(e)}")
    
    return wire_data

def load_standard_toroid_data(toroid_file):
    try:
        if Path(toroid_file).suffix == '.ods':
            toroid_data = pd.read_excel(toroid_file, engine='odf')
        else:
            toroid_data = pd.read_csv(toroid_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The toroid data file '{toroid_file}' was not found.")
    except Exception as e:
        raise ValueError(f"Error reading toroid file '{toroid_file}': {str(e)}")
    return toroid_data

def load_maginc_toroid_data(maginc_file):
    print(f"\nAttempting to load Mag-Inc file: {maginc_file}")
    print(f"File exists: {os.path.exists(maginc_file)}")
    
    try:
        if Path(maginc_file).suffix == '.ods':
            print("Reading as ODS file...")
            data = pd.read_excel(maginc_file, engine='odf')
        else:
            print("Reading as CSV file...")
            data = pd.read_csv(maginc_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The Mag Inc toroid file '{maginc_file}' was not found.")
    except Exception as e:
        print(f"Error details: {str(e)}")
        raise ValueError(f"Error reading Mag Inc file '{maginc_file}': {str(e)}")
    
    # List of permeability columns
    mu_columns = ['14u', '19u', '26u', '40u', '60u', '75u', '90u', '125u']
    
    # Print debug information about the raw data
    print("\nMag-Inc Toroid Data Summary:")
    print(f"Number of base cores: {len(data)}")
    print("\nColumns found:", data.columns.tolist())
    print("\nFirst few rows of raw data:")
    print(data.head())
    
    # Create expanded dataframe
    expanded_data = []
    for _, row in data.iterrows():
        for mu_col in mu_columns:
            if pd.notna(row[mu_col]):  # Only process non-None AL values
                expanded_row = {
                    'PN': f"{row['Core Data']}-{mu_col}",  # Append permeability to part number
                    'OD': row['OD'],
                    'ID': row['ID'],
                    'Height': row['HT'],
                    'AL': row[mu_col]
                }
                expanded_data.append(expanded_row)
    
    result_df = pd.DataFrame(expanded_data)
    
    # Convert mm to inches
    MM_TO_INCHES = 0.0393701
    result_df['OD'] = result_df['OD'] * MM_TO_INCHES
    result_df['ID'] = result_df['ID'] * MM_TO_INCHES
    result_df['Height'] = result_df['Height'] * MM_TO_INCHES
    
    # Print debug information about the processed data
    print("\nProcessed Mag-Inc Data Summary (dimensions converted to inches):")
    print(f"Number of expanded cores: {len(result_df)}")
    print("\nFirst few rows of processed data:")
    print(result_df.head())
    print("\nColumns in processed data:", result_df.columns.tolist())
    
    return result_df

def compute_parameters(toroid_data, wire_data, slop_factor):
    results = []
    for _, toroid in toroid_data.iterrows():
        for _, wire in wire_data.iterrows():
            effective_diameter = wire['Nom.'] * (1 + slop_factor)
            # Adjust circumferences by wire diameter
            adjusted_inner_circumference = np.pi * (toroid['ID'] - effective_diameter)
            adjusted_outer_circumference = np.pi * (toroid['OD'] + effective_diameter)
            # Use the smaller circumference to determine max turns
            turns = int(min(adjusted_inner_circumference, adjusted_outer_circumference) // effective_diameter)

            if turns < 1:
                continue

            # Calculate inductance in μH (AL is in nH/turn^2)
            inductance = (toroid['AL'] * turns * turns) / 1000
            
            # Calculate fill factor
            window_area = np.pi * (toroid['ID']/2)**2
            copper_area = np.pi * (wire['Nom.']/2)**2 * turns
            fill_factor = copper_area / window_area
            
            results.append({
                'PN': toroid['PN'],
                'OD': toroid['OD'],
                'ID': toroid['ID'],
                'Height': toroid['Height'],
                'AWG': wire['AWG'],
                'Min Diameter': wire['Min'],
                'Nominal Diameter': wire['Nom.'],
                'Max Diameter': wire['Max'],
                'Effective Diameter': effective_diameter,
                'Turns': turns,
                'AL': toroid['AL'],
                'Inductance': inductance,
                'Fill Factor': fill_factor,
            })
    return pd.DataFrame(results)

def generate_diagram(toroid, wire, turns, output_dir, slop_factor, style='color'):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=600)
    
    # Center point and scale factor
    center = (0.5, 0.5)
    scale = 1.0 / toroid['OD']  # Scale to fit in 1x1 box
    
    # Get style configuration
    style_config = STYLES[style]
    
    # Draw the toroid outer and inner circles
    outer_radius = (toroid['OD'] * scale) / 2
    inner_radius = (toroid['ID'] * scale) / 2
    
    # Outer circle
    outer_circle = plt.Circle(center, outer_radius, color=style_config['toroid']['edgecolor'], fill=False)
    ax.add_artist(outer_circle)
    
    # Inner circle
    inner_circle = plt.Circle(center, inner_radius, color=style_config['toroid']['edgecolor'], fill=False)
    ax.add_artist(inner_circle)
    
    # Fill the toroid area
    toroid_patch = plt.Circle(center, outer_radius, 
                            facecolor=style_config['toroid']['facecolor'],
                            edgecolor=style_config['toroid']['edgecolor'],
                            alpha=style_config['toroid']['alpha'])
    inner_patch = plt.Circle(center, inner_radius, color='white')
    ax.add_artist(toroid_patch)
    ax.add_artist(inner_patch)

    # Draw wire turns
    wire_radius = (wire['Nominal Diameter'] * scale) / 2
    effective_diameter = wire['Nominal Diameter'] * (1 + slop_factor)
    
    # Inner ring
    inner_ring_radius = inner_radius - (effective_diameter * scale / 2)
    for i in range(turns):
        angle = 2 * np.pi * i / turns
        x = center[0] + inner_ring_radius * np.cos(angle)
        y = center[1] + inner_ring_radius * np.sin(angle)
        # Draw the wire
        ax.add_artist(plt.Circle((x, y), wire_radius, 
                               facecolor=style_config['wire']['facecolor'],
                               edgecolor=style_config['wire']['edgecolor'],
                               linewidth=style_config['wire']['linewidth']))
        # Draw the effective diameter circle
        ax.add_artist(plt.Circle((x, y), effective_diameter * scale / 2,
                               color=style_config['effective']['color'],
                               fill=False,
                               alpha=style_config['effective']['alpha'],
                               linestyle=style_config['effective']['linestyle'],
                               linewidth=0.5))
    
    # Outer ring
    outer_ring_radius = outer_radius + (effective_diameter * scale / 2)
    for i in range(turns):
        angle = 2 * np.pi * i / turns
        x = center[0] + outer_ring_radius * np.cos(angle)
        y = center[1] + outer_ring_radius * np.sin(angle)
        # Draw the wire
        ax.add_artist(plt.Circle((x, y), wire_radius,
                               facecolor=style_config['wire']['facecolor'],
                               edgecolor=style_config['wire']['edgecolor'],
                               linewidth=style_config['wire']['linewidth']))
        # Draw the effective diameter circle
        ax.add_artist(plt.Circle((x, y), effective_diameter * scale / 2,
                               color=style_config['effective']['color'],
                               fill=False,
                               alpha=style_config['effective']['alpha'],
                               linestyle=style_config['effective']['linestyle'],
                               linewidth=0.5))

    # Add labels for OD and ID using styles
    plt.text(center[0], 
             center[1] + outer_radius + style_config['text']['outer_diameter']['offset'],
             f'OD = {toroid["OD"]:.2f} in',  # No change needed, already correct
             **{k: v for k, v in style_config['text']['outer_diameter'].items() if k != 'offset'})
    
    plt.text(center[0],
             center[1] + inner_radius + style_config['text']['inner_diameter']['offset'],
             f'ID = {toroid["ID"]:.2f} in',  # No change needed, already correct
             **{k: v for k, v in style_config['text']['inner_diameter'].items() if k != 'offset'})
    
    # Add title at top using styles
    plt.text(center[0],
             center[1] + outer_radius + style_config['text']['title']['offset'],
             f'Core {toroid["PN"]} - {int(wire["AWG"])} AWG',
             **{k: v for k, v in style_config['text']['title'].items() if k != 'offset'})

    # Add turns count in center using styles
    plt.text(center[0],
             center[1] + style_config['text']['turns_count']['offset'],
             f'N = {turns}',
             **{k: v for k, v in style_config['text']['turns_count'].items() if k != 'offset'})

    # Set plot limits with some padding
    padding = 0.15
    ax.set_xlim(center[0] - outer_radius - padding, center[0] + outer_radius + padding)
    ax.set_ylim(center[1] - outer_radius - padding, center[1] + outer_radius + padding)
    ax.set_aspect('equal')
    ax.axis('off')

    file_name = f"{toroid['PN']}_AWG{int(wire['AWG'])}.png"
    file_path = os.path.join(output_dir, 'images', file_name)
    plt.savefig(file_path)
    plt.close()

def clear_output_dir(output_dir):
    if os.path.exists(output_dir):
        print(f"Warning: Clearing existing contents in '{output_dir}'...")
        # First remove all files
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        
        # Then remove all directories from deepest first
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        
        # Finally remove the output dir itself
        if os.path.exists(output_dir):
            os.rmdir(output_dir)
    
    # Create fresh directories
    os.makedirs(output_dir)
    os.makedirs(os.path.join(output_dir, 'images'))

def main():
    parser = argparse.ArgumentParser(description="Single Layer Toroid Universe Tool")
    parser.add_argument('--slop_factor', type=float, default=0.02, help="Slop factor for wire diameter")
    parser.add_argument('--output_dir', default='output', help="Directory to save output files")
    parser.add_argument('--style', default='color', choices=['bw', 'color', 'creative'],
                      help="Style to use for the diagrams (default: color)")
    parser.add_argument('--generate-plots', action='store_true',
                      help="Generate visualization plots (default: False)")
    args = parser.parse_args()

    toroid_file = './toroid_cores_dimensions_01152025.ods'
    maginc_toroid_file = './kool_mu_cores.ods'  # Updated filename
    wire_file = './round_magnet_wire_dimensions_mws_01152025.ods'

    # Validate file paths
    if not os.path.isfile(toroid_file):
        raise FileNotFoundError(f"The toroid file '{toroid_file}' does not exist or is not a file.")
    if not os.path.isfile(maginc_toroid_file):
        raise FileNotFoundError(f"The Mag Inc toroid file '{maginc_toroid_file}' does not exist or is not a file.")
    if not os.path.isfile(wire_file):
        raise FileNotFoundError(f"The wire file '{wire_file}' does not exist or is not a file.")

    clear_output_dir(args.output_dir)

    # Load all data
    wire_data = load_wire_data(wire_file)
    standard_toroid_data = load_standard_toroid_data(toroid_file)
    maginc_toroid_data = load_maginc_toroid_data(maginc_toroid_file)
    
    # Combine toroid data
    all_toroid_data = pd.concat([standard_toroid_data, maginc_toroid_data], ignore_index=True)
    
    # Compute parameters for all combinations
    results = compute_parameters(all_toroid_data, wire_data, args.slop_factor)

    # Save results table
    results.to_csv(os.path.join(args.output_dir, 'master_table.csv'), index=False)
    print(f"Results saved to {args.output_dir}. Total configurations processed: {len(results)}")

    # Generate plots if requested
    if args.generate_plots:
        print("\nGenerating visualization plots...")
        for _, row in tqdm(results.iterrows(), total=len(results), desc="Generating plots"):
            generate_diagram(row, row, row['Turns'], args.output_dir, args.slop_factor, args.style)

if __name__ == "__main__":
    main()
