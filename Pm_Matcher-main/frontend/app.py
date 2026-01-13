import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import PyPDF2
import re
from io import BytesIO

# Configuration
API_BASE_URL = "http://localhost:8003"

# Page config
st.set_page_config(
    page_title="Internship Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .match-score {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2e8b57;
    }
    .recommendation-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict | None:
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            # Ensure we always return a dictionary for consistent type handling
            if isinstance(result, dict):
                return result
            elif isinstance(result, list):
                return {"data": result, "status": "success"}
            else:
                return {"value": result, "status": "success"}
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Please ensure the backend server is running on port 8003.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from resume text using keyword matching"""
    # Common technical skills
    technical_skills = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'nodejs', 'express',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'html', 'css', 'bootstrap',
        'tailwind', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux',
        'machine learning', 'artificial intelligence', 'data science', 'pandas', 'numpy',
        'tensorflow', 'pytorch', 'scikit-learn', 'flask', 'django', 'fastapi', 'spring',
        'restapi', 'graphql', 'microservices', 'devops', 'ci/cd', 'jenkins', 'terraform',
        'figma', 'photoshop', 'illustrator', 'ui/ux', 'android', 'ios', 'flutter', 'react native',
        'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'scala', 'kotlin', 'swift'
    ]
    
    soft_skills = [
        'communication', 'leadership', 'teamwork', 'problem solving', 'analytical thinking',
        'project management', 'time management', 'adaptability', 'creativity', 'critical thinking'
    ]
    
    all_skills = technical_skills + soft_skills
    text_lower = text.lower()
    found_skills = []
    
    for skill in all_skills:
        if skill in text_lower:
            # Capitalize properly
            found_skills.append(' '.join(word.capitalize() for word in skill.split()))
    
    return list(set(found_skills))  # Remove duplicates

def extract_education_from_text(text: str) -> Dict[str, str]:
    """Extract education information from resume text"""
    education_levels = ['phd', 'ph.d', 'doctorate', 'master', 'mtech', 'm.tech', 'mba', 'ms', 'm.s',
                       'bachelor', 'btech', 'b.tech', 'be', 'b.e', 'bsc', 'b.sc', 'ba', 'b.a',
                       'diploma', 'graduate', 'undergraduate']
    
    fields = ['computer science', 'information technology', 'software engineering', 'electrical',
             'electronics', 'mechanical', 'civil', 'chemical', 'biotechnology', 'mathematics',
             'physics', 'chemistry', 'biology', 'business', 'management', 'finance', 'economics']
    
    text_lower = text.lower()
    
    # Find education level
    education_level = "Bachelor"  # default
    for level in education_levels:
        if level in text_lower:
            if level in ['phd', 'ph.d', 'doctorate']:
                education_level = "PhD"
                break
            elif level in ['master', 'mtech', 'm.tech', 'mba', 'ms', 'm.s']:
                education_level = "Master"
                break
            elif level in ['bachelor', 'btech', 'b.tech', 'be', 'b.e', 'bsc', 'b.sc', 'ba', 'b.a']:
                education_level = "Bachelor"
                break
            elif level in ['diploma']:
                education_level = "Diploma"
                break
    
    # Find field of study
    field_of_study = "Computer Science"  # default
    for field in fields:
        if field in text_lower:
            field_of_study = field.title()
            break
    
    # Extract CGPA/GPA using regex
    cgpa_pattern = r'(?:cgpa|gpa|grade)[:\s]*([0-9]+\.?[0-9]*)'
    cgpa_match = re.search(cgpa_pattern, text_lower)
    cgpa = cgpa_match.group(1) if cgpa_match else ""
    
    return {
        'education_level': education_level,
        'field_of_study': field_of_study,
        'cgpa': cgpa
    }

def extract_contact_info_from_text(text: str) -> Dict[str, str]:
    """Extract contact information from resume text"""
    # Email regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else ""
    
    # Phone regex (Indian format)
    phone_pattern = r'(?:\+91|91)?[\s-]?[6-9]\d{9}'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else ""
    
    # Name extraction (first few words, usually at the top)
    lines = text.strip().split('\n')
    name = ""
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
            # Likely a name if it's short, no numbers, and not empty
            if '@' not in line and not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum']):
                name = line
                break
    
    return {
        'name': name,
        'email': email,
        'phone': phone
    }

def display_match_card(match_data: Dict[str, Any], is_candidate_view: bool = True):
    """Display a match card with scores and details"""
    
    if not match_data or not isinstance(match_data, dict):
        st.error("Invalid match data provided")
        return
    
    if is_candidate_view:
        # Candidate viewing internship matches
        internship = match_data.get("internship", {})
        scores = match_data.get("scores", {})
        match_percentage = match_data.get("match_percentage", 0)
        
        if not internship:
            st.error("No internship data found")
            return
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(f"🏢 {internship.get('title', 'Unknown Position')}")
                st.write(f"**Company:** {internship.get('company_name', 'N/A')}")
                st.write(f"**Industry:** {internship.get('industry', 'N/A')}")
                st.write(f"**Location:** {internship.get('location', 'N/A')}")
                if internship.get('is_remote'):
                    st.write("🏠 **Remote Work Available**")
                st.write(f"**Duration:** {internship.get('duration_months', 'N/A')} months")
                st.write(f"**Stipend:** ₹{internship.get('stipend_amount', 0):,.0f}/month")
                
            with col2:
                st.markdown(f"<div class='match-score'>🎯 {match_percentage}% Match</div>", unsafe_allow_html=True)
                
                # Score breakdown
                st.write("**Score Breakdown:**")
                skill_score = scores.get('skill_similarity', scores.get('skill_match_score', 0))
                if isinstance(skill_score, (int, float)):
                    st.progress(float(skill_score))
                    st.caption(f"Skills: {skill_score:.2f}")
                
                qual_score = scores.get('qualification_match', scores.get('qualification_match_score', 0))
                if isinstance(qual_score, (int, float)):
                    st.progress(float(qual_score))
                    st.caption(f"Qualifications: {qual_score:.2f}")
                
                location_score = scores.get('location_match', scores.get('location_match_score', 0))
                if isinstance(location_score, (int, float)):
                    st.progress(float(location_score))
                    st.caption(f"Location: {location_score:.2f}")
            
            with col3:
                internship_id = internship.get('id', 0)
                match_index = match_data.get('_match_index', 0)  # Use match index for uniqueness
                unique_key_suffix = f"{internship_id}_{match_index}_{hash(str(match_data)) % 1000}"
                
                if st.button(f"Apply Now", key=f"apply_{unique_key_suffix}"):
                    st.success(f"✅ Application submitted for {internship.get('title', 'internship')}!")
                    st.balloons()
                
                if st.button(f"View Details", key=f"details_{unique_key_suffix}"):
                    st.session_state[f"show_details_{unique_key_suffix}"] = not st.session_state.get(f"show_details_{unique_key_suffix}", False)
                    st.rerun()
                
                # Verbose AI Analysis button - always show for better UX
                if st.button(f"🤖 AI Analysis", key=f"ai_analysis_{unique_key_suffix}"):
                    # Try to get candidate ID from session state or use a default
                    candidate_id = st.session_state.get('current_candidate_id')
                    
                    if not candidate_id:
                        st.error("❌ Please set candidate ID first by using 'Find Matches' with a valid candidate ID")
                    else:
                        with st.spinner("🤖 Generating detailed AI analysis..."):
                            ai_result = make_api_request(f"/verbose-ai-analysis/{candidate_id}/{internship_id}")
                            
                        if ai_result and isinstance(ai_result, dict):
                            # Check for different response formats
                            ai_analysis = None
                            if 'ai_analysis' in ai_result:
                                ai_analysis = ai_result['ai_analysis']
                            elif 'analysis' in ai_result:
                                ai_analysis = ai_result['analysis'] 
                            elif 'data' in ai_result:
                                ai_analysis = ai_result['data']
                            else:
                                ai_analysis = ai_result
                            
                            if ai_analysis and isinstance(ai_analysis, dict):
                                st.session_state[f"show_ai_{unique_key_suffix}"] = ai_analysis
                                st.rerun()
                            else:
                                st.error("❌ AI analysis format not recognized")
                                st.write("Debug - API Response:", ai_result)
                        else:
                            st.error("❌ Failed to get AI analysis from backend")
                
                # Show AI analysis if available
                if st.session_state.get(f"show_ai_{unique_key_suffix}"):
                    ai_analysis = st.session_state[f"show_ai_{unique_key_suffix}"]
                    with st.expander("🤖 Detailed AI Analysis", expanded=True):
                        st.write("**Overall Recommendation:**")
                        st.info(ai_analysis.get('recommendation', 'No recommendation available'))
                        
                        if ai_analysis.get('fit_summary'):
                            st.write("**Fit Summary:**")
                            st.write(ai_analysis['fit_summary'])
                        
                        if ai_analysis.get('strengths'):
                            st.write("**Your Strengths:**")
                            st.write(ai_analysis['strengths'])
                        
                        if ai_analysis.get('growth_opportunities'):
                            st.write("**Growth Opportunities:**")
                            st.write(ai_analysis['growth_opportunities'])
                        
                        confidence = ai_analysis.get('confidence', 0)
                        if isinstance(confidence, (int, float)):
                            st.write(f"**AI Confidence:** {confidence:.1%}")
                        
                        if st.button("Close AI Analysis", key=f"close_ai_{unique_key_suffix}"):
                            del st.session_state[f"show_ai_{unique_key_suffix}"]
                            st.rerun()
                
                # Show details if button was clicked
                if st.session_state.get(f"show_details_{unique_key_suffix}", False):
                    with st.expander("🔍 Detailed Analysis", expanded=True):
                        st.write("**📋 Internship Description:**")
                        st.write(internship.get('description', 'No description available'))
                        
                        st.write("**🛠️ Required Skills:**")
                        skills = internship.get('required_skills', [])
                        if skills:
                            for skill in skills:
                                st.write(f"• {skill}")
                        
                        st.write("**📚 Requirements:**")
                        st.write(f"• Min Education: {internship.get('min_education_level', 'N/A')}")
                        st.write(f"• Min CGPA: {internship.get('min_cgpa', 'N/A')}")
                        st.write(f"• Experience Required: {'Yes' if internship.get('experience_required') else 'No'}")
                        
                        st.write("**📊 Availability:**")
                        total_positions = internship.get('total_positions', 0)
                        filled_positions = internship.get('filled_positions', 0)
                        available = total_positions - filled_positions
                        st.write(f"• Positions Available: {available}/{total_positions}")
                        
                        # Show AI reasoning if available
                        ai_reasoning = match_data.get('ai_reasoning')
                        if ai_reasoning:
                            st.write("**🤖 Quick AI Analysis:**")
                            st.info(ai_reasoning)
                        
                        # Show embedding similarity
                        embedding_similarity = match_data.get('embedding_similarity')
                        if embedding_similarity and isinstance(embedding_similarity, (int, float)):
                            st.write("**🧠 Skill Similarity Analysis:**")
                            similarity_pct = embedding_similarity * 100
                            st.progress(float(embedding_similarity))
                            st.write(f"Semantic Skill Match: {similarity_pct:.1f}%")
                        
                        if st.button("Close Details", key=f"close_{unique_key_suffix}"):
                            st.session_state[f"show_details_{unique_key_suffix}"] = False
                            st.rerun()
    else:
        # Company viewing candidate matches (simplified for now)
        candidate = match_data.get("candidate", {})
        scores = match_data.get("scores", {})
        match_percentage = match_data.get("match_percentage", 0)
        
        if not candidate:
            st.error("No candidate data found")
            return
            
        st.write(f"**👤 {candidate.get('name', 'Unknown')}** - {match_percentage}% Match")
        st.write(f"Email: {candidate.get('email', 'N/A')}")
        st.write(f"Education: {candidate.get('education_level', 'N/A')} in {candidate.get('field_of_study', 'N/A')}")
        
        # Show skills if available
        skills = candidate.get('skills', [])
        if skills:
            st.write("Skills:")
            for skill in skills[:5]:  # Show first 5 skills
                st.write(f"• {skill}")
            if len(skills) > 5:
                st.write(f"... and {len(skills) - 5} more")
        
        # End of first else block - candidate display complete

# Sidebar navigation
def render_sidebar():
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1f77b4/white?text=InternMatch", width=150)
        
        st.markdown("### 🧭 Navigation")
        
        pages = {
            "🏠 Home": "home",
            "👤 Register as Candidate": "register_candidate",
            "🔍 Find Matches": "find_matches",
            "📋 View Applications": "applications",
            "📊 Analytics": "analytics"
        }
        
        for page_name, page_key in pages.items():
            if st.button(page_name, key=f"nav_{page_key}"):
                st.session_state.page = page_key
                st.rerun()

# Main app
def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    render_sidebar()
    
    # Route to appropriate page
    if st.session_state.page == 'home':
        render_home_page()
    elif st.session_state.page == 'register_candidate':
        render_candidate_registration()
    elif st.session_state.page == 'find_matches':
        render_matching_page()
    elif st.session_state.page == 'applications':
        render_applications_page()
    elif st.session_state.page == 'analytics':
        render_analytics_page()

def render_home_page():
    st.markdown("<h1 class='main-header'>🎯 Smart Internship Matcher</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to India's First AI-Powered Internship Matching Platform
    
    Our platform uses advanced machine learning to match candidates with internships while ensuring 
    fair representation across social categories, rural/urban areas, and promoting diversity in internships.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>🤖 AI-Powered Matching</h3>
            <p>Advanced embeddings and LLM recommendations ensure the best matches based on skills, qualifications, and preferences.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>⚖️ Affirmative Action</h3>
            <p>Ensuring fair representation for SC/ST/BC categories, rural candidates, and first-generation graduates.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>🎯 Smart Recommendations</h3>
            <p>Meta Llama AI provides detailed explanations for every match recommendation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    # Try to get stats from API
    candidates_data = make_api_request("/candidates/")
    companies_data = make_api_request("/companies/")
    internships_data = make_api_request("/internships/")
    
    with col1:
        candidate_count = len(candidates_data) if candidates_data else 0
        st.metric("👥 Registered Candidates", candidate_count)
    
    with col2:
        company_count = len(companies_data) if companies_data else 0
        st.metric("🏢 Partner Companies", company_count)
    
    with col3:
        internship_count = len(internships_data) if internships_data else 0
        st.metric("💼 Available Internships", internship_count)
    
    with col4:
        # Calculate active internships
        active_internships = make_api_request("/internships/active")
        active_count = len(active_internships) if active_internships else 0
        st.metric("🔥 Active Opportunities", active_count)

def render_candidate_registration():
    st.markdown("<h1 class='main-header'>👤 Candidate Registration</h1>", unsafe_allow_html=True)
    
    # Resume upload section
    st.markdown("### 📄 Option 1: Upload Resume (PDF only)")
    st.info("💡 Upload your resume to auto-fill the form, or fill manually below")
    
    uploaded_file = st.file_uploader("Choose your resume (PDF)", type=['pdf'], key="resume_upload")
    
    # Initialize session state for form data
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Process uploaded resume
    if uploaded_file is not None:
        if st.button("📝 Extract Information from Resume", key="extract_resume"):
            with st.spinner("🔍 Analyzing your resume..."):
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                
                if resume_text:
                    # Extract information
                    contact_info = extract_contact_info_from_text(resume_text)
                    education_info = extract_education_from_text(resume_text)
                    skills = extract_skills_from_text(resume_text)
                    
                    # Store in session state
                    st.session_state.form_data.update({
                        'name': contact_info['name'],
                        'email': contact_info['email'],
                        'phone': contact_info['phone'],
                        'education_level': education_info['education_level'],
                        'field_of_study': education_info['field_of_study'],
                        'cgpa': education_info['cgpa'],
                        'skills': skills
                    })
                    
                    st.success("✅ Resume processed successfully! Information extracted and filled below.")
                    st.info(f"📋 Extracted {len(skills)} skills from your resume")
                    
                    # Show extracted skills
                    if skills:
                        st.write("**🔧 Extracted Skills:**")
                        skill_cols = st.columns(4)
                        for i, skill in enumerate(skills):
                            with skill_cols[i % 4]:
                                st.write(f"• {skill}")
                else:
                    st.error("❌ Could not extract text from the PDF. Please try again or fill the form manually.")
    
    st.markdown("### 📝 Option 2: Fill Details Manually")
    
    with st.form("candidate_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            name = st.text_input("Full Name*", 
                                value=st.session_state.form_data.get('name', ''),
                                placeholder="Enter your full name")
            email = st.text_input("Email Address*", 
                                 value=st.session_state.form_data.get('email', ''),
                                 placeholder="your.email@example.com")
            phone = st.text_input("Phone Number*", 
                                 value=st.session_state.form_data.get('phone', ''),
                                 placeholder="+91 9876543210")
            
            st.subheader("Academic Information")
            education_level = st.selectbox(
                "Education Level*",
                ["Diploma", "UG", "Bachelor", "PG", "Master", "PhD", "Doctorate"],
                index=["Diploma", "UG", "Bachelor", "PG", "Master", "PhD", "Doctorate"].index(
                    st.session_state.form_data.get('education_level', 'Bachelor'))
            )
            field_of_study = st.text_input("Field of Study*", 
                                          value=st.session_state.form_data.get('field_of_study', ''),
                                          placeholder="Computer Science")
            cgpa = st.text_input("CGPA", 
                                value=st.session_state.form_data.get('cgpa', ''),
                                placeholder="8.5")
            graduation_year = st.number_input("Graduation Year", min_value=2020, max_value=2030, value=2024)
            institution = st.text_input("Institution", placeholder="University/College name")
        
        with col2:
            st.subheader("Skills & Experience")
            
            # Pre-populate skills if extracted from resume
            default_skills = ""
            if 'skills' in st.session_state.form_data and st.session_state.form_data['skills']:
                default_skills = '\n'.join(st.session_state.form_data['skills'])
            
            skills_input = st.text_area(
                "Skills* (one per line)",
                value=default_skills,
                placeholder="Python\nJavaScript\nMachine Learning\nReact\nSQL",
                height=100,
                help="💡 These were auto-filled from your resume. You can edit them." if default_skills else None
            )
            
            st.subheader("Location Preferences")
            current_location = st.text_input("Current Location*", placeholder="City, State")
            preferred_locations_input = st.text_area(
                "Preferred Locations (one per line)",
                placeholder="Mumbai\nBangalore\nHyderabad",
                height=80
            )
            willing_to_relocate = st.checkbox("Willing to relocate", value=True)
        
        st.subheader("Background Information (for Affirmative Action)")
        col3, col4 = st.columns(2)
        
        with col3:
            social_category = st.selectbox(
                "Social Category*",
                ["OC", "BC", "SC", "ST", "OTHERS"],
                help="This information is used for diversity and inclusion purposes"
            )
            area_type = st.selectbox(
                "Area Type*",
                ["RURAL", "URBAN", "SEMI_URBAN"]
            )
            state = st.text_input("State*", placeholder="Maharashtra")
            district = st.text_input("District*", placeholder="Pune")
        
        with col4:
            is_first_generation_graduate = st.checkbox("First Generation Graduate")
        
        submitted = st.form_submit_button("Register Candidate", type="primary")
        
        if submitted:
            if not all([name, email, phone, education_level, field_of_study, current_location, social_category, area_type, state, district]):
                st.error("Please fill all required fields marked with *")
            else:
                # Process skills and other lists
                skills = [skill.strip() for skill in skills_input.split('\n') if skill.strip()]
                preferred_locations = [loc.strip() for loc in preferred_locations_input.split('\n') if loc.strip()]
                
                candidate_data = {
                    "email": email,
                    "name": name,
                    "phone": phone,
                    "education_level": education_level,
                    "field_of_study": field_of_study,
                    "cgpa": cgpa if cgpa and cgpa.strip() else None,
                    "graduation_year": graduation_year,
                    "institution": institution if institution else None,
                    "skills": skills,
                    "experience_months": 0,
                    "projects": [],
                    "preferred_locations": preferred_locations,
                    "current_location": current_location,
                    "willing_to_relocate": willing_to_relocate,
                    "social_category": social_category,
                    "area_type": area_type,
                    "state": state,
                    "district": district,
                    "is_first_generation_graduate": is_first_generation_graduate,
                    "family_income_annual": None,
                    "previous_internships_count": 0,
                    "previous_internship_companies": []
                }
                
                result = make_api_request("/candidates/", "POST", candidate_data)
                
                if result:
                    st.success(f"✅ Candidate registered successfully! Your ID is: {result['candidate_id']}")
                    st.balloons()
                    # Store candidate ID in session state
                    st.session_state.candidate_id = result['candidate_id']
                    # Clear form data
                    st.session_state.form_data = {}
                    
                    # Auto-find matches after registration
                    st.info("🔍 Finding your internship matches...")
                    matches_response = make_api_request(f"/matches/candidate/{result['candidate_id']}")
                    if matches_response:
                        # Store matches for display
                        st.session_state.resume_matches = {
                            'candidate_data': candidate_data,
                            'matches': matches_response,
                            'candidate_id': result['candidate_id']
                        }
                        st.success("🎯 Registration complete! Click 'Find Matches' to see your internship opportunities.")
                    
    # Clear form data button
    if st.session_state.form_data:
        if st.button("🗑️ Clear Auto-filled Data"):
            st.session_state.form_data = {}
            st.rerun()

def render_company_registration():
    st.markdown("<h1 class='main-header'>🏢 Company Registration</h1>", unsafe_allow_html=True)
    
    with st.form("company_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Company Information")
            name = st.text_input("Company Name*", placeholder="Tech Corp Pvt Ltd")
            industry = st.text_input("Industry*", placeholder="Information Technology")
            description = st.text_area("Company Description", placeholder="Brief description of your company...", height=100)
            headquarters = st.text_input("Headquarters", placeholder="Mumbai, Maharashtra")
            
            locations_input = st.text_area(
                "Office Locations (one per line)",
                placeholder="Mumbai\nBangalore\nPune\nHyderabad",
                height=80
            )
        
        with col2:
            st.subheader("Internship Capacity & Diversity")
            total_internship_capacity = st.number_input("Total Internship Capacity*", min_value=1, value=10)
            diversity_commitment = st.slider("Diversity Commitment (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
            rural_quota = st.slider("Rural Candidate Quota (%)", min_value=0.0, max_value=50.0, value=20.0, step=1.0)
            
            st.subheader("Social Category Quotas (%)")
            sc_quota = st.number_input("SC Quota", min_value=0.0, max_value=50.0, value=15.0, step=0.5)
            st_quota = st.number_input("ST Quota", min_value=0.0, max_value=50.0, value=7.5, step=0.5)
            bc_quota = st.number_input("BC Quota", min_value=0.0, max_value=50.0, value=27.0, step=0.5)
            oc_quota = st.number_input("OC Quota", min_value=0.0, max_value=100.0, value=50.5, step=0.5)
        
        submitted = st.form_submit_button("Register Company", type="primary")
        
        if submitted:
            if not all([name, industry, total_internship_capacity]):
                st.error("Please fill all required fields marked with *")
            else:
                locations = [loc.strip() for loc in locations_input.split('\n') if loc.strip()]
                
                company_data = {
                    "name": name,
                    "industry": industry,
                    "description": description if description else None,
                    "headquarters": headquarters if headquarters else None,
                    "locations": locations,
                    "total_internship_capacity": total_internship_capacity,
                    "diversity_commitment": diversity_commitment / 100.0,
                    "rural_quota": rural_quota / 100.0,
                    "category_quotas": {
                        "SC": sc_quota / 100.0,
                        "ST": st_quota / 100.0,
                        "BC": bc_quota / 100.0,
                        "OC": oc_quota / 100.0
                    }
                }
                
                result = make_api_request("/companies/", "POST", company_data)
                
                if result:
                    st.success(f"✅ Company registered successfully! Your Company ID is: {result['company_id']}")
                    st.balloons()
                    st.session_state.company_id = result['company_id']

def render_internship_posting():
    st.markdown("<h1 class='main-header'>📝 Post New Internship</h1>", unsafe_allow_html=True)
    
    # Get companies for dropdown
    companies_response = make_api_request("/companies/")
    companies_data = []
    
    if companies_response:
        if isinstance(companies_response, list):
            companies_data = companies_response
        elif isinstance(companies_response, dict):
            if 'data' in companies_response:
                companies_data = companies_response['data']
            elif companies_response:
                companies_data = list(companies_response.values()) if isinstance(list(companies_response.values())[0], dict) else []
    
    if not companies_data:
        st.error("No companies found. Please register a company first.")
        return
    
    # Safely create company options
    company_options = {}
    for comp in companies_data:
        if isinstance(comp, dict) and 'name' in comp and 'id' in comp:
            company_options[f"{comp['name']} (ID: {comp['id']})"] = comp['id']
    
    if not company_options:
        st.error("No valid company data found.")
        return
    
    with st.form("internship_posting"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Information")
            selected_company = st.selectbox("Select Company*", options=list(company_options.keys()))
            company_id = company_options[selected_company]
            
            title = st.text_input("Internship Title*", placeholder="Software Development Intern")
            description = st.text_area("Job Description*", placeholder="Detailed description of the internship role...", height=150)
            
            required_skills_input = st.text_area(
                "Required Skills* (one per line)",
                placeholder="Python\nReact\nSQL\nGit",
                height=100
            )
            
            location = st.text_input("Location*", placeholder="Mumbai, Maharashtra")
            is_remote = st.checkbox("Remote Work Available")
            
        with col2:
            st.subheader("Requirements & Details")
            min_education_level = st.selectbox(
                "Minimum Education Level*",
                ["Diploma", "UG", "Bachelor", "PG", "Master", "PhD"]
            )
            
            preferred_fields_input = st.text_area(
                "Preferred Fields of Study (one per line)",
                placeholder="Computer Science\nInformation Technology\nElectronics",
                height=80
            )
            
            min_cgpa = st.number_input("Minimum CGPA", min_value=0.0, max_value=10.0, value=6.0, step=0.1)
            experience_required = st.checkbox("Prior Experience Required")
            
            duration_months = st.number_input("Duration (months)*", min_value=1, max_value=12, value=3)
            
            col2a, col2b = st.columns(2)
            with col2a:
                start_date = st.date_input("Start Date*", value=datetime.now().date() + timedelta(days=30))
            with col2b:
                application_deadline = st.date_input("Application Deadline*", value=datetime.now().date() + timedelta(days=14))
            
            stipend_amount = st.number_input("Monthly Stipend (INR)", min_value=0, value=15000, step=1000)
            total_positions = st.number_input("Total Positions*", min_value=1, value=2)
        
        st.subheader("Diversity Reservations (Optional)")
        col3, col4 = st.columns(2)
        
        with col3:
            sc_reserved = st.number_input("SC Reserved Positions", min_value=0, value=0)
            st_reserved = st.number_input("ST Reserved Positions", min_value=0, value=0)
        
        with col4:
            bc_reserved = st.number_input("BC Reserved Positions", min_value=0, value=0)
            rural_reserved = st.number_input("Rural Reserved Positions", min_value=0, value=0)
        
        submitted = st.form_submit_button("Post Internship", type="primary")
        
        if submitted:
            required_fields = [title, description, location, min_education_level, duration_months, total_positions]
            if not all(required_fields) or not required_skills_input.strip():
                st.error("Please fill all required fields marked with *")
            elif application_deadline <= datetime.now().date():
                st.error("Application deadline must be in the future")
            elif start_date <= application_deadline:
                st.error("Start date must be after application deadline")
            else:
                required_skills = [skill.strip() for skill in required_skills_input.split('\n') if skill.strip()]
                preferred_fields = [field.strip() for field in preferred_fields_input.split('\n') if field.strip()]
                
                internship_data = {
                    "company_id": company_id,
                    "title": title,
                    "description": description,
                    "required_skills": required_skills,
                    "min_education_level": min_education_level,
                    "preferred_fields": preferred_fields,
                    "min_cgpa": min_cgpa,
                    "experience_required": experience_required,
                    "location": location,
                    "is_remote": is_remote,
                    "duration_months": duration_months,
                    "start_date": start_date.isoformat(),
                    "application_deadline": application_deadline.isoformat(),
                    "stipend_amount": stipend_amount,
                    "total_positions": total_positions,
                    "reserved_positions": {
                        "SC": sc_reserved,
                        "ST": st_reserved,
                        "BC": bc_reserved,
                        "rural": rural_reserved
                    }
                }
                
                result = make_api_request("/internships/", "POST", internship_data)
                
                if result:
                    st.success(f"✅ Internship posted successfully! Internship ID: {result['internship_id']}")
                    st.balloons()

def render_applications_page():
    st.markdown("<h1 class='main-header'>📋 View Applications</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 Candidate Applications", "🏢 Internship Applications"])
    
    with tab1:
        st.subheader("View Applications by Candidate")
        candidate_id = st.number_input("Enter Candidate ID", min_value=1, value=1, key="app_candidate_id")
        
        if st.button("Load Applications", key="load_candidate_apps"):
            applications = make_api_request(f"/applications/candidate/{candidate_id}")
            
            if applications:
                st.success(f"Found {len(applications)} applications")
                
                for app in applications:
                    if isinstance(app, dict):
                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.write(f"**{app.get('internship_title', 'N/A')}** at {app.get('company_name', 'N/A')}")
                                st.write(f"Location: {app.get('location', 'N/A')}")
                                applied_at = app.get('applied_at', '')
                                if applied_at and len(applied_at) >= 10:
                                    st.write(f"Applied: {applied_at[:10]}")
                                else:
                                    st.write("Applied: N/A")
                                st.write(f"Status: {app.get('status', 'N/A')}")
                            
                            with col2:
                                st.write("**Match Scores:**")
                                overall_score = app.get('overall_score', 0)
                                if isinstance(overall_score, (int, float)):
                                    st.write(f"Overall: {overall_score:.2f}")
                                else:
                                    st.write("Overall: N/A")
                                
                                skill_score = app.get('skill_match_score', 0)
                                if isinstance(skill_score, (int, float)):
                                    st.write(f"Skills: {skill_score:.2f}")
                                else:
                                    st.write("Skills: N/A")
                                
                                qual_score = app.get('qualification_match_score', 0)
                                if isinstance(qual_score, (int, float)):
                                    st.write(f"Qualifications: {qual_score:.2f}")
                                else:
                                    st.write("Qualifications: N/A")
                            
                            with col3:
                                st.write("**AI Recommendation:**")
                                recommendation = app.get('ai_recommendation', 'N/A') if isinstance(app, dict) else 'N/A'
                                st.write(f"{recommendation}")
                                confidence = app.get('recommendation_confidence') if isinstance(app, dict) else None
                                if confidence and isinstance(confidence, (int, float)):
                                    st.write(f"Confidence: {confidence:.2f}")
                            
                            app_id = app.get('id', 0)
                            if st.button(f"View Details", key=f"view_app_{app_id}"):
                                with st.expander("Application Details", expanded=True):
                                    st.write("**AI Reasoning:**")
                                    st.write(app.get('ai_reasoning', 'No reasoning provided'))
                                    
                                    cover_letter = app.get('cover_letter') if isinstance(app, dict) else None
                                    if cover_letter:
                                        st.write("**Cover Letter:**")
                                        st.write(cover_letter)
                        
                        st.markdown("---")
            else:
                st.info("No applications found for this candidate.")
    
    with tab2:
        st.subheader("View Applications by Internship")
        internship_id = st.number_input("Enter Internship ID", min_value=1, value=1, key="app_internship_id")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Applications", key="load_internship_apps"):
                applications = make_api_request(f"/applications/internship/{internship_id}")
                st.session_state.internship_applications = applications
        
        with col2:
            if st.button("View Diversity Analytics", key="load_diversity"):
                analytics = make_api_request(f"/analytics/diversity/{internship_id}")
                st.session_state.diversity_analytics = analytics
        
        # Display applications
        if hasattr(st.session_state, 'internship_applications') and st.session_state.internship_applications:
            applications = st.session_state.internship_applications
            st.success(f"Found {len(applications)} applications")
            
            # Create a DataFrame for better display
            app_data = []
            for app in applications:
                if isinstance(app, dict):
                    overall_score = app.get('overall_score', 0)
                    skill_score = app.get('skill_match_score', 0)
                    applied_at = app.get('applied_at', '')
                    
                    app_data.append({
                        "Candidate": app.get('candidate_name', 'N/A'),
                        "Email": app.get('candidate_email', 'N/A'),
                        "Category": app.get('social_category', 'N/A'),
                        "Area": app.get('area_type', 'N/A'),
                        "Overall Score": round(float(overall_score), 3) if isinstance(overall_score, (int, float)) else 0.0,
                        "Skills Score": round(float(skill_score), 3) if isinstance(skill_score, (int, float)) else 0.0,
                        "AI Recommendation": app.get('ai_recommendation', 'N/A'),
                        "Status": app.get('status', 'N/A'),
                        "Applied Date": applied_at[:10] if applied_at and len(applied_at) >= 10 else 'N/A'
                    })
            
            if app_data:
                df = pd.DataFrame(app_data)
                st.dataframe(df, use_container_width=True)
                
                # Sort by overall score
                if st.button("Sort by Best Matches"):
                    sorted_df = df.sort_values("Overall Score", ascending=False)
                    st.dataframe(sorted_df, use_container_width=True)
        
        # Display diversity analytics
        if hasattr(st.session_state, 'diversity_analytics') and st.session_state.diversity_analytics:
            analytics = st.session_state.diversity_analytics
            
            st.subheader("📊 Diversity Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Applications", analytics['total_applications'])
                
                # Social category distribution
                category_data = analytics['social_category_distribution']
                if category_data:
                    fig = px.pie(
                        values=[data['count'] for data in category_data.values()],
                        names=list(category_data.keys()),
                        title="Social Category Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Area type distribution
                area_data = analytics['area_type_distribution']
                if area_data:
                    fig = px.bar(
                        x=list(area_data.keys()),
                        y=[data['count'] for data in area_data.values()],
                        title="Rural vs Urban Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Special categories
                st.metric("First Generation Graduates", 
                         f"{analytics['first_generation_graduates']['count']} ({analytics['first_generation_graduates']['percentage']}%)")
                st.metric("First-time Applicants", 
                         f"{analytics['first_time_applicants']['count']} ({analytics['first_time_applicants']['percentage']}%)")

def render_matching_page():
    st.markdown("<h1 class='main-header'>🔍 Find Internship Matches</h1>", unsafe_allow_html=True)

    # Check if we have resume-based results
    if 'resume_matches' in st.session_state:
        st.success("🎯 Showing results from your uploaded resume!")
        resume_data = st.session_state['resume_matches']
        
        # Extract data
        candidate_data = resume_data['candidate_data']
        matches_data = resume_data['matches']
        candidate_id = resume_data['candidate_id']
        
        # Display candidate info
        st.subheader(f"👤 Results for {candidate_data['name']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Education", f"{candidate_data['education_level']} in {candidate_data['field_of_study']}")
        with col2:
            st.metric("Skills Count", len(candidate_data['skills']))
        with col3:
            st.metric("Location", candidate_data['current_location'])
        
        # Show skills
        st.write("**🔧 Your Skills:**")
        skills_cols = st.columns(4)
        for i, skill in enumerate(candidate_data['skills']):
            with skills_cols[i % 4]:
                st.write(f"• {skill}")
        
        # Clear button and refresh button
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Clear Resume Results & Start Fresh"):
                del st.session_state['resume_matches']
                if 'current_matches' in st.session_state:
                    del st.session_state['current_matches']
                if 'current_candidate_id' in st.session_state:
                    del st.session_state['current_candidate_id']
                st.rerun()
        
        with col_btn2:
            if st.button("🔄 Refresh Matches"):
                # Get fresh matches from API
                with st.spinner("🔍 Getting latest matches..."):
                    fresh_matches = make_api_request(f"/matches/candidate/{candidate_id}")
                    if fresh_matches:
                        # Update matches data with fresh results
                        if isinstance(fresh_matches, dict) and 'matches' in fresh_matches:
                            matches_data = fresh_matches['matches']
                        elif isinstance(fresh_matches, list):
                            matches_data = fresh_matches
                        else:
                            matches_data = fresh_matches
                        
                        # Update the resume_matches with fresh data
                        st.session_state.resume_matches['matches'] = matches_data
                        st.success("✅ Matches refreshed with latest filtering!")
                        st.rerun()
        
        st.markdown("---")
        
        # Store the matches data for display
        st.session_state['current_matches'] = matches_data
        st.session_state['current_candidate_id'] = candidate_id
        
        # Display the matches
        if matches_data:
            # Handle different response formats from API
            actual_matches = []
            if isinstance(matches_data, dict):
                if 'matches' in matches_data:
                    actual_matches = matches_data['matches']
                elif 'data' in matches_data:
                    actual_matches = matches_data['data']
                else:
                    # Single match in dict format
                    actual_matches = [matches_data]
            elif isinstance(matches_data, list):
                actual_matches = matches_data
            
            if actual_matches:
                st.subheader(f"🎯 Your Internship Matches ({len(actual_matches)} found)")
                for i, match in enumerate(actual_matches):
                    if isinstance(match, dict):
                        match['_match_index'] = f"resume_{i}"  # Add unique index
                        display_match_card(match, is_candidate_view=True)
                        st.markdown("---")
            else:
                st.info("🔍 No relevant matches found. Try refreshing to get latest results.")
        else:
            st.info("No matches found for your profile.")
    
    # Manual candidate ID input section
    st.subheader("🔍 Or Find Matches by Candidate ID")
    candidate_id = st.number_input("Enter your Candidate ID", min_value=1, step=1, key="match_candidate_id")
    
    if st.button("Find Matches", key="find_matches_btn"):
        with st.spinner("🔍 Finding your internship matches..."):
            matches_response = make_api_request(f"/matches/candidate/{candidate_id}")
            
        if matches_response:
            # Handle wrapped response
            matches = []
            if isinstance(matches_response, dict):
                if 'data' in matches_response:
                    matches = matches_response['data']
                elif 'matches' in matches_response:
                    matches = matches_response['matches']
                else:
                    # Assume the whole response is a single match or list of matches
                    matches = [matches_response] if isinstance(matches_response, dict) else []
            elif isinstance(matches_response, list):
                matches = matches_response
            
            if matches:
                st.success(f"Found {len(matches)} internship matches for Candidate ID {candidate_id}")
                st.session_state.current_candidate_id = candidate_id  # Store for AI analysis
                st.session_state.current_matches = matches  # Store matches
                
                for i, match in enumerate(matches):
                    if isinstance(match, dict):
                        match['_match_index'] = f"manual_{i}"  # Add unique index
                        display_match_card(match, is_candidate_view=True)
                        st.markdown("---")
            else:
                st.info("No matches found for this candidate ID.")
        else:
            st.error("No matches found or invalid Candidate ID. Please check if the candidate ID exists.")
    
    # Display current matches if available (from manual search ONLY - not when resume results exist)
    if 'current_matches' in st.session_state and 'resume_matches' not in st.session_state:
        matches = st.session_state['current_matches']
        candidate_id = st.session_state.get('current_candidate_id')
        
        if matches and candidate_id:
            st.subheader(f"🎯 Matches for Candidate ID {candidate_id}")
            
            for i, match in enumerate(matches):
                if isinstance(match, dict):
                    match['_match_index'] = f"stored_{i}"  # Add unique index
                    display_match_card(match, is_candidate_view=True)
                    st.markdown("---")

def render_analytics_page():
    st.markdown("<h1 class='main-header'>📊 Platform Analytics</h1>", unsafe_allow_html=True)
    
    # Get data for analytics
    candidates_response = make_api_request("/candidates/")
    companies_response = make_api_request("/companies/")
    internships_response = make_api_request("/internships/")
    
    # Extract data from response - handle both direct lists and wrapped responses
    candidates_data = []
    if candidates_response:
        if isinstance(candidates_response, list):
            candidates_data = candidates_response
        elif isinstance(candidates_response, dict) and 'data' in candidates_response:
            candidates_data = candidates_response['data']
        elif isinstance(candidates_response, dict):
            candidates_data = list(candidates_response.values()) if candidates_response else []
    
    companies_data = []
    if companies_response:
        if isinstance(companies_response, list):
            companies_data = companies_response
        elif isinstance(companies_response, dict) and 'data' in companies_response:
            companies_data = companies_response['data']
        elif isinstance(companies_response, dict):
            companies_data = list(companies_response.values()) if companies_response else []
    
    internships_data = []
    if internships_response:
        if isinstance(internships_response, list):
            internships_data = internships_response
        elif isinstance(internships_response, dict) and 'data' in internships_response:
            internships_data = internships_response['data']
        elif isinstance(internships_response, dict):
            internships_data = list(internships_response.values()) if internships_response else []
    
    if not any([candidates_data, companies_data, internships_data]):
        st.error("Unable to load analytics data. Please ensure the backend is running.")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", len(candidates_data))
    with col2:
        st.metric("Total Companies", len(companies_data))
    with col3:
        st.metric("Total Internships", len(internships_data))
    with col4:
        # Filter active internships safely
        active_internships = []
        for i in internships_data:
            if isinstance(i, dict) and i.get('is_active', True):
                active_internships.append(i)
        st.metric("Active Internships", len(active_internships))
    
    st.markdown("---")
    
    if not candidates_data:
        st.info("No candidate data available yet.")
        return
    
    # Candidate analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Candidate Demographics")
        
        # Social category distribution
        categories = []
        for c in candidates_data:
            if isinstance(c, dict):
                categories.append(c.get('social_category', 'Unknown'))
        
        if categories:
            category_counts = pd.Series(categories).value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Social Category Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Area type distribution
        areas = []
        for c in candidates_data:
            if isinstance(c, dict):
                areas.append(c.get('area_type', 'Unknown'))
        
        if areas:
            area_counts = pd.Series(areas).value_counts()
            fig = px.bar(
                x=area_counts.index,
                y=area_counts.values,
                title="Rural vs Urban Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Company & Internship Analytics")
        
        if companies_data:
            # Industry distribution
            industries = []
            for c in companies_data:
                if isinstance(c, dict):
                    industries.append(c.get('industry', 'Unknown'))
            
            if industries:
                industry_counts = pd.Series(industries).value_counts()
                fig = px.bar(
                    x=industry_counts.values,
                    y=industry_counts.index,
                    orientation='h',
                    title="Companies by Industry"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        if internships_data:
            # Internship locations
            locations = []
            for i in internships_data:
                if isinstance(i, dict):
                    locations.append(i.get('location', 'Unknown'))
            
            if locations:
                location_counts = pd.Series(locations).value_counts().head(10)
            
            if not location_counts.empty:
                fig = px.bar(
                    x=location_counts.index,
                    y=location_counts.values,
                    title="Top 10 Internship Locations"
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
    
    # Skills analysis
    st.subheader("🛠️ Skills Analysis")
    
    all_skills = []
    for candidate in candidates_data:
        if isinstance(candidate, dict):
            skills = candidate.get('skills', [])
            if isinstance(skills, list):
                all_skills.extend([skill.lower() for skill in skills])
            elif isinstance(skills, str):
                try:
                    skills_list = json.loads(skills)
                    all_skills.extend([skill.lower() for skill in skills_list])
                except:
                    pass
    
    if all_skills:
        skills_counts = pd.Series(all_skills).value_counts().head(20)
        
        fig = px.bar(
            x=skills_counts.values,
            y=skills_counts.index,
            orientation='h',
            title="Top 20 Most Common Skills"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Diversity metrics
    st.subheader("⚖️ Diversity Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        first_gen_count = 0
        for c in candidates_data:
            if isinstance(c, dict) and c.get('is_first_generation_graduate', False):
                first_gen_count += 1
        first_gen_percentage = (first_gen_count / len(candidates_data)) * 100 if candidates_data else 0
        st.metric("First Generation Graduates", f"{first_gen_count} ({first_gen_percentage:.1f}%)")
    
    with col2:
        first_internship_count = 0
        for c in candidates_data:
            if isinstance(c, dict) and c.get('previous_internships_count', 0) == 0:
                first_internship_count += 1
        first_internship_percentage = (first_internship_count / len(candidates_data)) * 100 if candidates_data else 0
        st.metric("First-time Applicants", f"{first_internship_count} ({first_internship_percentage:.1f}%)")
    
    with col3:
        rural_count = 0
        for c in candidates_data:
            if isinstance(c, dict) and c.get('area_type') == 'RURAL':
                rural_count += 1
        rural_percentage = (rural_count / len(candidates_data)) * 100 if candidates_data else 0
        st.metric("Rural Candidates", f"{rural_count} ({rural_percentage:.1f}%)")

if __name__ == "__main__":
    main()
