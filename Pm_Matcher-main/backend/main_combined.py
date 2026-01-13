import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.embeddings import EmbeddingManager
from utils.ai_integration import GroqAIManager

# Initialize managers
embedding_manager = EmbeddingManager()
ai_manager = GroqAIManager()

app = FastAPI(
    title="Internship Matcher API", 
    description="AI-powered internship matching with affirmative action",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data stores with embeddings
candidates_db = []
companies_db = []
internships_db = []
applications_db = []

# Pydantic models
class CandidateCreate(BaseModel):
    email: str
    name: str
    phone: str
    education_level: str
    field_of_study: str
    cgpa: Optional[str] = None
    graduation_year: int
    institution: Optional[str] = None
    skills: List[str]
    experience_months: int = 0
    projects: List[str] = []
    preferred_locations: List[str] = []
    current_location: str
    willing_to_relocate: bool = True
    social_category: str
    area_type: str
    state: str
    district: str
    is_first_generation_graduate: bool = False
    family_income_annual: Optional[float] = None
    previous_internships_count: int = 0
    previous_internship_companies: List[str] = []

@app.on_event("startup")
async def initialize_system():
    """Initialize the system with mock data"""
    print("🚀 Starting Advanced Internship Matcher API...")
    print("🔧 Initializing Embedding System...")
    
    # Test embeddings
    test_embedding = embedding_manager.generate_skills_embedding(["Python", "Machine Learning"])
    print(f"✅ Embeddings working! Dimension: {len(test_embedding)}")
    
    # Test AI
    try:
        test_response = ai_manager.generate_internship_recommendation({}, {}, {})
        print("✅ AI Integration working!")
    except Exception as e:
        print(f"⚠️ AI Integration issue: {e}")
    
    # Initialize mock data
    initialize_mock_data()
    print("📊 Mock data initialized successfully!")
    print(f"📍 API Documentation: http://localhost:8002/docs")

def initialize_mock_data():
    """Initialize comprehensive mock data with embeddings"""
    
    # Mock companies
    mock_companies = [
        {
            "id": 1,
            "name": "TechCorp India",
            "industry": "Information Technology",
            "description": "Leading IT services company with focus on innovation and diversity",
            "headquarters": "Bangalore, Karnataka",
            "locations": ["Bangalore", "Mumbai", "Chennai", "Hyderabad"],
            "total_internship_capacity": 25,
            "diversity_commitment": 0.35,
            "rural_quota": 0.25,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 2,
            "name": "StartupXYZ",
            "industry": "E-commerce",
            "description": "Fast-growing e-commerce startup focused on rural markets",
            "headquarters": "Mumbai, Maharashtra",
            "locations": ["Mumbai", "Pune", "Delhi"],
            "total_internship_capacity": 15,
            "diversity_commitment": 0.40,
            "rural_quota": 0.30,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 3,
            "name": "DataTech Solutions",
            "industry": "Data Analytics",
            "description": "Data analytics and AI solutions company",
            "headquarters": "Chennai, Tamil Nadu",
            "locations": ["Chennai", "Bangalore", "Coimbatore"],
            "total_internship_capacity": 20,
            "diversity_commitment": 0.32,
            "rural_quota": 0.20,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 4,
            "name": "GreenTech Innovations",
            "industry": "Renewable Energy",
            "description": "Clean energy and sustainable technology company",
            "headquarters": "Pune, Maharashtra",
            "locations": ["Pune", "Mumbai", "Ahmedabad"],
            "total_internship_capacity": 12,
            "diversity_commitment": 0.38,
            "rural_quota": 0.28,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 5,
            "name": "FinanceMax",
            "industry": "Financial Services",
            "description": "Digital banking and financial services company",
            "headquarters": "Mumbai, Maharashtra",
            "locations": ["Mumbai", "Delhi", "Bangalore"],
            "total_internship_capacity": 18,
            "diversity_commitment": 0.30,
            "rural_quota": 0.22,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 6,
            "name": "Creative Arts Studio",
            "industry": "Creative Arts",
            "description": "Digital art and design studio creating content for media and advertising",
            "headquarters": "Mumbai, Maharashtra",
            "locations": ["Mumbai", "Delhi"],
            "total_internship_capacity": 8,
            "diversity_commitment": 0.35,
            "rural_quota": 0.25,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 7,
            "name": "Sports Excellence Academy",
            "industry": "Sports & Fitness",
            "description": "Sports training and management academy developing athletic talent",
            "headquarters": "Pune, Maharashtra",
            "locations": ["Pune", "Mumbai", "Delhi"],
            "total_internship_capacity": 10,
            "diversity_commitment": 0.40,
            "rural_quota": 0.30,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 8,
            "name": "Culinary Innovations",
            "industry": "Food & Hospitality",
            "description": "Restaurant chain and culinary institute promoting Indian cuisine globally",
            "headquarters": "Delhi, India",
            "locations": ["Delhi", "Mumbai", "Bangalore"],
            "total_internship_capacity": 12,
            "diversity_commitment": 0.32,
            "rural_quota": 0.25,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 9,
            "name": "Music Production House",
            "industry": "Entertainment",
            "description": "Music production and recording studio working with independent and commercial artists",
            "headquarters": "Chennai, Tamil Nadu",
            "locations": ["Chennai", "Mumbai"],
            "total_internship_capacity": 6,
            "diversity_commitment": 0.35,
            "rural_quota": 0.30,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        },
        {
            "id": 10,
            "name": "Agricultural Research Institute",
            "industry": "Agriculture",
            "description": "Research organization developing sustainable farming technologies and practices",
            "headquarters": "Bangalore, Karnataka",
            "locations": ["Bangalore", "Chennai", "Pune"],
            "total_internship_capacity": 15,
            "diversity_commitment": 0.45,
            "rural_quota": 0.40,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}
        }
    ]
    
    # Mock internships with embeddings
    mock_internships = [
        {
            "id": 1,
            "company_id": 1,
            "company_name": "TechCorp India",
            "industry": "Information Technology",
            "title": "Software Development Intern",
            "description": "Work on cutting-edge web applications using modern frameworks. Gain hands-on experience with full-stack development, work with senior developers, and contribute to real projects that impact millions of users.",
            "required_skills": ["Python", "JavaScript", "React", "SQL", "Git"],
            "required_skills_embedding": None,  # Will be generated
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Information Technology", "Software Engineering"],
            "min_cgpa": 7.0,
            "experience_required": False,
            "location": "Bangalore, Karnataka",
            "is_remote": True,
            "duration_months": 6,
            "start_date": "2024-01-15",
            "application_deadline": "2023-12-15",
            "stipend_amount": 25000,
            "total_positions": 5,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 1},
            "previous_participants": [
                {"name": "Priya Sharma", "category": "SC", "area": "RURAL", "performance": "Excellent", "year": "2023"},
                {"name": "Amit Kumar", "category": "OC", "area": "URBAN", "performance": "Good", "year": "2023"},
                {"name": "Rakesh Singh", "category": "BC", "area": "SEMI_URBAN", "performance": "Very Good", "year": "2022"}
            ]
        },
        {
            "id": 2,
            "company_id": 2,
            "company_name": "StartupXYZ",
            "industry": "E-commerce",
            "title": "Digital Marketing Intern",
            "description": "Join our marketing team to create compelling campaigns for rural markets. Learn digital marketing strategies, social media management, and data-driven marketing approaches.",
            "required_skills": ["Digital Marketing", "Social Media", "Content Writing", "Analytics", "SEO"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Marketing", "Business Administration", "Communications", "Mass Media"],
            "min_cgpa": 6.5,
            "experience_required": False,
            "location": "Mumbai, Maharashtra",
            "is_remote": False,
            "duration_months": 4,
            "start_date": "2024-02-01",
            "application_deadline": "2023-12-30",
            "stipend_amount": 20000,
            "total_positions": 3,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 0, "ST": 1, "BC": 1, "rural": 1},
            "previous_participants": [
                {"name": "Sunita Patel", "category": "ST", "area": "RURAL", "performance": "Excellent", "year": "2023"},
                {"name": "Karan Mehta", "category": "OC", "area": "URBAN", "performance": "Good", "year": "2023"}
            ]
        },
        {
            "id": 3,
            "company_id": 3,
            "company_name": "DataTech Solutions",
            "industry": "Data Analytics",
            "title": "Data Science Intern",
            "description": "Dive deep into machine learning and data analytics. Work with real datasets, build predictive models, and learn from experienced data scientists.",
            "required_skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "Statistics"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Statistics", "Mathematics", "Data Science"],
            "min_cgpa": 7.5,
            "experience_required": False,
            "location": "Chennai, Tamil Nadu",
            "is_remote": True,
            "duration_months": 6,
            "start_date": "2024-01-20",
            "application_deadline": "2023-12-20",
            "stipend_amount": 30000,
            "total_positions": 4,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 1},
            "previous_participants": [
                {"name": "Meera Reddy", "category": "BC", "area": "RURAL", "performance": "Outstanding", "year": "2023"},
                {"name": "Vikram Gupta", "category": "OC", "area": "URBAN", "performance": "Very Good", "year": "2023"},
                {"name": "Arjun Das", "category": "SC", "area": "SEMI_URBAN", "performance": "Good", "year": "2022"}
            ]
        },
        {
            "id": 4,
            "company_id": 4,
            "company_name": "GreenTech Innovations",
            "industry": "Renewable Energy",
            "title": "Renewable Energy Research Intern",
            "description": "Research and develop sustainable energy solutions. Work on solar panel efficiency, wind energy optimization, and energy storage technologies.",
            "required_skills": ["Research", "Solar Energy", "Wind Energy", "Data Analysis", "Technical Writing"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Electrical Engineering", "Mechanical Engineering", "Environmental Science", "Physics"],
            "min_cgpa": 7.0,
            "experience_required": False,
            "location": "Pune, Maharashtra",
            "is_remote": False,
            "duration_months": 5,
            "start_date": "2024-02-15",
            "application_deadline": "2024-01-10",
            "stipend_amount": 22000,
            "total_positions": 3,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 1},
            "previous_participants": [
                {"name": "Pooja Yadav", "category": "BC", "area": "RURAL", "performance": "Excellent", "year": "2023"}
            ]
        },
        {
            "id": 5,
            "company_id": 5,
            "company_name": "FinanceMax",
            "industry": "Financial Services",
            "title": "Financial Technology Intern",
            "description": "Work on fintech applications, payment gateways, and blockchain technology. Learn about digital banking and financial data analysis.",
            "required_skills": ["Java", "Blockchain", "Financial Analysis", "Database Management", "API Development"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Finance", "Economics", "Information Technology"],
            "min_cgpa": 7.2,
            "experience_required": False,
            "location": "Mumbai, Maharashtra",
            "is_remote": True,
            "duration_months": 4,
            "start_date": "2024-03-01",
            "application_deadline": "2024-01-25",
            "stipend_amount": 28000,
            "total_positions": 4,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 1},
            "previous_participants": [
                {"name": "Rohit Kumar", "category": "SC", "area": "RURAL", "performance": "Very Good", "year": "2023"},
                {"name": "Neha Agarwal", "category": "OC", "area": "URBAN", "performance": "Good", "year": "2023"}
            ]
        },
        {
            "id": 6,
            "company_id": 1,
            "company_name": "TechCorp India",
            "industry": "Information Technology",
            "title": "Mobile App Development Intern",
            "description": "Develop mobile applications for Android and iOS platforms. Learn Flutter, React Native, and native development while working on user-centric apps.",
            "required_skills": ["Flutter", "React Native", "Mobile Development", "UI/UX Design", "Firebase"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Information Technology", "Mobile Computing"],
            "min_cgpa": 6.8,
            "experience_required": False,
            "location": "Hyderabad, Telangana",
            "is_remote": True,
            "duration_months": 5,
            "start_date": "2024-02-10",
            "application_deadline": "2024-01-05",
            "stipend_amount": 24000,
            "total_positions": 4,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 1, "BC": 1, "rural": 1},
            "previous_participants": [
                {"name": "Anjali Singh", "category": "ST", "area": "RURAL", "performance": "Outstanding", "year": "2023"},
                {"name": "Deepak Joshi", "category": "OC", "area": "URBAN", "performance": "Very Good", "year": "2023"}
            ]
        },
        {
            "id": 7,
            "company_id": 6,
            "company_name": "Creative Arts Studio",
            "industry": "Creative Arts",
            "title": "Digital Art & Design Intern",
            "description": "Create digital artwork, illustrations, and graphic designs. Work on creative projects for advertising, web design, and multimedia content.",
            "required_skills": ["Graphic Design", "Adobe Photoshop", "Adobe Illustrator", "Digital Art", "Creative Thinking"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Fine Arts", "Graphic Design", "Visual Arts", "Multimedia"],
            "min_cgpa": 6.0,
            "experience_required": False,
            "location": "Mumbai, Maharashtra",
            "is_remote": True,
            "duration_months": 3,
            "start_date": "2024-03-01",
            "application_deadline": "2024-02-01",
            "stipend_amount": 15000,
            "total_positions": 3,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 1},
            "previous_participants": []
        },
        {
            "id": 8,
            "company_id": 7,
            "company_name": "Sports Excellence Academy",
            "industry": "Sports & Fitness",
            "title": "Sports Management Intern",
            "description": "Learn sports administration, event management, and athlete development. Assist in organizing tournaments and managing sports facilities.",
            "required_skills": ["Sports Management", "Event Planning", "Team Leadership", "Physical Fitness", "Communication"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Sports Science", "Physical Education", "Management", "Recreation"],
            "min_cgpa": 6.5,
            "experience_required": False,
            "location": "Pune, Maharashtra",
            "is_remote": False,
            "duration_months": 4,
            "start_date": "2024-04-01",
            "application_deadline": "2024-03-01",
            "stipend_amount": 18000,
            "total_positions": 4,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 1, "BC": 1, "rural": 1},
            "previous_participants": []
        },
        {
            "id": 9,
            "company_id": 8,
            "company_name": "Culinary Innovations",
            "industry": "Food & Hospitality",
            "title": "Culinary Arts Intern",
            "description": "Learn professional cooking techniques, menu development, and restaurant operations. Work in a professional kitchen environment.",
            "required_skills": ["Cooking", "Food Safety", "Menu Planning", "Kitchen Management", "Creativity"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Hotel Management", "Culinary Arts", "Food Technology", "Hospitality"],
            "min_cgpa": 6.0,
            "experience_required": False,
            "location": "Delhi, India",
            "is_remote": False,
            "duration_months": 6,
            "start_date": "2024-03-15",
            "application_deadline": "2024-02-15",
            "stipend_amount": 20000,
            "total_positions": 3,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 1},
            "previous_participants": []
        },
        {
            "id": 10,
            "company_id": 9,
            "company_name": "Music Production House",
            "industry": "Entertainment",
            "title": "Music Production Intern",
            "description": "Learn music production, sound engineering, and audio editing. Work with recording artists and create commercial music tracks.",
            "required_skills": ["Music Production", "Audio Engineering", "Sound Design", "Recording", "Creative Arts"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Music", "Audio Engineering", "Media Studies", "Fine Arts"],
            "min_cgpa": 6.0,
            "experience_required": False,
            "location": "Chennai, Tamil Nadu",
            "is_remote": False,
            "duration_months": 4,
            "start_date": "2024-05-01",
            "application_deadline": "2024-04-01",
            "stipend_amount": 22000,
            "total_positions": 2,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 0, "ST": 1, "BC": 0, "rural": 1},
            "previous_participants": []
        },
        {
            "id": 11,
            "company_id": 10,
            "company_name": "Agricultural Research Institute",
            "industry": "Agriculture",
            "title": "Agricultural Technology Intern",
            "description": "Research modern farming techniques, crop optimization, and sustainable agriculture practices. Work on IoT solutions for farming.",
            "required_skills": ["Agriculture", "Research", "Data Analysis", "IoT", "Sustainability"],
            "required_skills_embedding": None,
            "min_education_level": "UG",
            "preferred_fields": ["Agriculture", "Biotechnology", "Environmental Science", "Engineering"],
            "min_cgpa": 7.0,
            "experience_required": False,
            "location": "Bangalore, Karnataka",
            "is_remote": False,
            "duration_months": 5,
            "start_date": "2024-06-01",
            "application_deadline": "2024-04-30",
            "stipend_amount": 25000,
            "total_positions": 3,
            "filled_positions": 0,
            "is_active": True,
            "reserved_positions": {"SC": 1, "ST": 1, "BC": 1, "rural": 2},
            "previous_participants": []
        }
    ]
    
    # Generate embeddings for internships
    for internship in mock_internships:
        skills_embedding = embedding_manager.generate_skills_embedding(internship["required_skills"])
        internship["required_skills_embedding"] = skills_embedding
    
    # Store data
    companies_db.extend(mock_companies)
    internships_db.extend(mock_internships)

@app.post("/candidates/", response_model=dict)
def create_candidate(candidate: CandidateCreate):
    """Create a new candidate profile with embeddings"""
    
    # Check if email already exists
    existing = next((c for c in candidates_db if c["email"] == candidate.email), None)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate embeddings for skills
    skills_embedding = embedding_manager.generate_skills_embedding(candidate.skills)
    
    # Convert CGPA to float if possible
    cgpa_float = None
    if candidate.cgpa:
        try:
            cgpa_float = float(candidate.cgpa)
        except:
            cgpa_float = None
    
    # Create candidate record
    candidate_data = {
        "id": len(candidates_db) + 1,
        "email": candidate.email,
        "name": candidate.name,
        "phone": candidate.phone,
        "education_level": candidate.education_level,
        "field_of_study": candidate.field_of_study,
        "cgpa": cgpa_float,
        "graduation_year": candidate.graduation_year,
        "institution": candidate.institution,
        "skills": candidate.skills,
        "skills_embedding": skills_embedding,
        "experience_months": candidate.experience_months,
        "projects": candidate.projects,
        "preferred_locations": candidate.preferred_locations,
        "current_location": candidate.current_location,
        "willing_to_relocate": candidate.willing_to_relocate,
        "social_category": candidate.social_category,
        "area_type": candidate.area_type,
        "state": candidate.state,
        "district": candidate.district,
        "is_first_generation_graduate": candidate.is_first_generation_graduate,
        "family_income_annual": candidate.family_income_annual,
        "previous_internships_count": candidate.previous_internships_count,
        "previous_internship_companies": candidate.previous_internship_companies,
        "created_at": datetime.now().isoformat()
    }
    
    candidates_db.append(candidate_data)
    
    return {"candidate_id": candidate_data["id"], "message": "Candidate registered successfully"}

def get_trending_skills_by_industry():
    """Return trending skills by industry"""
    return {
        "Information Technology": ["Python", "JavaScript", "React", "Cloud Computing", "DevOps"],
        "Data Analytics": ["Machine Learning", "SQL", "Python", "Statistics", "Data Visualization"],
        "Creative Arts": ["Graphic Design", "Video Editing", "Adobe Creative Suite", "UI/UX Design"],
        "Sports & Fitness": ["Sports Analytics", "Digital Marketing", "Event Management", "Health Technology"],
        "Food & Hospitality": ["Food Technology", "Restaurant Management", "Digital Marketing", "Supply Chain"],
        "Entertainment": ["Audio Engineering", "Video Production", "Streaming Technology", "Social Media"],
        "Agriculture": ["Precision Agriculture", "IoT", "Data Analysis", "Sustainability"]
    }

def get_alternative_career_paths(candidate_skills):
    """Suggest alternative career paths based on candidate skills"""
    skill_keywords = [skill.lower() for skill in candidate_skills]
    
    if any(word in skill_keywords for word in ["art", "design", "creative", "painting", "music"]):
        return ["UI/UX Design", "Digital Marketing", "Content Creation", "Media Production"]
    elif any(word in skill_keywords for word in ["sport", "fitness", "physical", "coaching"]):
        return ["Sports Analytics", "Event Management", "Health Technology", "Digital Marketing"]
    elif any(word in skill_keywords for word in ["cooking", "food", "culinary", "kitchen"]):
        return ["Food Technology", "Restaurant Management", "Supply Chain", "Hospitality Technology"]
    else:
        return ["Digital Marketing", "Data Entry", "Customer Service", "Administrative Support"]

@app.get("/matches/candidate/{candidate_id}")
def get_candidate_matches(candidate_id: int):
    """Get AI-powered internship matches for a candidate using embeddings"""
    
    # Get candidate
    candidate = next((c for c in candidates_db if c["id"] == candidate_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    matches = []
    candidate_embedding = candidate["skills_embedding"]
    
    # Define minimum skill similarity threshold for "relevant" matches
    RELEVANT_MATCH_THRESHOLD = 0.50  # Increased threshold for better relevance - only show truly relevant matches
    relevant_matches = []
    
    for internship in internships_db:
        if internship.get("is_active", True):
            
            # Calculate embedding-based skill similarity
            internship_embedding = internship["required_skills_embedding"]
            skill_similarity = embedding_manager.calculate_similarity(candidate_embedding, internship_embedding)
            
            print(f"🔍 Matching {candidate['name']} with {internship['title']}")
            print(f"   Skills similarity: {skill_similarity:.3f}")
            
            # Location matching
            location_match = 0.5  # Default
            if candidate.get("current_location", "").lower() in internship.get("location", "").lower():
                location_match = 1.0
            elif candidate.get("willing_to_relocate", False):
                location_match = 0.8
            elif internship.get("is_remote", False):
                location_match = 0.9
            
            # Education/Qualification matching
            education_levels = {"Diploma": 1, "UG": 2, "Bachelor": 2, "PG": 3, "Master": 3, "PhD": 4, "Doctorate": 4}
            candidate_edu_level = education_levels.get(candidate.get("education_level", "UG"), 2)
            required_edu_level = education_levels.get(internship.get("min_education_level", "UG"), 2)
            qualification_match = 1.0 if candidate_edu_level >= required_edu_level else 0.7
            
            # CGPA boost
            if internship.get("min_cgpa", 0) > 0 and candidate.get("cgpa", 0):
                if candidate.get("cgpa", 0) >= internship.get("min_cgpa", 0):
                    qualification_match = min(qualification_match + 0.2, 1.0)
                else:
                    qualification_match *= 0.8
            
            # Affirmative action boost
            affirmative_boost = 0.0
            
            # Social category boost
            if candidate.get("social_category") in ["SC", "ST", "BC"]:
                affirmative_boost += 0.12
            
            # Rural area boost
            if candidate.get("area_type") == "RURAL":
                affirmative_boost += 0.08
            elif candidate.get("area_type") == "SEMI_URBAN":
                affirmative_boost += 0.04
            
            # First generation graduate boost
            if candidate.get("is_first_generation_graduate"):
                affirmative_boost += 0.06
            
            # First-time participant boost
            if candidate.get("previous_internships_count", 0) == 0:
                affirmative_boost += 0.15
            
            # Company diversity history boost
            previous_participants = internship.get("previous_participants", [])
            if previous_participants:
                diverse_participants = [p for p in previous_participants if p.get("category") in ["SC", "ST", "BC"] or p.get("area") == "RURAL"]
                diversity_ratio = len(diverse_participants) / len(previous_participants)
                if diversity_ratio > 0.4:
                    if candidate.get("social_category") in ["SC", "ST", "BC"] or candidate.get("area_type") == "RURAL":
                        affirmative_boost += 0.04
            
            # Calculate weighted overall score
            weights = {"skill": 0.4, "location": 0.2, "qualification": 0.25, "affirmative": 0.15}
            overall_score = (
                skill_similarity * weights["skill"] +
                location_match * weights["location"] +
                qualification_match * weights["qualification"] +
                affirmative_boost * weights["affirmative"]
            )
            
            match_percentage = min(int(overall_score * 100), 100)
            
            print(f"   Overall score: {overall_score:.3f} ({match_percentage}%)")
            
            # Check if this is a relevant match based on skill similarity
            if skill_similarity >= RELEVANT_MATCH_THRESHOLD:
                relevant_matches.append({
                    "internship": internship,
                    "skill_similarity": skill_similarity,
                    "match_percentage": match_percentage,
                    "overall_score": overall_score,
                    "affirmative_boost": affirmative_boost
                })
                
                # Add to main matches if it meets skill threshold (removed the 30% overall score check)
                # Use simple placeholders for main matching - real AI analysis is in verbose endpoint
                ai_recommendation = "✅ Recommended" if match_percentage > 70 else "🎯 Good Fit" if match_percentage > 50 else "💡 Consider"
                ai_reasoning = f"Match score: {match_percentage}% with {skill_similarity:.1%} skill alignment"
                recommendation_confidence = overall_score
                
                match_data = {
                    "internship": internship,
                    "match_percentage": match_percentage,
                    "embedding_similarity": skill_similarity,
                    "scores": {
                        "skill_similarity": skill_similarity,
                        "location_match": location_match,
                        "qualification_match": qualification_match,
                        "affirmative_action_boost": affirmative_boost,
                        "overall_score": overall_score
                    },
                    "ai_recommendation": ai_recommendation,
                    "ai_reasoning": ai_reasoning,
                    "recommendation_confidence": recommendation_confidence,
                    "weights_used": weights,
                    "has_verbose_analysis": True  # Indicates verbose analysis is available
                }
                
                matches.append(match_data)
    
    # Sort matches by overall score
    matches.sort(key=lambda x: x["scores"]["overall_score"], reverse=True)
    
    # Check if we have relevant matches
    result = {
        "candidate_id": candidate_id,
        "candidate_name": candidate.get("name", "Unknown"),
        "candidate_skills": candidate.get("skills", []),
        "total_matches_found": len(matches),
        "relevant_matches_count": len(relevant_matches),
        "skill_match_threshold": RELEVANT_MATCH_THRESHOLD
    }
    
    if len(relevant_matches) == 0:
        # No relevant matches found based on skill similarity
        result.update({
            "status": "no_relevant_matches",
            "message": "No relevant matches found based on your skills. Here are some alternative opportunities to consider:",
            "matches": matches[:3],  # Show top 3 alternatives
            "suggestions": {
                "message": "Consider developing skills in these areas to improve your match rates:",
                "recommended_skills": get_trending_skills_by_industry(),
                "alternative_fields": get_alternative_career_paths(candidate.get("skills", [])),
                "skill_development_resources": [
                    "Consider online courses in high-demand technical skills",
                    "Look for entry-level positions that offer training",
                    "Explore internships in adjacent fields that value transferable skills"
                ]
            }
        })
    else:
        # Good matches found - only return the relevant ones
        result.update({
            "status": "matches_found",
            "message": f"Found {len(relevant_matches)} relevant matches based on your skills!",
            "matches": matches  # This already contains only relevant matches from the filtering logic above
        })
    
    return result

# Other endpoints
@app.get("/candidates/")
def get_candidates():
    return candidates_db

@app.get("/companies/")
def get_companies():
    return companies_db

@app.get("/internships/")
def get_internships():
    return internships_db

@app.get("/internships/active")
def get_active_internships():
    return [i for i in internships_db if i.get("is_active", True)]

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "embeddings_loaded": hasattr(embedding_manager.model, 'get_sentence_embedding_dimension'),
        "ai_available": ai_manager is not None,
        "candidates": len(candidates_db),
        "internships": len(internships_db)
    }

@app.get("/test-embeddings")
def test_embeddings():
    """Test endpoint to show how embeddings work"""
    test_skills_1 = ["Python", "Machine Learning", "Data Science"]
    test_skills_2 = ["JavaScript", "React", "Frontend Development"]
    test_skills_3 = ["Python", "AI", "Deep Learning"]
    
    embedding_1 = embedding_manager.generate_skills_embedding(test_skills_1)
    embedding_2 = embedding_manager.generate_skills_embedding(test_skills_2)
    embedding_3 = embedding_manager.generate_skills_embedding(test_skills_3)
    
    similarity_1_2 = embedding_manager.calculate_similarity(embedding_1, embedding_2)
    similarity_1_3 = embedding_manager.calculate_similarity(embedding_1, embedding_3)
    
    return {
        "test_skills_1": test_skills_1,
        "test_skills_2": test_skills_2,
        "test_skills_3": test_skills_3,
        "embedding_dimension": len(embedding_1),
        "similarity_python_ml_vs_js_react": similarity_1_2,
        "similarity_python_ml_vs_python_ai": similarity_1_3,
        "explanation": f"Higher similarity ({similarity_1_3:.3f}) between Python/ML and Python/AI vs Python/ML and JS/React ({similarity_1_2:.3f})"
    }

@app.post("/test-candidate-profiles")
def test_different_candidate_profiles():
    """Test matching for different candidate profiles to show diversity and skill matching"""
    
    test_candidates = [
        {
            "name": "Arjun Kumar (Rural SC Student)",
            "skills": ["Python", "Machine Learning", "Data Analysis"],
            "social_category": "SC",
            "area_type": "RURAL",
            "current_location": "Village, Uttar Pradesh",
            "education_level": "UG",
            "field_of_study": "Computer Science",
            "cgpa": 7.8,
            "is_first_generation_graduate": True,
            "previous_internships_count": 0,
            "willing_to_relocate": True
        },
        {
            "name": "Priya Sharma (Urban General Category)",
            "skills": ["JavaScript", "React", "Node.js", "Frontend Development"],
            "social_category": "OC",
            "area_type": "URBAN",
            "current_location": "Mumbai, Maharashtra",
            "education_level": "UG",
            "field_of_study": "Information Technology",
            "cgpa": 8.5,
            "is_first_generation_graduate": False,
            "previous_internships_count": 2,
            "willing_to_relocate": False
        },
        {
            "name": "Ravi Patel (ST Student - Renewable Energy)",
            "skills": ["Research", "Solar Energy", "Data Analysis", "Technical Writing"],
            "social_category": "ST",
            "area_type": "SEMI_URBAN",
            "current_location": "Vadodara, Gujarat", 
            "education_level": "UG",
            "field_of_study": "Electrical Engineering",
            "cgpa": 7.2,
            "is_first_generation_graduate": True,
            "previous_internships_count": 0,
            "willing_to_relocate": True
        },
        {
            "name": "Meera Singh (BC Student - Finance)",
            "skills": ["Java", "Financial Analysis", "Database Management", "API Development"],
            "social_category": "BC",
            "area_type": "RURAL",
            "current_location": "Patna, Bihar",
            "education_level": "UG", 
            "field_of_study": "Computer Science",
            "cgpa": 8.0,
            "is_first_generation_graduate": True,
            "previous_internships_count": 0,
            "willing_to_relocate": True
        }
    ]
    
    results = []
    
    for candidate in test_candidates:
        # Generate embeddings for candidate skills
        candidate_embedding = embedding_manager.generate_skills_embedding(candidate["skills"])
        
        candidate_matches = []
        
        for internship in internships_db:
            if internship.get("is_active", True):
                
                # Calculate embedding-based skill similarity  
                internship_embedding = internship["required_skills_embedding"]
                skill_similarity = embedding_manager.calculate_similarity(candidate_embedding, internship_embedding)
                
                # Location matching
                location_match = 0.5
                if candidate.get("current_location", "").lower().split(',')[0].strip() in internship.get("location", "").lower():
                    location_match = 1.0
                elif candidate.get("willing_to_relocate", False):
                    location_match = 0.8
                elif internship.get("is_remote", False):
                    location_match = 0.9
                
                # Education/Qualification matching
                education_levels = {"Diploma": 1, "UG": 2, "Bachelor": 2, "PG": 3, "Master": 3, "PhD": 4, "Doctorate": 4}
                candidate_edu_level = education_levels.get(candidate.get("education_level", "UG"), 2)
                required_edu_level = education_levels.get(internship.get("min_education_level", "UG"), 2)
                qualification_match = 1.0 if candidate_edu_level >= required_edu_level else 0.7
                
                # CGPA boost
                if internship.get("min_cgpa", 0) > 0 and candidate.get("cgpa", 0):
                    if candidate.get("cgpa", 0) >= internship.get("min_cgpa", 0):
                        qualification_match = min(qualification_match + 0.2, 1.0)
                    else:
                        qualification_match *= 0.8
                
                # Affirmative action boost
                affirmative_boost = 0.0
                
                # Social category boost
                if candidate.get("social_category") in ["SC", "ST", "BC"]:
                    affirmative_boost += 0.12
                
                # Rural area boost
                if candidate.get("area_type") == "RURAL":
                    affirmative_boost += 0.08
                elif candidate.get("area_type") == "SEMI_URBAN":
                    affirmative_boost += 0.04
                
                # First generation graduate boost
                if candidate.get("is_first_generation_graduate"):
                    affirmative_boost += 0.06
                
                # First-time participant boost
                if candidate.get("previous_internships_count", 0) == 0:
                    affirmative_boost += 0.15
                
                # Calculate weighted overall score
                weights = {"skill": 0.4, "location": 0.2, "qualification": 0.25, "affirmative": 0.15}
                overall_score = (
                    skill_similarity * weights["skill"] +
                    location_match * weights["location"] +
                    qualification_match * weights["qualification"] +
                    affirmative_boost * weights["affirmative"]
                )
                
                match_percentage = min(int(overall_score * 100), 100)
                
                if match_percentage > 30:  # Only include decent matches
                    candidate_matches.append({
                        "internship_title": internship["title"],
                        "company": internship["company_name"],
                        "industry": internship["industry"],
                        "match_percentage": match_percentage,
                        "skill_similarity": round(skill_similarity, 3),
                        "location_match": round(location_match, 3),
                        "qualification_match": round(qualification_match, 3),
                        "affirmative_boost": round(affirmative_boost, 3),
                        "overall_score": round(overall_score, 3)
                    })
        
        # Sort matches by overall score
        candidate_matches.sort(key=lambda x: x["overall_score"], reverse=True)
        
        results.append({
            "candidate": candidate,
            "top_matches": candidate_matches[:3],  # Top 3 matches
            "total_matches": len(candidate_matches)
        })
    
    return {
        "test_results": results,
        "analysis": {
            "diversity_representation": "Shows how affirmative action boosts help underrepresented candidates",
            "skill_matching": "Demonstrates semantic skill similarity using embeddings", 
            "location_preferences": "Shows impact of location and willingness to relocate",
            "first_time_preference": "First-time internship applicants get significant boost"
        }
    }

@app.get("/test-verbose-ai/{candidate_id}/{internship_id}")
def test_verbose_ai_recommendation(candidate_id: int, internship_id: int):
    """Get detailed AI analysis for a specific candidate-internship pair"""
    
    # Find candidate and internship
    candidate = next((c for c in candidates_db if c["id"] == candidate_id), None)
    internship = next((i for i in internships_db if i["id"] == internship_id), None)
    
    if not candidate or not internship:
        raise HTTPException(status_code=404, detail="Candidate or internship not found")
    
    # Calculate detailed match scores
    candidate_embedding = candidate["skills_embedding"]
    internship_embedding = internship["required_skills_embedding"]
    skill_similarity = embedding_manager.calculate_similarity(candidate_embedding, internship_embedding)
    
    # Prepare comprehensive data for AI
    detailed_candidate = {
        **candidate,
        "skills_analysis": {
            "technical_skills": [s for s in candidate["skills"] if s.lower() in ["python", "javascript", "java", "sql", "machine learning", "react", "node.js"]],
            "soft_skills": [s for s in candidate["skills"] if s.lower() in ["research", "technical writing", "analytics", "communication"]],
            "domain_skills": [s for s in candidate["skills"] if s.lower() in ["digital marketing", "financial analysis", "solar energy", "blockchain"]]
        },
        "diversity_profile": {
            "is_underrepresented": candidate.get("social_category") in ["SC", "ST", "BC"],
            "rural_background": candidate.get("area_type") == "RURAL",
            "first_generation": candidate.get("is_first_generation_graduate", False),
            "first_time_applicant": candidate.get("previous_internships_count", 0) == 0
        }
    }
    
    detailed_internship = {
        **internship,
        "company_diversity_record": {
            "previous_diverse_hires": len([p for p in internship.get("previous_participants", []) if p.get("category") in ["SC", "ST", "BC"] or p.get("area") == "RURAL"]),
            "total_previous_participants": len(internship.get("previous_participants", [])),
            "diversity_ratio": len([p for p in internship.get("previous_participants", []) if p.get("category") in ["SC", "ST", "BC"] or p.get("area") == "RURAL"]) / max(len(internship.get("previous_participants", [])), 1)
        },
        "skill_requirements_analysis": {
            "core_technical": internship["required_skills"][:3],
            "additional_skills": internship["required_skills"][3:],
            "skill_flexibility": "High" if len(internship["required_skills"]) <= 4 else "Medium"
        }
    }
    
    try:
        # Get AI recommendation with detailed context
        ai_response = ai_manager.generate_internship_recommendation(
            detailed_candidate,
            detailed_internship,
            {
                "skill_similarity": skill_similarity,
                "provide_detailed_analysis": True,
                "include_diversity_considerations": True,
                "similarity_threshold": 0.3
            }
        )
        
        return {
            "candidate_name": candidate["name"],
            "internship_title": internship["title"],
            "company": internship["company_name"],
            "skill_similarity": skill_similarity,
            "ai_analysis": ai_response,
            "match_breakdown": {
                "technical_fit": f"{skill_similarity:.1%}",
                "cultural_fit": "Analyzing based on company diversity record",
                "growth_potential": "High for first-time applicants",
                "location_compatibility": "Remote available" if internship.get("is_remote") else "Location-dependent"
            },
            "detailed_reasoning": {
                "skill_analysis": f"Candidate skills {candidate['skills']} have {skill_similarity:.1%} similarity with required {internship['required_skills']}",
                "diversity_consideration": f"Candidate from {candidate.get('social_category', 'Unknown')} category and {candidate.get('area_type', 'Unknown')} area",
                "company_fit": f"Company has hired {detailed_internship['company_diversity_record']['previous_diverse_hires']} diverse candidates out of {detailed_internship['company_diversity_record']['total_previous_participants']} total"
            }
        }
        
    except Exception as e:
        return {
            "candidate_name": candidate["name"],
            "internship_title": internship["title"],
            "error": f"AI analysis failed: {str(e)}",
            "fallback_analysis": {
                "skill_match": f"{skill_similarity:.1%} semantic similarity",
                "recommendation": "CONSIDER" if skill_similarity > 0.3 else "WEAK_MATCH",
                "reasoning": f"Based on {skill_similarity:.1%} skill similarity between candidate's {candidate['skills']} and required {internship['required_skills']}"
            }
        }

@app.get("/verbose-ai-analysis/{candidate_id}/{internship_id}")
def get_verbose_ai_analysis(candidate_id: int, internship_id: int):
    """Get detailed AI analysis for a specific candidate-internship pair (only called when requested)"""
    
    # Get candidate
    candidate = next((c for c in candidates_db if c["id"] == candidate_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get internship
    internship = next((i for i in internships_db if i["id"] == internship_id), None)
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    # Calculate all the matching scores
    candidate_embedding = candidate["skills_embedding"]
    internship_embedding = internship["required_skills_embedding"]
    skill_similarity = embedding_manager.calculate_similarity(candidate_embedding, internship_embedding)
    
    # Location matching
    location_match = 0.5
    if candidate.get("current_location", "").lower() in internship.get("location", "").lower():
        location_match = 1.0
    elif candidate.get("willing_to_relocate", False):
        location_match = 0.8
    elif internship.get("is_remote", False):
        location_match = 0.9
    
    # Education/Qualification matching
    education_levels = {"Diploma": 1, "UG": 2, "Bachelor": 2, "PG": 3, "Master": 3, "PhD": 4, "Doctorate": 4}
    candidate_edu_level = education_levels.get(candidate.get("education_level", "UG"), 2)
    required_edu_level = education_levels.get(internship.get("min_education_level", "UG"), 2)
    qualification_match = 1.0 if candidate_edu_level >= required_edu_level else 0.7
    
    # CGPA boost
    if internship.get("min_cgpa", 0) > 0 and candidate.get("cgpa", 0):
        if candidate.get("cgpa", 0) >= internship.get("min_cgpa", 0):
            qualification_match = min(qualification_match + 0.2, 1.0)
        else:
            qualification_match *= 0.8
    
    # Affirmative action boost
    affirmative_boost = 0.0
    if candidate.get("social_category") in ["SC", "ST", "BC"]:
        affirmative_boost += 0.12
    if candidate.get("area_type") == "RURAL":
        affirmative_boost += 0.08
    elif candidate.get("area_type") == "SEMI_URBAN":
        affirmative_boost += 0.04
    if candidate.get("is_first_generation_graduate"):
        affirmative_boost += 0.06
    if candidate.get("previous_internships_count", 0) == 0:
        affirmative_boost += 0.15
    
    # Calculate overall score
    weights = {"skill": 0.4, "location": 0.2, "qualification": 0.25, "affirmative": 0.15}
    overall_score = (
        skill_similarity * weights["skill"] +
        location_match * weights["location"] +
        qualification_match * weights["qualification"] +
        affirmative_boost * weights["affirmative"]
    )
    
    # Prepare match scores for AI
    match_scores = {
        "skill_similarity": skill_similarity,
        "location_match": location_match,
        "qualification_match": qualification_match,
        "affirmative_boost": affirmative_boost,
        "overall_score": overall_score
    }
    
    try:
        print(f"🤖 Generating VERBOSE AI analysis for {candidate['name']} -> {internship['title']}")
        ai_response = ai_manager.generate_internship_recommendation(
            candidate,
            internship,
            match_scores
        )
        
        return {
            "candidate_id": candidate_id,
            "internship_id": internship_id,
            "candidate_name": candidate.get("name", "Unknown"),
            "internship_title": internship.get("title", "Unknown"),
            "match_scores": match_scores,
            "ai_analysis": ai_response,
            "status": "success"
        }
        
    except Exception as e:
        print(f"🚨 Verbose AI analysis failed: {e}")
        return {
            "candidate_id": candidate_id,
            "internship_id": internship_id,
            "error": str(e),
            "status": "error"
        }

if __name__ == "__main__":
    port = 8003
    print("🚀 Starting Advanced Internship Matcher API...")
    print(f"📍 API Documentation: http://localhost:{port}/docs")
    print(f"📍 Health Check: http://localhost:{port}/health")
    print(f"📍 Test Embeddings: http://localhost:{port}/test-embeddings")
    
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
