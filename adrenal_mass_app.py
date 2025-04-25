import streamlit as st

# Set page configuration
st.set_page_config(page_title="Adrenal Mass Decision Tool", layout="wide")

# Initialize session state to clear outputs when inputs change
if 'cleared' not in st.session_state:
    st.session_state.cleared = True

def clear_outputs():
    st.session_state['cleared'] = True

def validate_inputs(tumor_size, age, contrast, hu_venous, hu_delayed):
    errors = []
    if not tumor_size or not age:
        errors.append("Tumor size and age must be filled.")
    if contrast:
        if hu_venous is None or hu_delayed is None:
            errors.append("HU values for portal venous and delayed phase must be provided when contrast is used.")
    return errors

# Title
st.title("Adrenal Mass Imaging Evaluation Tool")
st.markdown("Developed by **Peter Sommer Ulriksen** and **Reza Piri**, Radiology Department, Rigshospitalet, Denmark")

# Layout with three columns
col1, col2, col3 = st.columns([1.2, 2, 1.2])

# LEFT COLUMN: INPUTS
with col1:
    st.header("Input Patient & Imaging Data")
    tumor_size = st.number_input("Tumor size (cm)", min_value=0.0, step=0.1, on_change=clear_outputs)
    age = st.number_input("Patient age", min_value=0, max_value=120, step=1, on_change=clear_outputs)

    macroscopic_fat = st.checkbox("Presence of macroscopic fat", on_change=clear_outputs)
    cyst_or_hemorrhage = st.checkbox("Cyst or hemorrhage (non-enhancing)", on_change=clear_outputs)
    calcified_mass = st.checkbox("Calcified mass (old hematoma or granuloma)", on_change=clear_outputs)
    density_below_10 = st.checkbox("Unenhanced CT density <10 HU", on_change=clear_outputs)
    mri_signal_loss = st.checkbox("Signal loss on opposed-phase MRI", on_change=clear_outputs)

    contrast = st.checkbox("Exam performed with contrast?", on_change=clear_outputs)
    hu_venous = st.number_input("HU Portal Venous Phase", value=None, step=1, on_change=clear_outputs)
    hu_delayed = st.number_input("HU Delayed Phase", value=None, step=1, on_change=clear_outputs)

    get_info = st.button("Get info")

# MIDDLE COLUMN: DETAILED INFO
with col2:
    st.header("Details")
    if get_info:
        errors = validate_inputs(tumor_size, age, contrast, hu_venous, hu_delayed)
        if errors:
            for err in errors:
                st.warning(err)
            st.session_state.cleared = True
        else:
            st.session_state.cleared = False

            # Example rules (expandable)
            if macroscopic_fat:
                st.markdown("**Finding:** Macroscopic fat present.\n\n**Interpretation:** Suggestive of myelolipoma → No further imaging needed.")
            elif cyst_or_hemorrhage:
                st.markdown("**Finding:** Cyst/hemorrhage without enhancement.\n\n**Interpretation:** Benign → No follow-up required.")
            elif density_below_10:
                st.markdown("**Finding:** Density <10 HU on unenhanced CT.\n\n**Interpretation:** Lipid-rich adenoma → No further imaging needed.")
            elif contrast:
                abs_washout = (hu_venous - hu_delayed) / (hu_venous - 10) * 100 if density_below_10 else None
                rel_washout = (hu_venous - hu_delayed) / hu_venous * 100
                if abs_washout and abs_washout >= 60:
                    st.markdown(f"**Washout analysis:** Absolute washout = {abs_washout:.1f}%\n\n**Interpretation:** Diagnostic of adenoma")
                elif rel_washout >= 40:
                    st.markdown(f"**Washout analysis:** Relative washout = {rel_washout:.1f}%\n\n**Interpretation:** Diagnostic of adenoma")
                else:
                    st.markdown("**Washout analysis:** Not diagnostic → Consider further evaluation")

# RIGHT COLUMN: FINAL CONCLUSION
with col3:
    st.header("Final Conclusion")
    if get_info and not st.session_state.cleared:
        if tumor_size >= 4:
            st.markdown("**Mass ≥4 cm:**\n\n→ Recommend surgical resection if no benign features.")
        elif tumor_size < 1:
            st.markdown("**Mass <1 cm:**\n\n→ Usually no follow-up if no suspicious features.")
        elif 1 <= tumor_size < 4:
            st.markdown("**Mass 1–4 cm:**\n\n→ Evaluate stability or consider dedicated adrenal CT.")
        else:
            st.markdown("Further workup may be needed depending on clinical context.")
