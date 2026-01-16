import streamlit as st
import base64
from utils import classify_parkes_zone, plot_parkes_grid, get_icgm_evaluation

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page config 
st.set_page_config(
    page_title="Actxa Parkes Error Grid Validation Tool",
    page_icon="assets/Actxa-Logo1C-2307.png",
    layout="wide"
)

local_css("assets/style.css")

# --------------------------------------------------
# Sidebar - Settings Only
# --------------------------------------------------
def get_image_base64(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

with st.sidebar:
    logo_path = "assets/Actxa-Logo1C-2307.png"
    logo_link = "https://www.actxa.com"
    
   
    base64_logo = get_image_base64(logo_path)
    st.markdown(
        f"""
        <div style="text-align: center;">
            <a href="{logo_link}" target="_blank">
                <img src="data:image/png;base64,{base64_logo}" style="width: 100%;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()
    st.header("Settings")
    diabetes_type = st.selectbox("Diabetes Type", ["Type 1", "Type 2"])
    unit = st.radio("Input Units", ["mg/dL", "mmol/L"])
    st.divider()
    st.caption("© 2026 Actxa. All rights reserved.")

# --------------------------------------------------
# Main Content
# --------------------------------------------------
st.title("Parkes Error Grid Analysis")

with st.expander("What is the Parkes Error Grid?", expanded=False):
    st.markdown("""
    The **Parkes (Consensus) Error Grid** is used to determine the clinical risk of errors in glucose monitoring.
    
    **How to use:**
    1.  Ensure the **Units** are correct in the sidebar.
    2.  Enter the **Reference** value (the 'ground truth' from a lab) and your **Predicted** value.
    3.  The tool will plot the point and tell you the clinical risk zone.
    
    **Why we use the Parkes Error Grid:**\n
    It provides a risk-based assessment of accuracy. Unlike simple percentage error, 
    it categorizes inaccuracies based on the likelihood they would lead to a dangerous clinical decision. 
    For a device to be considered safe, **99%** of results must be within **Zones A and B**. 
    
    **Zone Definitions:** 
    * **Zone A**: No effect on clinical action.
    * **Zone B**: Little or no effect on clinical outcome.
    * **Zone C**: Likely to affect clinical outcome.
    * **Zone D**: Significant medical risk.
    * **Zone E**: Dangerous consequences.
                
    **References & Standards:**
    * [ISO 15197:2013 Standard](https://mdcpp.com/doc/standard/ISO15197-2013(E).PDF)
    * [J.L. Parkes et al.: A New Consensus Error Grid](https://pmc.ncbi.nlm.nih.gov/articles/PMC3876371/) 
    """)

col_plot, col_controls = st.columns([2, 1], gap="large")

default_ref = 100.0 if unit == "mg/dL" else 5.5
default_pred = 110.0 if unit == "mg/dL" else 6.1

with col_controls:
    st.subheader("Manual Entry")
    with st.container(border=True):
        max_limit = 550.0 if unit == "mg/dL" else 30.55

        ref_val = st.number_input(
            f"Reference Value ({unit})",
            min_value=0.0,
            max_value=max_limit,  
            value=default_ref,
            format="%.2f",
            help="Reference ground truth from Glucometers and CGMs are generally less precise than lab analysis"        
        )

        pred_val = st.number_input(
            f"BGEM Value ({unit})",
            min_value=0.0,
            max_value=max_limit,  
            value=default_pred,
            format="%.2f",
            help=f"Value predicted by the BGEM model."
        )

    zone = classify_parkes_zone(ref_val, pred_val, diabetes_type.lower(), unit)
    evaluation = get_icgm_evaluation(ref_val, pred_val, unit)     

    st.markdown("---")
    
    icgm_help_text = (
        f"**Analytical Evaluation (Range {evaluation['range']})**\n\n"
        f"The iCGM precision target for this range is **{evaluation['criteria']}**. "
        f"Current relative error: **{evaluation['rel_error']:.2f}%**.\n\n"
    )

    if evaluation['is_valid']:
        icgm_help_text += "This result meets the required analytical precision."
    else:
        icgm_help_text += "This result does not meet the specific precision target for this range."

    st.markdown(f"### Clinical Risk Zone: **{zone}**", help=icgm_help_text)

    if zone in ["A", "B"]:
        result_message = (
            f"Zone {zone} results are acceptable under ISO 15197:2013, "
            "which mandates 99% of readings fall within Zones A and B. \n\n"
            # f"The prediction shows a relative error of **{evaluation['rel_error']:.2f}%**."
        )
        st.success(result_message)
    else:
        # Adjusted wording for outside acceptable range
        risk_message = (
            f"Zone {zone} is outside the acceptable range. "
            "ISO 15197:2013 requires 99% of readings to be in Zones A and B for patient safety. \n\n"
            # f"The prediction shows a relative error of **{evaluation['rel_error']:.2f}%**."

        )
        st.error(risk_message)

with col_plot:
    fig = plot_parkes_grid(ref_val, pred_val, diabetes_type.lower(), unit)
    st.pyplot(fig, width='stretch')

st.divider()