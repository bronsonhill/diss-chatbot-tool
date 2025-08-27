import streamlit as st
from openai import OpenAI
from utils.mongodb import check_identifier

def is_identifier_valid():
    identifier = st.session_state.get("user_identifier", "").strip()
    if not identifier:
        return False
    return check_identifier(st.session_state["mongodb_uri"], identifier)

def setup():
    # Load prompts
    if "patient_prompt" not in st.session_state: 
        with open("./prompts/patient_prompt.txt", "r") as file:
            patientprompt = file.read()
        st.session_state["patient_prompt"] = patientprompt

    if "assessor_prompt" not in st.session_state:
        with open("./prompts/assessor_prompt.txt", "r") as file:
            assessorprompt = file.read()
        st.session_state["assessor_prompt"] = assessorprompt

    # Model configuration
    if "model" not in st.session_state:
        st.session_state["model"] = "gpt-4o-mini"

    # Chat histories
    if "patient_chat_history" not in st.session_state:
        st.session_state["patient_chat_history"] = []

    if "assessor_chat_history" not in st.session_state:
        st.session_state["assessor_chat_history"] = []

    # Response counters
    if "patient_response_counter" not in st.session_state:
        st.session_state["patient_response_counter"] = 0

    if "assessor_response_counter" not in st.session_state:
        st.session_state["assessor_response_counter"] = 0
    
    # Conversation states
    if "patient_conversation_done" not in st.session_state:
        st.session_state["patient_conversation_done"] = False

    if "diagnosis_done" not in st.session_state:
        st.session_state["diagnosis_done"] = False

    if "assessor_conversation_done" not in st.session_state:
        st.session_state["assessor_conversation_done"] = False

    # MongoDB connection
    if "mongodb_uri" not in st.session_state:
        st.session_state["mongodb_uri"] = st.secrets["MONGODB_CONNECTION_STRING"]

    # Session management
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None

    if "user_identifier" not in st.session_state:
        st.session_state["user_identifier"] = ""

    # Audio conversation session state variables
    if "audio_chat_history" not in st.session_state:
        st.session_state["audio_chat_history"] = []

    if "audio_conversation_finished" not in st.session_state:
        st.session_state["audio_conversation_finished"] = False

    if "audio_session_id" not in st.session_state:
        st.session_state["audio_session_id"] = None

    # Diagnosis results
    if "diagnosis_results" not in st.session_state:
        st.session_state["diagnosis_results"] = {}

    # Set up OpenAI API client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    return client

def init_page():
    setup()
    
    st.set_page_config(
        page_title="DiSS Adolescent Interview Practice",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 DiSS Adolescent Interview Practice")
    st.markdown(
        "**HEADSS Simulation for General Practitioners and Nurse Practitioners**\n\n"
        "This activity lets you rehearse a full HEADSS‐style consultation with a simulated high-school student."
    )
    
    st.markdown(
        "## How it works\n"
        "1. **Interview phase** – Chat with the simulated student just as you would face-to-face.\n"
        "2. **Assessment phase** – Complete a multiple choice diagnostic questionnaire.\n"
        "3. **Feedback phase** – Receive comprehensive feedback on your HEADSS assessment.\n"
        "4. **Reflect & retry** – Use the feedback to refine your approach; restart the simulation at any time.\n"
    )

    st.markdown(
        "## Instructions\n"
        "1. Enter your unique identifier below. This will be used to associate your conversation records with you.\n"
        "2. In the **Patient Interview** tab, converse with Jai (the simulated student) and apply the HEADSS assessment framework. Only click 'Finish Interview' when you are completely finished.\n"
        "3. Complete the **Diagnostic Assessment** with multiple choice questions about possible diagnoses.\n"
        "4. Review your **Feedback Report** to see how well you covered each HEADSS element.\n"
        "\n**Note:** Please ensure you have a stable internet connection to prevent any issues."
    )

    # Add identifier input after welcome message
    identifier = st.text_input(
        "Please enter your unique identifier:",
        key="identifier_input",
        value=st.session_state.get("user_identifier", ""),
        help="This identifier will be stored with your conversation records"
    )

    if identifier:
        if check_identifier(st.session_state["mongodb_uri"], identifier):
            st.session_state["user_identifier"] = identifier
            st.success("✅ Identifier validated successfully. You can now proceed to the interview pages.")
        else:
            st.error("❌ Invalid identifier. Please enter a valid identifier.")
            st.session_state["user_identifier"] = ""
    else:
        st.warning("⚠️ Please enter your identifier before starting any conversations.")

    # HEADSS Criteria Information
    with st.expander("📋 HEADSS Assessment Criteria"):
        st.markdown("""
        **H - Home & Family:** Living situation, relationships, safety, supports
        
        **E - Education/Employment:** School engagement, attendance, learning needs, bullying
        
        **A - Activities & Peers:** Hobbies, online life, friendships, strengths
        
        **D - Drugs & Risk Behaviours:** Substance use screening, non-judgemental tone, harm reduction
        
        **S - Sexual Health & Relationships:** Relationships, consent, contraception, STI risk, inclusivity
        
        **S - Suicide / Mental Health / Safety:** Mood, self-harm, suicidal thoughts, violence or abuse exposure
        """)

    # Important note
    st.info("""
    **Important Note:** This simulation tool is experimental. While we aim for realistic student responses and accurate assessment, 
    the system may sometimes miss nuances or over-interpret. Your real-world clinical judgement remains paramount.
    
    We welcome your feedback on the tool's accuracy, cultural safety, and usefulness.
    """)

if __name__ == "__main__":
    init_page()
