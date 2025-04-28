



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
with col1:
    st.header("Input Data")
    age = st.text_input("Age")
    mass_size = st.text_input("Mass size in mm (short axis)")
    history_cancer = st.checkbox("History of cancer")

    reason_referral = st.selectbox(
        "Reason of referral",
        ["Cancer work-up", "Hormonal imbalance", "Incidentaloma"]
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
        ["No prior scanning", "Increased >5 mm/year", "Increased <5 mm/year", "In doubt"]
    )
    bilateral = st.checkbox("Bilateral finding")
    heterogenicity = st.selectbox("Heterogenicity", ["", "Homogen", "Heterogen"])

    # Macroscopic fat detection based on HU values
    macro_fat_forced = False
    try:
        if (use_nc_ct and non_contrast_hu and float(non_contrast_hu) < 0) or (use_ce_ct and venous_phase_hu and float(venous_phase_hu) < 0):
            macro_fat_forced = True
    except ValueError:
        pass

    if macro_fat_forced:
        macro_fat = True
        st.checkbox("Sign of macroscopic fat", value=True, disabled=True)
        st.caption("Detected negative HU value → macroscopic fat automatically set.")
    else:
        macro_fat = st.checkbox("Sign of macroscopic fat")

    cystic = st.checkbox("Cystic")
    calcification = st.checkbox("Calcification")

    st.markdown("---")
    assess_button = st.button("Assess")

    if 'final_conclusion' in st.session_state and st.session_state['final_conclusion']:
        import pandas as pd
        df_export = pd.DataFrame({
            "Age": [age],
            "Mass Size (mm)": [mass_size],
            "History of Cancer": [history_cancer],
            "Reason of Referral": [reason_referral],
            "Non-contrast CT Used": [use_nc_ct],
            "Contrast Enhanced CT Used": [use_ce_ct],
            "Non-contrast HU": [non_contrast_hu],
            "Venous phase HU": [venous_phase_hu],
            "Delayed HU": [delayed_hu],
            "Mass Development": [mass_dev],
            "Bilateral Finding": [bilateral],
            "Heterogenicity": [heterogenicity],
            "Macroscopic Fat": [macro_fat],
            "Cystic": [cystic],
            "Calcification": [calcification],
            "Final Conclusion": [st.session_state['final_conclusion']]
        })

        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Save Final Report as CSV",
            data=csv,
            file_name='adrenal_mass_report.csv',
            mime='text/csv',
        )
# Column 2: Diagnostic Interpretation
with col2:
    st.header("Preliminary Interpretation")

    if assess_button:
        if not mass_size or (not use_nc_ct and not use_ce_ct):
            st.warning("Missing input: Please provide lesion size and select at least one imaging modality.")
        else:
            benign_reasons = []
            malignant_reasons = []
            complementary_comments = []
            probability_comments = []
            abs_washout = rel_washout = None

            try:
                size_value = float(mass_size) if mass_size else None
                non_contrast_val = float(non_contrast_hu) if non_contrast_hu else None
                venous_val = float(venous_phase_hu) if venous_phase_hu else None
                delayed_val = float(delayed_hu) if delayed_hu else None
                age_val = int(age) if age else None
            except ValueError:
                st.warning("Please make sure age, HU, and size values are valid numbers.")
                size_value = non_contrast_val = venous_val = delayed_val = age_val = None

            if macro_fat:
                benign_reasons.append("macroscopic fat")
                complementary_comments.append("Probably myelolipoma – no follow-up needed.")
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
                complementary_comments.append("Due to bilateral findings, consider pheochromocytoma, bilateral macronodular hyperplasia, congenital adrenal hyperplasia, ACTH-dependent Cushing, lymphoma, infection, bleeding, metastasis, granulomatous disease or 21-hydroxylase deficiency.")
            if mass_dev == "Increased >5 mm/year":
                malignant_reasons.append("growth > 5 mm/year")
            if venous_val is not None and non_contrast_val is not None:
                if (venous_val > 20 or non_contrast_val > 20) and not (venous_val - non_contrast_val < 10 and venous_val > 20):
                    malignant_reasons.append("high HU >20 without hematoma pattern")
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

            # Complementary interpretations
            if non_contrast_val is not None and non_contrast_val > 20:
                complementary_comments.append("Due to HU > 20, check plasma metanephrines.")
            if heterogenicity == "Heterogen":
                complementary_comments.append("Due to heterogenicity, check plasma metanephrines.")
            if venous_val is not None and venous_val > 120:
                complementary_comments.append("HU venous > 120 – consider hypervascular tumors such as RCC, HCC, or pheochromocytoma.")
            if delayed_val is not None and delayed_val > 120:
                complementary_comments.append("HU delayed > 120 – consider hypervascular tumors such as RCC, HCC, or pheochromocytoma.")
            if all(v is not None and v > 20 for v in [non_contrast_val, venous_val, delayed_val]) and \
               abs(non_contrast_val - venous_val) < 6 and abs(non_contrast_val - delayed_val) < 6:
                complementary_comments.append("Probably hematoma – no follow-up needed.")
            if size_value is not None and size_value < 50:
                complementary_comments.append("Probability of adrenal carcinoma is very low due to size < 5 cm.")

            # Probability comments
            if reason_referral == "Cancer work-up":
                probability_comments.append("The risk of malignancy because of the referral reason is 43%.")
            elif reason_referral == "Hormonal imbalance":
                probability_comments.append("The risk of malignancy because of the referral reason is 3%.")
            elif reason_referral == "Incidentaloma":
                probability_comments.append("The risk of malignancy because of the referral reason is 3%.")

            if age_val is not None:
                if age_val < 18:
                    probability_comments.append("Age-related risk of malignancy is 62%.")
                elif 18 <= age_val <= 39:
                    probability_comments.append("Age-related risk of malignancy is 4%.")
                elif 40 <= age_val <= 65:
                    probability_comments.append("Age-related risk of malignancy is 6%.")
                elif age_val > 65:
                    probability_comments.append("Age-related risk of malignancy is 11%.")

            if size_value is not None:
                if size_value < 40:
                    probability_comments.append("Size-related risk of malignancy is 2%.")
                elif 40 <= size_value <= 60:
                    probability_comments.append("Size-related risk of malignancy is 6%.")
                elif size_value > 60:
                    probability_comments.append("Size-related risk of adrenal carcinoma is 25% and for metastasis is 18%.")

            if benign_reasons:
                reasons_text = ", ".join(benign_reasons)
                st.success(f"The following features suggest a probably benign etiology: {reasons_text}.")

            if malignant_reasons:
                reasons_text = ", ".join(malignant_reasons)
                st.error(f"The following features suggest a probably malignant etiology: {reasons_text}.")

            if complementary_comments:
                st.markdown("### Complementary Interpretations")
                for comment in complementary_comments:
                    st.write("- " + comment)

            if probability_comments:
                st.markdown("### Probabilities")
                for comment in probability_comments:
                    st.write("- " + comment)

            if not benign_reasons and not malignant_reasons:
                st.info("No strong benign or malignant indicators found. Further evaluation may be needed.")

# Column 3 placeholder

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
        if size_value is not None and size_value >= 40:
            if history_cancer:
                final_conclusion = "Consider biopsy or PET-CT, also consider biochemical assays."
            else:
                final_conclusion = "Consider Resection and biochemical assays."
        elif macro_fat:
            final_conclusion = "The mass is probably a Myelolipoma. No follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, Consider biochemical assays to determine functional status."
        elif non_contrast_val is not None and venous_val is not None and (venous_val - non_contrast_val < 10) and venous_val > 20:
            final_conclusion = "There is a hematoma enhancement pattern. No follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, Consider biochemical assays to determine functional status."
        elif (non_contrast_val is not None and non_contrast_val <= 10) or (venous_val is not None and venous_val <= 10):
            final_conclusion = "Due to low attenuation, no follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, Consider biochemical assays to determine functional status."
        elif calcification:
            final_conclusion = "Calcification of the mass is a benign sign. No follow-up needed."
            if malignant_signs:
                final_conclusion += f" But, due to the existence of {', '.join(malignant_signs)}, Consider biochemical assays to determine functional status."
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

    if final_conclusion:
        st.markdown(f"<p style='color:black;'>{final_conclusion}</p>", unsafe_allow_html=True)
        st.session_state['final_conclusion'] = final_conclusion
