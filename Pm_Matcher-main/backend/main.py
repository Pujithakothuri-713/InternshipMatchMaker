import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uvicorn
import json
from datetime import datetime

from database.models import (
    create_database, get_session, Candidate, Company, Internship, Application,
    SocialCategory, AreaType, ApplicationStatus
)
from utils.embeddings import get_embedding_manager, preprocess_skills
from utils.matching_algorithm import get_matcher, convert_model_to_dict
from utils.ai_integration import GroqAIManager

# Initialize AI manager
ai_manager = GroqAIManager()

app = FastAPI(
    title="Internship Matcher API",
    description="Smart internship matching system with affirmative action support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    create_database()

# Dependency to get database session
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for API requests/responses
from pydantic import BaseModel

class CandidateCreate(BaseModel):
    email: str
    name: str
    phone: str
    education_level: str
    field_of_study: str
    cgpa: Optional[float] = None
    graduation_year: Optional[int] = None
    institution: Optional[str] = None
    skills: List[str]
    experience_months: int = 0
    projects: Optional[List[str]] = []
    preferred_locations: Optional[List[str]] = []
    current_location: str
    willing_to_relocate: bool = True
    social_category: str
    area_type: str
    state: str
    district: str
    is_first_generation_graduate: bool = False
    family_income_annual: Optional[float] = None
    previous_internships_count: int = 0
    previous_internship_companies: Optional[List[str]] = []

class CompanyCreate(BaseModel):
    name: str
    industry: str
    description: Optional[str] = None
    headquarters: Optional[str] = None
    locations: Optional[List[str]] = []
    total_internship_capacity: int
    diversity_commitment: float = 0.0
    rural_quota: float = 0.0
    category_quotas: Optional[Dict[str, float]] = {}

class InternshipCreate(BaseModel):
    company_id: int
    title: str
    description: str
    required_skills: List[str]
    min_education_level: str
    preferred_fields: Optional[List[str]] = []
    min_cgpa: float = 0.0
    experience_required: bool = False
    location: str
    is_remote: bool = False
    duration_months: int
    start_date: datetime
    application_deadline: datetime
    stipend_amount: float = 0.0
    total_positions: int
    reserved_positions: Optional[Dict[str, int]] = {}

class MatchRequest(BaseModel):
    candidate_id: int
    top_k: int = 10

class ApplicationCreate(BaseModel):
    candidate_id: int
    internship_id: int
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None

# Candidate endpoints
@app.post("/candidates/", response_model=dict)
async def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    """Create a new candidate profile"""
    
    # Check if email already exists
    existing = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Preprocess and generate embeddings for skills
    processed_skills = preprocess_skills(candidate.skills)
    embedding_manager = get_embedding_manager()
    skills_embedding = embedding_manager.generate_skills_embedding(processed_skills)
    
    # Create candidate record
    db_candidate = Candidate(
        email=candidate.email,
        name=candidate.name,
        phone=candidate.phone,
        education_level=candidate.education_level,
        field_of_study=candidate.field_of_study,
        cgpa=candidate.cgpa,
        graduation_year=candidate.graduation_year,
        institution=candidate.institution,
        skills=json.dumps(processed_skills),
        skills_embedding=json.dumps(skills_embedding),
        experience_months=candidate.experience_months,
        projects=json.dumps(candidate.projects or []),
        preferred_locations=json.dumps(candidate.preferred_locations or []),
        current_location=candidate.current_location,
        willing_to_relocate=candidate.willing_to_relocate,
        social_category=candidate.social_category,
        area_type=candidate.area_type,
        state=candidate.state,
        district=candidate.district,
        is_first_generation_graduate=candidate.is_first_generation_graduate,
        family_income_annual=candidate.family_income_annual,
        previous_internships_count=candidate.previous_internships_count,
        previous_internship_companies=json.dumps(candidate.previous_internship_companies or [])
    )
    
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    return {"message": "Candidate created successfully", "candidate_id": db_candidate.id}

@app.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get candidate by ID"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return convert_model_to_dict(candidate)

@app.get("/candidates/")
async def get_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all candidates with pagination"""
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    return [convert_model_to_dict(c) for c in candidates]

# Company endpoints
@app.post("/companies/", response_model=dict)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company"""
    
    db_company = Company(
        name=company.name,
        industry=company.industry,
        description=company.description,
        headquarters=company.headquarters,
        locations=json.dumps(company.locations or []),
        total_internship_capacity=company.total_internship_capacity,
        diversity_commitment=company.diversity_commitment,
        rural_quota=company.rural_quota,
        category_quotas=json.dumps(company.category_quotas or {})
    )
    
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return {"message": "Company created successfully", "company_id": db_company.id}

@app.get("/companies/")
async def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all companies with pagination"""
    companies = db.query(Company).offset(skip).limit(limit).all()
    return [convert_model_to_dict(c) for c in companies]

# Internship endpoints
@app.post("/internships/", response_model=dict)
async def create_internship(internship: InternshipCreate, db: Session = Depends(get_db)):
    """Create a new internship"""
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == internship.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Generate embeddings for required skills
    processed_skills = preprocess_skills(internship.required_skills)
    embedding_manager = get_embedding_manager()
    skills_embedding = embedding_manager.generate_job_requirements_embedding(
        internship.title, internship.description, processed_skills
    )
    
    db_internship = Internship(
        company_id=internship.company_id,
        title=internship.title,
        description=internship.description,
        required_skills=json.dumps(processed_skills),
        skills_embedding=json.dumps(skills_embedding),
        min_education_level=internship.min_education_level,
        preferred_fields=json.dumps(internship.preferred_fields or []),
        min_cgpa=internship.min_cgpa,
        experience_required=internship.experience_required,
        location=internship.location,
        is_remote=internship.is_remote,
        duration_months=internship.duration_months,
        start_date=internship.start_date,
        application_deadline=internship.application_deadline,
        stipend_amount=internship.stipend_amount,
        total_positions=internship.total_positions,
        reserved_positions=json.dumps(internship.reserved_positions or {})
    )
    
    db.add(db_internship)
    db.commit()
    db.refresh(db_internship)
    
    return {"message": "Internship created successfully", "internship_id": db_internship.id}

@app.get("/internships/")
async def get_internships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all internships with pagination"""
    internships = db.query(Internship).join(Company).offset(skip).limit(limit).all()
    
    result = []
    for internship in internships:
        internship_dict = convert_model_to_dict(internship)
        internship_dict["company_name"] = internship.company.name
        internship_dict["industry"] = internship.company.industry
        result.append(internship_dict)
    
    return result

@app.get("/internships/active")
async def get_active_internships(db: Session = Depends(get_db)):
    """Get all active internships (not past deadline and not full)"""
    now = datetime.utcnow()
    
    internships = db.query(Internship).join(Company).filter(
        Internship.application_deadline > now,
        Internship.is_active == True,
        Internship.filled_positions < Internship.total_positions
    ).all()
    
    result = []
    for internship in internships:
        internship_dict = convert_model_to_dict(internship)
        internship_dict["company_name"] = internship.company.name
        internship_dict["industry"] = internship.company.industry
        result.append(internship_dict)
    
    return result

# Matching endpoints
@app.post("/match/candidate")
async def find_matches_for_candidate(request: MatchRequest, db: Session = Depends(get_db)):
    """Find best internship matches for a candidate"""
    
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get active internships
    now = datetime.utcnow()
    internships = db.query(Internship).join(Company).filter(
        Internship.application_deadline > now,
        Internship.is_active == True,
        Internship.filled_positions < Internship.total_positions
    ).all()
    
    # Convert to dictionaries
    candidate_data = convert_model_to_dict(candidate)
    internship_data_list = []
    for internship in internships:
        internship_dict = convert_model_to_dict(internship)
        internship_dict["company_name"] = internship.company.name
        internship_dict["industry"] = internship.company.industry
        internship_dict["category_quotas"] = convert_model_to_dict(internship.company).get("category_quotas", {})
        internship_data_list.append(internship_dict)
    
    # Find matches
    matcher = get_matcher()
    matches = matcher.find_best_matches_for_candidate(
        candidate_data, internship_data_list, request.top_k
    )
    
    return {
        "candidate_id": request.candidate_id,
        "matches": [
            {
                "internship": match[0],
                "scores": match[1],
                "match_percentage": round(match[1]["overall_score"] * 100, 2)
            }
            for match in matches
        ]
    }

@app.post("/match/internship/{internship_id}")
async def find_candidates_for_internship(internship_id: int, top_k: int = 50, db: Session = Depends(get_db)):
    """Find best candidate matches for an internship"""
    
    # Get internship
    internship = db.query(Internship).join(Company).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    # Get all active candidates
    candidates = db.query(Candidate).filter(Candidate.is_active == True).all()
    
    # Convert to dictionaries
    internship_data = convert_model_to_dict(internship)
    internship_data["company_name"] = internship.company.name
    internship_data["industry"] = internship.company.industry
    internship_data["category_quotas"] = convert_model_to_dict(internship.company).get("category_quotas", {})
    
    candidate_data_list = [convert_model_to_dict(c) for c in candidates]
    
    # Find matches
    matcher = get_matcher()
    matches = matcher.find_best_candidates_for_internship(
        internship_data, candidate_data_list, top_k
    )
    
    return {
        "internship_id": internship_id,
        "matches": [
            {
                "candidate": match[0],
                "scores": match[1],
                "match_percentage": round(match[1]["overall_score"] * 100, 2)
            }
            for match in matches
        ]
    }

# Application endpoints
@app.post("/applications/")
async def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    """Create a new application with AI recommendation"""
    
    # Verify candidate and internship exist
    candidate = db.query(Candidate).filter(Candidate.id == application.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    internship = db.query(Internship).join(Company).filter(Internship.id == application.internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    # Check if application already exists
    existing = db.query(Application).filter(
        Application.candidate_id == application.candidate_id,
        Application.internship_id == application.internship_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application already exists")
    
    # Calculate match scores
    candidate_data = convert_model_to_dict(candidate)
    internship_data = convert_model_to_dict(internship)
    internship_data["company_name"] = internship.company.name
    internship_data["industry"] = internship.company.industry
    
    # Simple matching without the complex algorithm for now
    # matcher = get_matcher()
    
    # Calculate basic skill similarity using embeddings
    embedding_manager = get_embedding_manager()
    candidate_skills_embedding = embedding_manager.generate_skills_embedding(candidate_data.get("skills", []))
    internship_skills_embedding = embedding_manager.generate_skills_embedding(internship_data.get("required_skills", []))
    
    skill_similarity = embedding_manager.calculate_similarity(candidate_skills_embedding, internship_skills_embedding)
    
    # Simple score calculation
    scores = {
        "skill_match_score": skill_similarity,
        "location_match_score": 1.0 if candidate_data.get("location") == internship_data.get("location") else 0.5,
        "qualification_match_score": 0.8,  # Default value
        "affirmative_action_boost": 0.1 if candidate_data.get("category") != "OC" else 0.0,
        "overall_score": (skill_similarity + 0.8 + 0.5) / 3
    }
    
    # Generate AI recommendation
    # ai_manager = get_ai_manager()
    ai_result = ai_manager.generate_internship_recommendation(
        candidate_data, internship_data, scores
    )
    
    # Create application record
    db_application = Application(
        candidate_id=application.candidate_id,
        internship_id=application.internship_id,
        skill_match_score=scores["skill_match_score"],
        location_match_score=scores["location_match_score"],
        qualification_match_score=scores["qualification_match_score"],
        affirmative_action_boost=scores["affirmative_action_boost"],
        overall_score=scores["overall_score"],
        ai_recommendation=ai_result["recommendation"],
        ai_reasoning=ai_result["reasoning"],
        recommendation_confidence=ai_result["confidence"],
        cover_letter=application.cover_letter,
        resume_url=application.resume_url
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    return {
        "message": "Application created successfully",
        "application_id": db_application.id,
        "match_scores": scores,
        "ai_recommendation": ai_result
    }

@app.get("/applications/candidate/{candidate_id}")
async def get_candidate_applications(candidate_id: int, db: Session = Depends(get_db)):
    """Get all applications for a candidate"""
    applications = db.query(Application).join(Internship).join(Company).filter(
        Application.candidate_id == candidate_id
    ).all()
    
    result = []
    for app in applications:
        app_dict = convert_model_to_dict(app)
        app_dict["internship_title"] = app.internship.title
        app_dict["company_name"] = app.internship.company.name
        app_dict["location"] = app.internship.location
        result.append(app_dict)
    
    return result

@app.get("/applications/internship/{internship_id}")
async def get_internship_applications(internship_id: int, db: Session = Depends(get_db)):
    """Get all applications for an internship"""
    applications = db.query(Application).join(Candidate).filter(
        Application.internship_id == internship_id
    ).all()
    
    result = []
    for app in applications:
        app_dict = convert_model_to_dict(app)
        app_dict["candidate_name"] = app.candidate.name
        app_dict["candidate_email"] = app.candidate.email
        app_dict["social_category"] = app.candidate.social_category
        app_dict["area_type"] = app.candidate.area_type
        result.append(app_dict)
    
    return result

# Analytics endpoints
@app.get("/analytics/diversity/{internship_id}")
async def get_diversity_analytics(internship_id: int, db: Session = Depends(get_db)):
    """Get diversity analytics for an internship"""
    
    applications = db.query(Application).join(Candidate).filter(
        Application.internship_id == internship_id
    ).all()
    
    total_applications = len(applications)
    if total_applications == 0:
        return {"message": "No applications found"}
    
    # Social category distribution
    category_counts = {}
    area_counts = {}
    first_gen_count = 0
    first_internship_count = 0
    
    for app in applications:
        category = app.candidate.social_category
        area = app.candidate.area_type
        
        category_counts[category] = category_counts.get(category, 0) + 1
        area_counts[area] = area_counts.get(area, 0) + 1
        
        if app.candidate.is_first_generation_graduate:
            first_gen_count += 1
        
        if app.candidate.previous_internships_count == 0:
            first_internship_count += 1
    
    return {
        "total_applications": total_applications,
        "social_category_distribution": {
            category: {"count": count, "percentage": round(count/total_applications * 100, 2)}
            for category, count in category_counts.items()
        },
        "area_type_distribution": {
            area: {"count": count, "percentage": round(count/total_applications * 100, 2)}
            for area, count in area_counts.items()
        },
        "first_generation_graduates": {
            "count": first_gen_count,
            "percentage": round(first_gen_count/total_applications * 100, 2)
        },
        "first_time_applicants": {
            "count": first_internship_count,
            "percentage": round(first_internship_count/total_applications * 100, 2)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
