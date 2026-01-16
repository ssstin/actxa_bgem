import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np

# --------------------------------------------------
# 1. Parkes Error Grid Polygons (mg/dL)
# --------------------------------------------------
def get_parkes_polygons_mgdl(diabetes_type='type 2'):
    diabetes_type = diabetes_type.lower()
    if diabetes_type == 'type 1':
        return {
            'B_upp': [(0,50),(30,50),(140,170),(280,380),(430,550),(260,550),(70,110),(50,80),(30,60),(0,60),(0,50)],
            'B_low': [(50,0),(50,30),(170,145),(385,300),(550,450),(550,250),(260,130),(120,30),(120,0),(50,0)],
            'C_upp': [(0,60),(30,60),(50,80),(70,110),(260,550),(125,550),(80,215),(50,125),(25,100),(0,100),(0,60)],
            'C_low': [(120,0),(120,30),(260,130),(550,250),(550,150),(250,40),(250,0),(120,0)],
            'D_upp': [(0,100),(25,100),(50,125),(80,215),(125,550),(50,550),(35,155),(0,150),(0,100)],
            'D_low': [(250,0),(250,40),(550,150),(550,0),(250,0)],
            'E_upp': [(0,150),(35,155),(50,550),(0,550),(0,150)]
        }
    return {
        'B_upp': [(0,50),(30,50),(230,330),(440,550),(280,550),(30,60),(0,60),(0,50)],
        'B_low': [(50,0),(50,30),(90,80),(330,230),(550,450),(550,250),(260,130),(90,0),(50,0)],
        'C_upp': [(0,60),(30,60),(280,550),(125,550),(35,90),(25,80),(0,80),(0,60)],
        'C_low': [(90,0),(260,130),(550,250),(550,160),(410,110),(250,40),(250,0),(90,0)],
        'D_upp': [(0,80),(25,80),(35,90),(125,550),(50,550),(35,200),(0,200),(0,80)],
        'D_low': [(250,0),(250,40),(410,110),(550,160),(550,0),(250,0)],
        'E_upp': [(0,200),(35,200),(50,550),(0,550),(0,200)]
    }

# --------------------------------------------------
# 2. Parkes Error Grid Polygons (mmol/L)
# --------------------------------------------------
def get_parkes_polygons_mmol(diabetes_type='type 2'):
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
    if unit.lower() == 'mmol/l':
        ref_val *= 18.0182
        pred_val *= 18.0182
    zones = get_parkes_polygons_mgdl(diabetes_type)
    priority = ['E_upp', 'D_low', 'D_upp', 'C_low', 'C_upp', 'B_low', 'B_upp']
    for key in priority:
        path = Path(zones[key])
        radius = -1e-6 if 'low' in key else 1e-6
        if path.contains_point((ref_val, pred_val), radius=radius):
            return key.split('_')[0].upper()
    return 'A'

# --------------------------------------------------
# 4. Label Positions (mg/dL Space)
# --------------------------------------------------
def get_zone_label_positions(diabetes_type='type 2'):
    return [('A', 325, 400), ('A', 400, 350), ('B', 270, 470), ('B', 470, 320),
            ('C', 170, 500), ('C', 500, 170), ('D', 80, 500), ('D', 500, 80), ('E', 20, 500)]

# --------------------------------------------------
# 5. Error Metrics Calculation
# --------------------------------------------------
def get_icgm_evaluation(ref_val, pred_val, unit='mg/dL'):
    """Identifies the iCGM condition and evaluates the result."""
    is_mmol = unit.lower() == 'mmol/l'
    low_limit = 70.0 if not is_mmol else 3.88
    high_limit = 180.0 if not is_mmol else 10.0
    
    abs_diff = abs(pred_val - ref_val)
    rel_error = (abs_diff / ref_val * 100) if ref_val > 0 else 0
    
    # Identify the specific condition range
    if ref_val < low_limit:
        range_label = f": <70 {unit})"
        threshold_text = f"±15 {unit}"
        is_valid = abs_diff <= (15.0 if not is_mmol else 0.83)
    elif low_limit <= ref_val <= high_limit:
        range_label = f": {low_limit}-{high_limit} {unit})"
        threshold_text = "±15%"
        is_valid = rel_error <= 15.0
    else:
        range_label = f":>{high_limit} {unit})"
        threshold_text = "±15%"
        is_valid = rel_error <= 15.0
        
    return {
        "range": range_label,
        "criteria": threshold_text,
        "is_valid": is_valid,
        "rel_error": rel_error,
        "abs_diff": abs_diff
    }

# --------------------------------------------------
# 6. Main Plotting Function
# --------------------------------------------------
def plot_parkes_grid(ref_val, pred_val, diabetes_type='type 2', unit='mg/dL'):
    """Generates the figure with light background colors for all zones."""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    zone = classify_parkes_zone(ref_val, pred_val, diabetes_type, unit)
    point_color = 'yellowgreen' if zone in ['A', 'B'] else 'red'
    
    scale = 1 / 18.0182 if unit.lower() == 'mmol/l' else 1.0
    max_val = 550 * scale
    zones = get_parkes_polygons_mgdl(diabetes_type)

    # Draw the zones with light background colors
    grid_rect = patches.Rectangle((0, 0), max_val, max_val, 
                                facecolor='#f0f9eb', alpha=1.0, zorder=0)
    ax.add_patch(grid_rect)

    # Overlap other zones on top of the green background
    for key, coords in zones.items():
        scaled_coords = [(px * scale, py * scale) for px, py in coords]
        path = Path(scaled_coords)
        
        if key.startswith('B'):
            fill_color = '#f0f9eb'
        else:
            fill_color = '#fdf2f2' 
        
        # Add the colored patch
        patch = patches.PathPatch(path, facecolor=fill_color, edgecolor='none', 
                                alpha=1.0, zorder=1)
        ax.add_patch(patch)

    # Setup Grid & Axes
    ticks = np.arange(0, 35, 5) if unit.lower() == 'mmol/l' else np.arange(0, 551, 50)
    ax.set_xlim(0, max_val); ax.set_ylim(0, max_val)
    ax.set_xticks(ticks); ax.set_yticks(ticks)
    ax.set_aspect('equal')
    ax.set_xlabel(f"Reference Concentration ({unit})")
    ax.set_ylabel(f"Prediction Concentration ({unit})")

    # Draw Polygon Outlines (Dashed)
    for coords in zones.values():
        scaled_coords = [(px * scale, py * scale) for px, py in coords]
        ax.add_patch(patches.PathPatch(Path(scaled_coords), facecolor='none', 
                                        edgecolor='black', lw=0.8, ls=':', alpha=0.3))
    
    # Reference Identity Line
    ax.plot([0, max_val], [0, max_val], '--', color='black', lw=1.5, alpha=0.3)
    
    # Plot User Data Point
    ax.scatter(ref_val, pred_val, s=60, color=point_color, edgecolors='black', zorder=10)

    # Zone Labels
    label_positions = get_zone_label_positions(diabetes_type)
    for zone_lbl, x, y in label_positions:
        ax.annotate(zone_lbl, xy=(x * scale, y * scale), fontsize=14, 
                    fontweight='bold', ha='center', va='center', alpha=0.4)

    # BGEM Watermark 
    logo_path = "assets/BGEM-LogoFC.png"
    img = mpimg.imread(logo_path)
    imagebox = OffsetImage(img, zoom=0.02, alpha=0.6) 
    ab = AnnotationBbox(imagebox, (0.85, 0.08), xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)

    ax.set_title(f"Parkes Error Grid ({diabetes_type.title()} Diabetes)")
    return fig