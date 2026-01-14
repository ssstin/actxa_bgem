import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

# --------------------------------------------------
# 1. Parkes Error Grid Polygons (mg/dL)
# --------------------------------------------------
def get_parkes_polygons_mgdl(diabetes_type='type 2'):
    """Original coordinates in mg/dL as per clinical standards."""
    diabetes_type = diabetes_type.lower()

    if diabetes_type == 'type 1':
        return {
            'B_upp': [(0,50),(30,50),(140,170),(280,380),(430,550),(260,550),
                      (70,110),(50,80),(30,60),(0,60),(0,50)],
            'B_low': [(50,0),(50,30),(170,145),(385,300),(550,450),(550,250),
                      (260,130),(120,30),(120,0),(50,0)],
            'C_upp': [(0,60),(30,60),(50,80),(70,110),(260,550),(125,550),
                      (80,215),(50,125),(25,100),(0,100),(0,60)],
            'C_low': [(120,0),(120,30),(260,130),(550,250),(550,150),
                      (250,40),(250,0),(120,0)],
            'D_upp': [(0,100),(25,100),(50,125),(80,215),(125,550),(50,550),
                      (35,155),(0,150),(0,100)],
            'D_low': [(250,0),(250,40),(550,150),(550,0),(250,0)],
            'E_upp': [(0,150),(35,155),(50,550),(0,550),(0,150)]
        }

    return {
        'B_upp': [(0,50),(30,50),(230,330),(440,550),(280,550),
                  (30,60),(0,60),(0,50)],
        'B_low': [(50,0),(50,30),(90,80),(330,230),(550,450),(550,250),
                  (260,130),(90,0),(50,0)],
        'C_upp': [(0,60),(30,60),(280,550),(125,550),
                  (35,90),(25,80),(0,80),(0,60)],
        'C_low': [(90,0),(260,130),(550,250),(550,160),
                  (410,110),(250,40),(250,0),(90,0)],
        'D_upp': [(0,80),(25,80),(35,90),(125,550),(50,550),
                  (35,200),(0,200),(0,80)],
        'D_low': [(250,0),(250,40),(410,110),(550,160),
                  (550,0),(250,0)],
        'E_upp': [(0,200),(35,200),(50,550),(0,550),(0,200)]
    }

# --------------------------------------------------
# 2. Parkes Error Grid Polygons (mmol/L)
# --------------------------------------------------
def get_parkes_polygons_mmol(diabetes_type='type 2'):
    """Pre-scaled coordinates for mmol/L grids."""
    mg_polys = get_parkes_polygons_mgdl(diabetes_type)
    scale = 1 / 18.0182
    
    mmol_polys = {}
    for key, coords in mg_polys.items():
        mmol_polys[key] = [(x * scale, y * scale) for x, y in coords]
    return mmol_polys

# --------------------------------------------------
# 3. Zone Classification (BOUNDARY-SAFE)
# --------------------------------------------------
def classify_parkes_zone(ref_val, pred_val, diabetes_type='type 2', unit='mg/dL'):
    """Classifies the result point into clinical risk zones."""
    if unit.lower() == 'mmol/l':
        ref_val *= 18.0182
        pred_val *= 18.0182

    zones = get_parkes_polygons_mgdl(diabetes_type)
    priority = ['E_upp', 'D_low', 'D_upp', 'C_low', 'C_upp', 'B_low', 'B_upp']

    for key in priority:
        coords = zones[key]
        path = Path(coords)

        # Buffer logic to handle line-boundary detection
        if 'low' in key:
            inside = path.contains_point((ref_val, pred_val), radius=-1e-6)
        else:
            inside = path.contains_point((ref_val, pred_val), radius=+1e-6)

        if inside:
            return key.split('_')[0].upper()

    return 'A'

# --------------------------------------------------
# 4. Label Positions (mg/dL Space)
# --------------------------------------------------
def get_zone_label_positions(diabetes_type='type 2'):
    """Returns canonical label positions for both Type 1 and Type 2 grids."""
    return [
        ('A', 325, 400), ('A', 400, 350), ('B', 270, 470), ('B', 470, 320),
        ('C', 170, 500), ('C', 500, 170), ('D', 80, 500),  ('D', 500, 80),
        ('E', 20, 500),
    ]

# --------------------------------------------------
# 5. Main Plotting Function
# --------------------------------------------------
def plot_parkes_grid(ref_val, pred_val, diabetes_type='type 2', unit='mg/dL'):
    """Generates the figure with unit-specific scaling and axis formatting."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # Determine scale and coordinate set
    is_mmol = unit.lower() == 'mmol/l'
    scale = 1 / 18.0182 if is_mmol else 1.0
    max_val = 550 * scale

    if is_mmol:
        zones = get_parkes_polygons_mmol(diabetes_type)
        ticks = np.arange(0, 35, 5)
        ax.set_xlabel("Reference Concentration (mmol/L)")
        ax.set_ylabel("Prediction Concentration (mmol/L)")
    else:
        zones = get_parkes_polygons_mgdl(diabetes_type)
        ticks = np.arange(0, 551, 50)
        ax.set_xlabel("Reference Concentration (mg/dL)")
        ax.set_ylabel("Prediction Concentration (mg/dL)")

    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_aspect('equal')

    # Draw Polygons
    for coords in zones.values():
        path = Path(coords)
        patch = patches.PathPatch(path, facecolor='none', edgecolor='black', lw=1.2, ls=':')
        ax.add_patch(patch)

    # Reference Identity Line
    ax.plot([0, max_val], [0, max_val], '--', color='black', lw=1.5, alpha=0.5)

    # Plot User Data Point
    ax.scatter(ref_val, pred_val, s=30, color='yellowgreen', edgecolors='black', zorder=10)

    # Scale and Draw Zone Labels
    label_positions = get_zone_label_positions(diabetes_type)
    for zone, x, y in label_positions:
        ax.annotate(zone, xy=(x * scale, y * scale), fontsize=15, fontweight='bold', 
                    ha='center', va='center', alpha=0.5)

    ax.set_title(f"Parkes Error Grid ({diabetes_type.title()} Diabetes)")

    return fig