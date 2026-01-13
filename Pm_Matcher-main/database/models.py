from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from enum import Enum
import json

Base = declarative_base()

class SocialCategory(str, Enum):
    OC = "OC"  # Open Category
    BC = "BC"  # Backward Class
    SC = "SC"  # Scheduled Caste
    ST = "ST"  # Scheduled Tribe
    OTHERS = "OTHERS"

class AreaType(str, Enum):
    RURAL = "RURAL"
    URBAN = "URBAN"
    SEMI_URBAN = "SEMI_URBAN"

class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    SHORTLISTED = "SHORTLISTED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    
    # Academic Information
    education_level = Column(String, nullable=False)  # "UG", "PG", "Diploma", etc.
    field_of_study = Column(String, nullable=False)
    cgpa = Column(Float)
    graduation_year = Column(Integer)
    institution = Column(String)
    
    # Skills and Experience
    skills = Column(JSON)  # List of skills
    skills_embedding = Column(JSON)  # Embedding vector for skills
    experience_months = Column(Integer, default=0)
    projects = Column(JSON)  # List of project descriptions
    
    # Location Preferences
    preferred_locations = Column(JSON)  # List of preferred cities/states
    current_location = Column(String)
    willing_to_relocate = Column(Boolean, default=True)
    
    # Affirmative Action Fields
    social_category = Column(String, nullable=False)  # OC, BC, SC, ST, OTHERS
    area_type = Column(String, nullable=False)  # RURAL, URBAN, SEMI_URBAN
    state = Column(String, nullable=False)
    district = Column(String, nullable=False)
    is_first_generation_graduate = Column(Boolean, default=False)
    family_income_annual = Column(Float)  # In INR
    
    # Previous Participation
    previous_internships_count = Column(Integer, default=0)
    previous_internship_companies = Column(JSON)  # List of previous companies
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    applications = relationship("Application", back_populates="candidate")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    description = Column(Text)
    
    # Location
    headquarters = Column(String)
    locations = Column(JSON)  # List of office locations
    
    # Capacity and Diversity
    total_internship_capacity = Column(Integer, nullable=False)
    current_intern_count = Column(Integer, default=0)
    diversity_commitment = Column(Float, default=0.0)  # Percentage commitment to diversity
    rural_quota = Column(Float, default=0.0)  # Percentage for rural candidates
    category_quotas = Column(JSON)  # Quotas for different social categories
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    internships = relationship("Internship", back_populates="company")

class Internship(Base):
    __tablename__ = "internships"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Requirements
    required_skills = Column(JSON, nullable=False)  # List of required skills
    skills_embedding = Column(JSON)  # Embedding vector for required skills
    min_education_level = Column(String, nullable=False)
    preferred_fields = Column(JSON)  # Preferred fields of study
    min_cgpa = Column(Float, default=0.0)
    experience_required = Column(Boolean, default=False)
    
    # Location and Duration
    location = Column(String, nullable=False)
    is_remote = Column(Boolean, default=False)
    duration_months = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    application_deadline = Column(DateTime, nullable=False)
    
    # Compensation
    stipend_amount = Column(Float, default=0.0)
    currency = Column(String, default="INR")
    
    # Capacity and Diversity
    total_positions = Column(Integer, nullable=False)
    filled_positions = Column(Integer, default=0)
    reserved_positions = Column(JSON)  # Positions reserved for different categories
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    company = relationship("Company", back_populates="internships")
    applications = relationship("Application", back_populates="internship")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    internship_id = Column(Integer, ForeignKey("internships.id"))
    
    # Matching Scores
    skill_match_score = Column(Float, default=0.0)  # 0-1 based on embedding similarity
    location_match_score = Column(Float, default=0.0)  # 0-1 based on location preference
    qualification_match_score = Column(Float, default=0.0)  # 0-1 based on education/CGPA
    affirmative_action_boost = Column(Float, default=0.0)  # Boost for diversity
    overall_score = Column(Float, default=0.0)  # Weighted combination of above scores
    
    # AI Recommendation
    ai_recommendation = Column(Text)  # LLM-generated recommendation
    ai_reasoning = Column(Text)  # Explanation for the recommendation
    recommendation_confidence = Column(Float, default=0.0)  # 0-1 confidence score
    
    # Application Status
    status = Column(String, default=ApplicationStatus.PENDING.value)
    applied_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    
    # Additional Fields
    cover_letter = Column(Text)
    resume_url = Column(String)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    internship = relationship("Internship", back_populates="applications")

# Database utility functions
def create_database():
    """Create the database and all tables"""
    engine = create_engine("sqlite:///internship_matcher.db", echo=True)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session():
    """Get database session"""
    engine = create_engine("sqlite:///internship_matcher.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
