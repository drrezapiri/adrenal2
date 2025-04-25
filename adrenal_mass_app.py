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

# Column 2 and 3 placeholders for future content
with col2:
    st.header("")
    st.markdown("(Reserved for analysis output or images)")

with col3:
    st.header("")
    st.markdown("(Reserved for tips, references or diagnostic suggestions)")
