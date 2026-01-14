import streamlit as st
from utils import classify_parkes_zone, plot_parkes_grid

# Custom CSS to handle toolbar scrolling and UI refinements
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

# Page config with branding in the tab
st.set_page_config(
    page_title="Actxa Parkes Error Grid Validation Tool",
    page_icon="assets/Actxa-Logo1C-2307.png",
    layout="wide"
)

# --------------------------------------------------
# Sidebar - Clean Logo Placement & Branding
# --------------------------------------------------
with st.sidebar:
    st.image("assets/Actxa-Logo1C-2307.png", width='stretch')
    st.divider()
    
    st.header("Settings")
    diabetes_type = st.selectbox("Diabetes Type", ["Type 1", "Type 2"])
    unit = st.radio("Input Units", ["mg/dL", "mmol/L"])
    
    # Bottom branding (no excessive spacer to prevent scrolling)
    st.divider()
    st.caption("Powered by **BGEM**")
    st.image("assets/BGEM-LogoFC.png")

# --------------------------------------------------
# Main Header & Instructions
# --------------------------------------------------
st.title("Parkes Error Grid Analysis")

with st.expander("What is the Parkes Error Grid?", expanded=False):
    st.markdown("""
    The **Parkes (Consensus) Error Grid** is used to determine the clinical risk of errors in glucose monitoring.
    
    **How to use:**
    1.  Ensure your **Diabetes Type** and **Units** are correct in the sidebar.
    2.  Enter the **Reference** value (the 'ground truth' from a lab) and your **Predicted** value.
    3.  The tool will plot the point and tell you the clinical risk zone.
    
    **Zone Definitions:**
    * **Zone A**: No clinical risk.
    * **Zone B**: Little or no clinical risk.
    * **Zone C**: Likely to affect clinical action.
    * **Zone D**: Significant medical risk.
    * **Zone E**: Dangerous consequences.
    """)

# --------------------------------------------------
# Main Layout: Grid on Left, Inputs/Results on Right
# --------------------------------------------------
col_plot, col_controls = st.columns([1.5, 1], gap="large")

# Initialise default values based on unit
default_ref = 100.0 if unit == "mg/dL" else 5.5
default_pred = 110.0 if unit == "mg/dL" else 6.1

with col_controls:
    st.subheader("Manual Entry")
    with st.container(border=True):
        ref_val = st.number_input(
            f"Reference Value ({unit})",
            min_value=0.0,
            value=default_ref,
            format="%.2f",
            help="Reference ground truth from a lab method."
        )

        pred_val = st.number_input(
            f"BGEM Value ({unit})",
            min_value=0.0,
            value=default_pred,
            format="%.2f",
            help="Value predicted by the BGEM model."
        )

    # Processing Logic
    zone = classify_parkes_zone(
        ref_val, pred_val,
        diabetes_type=diabetes_type.lower(),
        unit=unit
    )

    # Analysis Results Section (Moved below entry)
    st.markdown("---")
    st.subheader("Analysis Results")
    
    st.metric(label="Clinical Risk Zone", value=f"Zone {zone}")
    
    desc = {
        "A": "No clinical risk.",
        "B": "Little or no clinical risk.",
        "C": "Likely to affect clinical action.",
        "D": "Significant medical risk.",
        "E": "Dangerous consequences."
    }
    
    # Styled Alert Boxes for feedback
    if zone == "A":
        st.success(f"**Zone {zone}**: {desc[zone]}")
    elif zone == "B":
        st.info(f"**Zone {zone}**: {desc[zone]}")
    elif zone == "C":
        st.warning(f"**Zone {zone}**: {desc[zone]}")
    else:
        st.error(f"**Zone {zone}**: {desc[zone]}")

with col_plot:
    # Generate and display the grid
    fig = plot_parkes_grid(
        ref_val, 
        pred_val, 
        diabetes_type=diabetes_type.lower(),
        unit=unit
    )
    st.pyplot(fig, width='stretch')

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
f1, f2 = st.columns([4, 1])
with f1:
    st.caption("© 2026 Actxa. All rights reserved.")