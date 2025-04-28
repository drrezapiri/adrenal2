import streamlit as st
import pandas as pd
# Set page configuration
st.set_page_config(
    page_title="Adrenal Mass Approach",
    page_icon="🩺",
    layout="wide"
)

# Title and credits
st.title("Adrenal Mass Approach")
st.caption("This app was developed by Peter Sommer Ulriksen and Reza Piri from Radiology Department in Rigshospitalet")

# Create three columns
col1, col2, col3 = st.columns(3)

# Column 1: Input Data
with col3:
    st.header("Final Conclusion")

    final_conclusion = ""

    if assess_button:
        try:
            size_value = float(mass_size) if mass_size else None
            non_contrast_val = float(non_contrast_hu) if non_contrast_hu else None
            venous_val = float(venous_phase_hu) if venous_phase_hu else None
            delayed_val = float(delayed_hu) if delayed_hu else None
            age_val = int(age) if age else None
        except:
            size_value = non_contrast_val = venous_val = delayed_val = age_val = None

        malignant_signs = []

        if venous_val is not None and non_contrast_val is not None:
            if venous_val - non_contrast_val > 10:
                malignant_signs.append("enhancement >10 HU")
        if venous_val is not None and non_contrast_val is None:
            if venous_val > 40:
                malignant_signs.append("venous HU >40 without non-contrast")
        if bilateral:
            malignant_signs.append("bilateral finding")
        if mass_dev == "Increased >5 mm/year":
            malignant_signs.append("growth >5 mm/year")
        if size_value is not None and size_value > 40:
            malignant_signs.append("size >4 cm")
        if heterogenicity == "Heterogen":
            malignant_signs.append("heterogenicity")
        if venous_val and delayed_val and non_contrast_val:
            try:
                abs_washout = ((venous_val - delayed_val) / (venous_val - non_contrast_val)) * 100
                rel_washout = ((venous_val - delayed_val) / venous_val) * 100
                if abs_washout < 60:
                    malignant_signs.append("absolute washout <60%")
                if rel_washout < 40:
                    malignant_signs.append("relative washout <40%")
            except ZeroDivisionError:
                pass

        # Immediate small caption
        if ((non_contrast_val is not None and non_contrast_val < 10) or (venous_val is not None and venous_val < 10)) and (size_value is not None and size_value < 10):
            st.markdown("<p style='color:green;'>Benign</p>", unsafe_allow_html=True)
        elif ((non_contrast_val is not None and non_contrast_val < 10) or (venous_val is not None and venous_val < 10)) or (size_value is not None and size_value < 10):
            st.markdown("<p style='color:green;'>Probably benign</p>", unsafe_allow_html=True)
        elif ((non_contrast_val is not None and non_contrast_val < 20) or (venous_val is not None and venous_val < 20)) and (size_value is not None and size_value < 20):
            st.markdown("<p style='color:green;'>Probably benign</p>", unsafe_allow_html=True)
        elif ((non_contrast_val is not None and non_contrast_val < 40) or (venous_val is not None and venous_val < 40)) and (size_value is not None and size_value < 40):
            st.markdown("<p style='color:red;'>Possibly malignant</p>", unsafe_allow_html=True)
        elif ((non_contrast_val is not None and non_contrast_val > 40) or (venous_val is not None and venous_val > 40)) or (size_value is not None and size_value > 40):
            st.markdown("<p style='color:red;'>Probably malignant</p>", unsafe_allow_html=True)

        # Final Conclusion full rules
        if macro_fat:
            final_conclusion = "The mass is probably a Myelolipoma. No follow-up needed."
        elif non_contrast_val is not None and venous_val is not None and (venous_val - non_contrast_val < 10) and venous_val > 20:
            final_conclusion = "There is a hematoma enhancement pattern. No follow-up needed."
        elif (non_contrast_val is not None and non_contrast_val <= 10) or (venous_val is not None and venous_val <= 10):
            final_conclusion = "Due to low attenuation, no follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, consider biochemical assays to determine functional status."
        elif calcification:
            final_conclusion = "Calcification of the mass is a benign sign. No follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, approach B and consider biochemical assays to determine functional status."
        elif size_value is not None and size_value <= 10:
            final_conclusion = "Due to small size, no follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, consider biochemical assays to determine functional status."
        elif size_value is not None and 10 < size_value <= 20 and mass_dev == "No prior scanning" and not history_cancer:
            final_conclusion = "Probably benign, but consider biochemical assays to determine functional status and consider adrenal CT scanning after 12 months."
        elif size_value is not None and 10 < size_value <= 40 and mass_dev == "Increased <5 mm/year":
            final_conclusion = "Probably benign, No follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, consider biochemical assays to determine functional status."
        elif size_value is not None and 10 < size_value <= 40 and mass_dev in ["Increased >5 mm/year", "In doubt"] and not history_cancer:
            if non_contrast_val is not None and venous_val is not None and delayed_val is not None:
                if abs_washout is not None and rel_washout is not None and (abs_washout < 60 or rel_washout < 40):
                    final_conclusion = "Depending on the clinical scenario, Control with Adrenal CT, biopsy, PET-CT or Resection should be considered, also consider biochemical assays."
                else:
                    final_conclusion = "Resection recommended. Consider biochemical assays and adrenal CT."
            else:
                final_conclusion = "Resection recommended. Consider biochemical assays and adrenal CT."
        elif size_value is not None and 10 < size_value <= 40 and mass_dev in ["Increased >5 mm/year", "In doubt"] and history_cancer:
            final_conclusion = "Consider biopsy or PET-CT, including biochemical assays."
        elif size_value is not None and 20 < size_value < 40 and mass_dev == "No prior scanning" and not history_cancer:
            if non_contrast_val is None or venous_val is None or delayed_val is None:
                final_conclusion = "Consider Adrenal CT."
            else:
                if (venous_val - non_contrast_val < 10) or (non_contrast_val is not None and non_contrast_val <= 10):
                    final_conclusion = "Probably benign. No follow-up needed."
                elif abs_washout > 60 and rel_washout > 40:
                    final_conclusion = "Probably benign, No follow-up needed, but biochemical assays to determine functional status can be considered."
                else:
                    final_conclusion = "Depending on the clinical scenario, control with adrenal CT, biopsy, PET-CT or resection should be considered, also consider biochemical assays."
        elif size_value is not None and 20 < size_value < 40 and mass_dev == "No prior scanning" and history_cancer:
            if non_contrast_val is None or venous_val is None or delayed_val is None:
                final_conclusion = "Consider Adrenal CT."
            else:
                if (venous_val - non_contrast_val < 10) or (non_contrast_val is not None and non_contrast_val <= 10):
                    final_conclusion = "Probably benign. No follow-up needed."
                elif abs_washout > 60 and rel_washout > 40:
                    final_conclusion = "Probably benign. No follow-up needed. Biochemical assays may be considered."
                else:
                    final_conclusion = "Depending on the clinical scenario, control with adrenal CT, biopsy, PET-CT or resection should be considered, also consider biochemical assays."
        elif size_value is not None and size_value >= 40:
            if history_cancer:
                final_conclusion = "Consider biopsy or PET-CT, also consider biochemical assays."
            else:
                final_conclusion = "Consider Resection and biochemical assays."

    if final_conclusion:
        st.markdown(f"<p style='color:black;'>{final_conclusion}</p>", unsafe_allow_html=True)
        st.session_state['final_conclusion'] = final_conclusion


