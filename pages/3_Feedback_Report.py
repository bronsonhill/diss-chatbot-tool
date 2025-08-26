import streamlit as st
import json
from Home import setup
from utils.mongodb import log_transcript

# Check if user has entered identifier
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

# Check if previous steps are completed
if not st.session_state.get("patient_conversation_done", False):
    st.error("Please complete the Patient Interview first.")
    st.stop()

if not st.session_state.get("diagnosis_done", False):
    st.error("Please complete the Diagnostic Assessment first.")
    st.stop()

client = setup()

st.title("📋 Feedback Report")
st.markdown("Comprehensive feedback on your HEADSS assessment and diagnostic accuracy")

# Get the conversation history
if st.session_state.get("audio_conversation_finished", False):
    # Use audio conversation history
    conversation_history = st.session_state.get("audio_chat_history", [])
    conversation_type = "audio"
else:
    # Use text conversation history
    conversation_history = st.session_state.get("patient_chat_history", [])
    conversation_type = "text"

# Get diagnosis results
diagnosis_results = st.session_state.get("diagnosis_results", {})

# Debug: Check if we have the required data
if not conversation_history:
    st.error("No conversation history found. Please complete the patient interview first.")
    st.stop()

if not diagnosis_results:
    st.error("No diagnosis results found. Please complete the diagnostic assessment first.")
    st.stop()

# Format conversation for the assessor
if conversation_history:
    formatted_messages = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in conversation_history])
    
    # Format diagnosis results
    diagnosis_summary = f"""
    DIAGNOSTIC ASSESSMENT RESULTS:
    
    Correctly Identified: {', '.join(diagnosis_results.get('correct_selections', []))}
    Incorrectly Selected: {', '.join(diagnosis_results.get('incorrect_selections', []))}
    Missed Diagnoses: {', '.join(diagnosis_results.get('missed_diagnoses', []))}
    
    Total Correct: {diagnosis_results.get('total_correct', 0)}/4
    Total Incorrect: {diagnosis_results.get('total_incorrect', 0)}
    Total Missed: {diagnosis_results.get('total_missed', 0)}
    """
    
    # Combine prompts with structured output instructions
    systemprompt = f"{st.session_state['assessor_prompt']} \n\n CONVERSATION TRANSCRIPT: \n {formatted_messages} \n\n {diagnosis_summary} \n\n IMPORTANT: Provide your feedback in the exact JSON structure specified. Include specific, actionable items in the strengths, areas_for_improvement, and recommendations arrays. For HEADSS coverage, evaluate each element as true (met) or false (not met) based on the conversation transcript."
    
    # Generate feedback if not already done
    if not st.session_state.get("assessor_conversation_done", False):
        st.markdown("### Generating Feedback Report...")
        
        with st.spinner("Analyzing your interview and diagnostic assessment..."):
            try:
                # Define structured output schema
                feedback_schema = {
                    "type": "object",
                    "properties": {
                        "Overall Assessment": {
                            "type": "string",
                            "description": "Brief summary of performance (2-3 sentences)"
                        },
                        "Strengths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of specific strengths demonstrated"
                        },
                        "Areas for Improvement": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "List of specific areas that need attention"
                        },
                        "HEADSS Coverage Analysis": {
                            "type": "object",
                            "properties": {
                                "Greeting & Rapport": {"type": "boolean"},
                                "Confidentiality & Rights": {"type": "boolean"},
                                "Cultural & Priority-Group Safety": {"type": "boolean"},
                                "Youth-Friendly / Normalising Language": {"type": "boolean"},
                                "Sensitivity to Cues & Pacing": {"type": "boolean"},
                                "Home & Family": {"type": "boolean"},
                                "Education / Learning Needs": {"type": "boolean"},
                                "Activities, Peers & Strengths": {"type": "boolean"},
                                "Drugs, Alcohol & Risk Behaviours": {"type": "boolean"},
                                "Sexual Health & Relationships": {"type": "boolean"},
                                "Mental Health & Suicide": {"type": "boolean"},
                                "Personal Safety / Violence": {"type": "boolean"},
                                "Summary & Follow-Up Plan": {"type": "boolean"}
                            },
                            "required": ["Greeting & Rapport", "Confidentiality & Rights", "Cultural & Priority-Group Safety", 
                                       "Youth-Friendly / Normalising Language", "Sensitivity to Cues & Pacing", "Home & Family", 
                                       "Education / Learning Needs", "Activities, Peers & Strengths", "Drugs, Alcohol & Risk Behaviours", 
                                       "Sexual Health & Relationships", "Mental Health & Suicide", "Personal Safety / Violence", "Summary & Follow-Up Plan"]
                        },
                        "Diagnostic Accuracy": {
                            "type": "object",
                            "properties": {
                                "Correctly Identified": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of correctly identified diagnoses"
                                },
                                "Incorrectly Selected": {
                                    "type": "string",
                                    "description": "Incorrectly selected diagnosis"
                                },
                                "Missed Diagnoses": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of missed diagnoses"
                                },
                                "Total Correct": {"type": "integer"},
                                "Total Incorrect": {"type": "integer"},
                                "Total Missed": {"type": "integer"}
                            },
                            "required": ["Correctly Identified", "Incorrectly Selected", "Missed Diagnoses", "Total Correct", "Total Incorrect", "Total Missed"]
                        },
                        "Recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of specific, actionable recommendations"
                        },
                        "Detailed Feedback": {
                            "type": "string",
                            "description": "Comprehensive narrative feedback report"
                        }
                    },
                    "required": ["Overall Assessment", "Strengths", "Areas for Improvement", 
                               "HEADSS Coverage Analysis", "Diagnostic Accuracy", "Recommendations", "Detailed Feedback"]
                }
                
                # Try structured feedback first, fallback to unstructured if needed
                try:
                    response = client.chat.completions.create(
                        model=st.session_state["model"],
                        messages=[{"role": "system", "content": systemprompt}],
                        response_format={"type": "json_object"}
                    )
                    use_structured = True
                except Exception as e:
                    st.warning(f"Structured output not supported by this model, falling back to unstructured: {str(e)}")
                    # Fallback to unstructured output
                    response = client.chat.completions.create(
                        model=st.session_state["model"],
                        messages=[{"role": "system", "content": systemprompt}],
                    )
                    use_structured = False
                
                # Parse the response based on whether structured output was used
                if use_structured:
                    try:
                        feedback_data = json.loads(response.choices[0].message.content)
                        
                        # Map the actual response structure to our expected format
                        mapped_feedback_data = {
                            "overall_assessment": feedback_data.get("Overall Assessment", ""),
                            "strengths": feedback_data.get("Strengths", []),
                            "areas_for_improvement": feedback_data.get("Areas for Improvement", []),
                            "headss_coverage": feedback_data.get("HEADSS Coverage Analysis", {}),
                            "recommendations": feedback_data.get("Recommendations", []),
                            "diagnostic_accuracy": feedback_data.get("Diagnostic Accuracy", {}),
                            "detailed_feedback": feedback_data.get("Detailed Feedback", "")
                        }
                        
                        # If no detailed feedback field, create one from the structured data
                        if not mapped_feedback_data["detailed_feedback"]:
                            detailed_feedback = f"""
**Overall Assessment:**
{mapped_feedback_data['overall_assessment']}

**Strengths:**
{chr(10).join([f"- {strength}" for strength in mapped_feedback_data['strengths']])}

**Areas for Improvement:**
{chr(10).join([f"- {improvement}" for improvement in mapped_feedback_data['areas_for_improvement']])}

**HEADSS Coverage Analysis:**
{chr(10).join([f"- {key}: {'✅' if value else '❌'}" for key, value in mapped_feedback_data['headss_coverage'].items()])}

**Recommendations:**
{chr(10).join([f"- {rec}" for rec in mapped_feedback_data['recommendations']])}
                            """
                            mapped_feedback_data["detailed_feedback"] = detailed_feedback.strip()
                        
                        st.session_state["feedback_data"] = mapped_feedback_data
                        st.session_state["feedback_report"] = mapped_feedback_data["detailed_feedback"]
                        
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing structured feedback: {str(e)}")
                        st.error("Raw response: " + response.choices[0].message.content[:500])
                        
                        # Fallback to unstructured feedback
                        feedback_report = response.choices[0].message.content
                        st.session_state["feedback_report"] = feedback_report
                        st.session_state["feedback_data"] = {
                            "overall_assessment": "Feedback generated successfully but structured parsing failed.",
                            "strengths": ["Review the full report for strengths analysis"],
                            "areas_for_improvement": ["Review the full report for improvement areas"],
                            "headss_coverage": {},
                            "recommendations": ["Review the full report for recommendations"],
                            "detailed_feedback": feedback_report
                        }
                else:
                    # Handle unstructured response
                    feedback_report = response.choices[0].message.content
                    st.session_state["feedback_report"] = feedback_report
                    
                    # Create a basic structured format from unstructured text
                    st.session_state["feedback_data"] = {
                        "overall_assessment": "Feedback generated using unstructured format.",
                        "strengths": ["Review the full report for strengths analysis"],
                        "areas_for_improvement": ["Review the full report for improvement areas"],
                        "headss_coverage": {},
                        "recommendations": ["Review the full report for recommendations"],
                        "detailed_feedback": feedback_report
                    }
                
                st.session_state["assessor_conversation_done"] = True
                
                # Log the feedback
                log_transcript(
                    st.session_state["mongodb_uri"],
                    "assessor",
                    [{"role": "assistant", "content": json.dumps(feedback_data, indent=2)}]
                )
                
            except Exception as e:
                st.error(f"Error generating feedback: {str(e)}")
                st.stop()
    
    # Display the feedback report
    if st.session_state.get("assessor_conversation_done", False):
        feedback_report = st.session_state.get("feedback_report", "")
        feedback_data = st.session_state.get("feedback_data", {})
        
        # Display feedback in a nice format
        st.markdown("### 📊 Your Feedback Report")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Full Report", "🎯 Key Points", "📈 Performance Metrics", "💡 Recommendations", "🐛 Debug"])
        
        with tab1:
            if not feedback_report:
                st.error("No feedback report available. Please regenerate the feedback.")
                if st.button("🔄 Regenerate Feedback"):
                    # Reset the feedback state
                    if "assessor_conversation_done" in st.session_state:
                        del st.session_state["assessor_conversation_done"]
                    if "feedback_report" in st.session_state:
                        del st.session_state["feedback_report"]
                    if "feedback_data" in st.session_state:
                        del st.session_state["feedback_data"]
                    st.rerun()
        
        with tab2:
            st.markdown("#### Key Strengths and Areas for Improvement")
            
            # Get structured feedback data
            feedback_data = st.session_state.get("feedback_data", {})
            
            # Display overall assessment
            overall_assessment = feedback_data.get("overall_assessment", "")
            if overall_assessment:
                st.info("**📊 Overall Assessment:**")
                st.markdown(overall_assessment)
            
            # Display strengths
            strengths = feedback_data.get("strengths", [])
            if strengths:
                st.success("**✅ Strengths Identified:**")
                for strength in strengths:
                    st.markdown(f"• {strength}")
            else:
                st.info("**📋 Strengths:**")
                st.markdown("No specific strengths identified in this session.")
            
            # Display areas for improvement
            improvements = feedback_data.get("areas_for_improvement", [])
            if improvements:
                st.warning("**⚠️ Areas for Improvement:**")
                for improvement in improvements:
                    st.markdown(f"• {improvement}")
            else:
                st.info("**📋 Areas for Improvement:**")
                st.markdown("No specific areas for improvement identified.")
        
        with tab3:
            st.markdown("#### Performance Metrics")
            
            # HEADSS Coverage Analysis
            st.markdown("**HEADSS Assessment Coverage:**")
            
            # Get structured HEADSS coverage data
            headss_coverage = feedback_data.get("headss_coverage", {})
            
            # Define HEADSS elements with their corresponding keys (matching actual response)
            headss_elements = {
                "Greeting & Rapport": "Greeting & Rapport",
                "Confidentiality & Rights": "Confidentiality & Rights", 
                "Cultural & Priority-Group Safety": "Cultural & Priority-Group Safety",
                "Youth-Friendly / Normalising Language": "Youth-Friendly Language",
                "Sensitivity to Cues & Pacing": "Sensitivity to Cues & Pacing",
                "Home & Family": "Home & Family",
                "Education / Learning Needs": "Education/Learning Needs",
                "Activities, Peers & Strengths": "Activities, Peers & Strengths",
                "Drugs, Alcohol & Risk Behaviours": "Drugs, Alcohol & Risk Behaviours",
                "Sexual Health & Relationships": "Sexual Health & Relationships",
                "Mental Health & Suicide": "Mental Health & Suicide",
                "Personal Safety / Violence": "Personal Safety/Violence",
                "Summary & Follow-Up Plan": "Summary & Follow-Up Plan"
            }
            
            # Display HEADSS coverage using structured data
            for key, display_name in headss_elements.items():
                if headss_coverage.get(key, False):
                    st.markdown(f"✅ {display_name}")
                else:
                    st.markdown(f"❌ {display_name}")
            
            # Diagnostic Accuracy
            st.markdown("**Diagnostic Accuracy:**")
            
            # Get diagnostic accuracy from structured feedback if available
            diagnostic_accuracy = feedback_data.get("diagnostic_accuracy", {})
            if diagnostic_accuracy:
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_correct = diagnostic_accuracy.get('Total Correct', diagnosis_results.get('total_correct', 0))
                    st.metric("Correct Diagnoses", total_correct, "out of 4")
                with col2:
                    accuracy_pct = (total_correct / 4) * 100 if total_correct else 0
                    st.metric("Accuracy", f"{accuracy_pct:.0f}%")
                with col3:
                    total_missed = diagnostic_accuracy.get('Total Missed', diagnosis_results.get('total_missed', 0))
                    st.metric("Missed Diagnoses", total_missed)
                
                # Show detailed diagnostic breakdown
                st.markdown("**Detailed Breakdown:**")
                if diagnostic_accuracy.get('Correctly Identified'):
                    st.success(f"✅ **Correctly Identified:** {', '.join(diagnostic_accuracy['Correctly Identified'])}")
                if diagnostic_accuracy.get('Incorrectly Selected'):
                    st.error(f"❌ **Incorrectly Selected:** {diagnostic_accuracy['Incorrectly Selected']}")
                if diagnostic_accuracy.get('Missed Diagnoses'):
                    st.warning(f"⚠️ **Missed Diagnoses:** {', '.join(diagnostic_accuracy['Missed Diagnoses'])}")
            else:
                # Fallback to original diagnosis results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Correct Diagnoses", diagnosis_results.get('total_correct', 0), "out of 4")
                with col2:
                    st.metric("Accuracy", f"{diagnosis_results.get('total_correct', 0)/4*100:.0f}%")
                with col3:
                    st.metric("Missed Diagnoses", diagnosis_results.get('total_missed', 0))
        
        with tab4:
            st.markdown("#### Recommendations for Improvement")
            
            # Get structured recommendations
            recommendations = feedback_data.get("recommendations", [])
            if recommendations:
                st.markdown("**💡 Key Recommendations:**")
                for i, recommendation in enumerate(recommendations, 1):
                    st.markdown(f"{i}. {recommendation}")
            else:
                st.info("**📋 Recommendations:**")
                st.markdown("No specific recommendations provided for this session.")
            
            # General HEADSS tips
            st.markdown("**General HEADSS Assessment Tips:**")
            st.markdown("""
            1. **Build rapport first** - Establish trust before diving into sensitive topics
            2. **Use open-ended questions** - Encourage detailed responses
            3. **Be culturally sensitive** - Respect cultural identity and practices
            4. **Maintain confidentiality** - Clearly explain privacy limits
            5. **Check for safety** - Always assess for self-harm or harm to others
            6. **Use youth-friendly language** - Avoid medical jargon
            7. **Be patient** - Allow time for responses, especially with neurodiverse youth
            """)
        
        with tab5:
            st.markdown("#### Debug Information")
            st.markdown("**Session State Keys:**")
            st.json(list(st.session_state.keys()))
            
            st.markdown("**Feedback Report Length:**")
            st.write(len(feedback_report) if feedback_report else 0)
            
            st.markdown("**Feedback Data Keys:**")
            st.json(list(feedback_data.keys()) if feedback_data else [])
            
            st.markdown("**Raw Feedback Report (first 500 chars):**")
            st.code(feedback_report[:500] if feedback_report else "No feedback report")
            
            st.markdown("**Raw Feedback Data:**")
            st.json(feedback_data)
        
        # Download option
        st.markdown("---")
        st.markdown("### 📥 Download Report")
        
        # Create downloadable report
        report_content = f"""
DiSS Adolescent Interview Practice - Feedback Report

{feedback_report}

---
Generated on: {st.session_state.get("session_id", "Unknown Session")}
User Identifier: {st.session_state.get("user_identifier", "Unknown")}
        """
        
        st.download_button(
            label="📄 Download Feedback Report",
            data=report_content,
            file_name=f"diss_feedback_report_{st.session_state.get('user_identifier', 'unknown')}.txt",
            mime="text/plain"
        )
        
        # Session completion
        st.success("🎉 **Session Complete!**")
        st.markdown("""
        You have successfully completed the DiSS Adolescent Interview Practice session.
        
        **What you've accomplished:**
        - ✅ Completed a HEADSS-style interview with a simulated adolescent patient
        - ✅ Made diagnostic assessments based on the interview
        - ✅ Received comprehensive feedback on your performance
        - ✅ Identified areas for improvement and learning
        
        **Next steps:**
        - Review your feedback report carefully
        - Practice the areas identified for improvement
        - Consider retrying the simulation to apply your learning
        - Share your experience with colleagues and mentors
        """)
        
        # Restart option
        if st.button("🔄 Restart Simulation", use_container_width=True):
            # Reset session state
            for key in ["patient_chat_history", "audio_chat_history", "patient_conversation_done", 
                       "diagnosis_done", "assessor_conversation_done", "diagnosis_results", 
                       "diagnosis_selections", "feedback_report", "audio_conversation_finished"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

else:
    st.error("No conversation history found. Please complete the patient interview first.")
