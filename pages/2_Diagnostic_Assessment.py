import streamlit as st
from Home import setup
from utils.mongodb import log_transcript

# Check if user has entered identifier
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

# Check if patient interview is completed
if not st.session_state.get("patient_conversation_done", False):
    st.error("Please complete the Patient Interview first before proceeding to the Diagnostic Assessment.")
    st.stop()

client = setup()

st.title("🔍 Diagnostic Assessment")
st.markdown("Based on your interview with Jai, please select the diagnoses you believe are most appropriate.")

# Define the diagnostic options with correct answers
diagnoses = {
    "Alcohol Use Disorder": {"correct": False, "description": "Problematic pattern of alcohol use leading to clinically significant impairment or distress"},
    "Attention-Deficit / Hyperactivity Disorder (ADHD)": {"correct": False, "description": "Persistent pattern of inattention and/or hyperactivity-impulsivity that interferes with functioning"},
    "Atypical / Restrictive-type Eating Disorder (e.g., OSFED or early Anorexia Nervosa)": {"correct": True, "description": "Disturbance in eating behavior and body image, including restrictive eating patterns"},
    "Bipolar I Disorder": {"correct": False, "description": "Manic episodes with or without major depressive episodes"},
    "Body Dysmorphic Disorder": {"correct": True, "description": "Preoccupation with perceived defects or flaws in physical appearance"},
    "Cannabis Use Disorder": {"correct": False, "description": "Problematic pattern of cannabis use leading to clinically significant impairment or distress"},
    "Conduct Disorder": {"correct": False, "description": "Repetitive and persistent pattern of behavior that violates the rights of others or major age-appropriate societal norms"},
    "Generalized Anxiety Disorder": {"correct": False, "description": "Excessive anxiety and worry about various aspects of life"},
    "Major Depressive Episode": {"correct": True, "description": "Depressed mood or loss of interest/pleasure, plus other symptoms for at least 2 weeks"},
    "Oppositional Defiant Disorder": {"correct": False, "description": "Pattern of angry/irritable mood, argumentative/defiant behavior, or vindictiveness"},
    "Post-Traumatic Stress Disorder": {"correct": False, "description": "Exposure to actual or threatened death, serious injury, or sexual violence, followed by characteristic symptoms"},
    "Psychotic-Spectrum Disorder": {"correct": False, "description": "Presence of delusions, hallucinations, disorganized thinking, or grossly disorganized behavior"},
    "Social Anxiety Disorder": {"correct": True, "description": "Marked fear or anxiety about social situations where the individual may be scrutinized by others"},
    "Specific Learning Disorder": {"correct": False, "description": "Difficulties learning and using academic skills, despite adequate intelligence and education"}
}

# Initialize diagnosis results in session state if not exists
if "diagnosis_selections" not in st.session_state:
    st.session_state["diagnosis_selections"] = {}

# Display instructions
st.markdown("""
### Instructions
Based on your interview with Jai, select all the diagnoses that you believe are most appropriate for this patient. 
You may select multiple diagnoses if you believe they are relevant.

**Key considerations from the interview:**
- Jai shows signs of low mood, tiredness, and withdrawal from activities
- He has body image concerns and restrictive eating patterns
- He experiences social anxiety and avoids certain situations
- He has been the target of cyberbullying and body-shaming
- He shows neurodiverse traits and sensory sensitivities
""")

# Create the diagnostic assessment form
with st.form("diagnostic_assessment"):
    st.markdown("### Select Diagnoses")
    
    # Create checkboxes for each diagnosis
    for diagnosis, info in diagnoses.items():
        selected = st.checkbox(
            f"**{diagnosis}**",
            value=st.session_state["diagnosis_selections"].get(diagnosis, False),
            help=info["description"],
            key=f"diagnosis_{diagnosis}"
        )
        st.session_state["diagnosis_selections"][diagnosis] = selected
    
    # Submit button
    submitted = st.form_submit_button("Submit Diagnostic Assessment", use_container_width=True)

# Handle form submission
if submitted:
    # Calculate results
    correct_selections = []
    incorrect_selections = []
    missed_diagnoses = []
    
    for diagnosis, info in diagnoses.items():
        selected = st.session_state["diagnosis_selections"][diagnosis]
        if selected and info["correct"]:
            correct_selections.append(diagnosis)
        elif selected and not info["correct"]:
            incorrect_selections.append(diagnosis)
        elif not selected and info["correct"]:
            missed_diagnoses.append(diagnosis)
    
    # Store results in session state
    st.session_state["diagnosis_results"] = {
        "correct_selections": correct_selections,
        "incorrect_selections": incorrect_selections,
        "missed_diagnoses": missed_diagnoses,
        "total_correct": len(correct_selections),
        "total_incorrect": len(incorrect_selections),
        "total_missed": len(missed_diagnoses),
        "selections": st.session_state["diagnosis_selections"]
    }
    
    # Log the diagnosis results
    log_transcript(
        st.session_state["mongodb_uri"],
        "diagnosis",
        [],
        st.session_state["diagnosis_results"]
    )
    
    st.session_state["diagnosis_done"] = True
    st.rerun()

# Display results if assessment is completed
if st.session_state.get("diagnosis_done", False):
    st.success("✅ Diagnostic assessment completed!")
    
    results = st.session_state["diagnosis_results"]
    
    # Display summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Correct Diagnoses", results["total_correct"])
    with col2:
        st.metric("Incorrect Diagnoses", results["total_incorrect"])
    with col3:
        st.metric("Missed Diagnoses", results["total_missed"])
    
    # Display detailed results
    with st.expander("📊 Detailed Results", expanded=True):
        if results["correct_selections"]:
            st.markdown("**✅ Correctly Identified:**")
            for diagnosis in results["correct_selections"]:
                st.markdown(f"- {diagnosis}")
        
        if results["incorrect_selections"]:
            st.markdown("**❌ Incorrectly Selected:**")
            for diagnosis in results["incorrect_selections"]:
                st.markdown(f"- {diagnosis}")
        
        if results["missed_diagnoses"]:
            st.markdown("**⚠️ Missed Diagnoses:**")
            for diagnosis in results["missed_diagnoses"]:
                st.markdown(f"- {diagnosis}")
    
    # Show correct answers
    with st.expander("🔍 Correct Diagnoses for Jai", expanded=False):
        st.markdown("""
        **The correct diagnoses for Jai based on the interview are:**
        
        1. **Atypical / Restrictive-type Eating Disorder** - Jai shows signs of restrictive eating, body image concerns, and guilt around food
        2. **Body Dysmorphic Disorder** - Jai has significant preoccupation with his appearance and body image
        3. **Major Depressive Episode** - Jai exhibits low mood, withdrawal, and loss of interest in previously enjoyed activities
        4. **Social Anxiety Disorder** - Jai avoids social situations, changing rooms, and shows anxiety about being observed
        
        **Why other diagnoses were not appropriate:**
        - No evidence of substance use disorders
        - No evidence of conduct disorder or oppositional defiant disorder
        - While Jai has neurodiverse traits, they don't meet full criteria for ADHD or specific learning disorder
        - No evidence of psychotic symptoms or bipolar disorder
        - While Jai has experienced trauma from cyberbullying, symptoms don't meet full PTSD criteria
        """)
    
    st.success("You can now proceed to the Feedback Report to receive comprehensive feedback on your interview and diagnostic assessment.")

# Progress indicator
if not st.session_state.get("diagnosis_done", False):
    st.info("Please complete the diagnostic assessment above to proceed to the feedback report.")
