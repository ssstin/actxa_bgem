<div align="right">
  <img src="assets/Actxa-Logo1C-2307.png" width="160">
</div>

### Clinical Accuracy Analysis Powered by BGEM

This tool is developed by **Actxa** for users to validate the accuracy of our **BGEM (Blood Glucose Estimation Model)** against a reference reading. It utilises the **Parkes (Consensus) Error Grid** to classify the clinical significance of differences between estimated and reference values.

**Access the Webpage:** https://actxabgem.streamlit.app

---

## How to Use

1.  **Configure Settings**: In the left sidebar, select the **Diabetes Type** (Type 1 or 2) and **Input Units** (mg/dL or mmol/L).
2.  **Enter Data**: Use the **Manual Entry** section on the right to input your **Reference Value** and your **BGEM Value**.
3.  **Review Grid**: Your data point will plot automatically on the grid. 
4.  **Check Results**: The **Clinical Risk Zone** and its specific definition appear immediately below your entries.

---

## Clinical Zone Definitions
Zones are based on the original consensus defined by J.L. Parkes:

| Zone | Clinical Significance |
| :--- | :--- |
| **Zone A** | **No clinical risk.** Estimation leads to the same treatment decisions as reference. |
| **Zone B** | **Little or no clinical risk.** Minor errors with unlikely impact on treatment. |
| **Zone C** | **Likely to affect clinical action.** Errors may lead to unnecessary or incorrect treatment. |
| **Zone D** | **Significant medical risk.** Errors could lead to a failure to treat or dangerous treatment. |
| **Zone E** | **Dangerous consequences.** Leads to treatment opposite to what is required. |

**© 2026 Actxa. All rights reserved.**