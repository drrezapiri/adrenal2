import streamlit as st

# Set page configuration
st.set_page_config(page_title="Adrenal Mass Decision Tool", layout="wide")

# Initialize session state to clear outputs when inputs change
if 'cleared' not in st.session_state:
    st.session_state.cleared = True

def clear_outputs():
    st.session_state['cleared'] = True

def validate_inputs(age, reason, contrast_check, hu_venous, hu_delayed, hu_non):
    errors = []
    if age is None or reason == "":
        errors.append("Patient age and reason of referral must be filled.")
    if contrast_check:
        if hu_venous is None or hu_delayed is None or hu_non is None:
            errors.append("HU values for portal venous, delayed and non-enhanced must be provided when contrast is used.")
    return errors

# Title
st.title("Adrenal Mass Imaging Evaluation Tool")
st.markdown("Developed by **Peter Sommer Ulriksen** and **Reza Piri**, Radiology Department, Rigshospitalet, Denmark")

# Layout with three columns
col1, col2, col3 = st.columns([1.2, 2, 1.2])

# LEFT COLUMN: INPUTS
with col1:
    st.header("Input Patient & Imaging Data")
    age = st.number_input("Patient age", min_value=0, max_value=120, step=1, on_change=clear_outputs)
    reason = st.selectbox("Reason for referral", ["", "Cancer work-up", "Hormonal imbalance", "Incidentaloma"], on_change=clear_outputs)

    ct_scan = st.checkbox("Is there a CT scan performed?", on_change=clear_outputs)

    tumor_size = None
    hu_non = None
    size_growth = ""
    bilateral = False
    hetrogenicity = ""
    macroscopic_fat = False
    cystic = False
    calcification = False

    if ct_scan:
        tumor_size = st.number_input("Tumor size (short axis, cm)", min_value=0.0, step=0.1, on_change=clear_outputs)
        hu_non = st.number_input("HU non-enhanced", value=None, step=1, on_change=clear_outputs)
        size_growth = st.selectbox("Size growth over time", ["No prior scanning", "Increased more than 5 mm per year", "Increased less than 5 mm per year", "In doubt"], on_change=clear_outputs)
        bilateral = st.checkbox("Bilateral finding", on_change=clear_outputs)
        hetrogenicity = st.selectbox("Hetrogenicity", ["", "Homogen", "Hetrogen"], on_change=clear_outputs)
        macroscopic_fat = st.checkbox("Sign of macroscopic fat", on_change=clear_outputs)
        cystic = st.checkbox("Cystic", on_change=clear_outputs)
        calcification = st.checkbox("Calcification", on_change=clear_outputs)

    contrast_check = st.checkbox("Examination with contrast?", on_change=clear_outputs)
    hu_venous = None
    hu_delayed = None

    if contrast_check:
        hu_venous = st.number_input("HU Portal Venous Phase", value=None, step=1, on_change=clear_outputs)
        hu_delayed = st.number_input("HU Delayed Phase", value=None, step=1, on_change=clear_outputs)

    get_info = st.button("Get info")

# MIDDLE COLUMN: DETAILED INFO
with col2:
    st.header("Details")
    if get_info:
        errors = validate_inputs(age, reason, contrast_check, hu_venous, hu_delayed, hu_non)
        if errors:
            for err in errors:
                st.warning(err)
            st.session_state.cleared = True
        else:
            st.session_state.cleared = False

            # Referral risk
            referral_risks = {"Cancer work-up": 43, "Hormonal imbalance": 3, "Incidentaloma": 3}
            if reason in referral_risks:
                st.markdown(f"**Referral risk:** Risk of malignancy due to reason for referral is {referral_risks[reason]}%.")

            # Age-related risk
            if age:
                if age < 18:
                    age_risk = 62
                elif 18 <= age <= 39:
                    age_risk = 4
                elif 40 <= age <= 65:
                    age_risk = 6
                else:
                    age_risk = 11
                st.markdown(f"**Age-related risk:** Risk of malignancy based on age is {age_risk}%.")

            # Contrast and washout analysis
            if contrast_check and hu_venous and hu_delayed and hu_non:
                abs_washout = ((hu_venous - hu_delayed) / (hu_venous - hu_non)) * 100
                rel_washout = ((hu_venous - hu_delayed) / hu_venous) * 100
                st.markdown(f"**Absolute washout:** {abs_washout:.1f}%")
                st.markdown(f"**Relative washout:** {rel_washout:.1f}%")

            # Size-related malignancy risk
            if tumor_size:
                if tumor_size < 4:
                    risk = 2
                elif 4 <= tumor_size <= 6:
                    risk = 6
                else:
                    risk = 25
                st.markdown(f"**Size-related risk:** Risk of adrenal carcinoma is {risk}%.")

            # RULES AND INTERPRETATION
            if size_growth == "Increased less than 5 mm per year":
                st.markdown("**Interpretation:** Due to the size < 5 mm/year, very probably benign finding. No follow-up needed.")
            elif size_growth == "In doubt":
                st.markdown("**Interpretation:** Repeat CT scan without contrast in 6–12 months.")
            elif size_growth == "Increased more than 5 mm per year":
                st.markdown("**Interpretation:** Consider MDT or individual decision-making.")

            if tumor_size and tumor_size < 1:
                st.markdown("**Interpretation:** Very probably benign finding. No follow-up needed.")

            if hu_non and hu_venous and hu_delayed:
                if hu_non < 10 or abs(hu_venous - hu_delayed) < 10:
                    st.markdown("**Interpretation:** Very probably benign finding. No follow-up needed.")

            if macroscopic_fat:
                st.markdown("**Interpretation:** Probably myelolipoma. No follow-up needed.")

            if bilateral:
                st.markdown("**Interpretation:** Due to bilateral findings, consider hormonal evaluation or genetic syndromes.")

# RIGHT COLUMN: FINAL CONCLUSION
with col3:
    st.header("Final Conclusion")
    if get_info and not st.session_state.cleared:
        if tumor_size:
            if tumor_size >= 6:
                st.markdown("**Mass >6 cm:**\n\n→ Consider adrenal carcinoma or metastasis. Surgical referral recommended.")
            elif 4 <= tumor_size < 6:
                st.markdown("**Mass 4–6 cm:**\n\n→ Intermediate risk. Further imaging or MDT discussion advised.")
            elif tumor_size < 4:
                st.markdown("**Mass <4 cm:**\n\n→ Likely benign. Follow guidelines based on stability and features.")
        else:
            st.markdown("Complete tumor size input for final conclusion.")
