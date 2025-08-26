import streamlit as st
from Home import setup
from utils.mongodb import log_transcript

# Check if user has entered identifier
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

MAXIMUM_RESPONSES = 1000

client = setup()

st.title("👨‍⚕️ Patient Interview with Jai")
st.markdown("**Jai Murray, 16-year-old student from Murray Plains Secondary College**")

# Display patient information
with st.expander("📋 Patient Information", expanded=False):
    st.markdown("""
    **Name:** Jai Murray  
    **Age:** 16 years old  
    **School:** Murray Plains Secondary College (Year 10)  
    **Location:** Swan Hill, rural Victoria  
    **Background:** Aboriginal (Koori), neurodiverse, lives with Mum, step-dad, and two younger siblings  
    **Interests:** Digital drawing, local footy, fishing with Aunty, Aussie hip hop
    """)

# Voice/Text toggle
use_voice = st.checkbox("🎤 Use Voice Conversation", key="voice_toggle")

if use_voice:
    st.markdown("### Voice Conversation Mode")
    st.markdown("Click the button below to start a voice conversation with Jai.")
    
    # Import voice functionality
    try:
        from st_realtime_audio import realtime_audio_conversation
        
        # Check if OpenAI API key is available
        if not st.secrets.get("OPENAI_API_KEY"):
            st.error("OpenAI API key not configured. Please check your secrets configuration.")
            st.stop()

        # Only show the audio conversation component if not finished
        if not st.session_state.get("audio_conversation_finished", False):
            # Create the real-time audio conversation component
            conversation_result = realtime_audio_conversation(
                api_key=st.secrets["OPENAI_API_KEY"],
                voice="alloy",
                instructions=st.session_state["patient_prompt"],
                auto_start=False,
                temperature=0.8,
                turn_detection_threshold=0.5,
                key="audio_conversation"
            )

            # Display any errors
            if conversation_result.get("error"):
                st.error(f"Error: {conversation_result['error']}")

            # Display conversation transcript
            if conversation_result.get("transcript"):
                st.subheader("Conversation Transcript")
                
                # Sort transcript by sequence to ensure correct chronological order
                sorted_transcript = sorted(
                    conversation_result["transcript"], 
                    key=lambda x: x.get("sequence", x.get("timestamp", 0))
                )
                
                # Display transcript in chat format
                for message in sorted_transcript:
                    if message["type"] == "user":
                        st.chat_message("user").write(message["content"])
                    else:
                        st.chat_message("assistant").write(message["content"])
                
                # Store transcript in session state for logging
                if sorted_transcript and not st.session_state.get("audio_transcript_logged", False):
                    # Convert transcript to chat history format
                    chat_history = []
                    for message in sorted_transcript:
                        role = "user" if message["type"] == "user" else "assistant"
                        chat_history.append({"role": role, "content": message["content"]})
                    
                    st.session_state["audio_chat_history"] = chat_history

            # Add finish conversation button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if conversation_result.get("transcript") and st.session_state.get("audio_chat_history"):
                    if st.button("Finish Interview", key="finish_audio", use_container_width=True):
                        st.session_state.audio_conversation_finished = True
                        st.session_state.patient_conversation_done = True
                        
                        # Log the transcript
                        try:
                            session_id = log_transcript(
                                st.session_state["mongodb_uri"],
                                "patient_audio",
                                st.session_state.audio_chat_history
                            )
                            if session_id:
                                st.session_state.audio_session_id = session_id
                                st.session_state.session_id = session_id
                                st.success("Audio interview logged successfully!")
                            else:
                                st.warning("⚠️ Interview completed but could not be logged to database.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error logging audio interview: {str(e)}")
                            st.rerun()

        else:
            # Show completed conversation transcript
            if st.session_state.get("audio_chat_history"):
                st.subheader("Completed Audio Interview")
                st.success("✅ Audio interview completed and logged successfully!")
                
                # Display the logged transcript
                for message in st.session_state.audio_chat_history:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                
                # Show session ID
                if st.session_state.get("audio_session_id"):
                    st.info(f"Session ID: {st.session_state.audio_session_id}")

        # Simple help section
        with st.expander("How to Use Voice Conversation"):
            st.markdown("""
            **Getting Started:**
            1. Click "Start Conversation" 
            2. Allow microphone access when prompted
            3. Start speaking naturally!
            
            **Tips:**
            - Speak clearly and at normal volume
            - Wait for Jai to finish before speaking
            - Remember to click "Finish Interview" when done
            
            **Requirements:**
            - Microphone access
            - Stable internet connection
            - Chrome browser recommended for best experience
            """)

    except ImportError:
        st.error("Voice conversation requires the streamlit-realtime-audio package. Please install it or use text mode.")

else:
    # Text conversation mode
    st.markdown("### Text Conversation Mode")
    st.markdown("Chat with Jai using text messages below.")
    
    # Write chat history
    for message in st.session_state.patient_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat logic
    if prompt := st.chat_input(
        "Type your message here...",
        disabled=st.session_state.patient_conversation_done or st.session_state.patient_response_counter >= MAXIMUM_RESPONSES
    ):
        st.session_state.patient_chat_history.append({"role": "user", "content": prompt})

        if st.session_state.patient_response_counter < MAXIMUM_RESPONSES:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                messages_with_system_prompt = [{"role": "system", "content": st.session_state["patient_prompt"]}] + [
                    {"role": m["role"], "content": m["content"]}
                for m in st.session_state.patient_chat_history
                ]

                stream = client.chat.completions.create(
                    model=st.session_state["model"],
                    messages=messages_with_system_prompt,
                    stream=True,
                )
                response = st.write_stream(stream)

            st.session_state.patient_response_counter += 1
            st.session_state.patient_chat_history.append({"role": "assistant", "content": response})

        else:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                st.markdown("Thanks for talking with me, doc.")
            
            final_message = {"role": "assistant", "content": "Thanks for talking with me, doc."}
            st.session_state.patient_chat_history.append(final_message)
            st.session_state.patient_conversation_done = True

    # Add finish conversation button below chat input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.patient_conversation_done and st.session_state.patient_chat_history:
            if st.button("Finish Interview", key="finish_patient", use_container_width=True):
                st.session_state.patient_conversation_done = True
                try:
                    session_id = log_transcript(
                        st.session_state["mongodb_uri"],
                        "patient",
                        st.session_state.patient_chat_history
                    )
                    if session_id:
                        st.session_state.session_id = session_id
                    else:
                        st.warning("⚠️ Interview completed but could not be logged to database.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error logging interview: {str(e)}")
                    st.rerun()

# Progress indicator
if st.session_state.patient_conversation_done:
    st.success("✅ Interview completed! You can now proceed to the Diagnostic Assessment.")
