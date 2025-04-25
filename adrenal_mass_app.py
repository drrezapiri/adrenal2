import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Adrenal Mass Approach",
    page_icon="🩺",
    layout="wide"
)

# Title and credits
st.title("Adrenal Mass Approach")
st.caption("Credits: Peter Sommer Ulriksen and Reza Piri from Radiology Department in Rigshospitalet")

# Create three columns
col1, col2, col3 = st.columns(3)

# Column 1: Input Data
with col1:
    st.header("Input Data")
    age = st.text_input("Age")
    mass_size = st.text_input("Mass size in mm (short axis)")
    history_cancer = st.checkbox("History of cancer")

    reason_referral = st.selectbox(
        "Reason of referral",
        ["", "Cancer work-up", "Hormonal imbalance", "Incidentaloma"]
    )

    st.markdown("---")
    st.subheader("Modality used")
    use_nc_ct = st.checkbox("Non-contrast CT")
    use_ce_ct = st.checkbox("Contrast enhanced CT")

    non_contrast_hu = venous_phase_hu = delayed_hu = ""

    if use_nc_ct:
        non_contrast_hu = st.text_input("Non-contrast HU")

    if use_ce_ct:
        venous_phase_hu = st.text_input("Venous phase HU")
        delayed_hu = st.text_input("Delayed HU")

    st.markdown("---")
    st.subheader("Radiologic Features")

    mass_dev = st.selectbox(
        "Mass development",
        ["", "No prior scanning", "Increased >5 mm/year", "Increased <5 mm/year", "In doubt"]
    )

    bilateral = st.checkbox("Bilateral finding")
    heterogenicity = st.selectbox("Heterogenicity", ["", "Homogen", "Heterogen"])
    macro_fat = st.checkbox("Sign of macroscopic fat")
    cystic = st.checkbox("Cystic")
    calcification = st.checkbox("Calcification")

    st.markdown("---")
    assess_button = st.button("Assess")

# Column 2: Diagnostic Interpretation
with col2:
    st.header("Preliminary Interpretation")

    if assess_button:
        if not mass_size or (not use_nc_ct and not use_ce_ct):
            st.warning("Missing input: Please provide lesion size and select at least one imaging modality.")
        else:
            benign_reasons = []
            malignant_reasons = []
            abs_washout = rel_washout = None

            try:
                size_value = float(mass_size) if mass_size else None
                non_contrast_val = float(non_contrast_hu) if non_contrast_hu else None
                venous_val = float(venous_phase_hu) if venous_phase_hu else None
                delayed_val = float(delayed_hu) if delayed_hu else None
            except ValueError:
                st.warning("Please make sure HU and size values are valid numbers.")
                size_value = non_contrast_val = venous_val = delayed_val = None

            if macro_fat:
                benign_reasons.append("macroscopic fat")
            if calcification:
                benign_reasons.append("calcification")
            if size_value is not None and size_value < 10:
                benign_reasons.append("size smaller than 1 cm")
            if non_contrast_val is not None and non_contrast_val <= 10:
                benign_reasons.append("HU non-contrast ≤ 10")
            if venous_val is not None and venous_val <= 10:
                benign_reasons.append("HU venous ≤ 10")
            if mass_dev == "No prior scanning" or mass_dev == "Increased <5 mm/year":
                benign_reasons.append("no significant growth")
            if non_contrast_val is not None and venous_val is not None:
                if venous_val - non_contrast_val < 10:
                    benign_reasons.append("no enhancement (HU change < 10)")

            # Malignant features
            if venous_val is not None and non_contrast_val is not None:
                if venous_val - non_contrast_val > 10:
                    malignant_reasons.append("enhancement (HU change > 10)")
            elif venous_val is not None and non_contrast_val is None:
                if venous_val > 40:
                    malignant_reasons.append("HU venous > 40 (no non-contrast available)")

            if bilateral:
                malignant_reasons.append("bilateral finding")
            if mass_dev == "Increased >5 mm/year":
                malignant_reasons.append("growth > 5 mm/year")
            if size_value is not None and size_value > 40:
                malignant_reasons.append("size > 4 cm")
            if heterogenicity == "Heterogen":
                malignant_reasons.append("heterogenicity")

            # Washout calculations
            if venous_val is not None and delayed_val is not None and non_contrast_val is not None:
                try:
                    abs_washout = ((venous_val - delayed_val) / (venous_val - non_contrast_val)) * 100
                    rel_washout = ((venous_val - delayed_val) / venous_val) * 100

                    st.markdown(f"**Absolute washout**: {abs_washout:.1f}%")
                    st.markdown(f"**Relative washout**: {rel_washout:.1f}%")

                    if abs_washout < 60:
                        malignant_reasons.append("absolute washout < 60%")
                    if rel_washout < 40:
                        malignant_reasons.append("relative washout < 40%")

                except ZeroDivisionError:
                    st.warning("Division by zero in washout calculation. Check HU values.")

            if benign_reasons:
                reasons_text = ", ".join(benign_reasons)
                st.success(f"The following features suggest a probably benign etiology: {reasons_text}.")

            if malignant_reasons:
                reasons_text = ", ".join(malignant_reasons)
                st.error(f"The following features suggest a probably malignant etiology: {reasons_text}.")

            if not benign_reasons and not malignant_reasons:
                st.info("No strong benign or malignant indicators found. Further evaluation may be needed.")

# Column 3 placeholder
with col3:
    st.header("")
    st.markdown("(Reserved for tips, references or diagnostic suggestions)")
