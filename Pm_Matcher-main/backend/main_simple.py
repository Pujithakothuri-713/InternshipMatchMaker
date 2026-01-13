import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime

# Import only the working components
from utils.ai_integration import GroqAIManager

app = FastAPI(
    title="Internship Matcher API - Basic Version",
    description="Simple internship matching system with AI recommendations",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI manager
ai_manager = GroqAIManager()

# Pydantic models for API
class CandidateCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    skills: List[str] = []
    education: Optional[str] = None
    experience: Optional[str] = None
    location: str
    social_category: str = "OC"  # OC, BC, SC, ST, OTHERS
    area_type: str = "URBAN"     # URBAN, RURAL
    is_first_generation_graduate: bool = False

class CandidateCreateDetailed(BaseModel):
    email: str
    name: str
    phone: Optional[str] = None
    education_level: str
    field_of_study: str
    cgpa: Optional[float] = None
    graduation_year: int
    institution: Optional[str] = None
    skills: List[str] = []
    experience_months: int = 0
    projects: List[str] = []
    preferred_locations: List[str] = []
    current_location: str
    willing_to_relocate: bool = True
    social_category: str = "OC"
    area_type: str = "URBAN"
    state: str
    district: str
    is_first_generation_graduate: bool = False
    family_income_annual: Optional[float] = None
    previous_internships_count: int = 0
    previous_internship_companies: List[str] = []

class CompanyCreate(BaseModel):
    name: str
    industry: str
    description: Optional[str] = None
    headquarters: Optional[str] = None
    locations: List[str] = []
    total_internship_capacity: int
    diversity_commitment: float = 0.3
    rural_quota: float = 0.2
    category_quotas: Dict[str, float] = {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505}

class InternshipCreate(BaseModel):
    company_id: int
    title: str
    description: str
    required_skills: List[str] = []
    min_education_level: str
    preferred_fields: List[str] = []
    min_cgpa: float = 0.0
    experience_required: bool = False
    location: str
    is_remote: bool = False
    duration_months: int = 3
    start_date: str
    application_deadline: str
    stipend_amount: float = 0.0
    total_positions: int = 1
    reserved_positions: Dict[str, int] = {"SC": 0, "ST": 0, "BC": 0, "rural": 0}

class MatchRequest(BaseModel):
    candidate_skills: List[str]
    candidate_location: str
    candidate_category: str
    internship_title: str
    internship_skills: List[str]
    internship_location: str

# In-memory storage for demo (in real app, this would be a database)
candidates_db: List[Dict] = []
companies_db: List[Dict] = []
internships_db: List[Dict] = []
applications_db: List[Dict] = []

# Initialize mock data
def initialize_mock_data():
    """Initialize the system with realistic mock data"""
    global companies_db, internships_db
    
    # Mock Companies
    mock_companies = [
        {
            "id": 1,
            "name": "TechCorp India",
            "industry": "Information Technology",
            "description": "Leading IT services company specializing in digital transformation",
            "headquarters": "Mumbai, Maharashtra",
            "locations": ["Mumbai", "Bangalore", "Pune", "Hyderabad"],
            "total_internship_capacity": 25,
            "diversity_commitment": 0.35,
            "rural_quota": 0.25,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505},
            "created_at": "2024-01-15T10:00:00"
        },
        {
            "id": 2,
            "name": "DataSoft Solutions",
            "industry": "Data Analytics",
            "description": "Cutting-edge data science and machine learning company",
            "headquarters": "Bangalore, Karnataka",
            "locations": ["Bangalore", "Chennai", "Kochi"],
            "total_internship_capacity": 15,
            "diversity_commitment": 0.40,
            "rural_quota": 0.30,
            "category_quotas": {"SC": 0.16, "ST": 0.08, "BC": 0.28, "OC": 0.48},
            "created_at": "2024-02-01T09:30:00"
        },
        {
            "id": 3,
            "name": "InnovateFintech",
            "industry": "Financial Technology",
            "description": "Revolutionary fintech solutions for emerging markets",
            "headquarters": "Delhi, Delhi",
            "locations": ["Delhi", "Mumbai", "Gurgaon"],
            "total_internship_capacity": 20,
            "diversity_commitment": 0.32,
            "rural_quota": 0.22,
            "category_quotas": {"SC": 0.15, "ST": 0.075, "BC": 0.27, "OC": 0.505},
            "created_at": "2024-01-20T11:15:00"
        },
        {
            "id": 4,
            "name": "GreenTech Innovations",
            "industry": "Renewable Energy",
            "description": "Sustainable technology solutions for clean energy",
            "headquarters": "Pune, Maharashtra",
            "locations": ["Pune", "Mumbai", "Ahmedabad"],
            "total_internship_capacity": 12,
            "diversity_commitment": 0.45,
            "rural_quota": 0.35,
            "category_quotas": {"SC": 0.18, "ST": 0.09, "BC": 0.30, "OC": 0.43},
            "created_at": "2024-02-10T14:20:00"
        },
        {
            "id": 5,
            "name": "HealthTech Pro",
            "industry": "Healthcare Technology",
            "description": "Digital health solutions and telemedicine platforms",
            "headquarters": "Hyderabad, Telangana",
            "locations": ["Hyderabad", "Chennai", "Bangalore"],
            "total_internship_capacity": 18,
            "diversity_commitment": 0.38,
            "rural_quota": 0.28,
            "category_quotas": {"SC": 0.16, "ST": 0.08, "BC": 0.29, "OC": 0.47},
            "created_at": "2024-01-25T12:45:00"
        }
    ]
    
    companies_db.extend(mock_companies)
    
    # Mock Internships with detailed descriptions and previous participation data
    mock_internships = [
        {
            "id": 1,
            "company_id": 1,
            "company_name": "TechCorp India",
            "industry": "Information Technology",
            "title": "Software Development Intern",
            "description": "Work on cutting-edge web applications using React, Node.js, and MongoDB. Collaborate with senior developers on real client projects. Gain experience in agile development, code reviews, and deployment processes.",
            "required_skills": ["JavaScript", "React", "Node.js", "Git", "HTML", "CSS"],
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Information Technology", "Electronics"],
            "min_cgpa": 7.0,
            "experience_required": False,
            "location": "Mumbai, Maharashtra",
            "is_remote": True,
            "duration_months": 6,
            "start_date": "2025-01-15",
            "application_deadline": "2024-12-15",
            "stipend_amount": 25000.0,
            "total_positions": 8,
            "filled_positions": 2,
            "reserved_positions": {"SC": 1, "ST": 1, "BC": 2, "rural": 2},
            "is_active": True,
            "created_at": "2024-09-01T10:00:00",
            "previous_participants": [
                {"name": "Rajesh Kumar", "year": 2023, "category": "SC", "area": "RURAL", "performance": "Excellent"},
                {"name": "Priya Singh", "year": 2023, "category": "OC", "area": "URBAN", "performance": "Good"},
                {"name": "Arjun Patel", "year": 2024, "category": "BC", "area": "RURAL", "performance": "Outstanding"},
                {"name": "Sneha Reddy", "year": 2024, "category": "ST", "area": "RURAL", "performance": "Good"}
            ]
        },
        {
            "id": 2,
            "company_id": 2,
            "company_name": "DataSoft Solutions",
            "industry": "Data Analytics",
            "title": "Data Science Intern",
            "description": "Analyze large datasets using Python, pandas, and scikit-learn. Build machine learning models for predictive analytics. Create data visualizations and present insights to stakeholders.",
            "required_skills": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "Data Visualization"],
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Statistics", "Mathematics", "Data Science"],
            "min_cgpa": 7.5,
            "experience_required": False,
            "location": "Bangalore, Karnataka",
            "is_remote": False,
            "duration_months": 4,
            "start_date": "2025-02-01",
            "application_deadline": "2024-12-20",
            "stipend_amount": 30000.0,
            "total_positions": 5,
            "filled_positions": 1,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 1},
            "is_active": True,
            "created_at": "2024-09-05T11:30:00",
            "previous_participants": [
                {"name": "Vikram Sharma", "year": 2023, "category": "OC", "area": "URBAN", "performance": "Excellent"},
                {"name": "Kavya Nair", "year": 2024, "category": "BC", "area": "RURAL", "performance": "Outstanding"}
            ]
        },
        {
            "id": 3,
            "company_id": 3,
            "company_name": "InnovateFintech",
            "industry": "Financial Technology",
            "title": "Full Stack Developer Intern",
            "description": "Develop financial applications using modern tech stack. Work with React frontend, Spring Boot backend, and microservices architecture. Implement secure payment gateways and financial APIs.",
            "required_skills": ["Java", "Spring Boot", "React", "REST APIs", "MySQL", "Microservices"],
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Information Technology", "Software Engineering"],
            "min_cgpa": 7.2,
            "experience_required": True,
            "location": "Delhi, Delhi",
            "is_remote": True,
            "duration_months": 5,
            "start_date": "2025-01-20",
            "application_deadline": "2024-12-25",
            "stipend_amount": 28000.0,
            "total_positions": 6,
            "filled_positions": 0,
            "reserved_positions": {"SC": 1, "ST": 1, "BC": 2, "rural": 2},
            "is_active": True,
            "created_at": "2024-09-10T09:15:00",
            "previous_participants": [
                {"name": "Anita Gupta", "year": 2023, "category": "SC", "area": "RURAL", "performance": "Good"},
                {"name": "Rohit Jain", "year": 2023, "category": "OC", "area": "URBAN", "performance": "Excellent"},
                {"name": "Deepika Yadav", "year": 2024, "category": "BC", "area": "SEMI_URBAN", "performance": "Outstanding"}
            ]
        },
        {
            "id": 4,
            "company_id": 4,
            "company_name": "GreenTech Innovations",
            "industry": "Renewable Energy",
            "title": "IoT Development Intern",
            "description": "Design and develop IoT solutions for smart energy management. Work with Arduino, Raspberry Pi, and cloud platforms. Build sensors and monitoring systems for solar and wind energy installations.",
            "required_skills": ["IoT", "Arduino", "Python", "C++", "Cloud Computing", "Sensors"],
            "min_education_level": "UG",
            "preferred_fields": ["Electronics", "Computer Science", "Electrical Engineering"],
            "min_cgpa": 6.8,
            "experience_required": False,
            "location": "Pune, Maharashtra",
            "is_remote": False,
            "duration_months": 4,
            "start_date": "2025-02-15",
            "application_deadline": "2024-12-30",
            "stipend_amount": 22000.0,
            "total_positions": 4,
            "filled_positions": 0,
            "reserved_positions": {"SC": 1, "ST": 0, "BC": 1, "rural": 2},
            "is_active": True,
            "created_at": "2024-09-12T13:45:00",
            "previous_participants": [
                {"name": "Manish Kumar", "year": 2024, "category": "ST", "area": "RURAL", "performance": "Good"},
                {"name": "Pooja Agarwal", "year": 2024, "category": "OC", "area": "URBAN", "performance": "Excellent"}
            ]
        },
        {
            "id": 5,
            "company_id": 5,
            "company_name": "HealthTech Pro",
            "industry": "Healthcare Technology",
            "title": "Mobile App Development Intern",
            "description": "Develop mobile applications for healthcare using Flutter and React Native. Create user-friendly interfaces for patients and doctors. Integrate with hospital management systems and health APIs.",
            "required_skills": ["Flutter", "React Native", "Dart", "JavaScript", "Mobile Development", "APIs"],
            "min_education_level": "UG",
            "preferred_fields": ["Computer Science", "Information Technology", "Mobile Computing"],
            "min_cgpa": 7.0,
            "experience_required": False,
            "location": "Hyderabad, Telangana",
            "is_remote": True,
            "duration_months": 5,
            "start_date": "2025-01-10",
            "application_deadline": "2024-12-10",
            "stipend_amount": 26000.0,
            "total_positions": 6,
            "filled_positions": 1,
            "reserved_positions": {"SC": 1, "ST": 1, "BC": 2, "rural": 2},
            "is_active": True,
            "created_at": "2024-09-08T15:20:00",
            "previous_participants": [
                {"name": "Ravi Verma", "year": 2023, "category": "BC", "area": "RURAL", "performance": "Outstanding"},
                {"name": "Sita Devi", "year": 2024, "category": "SC", "area": "RURAL", "performance": "Good"},
                {"name": "Amit Singh", "year": 2024, "category": "OC", "area": "URBAN", "performance": "Excellent"}
            ]
        },
        {
            "id": 6,
            "company_id": 2,
            "company_name": "DataSoft Solutions",
            "industry": "Data Analytics",
            "title": "AI/ML Research Intern",
            "description": "Conduct research on advanced machine learning algorithms. Work on computer vision and natural language processing projects. Publish research papers and present findings at conferences.",
            "required_skills": ["Python", "TensorFlow", "PyTorch", "Computer Vision", "NLP", "Research"],
            "min_education_level": "PG",
            "preferred_fields": ["Computer Science", "Artificial Intelligence", "Data Science"],
            "min_cgpa": 8.0,
            "experience_required": True,
            "location": "Bangalore, Karnataka",
            "is_remote": False,
            "duration_months": 6,
            "start_date": "2025-03-01",
            "application_deadline": "2025-01-15",
            "stipend_amount": 35000.0,
            "total_positions": 3,
            "filled_positions": 0,
            "reserved_positions": {"SC": 0, "ST": 0, "BC": 1, "rural": 1},
            "is_active": True,
            "created_at": "2024-09-15T10:30:00",
            "previous_participants": [
                {"name": "Dr. Suresh Reddy", "year": 2024, "category": "BC", "area": "URBAN", "performance": "Outstanding"}
            ]
        }
    ]
    
    internships_db.extend(mock_internships)

@app.get("/")
def read_root():
    return {"message": "Internship Matcher API is running!", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.on_event("startup")
async def startup_event():
    """Initialize mock data when the server starts"""
    initialize_mock_data()
    print("✅ Mock data initialized successfully!")
    print(f"📊 Loaded {len(companies_db)} companies and {len(internships_db)} internships")

@app.post("/candidates/")
def create_candidate(candidate: CandidateCreateDetailed):
    """Create a new candidate profile"""
    candidate_dict = candidate.dict()
    candidate_dict["id"] = len(candidates_db) + 1
    candidate_dict["created_at"] = datetime.now().isoformat()
    candidates_db.append(candidate_dict)
    return {"message": "Candidate created successfully", "candidate_id": candidate_dict["id"], "candidate": candidate_dict}

@app.get("/candidates/")
def get_candidates():
    """Get all candidates"""
    return candidates_db

@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int):
    """Get a specific candidate"""
    candidate = next((c for c in candidates_db if c["id"] == candidate_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@app.post("/companies/")
def create_company(company: CompanyCreate):
    """Create a new company"""
    company_dict = company.dict()
    company_dict["id"] = len(companies_db) + 1
    company_dict["created_at"] = datetime.now().isoformat()
    companies_db.append(company_dict)
    return {"message": "Company created successfully", "company_id": company_dict["id"], "company": company_dict}

@app.get("/companies/")
def get_companies():
    """Get all companies"""
    return companies_db

@app.post("/internships/")
def create_internship(internship: InternshipCreate):
    """Create a new internship posting"""
    # Check if company exists
    company = next((c for c in companies_db if c["id"] == internship.company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    internship_dict = internship.dict()
    internship_dict["id"] = len(internships_db) + 1
    internship_dict["created_at"] = datetime.now().isoformat()
    internship_dict["company_name"] = company["name"]
    internship_dict["industry"] = company["industry"]
    internship_dict["filled_positions"] = 0
    internship_dict["is_active"] = True
    internships_db.append(internship_dict)
    return {"message": "Internship created successfully", "internship_id": internship_dict["id"], "internship": internship_dict}

@app.get("/internships/")
def get_internships():
    """Get all internships"""
    return internships_db

@app.get("/internships/active")
def get_active_internships():
    """Get active internships"""
    active_internships = [i for i in internships_db if i.get("is_active", True)]
    return active_internships

@app.get("/internships/{internship_id}")
def get_internship_details(internship_id: int):
    """Get detailed information about a specific internship including previous participants"""
    internship = next((i for i in internships_db if i["id"] == internship_id), None)
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    return internship

@app.get("/internships/{internship_id}/diversity-stats")
def get_internship_diversity_stats(internship_id: int):
    """Get diversity statistics for previous participants of an internship"""
    internship = next((i for i in internships_db if i["id"] == internship_id), None)
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    previous_participants = internship.get("previous_participants", [])
    if not previous_participants:
        return {"message": "No previous participation data available"}
    
    total_participants = len(previous_participants)
    
    # Category distribution
    categories = {}
    areas = {}
    performance_dist = {}
    
    for participant in previous_participants:
        category = participant.get("category", "Unknown")
        area = participant.get("area", "Unknown")
        performance = participant.get("performance", "Unknown")
        
        categories[category] = categories.get(category, 0) + 1
        areas[area] = areas.get(area, 0) + 1
        performance_dist[performance] = performance_dist.get(performance, 0) + 1
    
    return {
        "internship_title": internship["title"],
        "company_name": internship["company_name"],
        "total_previous_participants": total_participants,
        "category_distribution": {k: {"count": v, "percentage": round(v/total_participants*100, 1)} for k, v in categories.items()},
        "area_distribution": {k: {"count": v, "percentage": round(v/total_participants*100, 1)} for k, v in areas.items()},
        "performance_distribution": {k: {"count": v, "percentage": round(v/total_participants*100, 1)} for k, v in performance_dist.items()}
    }

@app.get("/matches/candidate/{candidate_id}")
def get_candidate_matches(candidate_id: int):
    """Get internship matches for a candidate"""
    # Get candidate
    candidate = next((c for c in candidates_db if c["id"] == candidate_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    matches = []
    for internship in internships_db:
        if internship.get("is_active", True):
            # Simple matching logic
            skill_overlap = len(set(candidate.get("skills", [])) & set(internship.get("required_skills", [])))
            skill_total = len(set(candidate.get("skills", [])) | set(internship.get("required_skills", [])))
            skill_match = skill_overlap / skill_total if skill_total > 0 else 0.5
            
            location_match = 1.0 if candidate.get("current_location", "").lower() in internship.get("location", "").lower() else 0.5
            
            # Education match
            education_levels = {"Diploma": 1, "UG": 2, "Bachelor": 2, "PG": 3, "Master": 3, "PhD": 4, "Doctorate": 4}
            candidate_edu_level = education_levels.get(candidate.get("education_level", "UG"), 2)
            required_edu_level = education_levels.get(internship.get("min_education_level", "UG"), 2)
            qualification_match = 1.0 if candidate_edu_level >= required_edu_level else 0.7
            
            # CGPA match
            if internship.get("min_cgpa", 0) > 0 and candidate.get("cgpa", 0) > 0:
                if candidate.get("cgpa", 0) >= internship.get("min_cgpa", 0):
                    qualification_match = min(qualification_match + 0.2, 1.0)
                else:
                    qualification_match *= 0.8
            
            # Affirmative action boost with enhanced first-time participant preference
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
            
            # First-time participant boost (major preference)
            candidate_previous_count = candidate.get("previous_internships_count", 0)
            candidate_previous_companies = candidate.get("previous_internship_companies", [])
            
            # Check if candidate has never done internships before
            if candidate_previous_count == 0:
                affirmative_boost += 0.15  # Strong boost for first-time participants
            
            # Check if candidate has never worked with this specific company
            company_name = internship.get("company_name", "")
            if company_name not in candidate_previous_companies:
                affirmative_boost += 0.08  # Boost for new company experience
            
            # Income-based boost (if family income is low)
            family_income = candidate.get("family_income_annual")
            if family_income and family_income > 0 and family_income < 300000:  # Less than 3 LPA
                affirmative_boost += 0.05
            elif family_income and family_income > 0 and family_income < 500000:  # Less than 5 LPA
                affirmative_boost += 0.03
            
            # Check company's historical diversity commitment
            # Companies with good track record of hiring diverse candidates get preference matching
            previous_participants = internship.get("previous_participants", [])
            if previous_participants:
                diverse_participants = [p for p in previous_participants if p.get("category") in ["SC", "ST", "BC"] or p.get("area") == "RURAL"]
                diversity_ratio = len(diverse_participants) / len(previous_participants)
                if diversity_ratio > 0.4:  # Company has good diversity track record
                    if candidate.get("social_category") in ["SC", "ST", "BC"] or candidate.get("area_type") == "RURAL":
                        affirmative_boost += 0.04
            
            # Calculate overall score
            weights = {"skill": 0.4, "location": 0.2, "qualification": 0.25, "affirmative": 0.15}
            overall_score = (
                skill_match * weights["skill"] +
                location_match * weights["location"] +
                qualification_match * weights["qualification"] +
                affirmative_boost * weights["affirmative"]
            )
            
            match_percentage = min(int(overall_score * 100), 100)
            
            if match_percentage > 30:  # Only show matches above 30%
                # Generate AI recommendation with comprehensive context
                try:
                    # Prepare enriched data for AI recommendation
                    enhanced_candidate_data = {
                        **candidate,
                        "match_scores": {
                            "skill_similarity": skill_match,
                            "location_match": location_match,
                            "qualification_match": qualification_match,
                            "affirmative_action_boost": affirmative_boost,
                            "overall_score": overall_score
                        }
                    }
                    
                    enhanced_internship_data = {
                        **internship,
                        "previous_participants": internship.get("previous_participants", []),
                        "diversity_commitment": companies_db[internship["company_id"]-1].get("diversity_commitment", 0.3) if internship["company_id"] <= len(companies_db) else 0.3
                    }
                    
                    # Add AI recommendation for matches above 50%
                    ai_recommendation = None
                    if match_percentage >= 50:
                        match_scores_dict = {
                            "skill_similarity": skill_match,
                            "location_match": location_match,
                            "qualification_match": qualification_match,
                            "overall_score": overall_score
                        }
                        ai_recommendation = ai_manager.generate_internship_recommendation(
                            enhanced_candidate_data, enhanced_internship_data, match_scores_dict
                        )
                    
                    matches.append({
                        "internship": internship,
                        "scores": {
                            "skill_match_score": skill_match,
                            "location_match_score": location_match,
                            "qualification_match_score": qualification_match,
                            "affirmative_action_boost": affirmative_boost,
                            "overall_score": overall_score
                        },
                        "match_percentage": match_percentage,
                        "ai_recommendation": ai_recommendation,
                        "first_time_applicant_boost": candidate_previous_count == 0,
                        "diversity_factors": {
                            "social_category": candidate.get("social_category"),
                            "area_type": candidate.get("area_type"),
                            "first_generation": candidate.get("is_first_generation_graduate", False),
                            "previous_internships": candidate_previous_count
                        }
                    })
                except Exception as e:
                    # If AI fails, still include the match without recommendation
                    matches.append({
                        "internship": internship,
                        "scores": {
                            "skill_match_score": skill_match,
                            "location_match_score": location_match,
                            "qualification_match_score": qualification_match,
                            "affirmative_action_boost": affirmative_boost,
                            "overall_score": overall_score
                        },
                        "match_percentage": match_percentage,
                        "ai_recommendation": f"AI recommendation temporarily unavailable: {str(e)}",
                        "first_time_applicant_boost": candidate_previous_count == 0,
                        "diversity_factors": {
                            "social_category": candidate.get("social_category"),
                            "area_type": candidate.get("area_type"),
                            "first_generation": candidate.get("is_first_generation_graduate", False),
                            "previous_internships": candidate_previous_count
                        }
                    })
    
    # Sort by overall score
    matches.sort(key=lambda x: x["scores"]["overall_score"], reverse=True)
    return matches[:10]  # Return top 10 matches

@app.get("/applications/candidate/{candidate_id}")
def get_candidate_applications(candidate_id: int):
    """Get applications for a candidate"""
    candidate_apps = [app for app in applications_db if app.get("candidate_id") == candidate_id]
    return candidate_apps

@app.get("/applications/internship/{internship_id}")
def get_internship_applications(internship_id: int):
    """Get applications for an internship"""
    internship_apps = [app for app in applications_db if app.get("internship_id") == internship_id]
    return internship_apps

@app.get("/analytics/diversity/{internship_id}")
def get_diversity_analytics(internship_id: int):
    """Get diversity analytics for an internship"""
    internship_apps = [app for app in applications_db if app.get("internship_id") == internship_id]
    
    total_applications = len(internship_apps)
    
    # Social category distribution
    category_dist = {}
    area_dist = {}
    first_gen_count = 0
    first_time_count = 0
    
    for app in internship_apps:
        # Get candidate details
        candidate = next((c for c in candidates_db if c["id"] == app.get("candidate_id")), {})
        
        category = candidate.get("social_category", "Unknown")
        area = candidate.get("area_type", "Unknown")
        
        if category not in category_dist:
            category_dist[category] = {"count": 0, "percentage": 0}
        category_dist[category]["count"] += 1
        
        if area not in area_dist:
            area_dist[area] = {"count": 0, "percentage": 0}
        area_dist[area]["count"] += 1
        
        if candidate.get("is_first_generation_graduate", False):
            first_gen_count += 1
        
        if candidate.get("previous_internships_count", 0) == 0:
            first_time_count += 1
    
    # Calculate percentages
    for category in category_dist:
        category_dist[category]["percentage"] = (category_dist[category]["count"] / total_applications * 100) if total_applications > 0 else 0
    
    for area in area_dist:
        area_dist[area]["percentage"] = (area_dist[area]["count"] / total_applications * 100) if total_applications > 0 else 0
    
    return {
        "total_applications": total_applications,
        "social_category_distribution": category_dist,
        "area_type_distribution": area_dist,
        "first_generation_graduates": {
            "count": first_gen_count,
            "percentage": (first_gen_count / total_applications * 100) if total_applications > 0 else 0
        },
        "first_time_applicants": {
            "count": first_time_count,
            "percentage": (first_time_count / total_applications * 100) if total_applications > 0 else 0
        }
    }

@app.post("/applications/")
def create_application(application_data: dict):
    """Create a new application"""
    application = {
        "id": len(applications_db) + 1,
        "candidate_id": application_data.get("candidate_id"),
        "internship_id": application_data.get("internship_id"),
        "applied_at": datetime.now().isoformat(),
        "status": "APPLIED",
        "cover_letter": application_data.get("cover_letter", ""),
        "overall_score": application_data.get("overall_score", 0.0),
        "skill_match_score": application_data.get("skill_match_score", 0.0),
        "qualification_match_score": application_data.get("qualification_match_score", 0.0),
        "ai_recommendation": application_data.get("ai_recommendation", ""),
        "ai_reasoning": application_data.get("ai_reasoning", ""),
        "recommendation_confidence": application_data.get("recommendation_confidence", 0.0)
    }
    
    # Add candidate and internship details for easy access
    candidate = next((c for c in candidates_db if c["id"] == application["candidate_id"]), {})
    internship = next((i for i in internships_db if i["id"] == application["internship_id"]), {})
    
    application.update({
        "candidate_name": candidate.get("name", "Unknown"),
        "candidate_email": candidate.get("email", "Unknown"),
        "social_category": candidate.get("social_category", "Unknown"),
        "area_type": candidate.get("area_type", "Unknown"),
        "internship_title": internship.get("title", "Unknown"),
        "company_name": internship.get("company_name", "Unknown"),
        "location": internship.get("location", "Unknown")
    })
    
    applications_db.append(application)
    return {"message": "Application submitted successfully", "application_id": application["id"]}

@app.post("/match/")
def get_match_recommendation(match_request: MatchRequest):
    """Get AI-powered match recommendation"""
    try:
        # Prepare data for AI recommendation
        candidate_data = {
            "skills": match_request.candidate_skills,
            "location": match_request.candidate_location,
            "category": match_request.candidate_category,
            "name": "Test Candidate"
        }
        
        internship_data = {
            "title": match_request.internship_title,
            "required_skills": match_request.internship_skills,
            "location": match_request.internship_location,
            "company": "Test Company"
        }
        
        # Calculate basic similarity scores
        skill_overlap = len(set(match_request.candidate_skills) & set(match_request.internship_skills))
        skill_total = len(set(match_request.candidate_skills) | set(match_request.internship_skills))
        skill_similarity = skill_overlap / skill_total if skill_total > 0 else 0
        
        location_match = 1.0 if match_request.candidate_location == match_request.internship_location else 0.5
        
        match_scores = {
            "skill_similarity": skill_similarity,
            "location_match": location_match,
            "qualification_match": 0.8,  # Default
            "overall_score": (skill_similarity + location_match + 0.8) / 3
        }
        
        # Get AI recommendation
        ai_recommendation = ai_manager.generate_internship_recommendation(
            candidate_data, internship_data, match_scores
        )
        
        return {
            "match_scores": match_scores,
            "ai_recommendation": ai_recommendation,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@app.get("/test-ai/")
def test_ai():
    """Test AI integration"""
    try:
        # Simple test data
        candidate_data = {
            "name": "Test Student",
            "skills": ["Python", "Data Analysis"],
            "location": "Mumbai",
            "category": "OC"
        }
        
        internship_data = {
            "title": "Data Science Intern", 
            "company": "Tech Corp",
            "required_skills": ["Python", "Machine Learning"],
            "location": "Mumbai"
        }
        
        match_scores = {
            "skill_similarity": 0.8,
            "location_match": 1.0,
            "qualification_match": 0.9,
            "overall_score": 0.85
        }
        
        recommendation = ai_manager.generate_internship_recommendation(
            candidate_data, internship_data, match_scores
        )
        
        return {
            "status": "success",
            "test_data": {
                "candidate": candidate_data,
                "internship": internship_data,
                "scores": match_scores
            },
            "ai_recommendation": recommendation
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "AI integration test failed"
        }

@app.delete("/reset/")
def reset_data():
    """Reset all data (for testing)"""
    global candidates_db, internships_db
    candidates_db.clear()
    internships_db.clear()
    return {"message": "All data reset successfully"}

if __name__ == "__main__":
    port = 8002  # Use different port to avoid conflicts
    print("🚀 Starting Internship Matcher API...")
    print(f"📍 API Documentation: http://localhost:{port}/docs")
    print(f"📍 Health Check: http://localhost:{port}/health")
    print(f"📍 Test AI: http://localhost:{port}/test-ai")
    
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
