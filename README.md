# DiSS Adolescent Interview Practice

A roleplay chatbot simulation for the Doctors in Secondary Schools (DiSS) program, designed to help General Practitioners and Nurse Practitioners practice HEADSS-style consultations with simulated high-school students.

## Overview

This application provides a comprehensive training environment for healthcare professionals working in school settings. It features:

- **Simulated Patient Interview**: Chat with Jai Murray, a 16-year-old Aboriginal student with complex mental health needs
- **Voice and Text Options**: Choose between text-based or voice-based conversations
- **Diagnostic Assessment**: Multiple choice questionnaire to test diagnostic accuracy
- **Comprehensive Feedback**: AI-powered assessment of HEADSS coverage and communication skills
- **Progress Tracking**: Session management and performance analytics

## Features

### 🏥 Patient Simulation
- **Jai Murray**: 16-year-old Koori student from rural Victoria
- **Complex Case**: Presents with eating disorders, body dysmorphic disorder, depression, and social anxiety
- **Cultural Sensitivity**: Authentic representation of Aboriginal identity and neurodiversity
- **Realistic Responses**: Dynamic conversation based on rapport building and trust

### 🎤 Voice and Text Options
- **Text Chat**: Traditional typing interface
- **Voice Chat**: Real-time audio conversation using OpenAI's voice API
- **Seamless Switching**: Toggle between modes as needed

### 🔍 Diagnostic Assessment
- **14 Diagnostic Options**: Covering common adolescent mental health conditions
- **Immediate Feedback**: See correct answers and explanations
- **Performance Metrics**: Track accuracy and identify learning gaps

### 📋 Comprehensive Feedback
- **HEADSS Assessment**: Detailed analysis of each HEADSS element coverage
- **Communication Skills**: Evaluation of rapport building, cultural safety, and youth-friendly language
- **Diagnostic Accuracy**: Analysis of diagnostic reasoning
- **Actionable Recommendations**: Specific tips for improvement

## Technical Architecture

### Backend
- **Streamlit**: Web application framework
- **OpenAI GPT-4**: AI-powered conversation and feedback generation
- **MongoDB**: Session storage and transcript logging
- **Real-time Audio**: Voice conversation capabilities

### Database Schema
```
diss_chatbot/
├── valid_identifiers/     # User authentication
├── transcripts/          # Session data
    ├── patient_messages
    ├── assessor_messages
    ├── diagnosis_results
    └── metadata
```

## Installation

### Prerequisites
- Python 3.8+
- MongoDB database
- OpenAI API key

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   # .streamlit/secrets.toml
   OPENAI_API_KEY = "your-openai-api-key"
   MONGODB_CONNECTION_STRING = "your-mongodb-connection-string"
   ```

4. Set up MongoDB collections:
   ```javascript
   // Create valid_identifiers collection
   db.valid_identifiers.insertMany([
     {identifier: "user1"},
     {identifier: "user2"}
   ])
   ```

5. Run the application:
   ```bash
   streamlit run Home.py
   ```

## Usage

### For Healthcare Professionals
1. **Login**: Enter your unique identifier
2. **Interview**: Chat with Jai using text or voice
3. **Assess**: Complete the diagnostic questionnaire
4. **Review**: Receive comprehensive feedback
5. **Practice**: Restart to apply learning

### For Administrators
- Add valid identifiers to MongoDB
- Monitor usage through database queries
- Export session data for analysis

## HEADSS Assessment Framework

The application evaluates performance across all HEADSS domains:

- **H** - Home & Family
- **E** - Education/Employment  
- **A** - Activities & Peers
- **D** - Drugs & Risk Behaviours
- **S** - Sexual Health & Relationships
- **S** - Suicide/Mental Health/Safety

## Patient Case Details

### Jai Murray - 16-year-old student
- **Background**: Aboriginal (Koori), neurodiverse, rural Victoria
- **Presenting Issues**: 
  - Low mood and withdrawal
  - Body image concerns and restrictive eating
  - Social anxiety and avoidance
  - Cyberbullying trauma
- **Strengths**: Artistic ability, family support, cultural connection

### Correct Diagnoses
1. Atypical/Restrictive-type Eating Disorder
2. Body Dysmorphic Disorder  
3. Major Depressive Episode
4. Social Anxiety Disorder

## Development

### Project Structure
```
diss-chatbot/
├── Home.py                 # Main application entry point
├── pages/                  # Streamlit pages
│   ├── 1_Patient_Interview.py
│   ├── 2_Diagnostic_Assessment.py
│   └── 3_Feedback_Report.py
├── prompts/                # AI system prompts
│   ├── patient_prompt.txt
│   └── assessor_prompt.txt
├── utils/                  # Utility functions
│   └── mongodb.py
└── requirements.txt        # Python dependencies
```

### Adding New Features
1. **New Patient Cases**: Modify patient prompts and diagnostic options
2. **Additional Assessments**: Extend feedback criteria in assessor prompt
3. **Custom Analytics**: Add new database fields and reporting

## Security and Privacy

- **User Authentication**: Identifier-based access control
- **Data Encryption**: Secure MongoDB connections
- **Session Management**: Automatic cleanup of sensitive data
- **Privacy Compliance**: No personal health information stored

## Support and Feedback

This is an experimental tool designed for educational purposes. While we aim for accuracy and cultural safety, real-world clinical judgment remains paramount.

For technical support or feedback on accuracy and cultural safety, please contact the development team.

## License

This project is developed for the University of Melbourne's Doctors in Secondary Schools program.

## Acknowledgments

- University of Melbourne Medical School
- Doctors in Secondary Schools program
- Aboriginal and Torres Strait Islander health experts
- Adolescent mental health specialists
