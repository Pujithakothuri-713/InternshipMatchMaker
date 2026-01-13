#!/usr/bin/env python3
"""
Comprehensive Demo: End-to-End Internship Matching System
Shows how embeddings, matching algorithm, and AI work together
"""

import sys
import os
from pathlib import Path
import json
import requests
import time

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.embeddings import get_embedding_manager, preprocess_skills
from utils.matching_algorithm import get_matcher, convert_model_to_dict
from utils.ai_integration import GroqAIManager

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_subsection(title):
    print(f"\n{'─'*40}")
    print(f"  {title}")
    print('─'*40)

def demo_embeddings():
    """Demonstrate embedding generation and similarity calculation"""
    print_section("🧠 EMBEDDINGS DEMO - How Skills Are Vectorized")
    
    # Initialize embedding manager
    embedding_manager = get_embedding_manager()
    print("✅ Loaded sentence-transformers model: all-MiniLM-L6-v2")
    
    # Example candidate skills
    candidate_skills = ["Python", "Machine Learning", "Data Analysis", "Pandas", "Scikit-learn"]
    internship_skills = ["Python", "Deep Learning", "TensorFlow", "Data Science", "Neural Networks"]
    
    print(f"\n📊 Candidate Skills: {candidate_skills}")
    print(f"📊 Internship Requirements: {internship_skills}")
    
    # Generate embeddings
    print_subsection("Step 1: Generate Skill Embeddings")
    
    processed_candidate_skills = preprocess_skills(candidate_skills)
    processed_internship_skills = preprocess_skills(internship_skills)
    
    print(f"🔧 Processed candidate skills: {processed_candidate_skills}")
    print(f"🔧 Processed internship skills: {processed_internship_skills}")
    
    candidate_embedding = embedding_manager.generate_skills_embedding(processed_candidate_skills)
    internship_embedding = embedding_manager.generate_skills_embedding(processed_internship_skills)
    
    print(f"🎯 Candidate embedding vector size: {len(candidate_embedding)}")
    print(f"🎯 Internship embedding vector size: {len(internship_embedding)}")
    print(f"📝 Sample embedding values: {candidate_embedding[:5]}... (showing first 5 dimensions)")
    
    # Calculate similarity
    print_subsection("Step 2: Calculate Semantic Similarity")
    
    similarity = embedding_manager.calculate_similarity(candidate_embedding, internship_embedding)
    print(f"🔍 Cosine Similarity Score: {similarity:.4f}")
    print(f"📈 Similarity Percentage: {similarity * 100:.2f}%")
    
    # Show what this means
    if similarity > 0.8:
        interpretation = "Excellent match! High skill overlap."
    elif similarity > 0.6:
        interpretation = "Good match! Similar skill domains."
    elif similarity > 0.4:
        interpretation = "Moderate match! Some relevant skills."
    else:
        interpretation = "Low match! Different skill areas."
    
    print(f"💡 Interpretation: {interpretation}")
    
    return {
        "candidate_skills": candidate_skills,
        "internship_skills": internship_skills,
        "candidate_embedding": candidate_embedding,
        "internship_embedding": internship_embedding,
        "similarity": similarity
    }

def demo_matching_algorithm(embedding_data):
    """Demonstrate the comprehensive matching algorithm"""
    print_section("🎯 MATCHING ALGORITHM DEMO - Multi-Factor Scoring")
    
    # Create sample candidate and internship data
    candidate_data = {
        "name": "Priya Sharma",
        "skills": embedding_data["candidate_skills"],
        "skills_embedding": embedding_data["candidate_embedding"],
        "current_location": "Mumbai",
        "preferred_locations": ["Mumbai", "Pune", "Bangalore"],
        "education_level": "Bachelor's",
        "field_of_study": "Computer Science",
        "cgpa": 8.5,
        "social_category": "BC",  # Backward Class
        "area_type": "RURAL",
        "is_first_generation_graduate": True,
        "previous_internships_count": 0,
        "experience_months": 6
    }
    
    internship_data = {
        "title": "Data Science Intern",
        "company": "TechCorp India",
        "description": "Work on machine learning projects using Python and TensorFlow",
        "required_skills": embedding_data["internship_skills"],
        "skills_embedding": embedding_data["internship_embedding"],
        "location": "Mumbai",
        "min_education_level": "Bachelor's",
        "min_cgpa": 7.0,
        "experience_required": False,
        "is_remote": False,
        "category_quotas": {
            "SC": 0.15,
            "ST": 0.075,
            "BC": 0.27,
            "OC": 0.50
        }
    }
    
    current_selections = {
        "total": 10,
        "sc": 1, "st": 0, "bc": 1, "oc": 8, "others": 0,
        "rural": 2, "first_generation": 1, "first_internship": 3
    }
    
    print(f"👤 Candidate: {candidate_data['name']}")
    print(f"   Skills: {candidate_data['skills']}")
    print(f"   Location: {candidate_data['current_location']}")
    print(f"   Education: {candidate_data['education_level']} in {candidate_data['field_of_study']}")
    print(f"   CGPA: {candidate_data['cgpa']}")
    print(f"   Social Category: {candidate_data['social_category']}")
    print(f"   Area Type: {candidate_data['area_type']}")
    print(f"   First Generation Graduate: {candidate_data['is_first_generation_graduate']}")
    
    print(f"\n🏢 Internship: {internship_data['title']} at {internship_data['company']}")
    print(f"   Required Skills: {internship_data['required_skills']}")
    print(f"   Location: {internship_data['location']}")
    print(f"   Min CGPA: {internship_data['min_cgpa']}")
    print(f"   Experience Required: {internship_data['experience_required']}")
    
    # Initialize matcher and calculate scores
    print_subsection("Step 1: Initialize Matching Algorithm")
    matcher = get_matcher()
    print("✅ Initialized InternshipMatcher with:")
    print("   - EmbeddingManager for semantic similarity")
    print("   - AffirmativeActionCalculator for diversity scoring")
    
    print_subsection("Step 2: Calculate Comprehensive Match Scores")
    scores = matcher.calculate_comprehensive_match_score(
        candidate_data, internship_data, current_selections
    )
    
    print("📊 Individual Score Breakdown:")
    print(f"   🧠 Skill Match (40% weight): {scores['skill_match_score']:.4f}")
    print(f"   📍 Location Match (20% weight): {scores['location_match_score']:.4f}")
    print(f"   🎓 Qualification Match (25% weight): {scores['qualification_match_score']:.4f}")
    print(f"   ⚖️  Affirmative Action Boost (15% weight): {scores['affirmative_action_boost']:.4f}")
    print(f"   🎯 Overall Score: {scores['overall_score']:.4f}")
    
    # Explain the scoring
    print_subsection("Step 3: Score Analysis")
    
    print("🔍 Detailed Analysis:")
    print(f"   • Skill matching uses semantic similarity from embeddings: {scores['skill_match_score']:.4f}")
    print(f"   • Location preference matches perfectly: {scores['location_match_score']:.4f}")
    print(f"   • Qualifications exceed minimum requirements: {scores['qualification_match_score']:.4f}")
    
    if scores['affirmative_action_boost'] > 0:
        print(f"   • Diversity boost applied for underrepresented candidate: {scores['affirmative_action_boost']:.4f}")
        print(f"     - Rural background representation")
        print(f"     - First generation graduate support")
        print(f"     - Social category ({candidate_data['social_category']}) representation")
    else:
        print(f"   • No diversity boost needed: {scores['affirmative_action_boost']:.4f}")
    
    # Final recommendation
    overall_percentage = scores['overall_score'] * 100
    print(f"\n🎯 Final Match Score: {overall_percentage:.1f}%")
    
    if overall_percentage >= 80:
        recommendation = "🟢 HIGHLY RECOMMENDED"
    elif overall_percentage >= 65:
        recommendation = "🟡 RECOMMENDED"
    elif overall_percentage >= 50:
        recommendation = "🟠 CONDITIONALLY RECOMMENDED"
    else:
        recommendation = "🔴 NOT RECOMMENDED"
    
    print(f"📝 System Recommendation: {recommendation}")
    
    return {
        "candidate_data": candidate_data,
        "internship_data": internship_data,
        "scores": scores,
        "recommendation": recommendation
    }

def demo_ai_integration(matching_data):
    """Demonstrate AI-powered recommendation generation"""
    print_section("🤖 AI INTEGRATION DEMO - Intelligent Recommendations")
    
    print("🔗 Connecting to Groq API with Llama 3.1-8B-Instant...")
    
    try:
        ai_manager = GroqAIManager()
        print("✅ AI Manager initialized successfully")
        
        print_subsection("Step 1: Prepare Data for AI Analysis")
        
        candidate_data = matching_data["candidate_data"]
        internship_data = matching_data["internship_data"]
        scores = matching_data["scores"]
        
        print("📊 Sending to AI:")
        print(f"   • Candidate profile: {candidate_data['name']}")
        print(f"   • Internship details: {internship_data['title']}")
        print(f"   • Calculated scores: {scores}")
        
        print_subsection("Step 2: Generate AI Recommendation")
        
        print("🤔 AI is analyzing:")
        print("   • Skill compatibility and gaps")
        print("   • Career progression potential")
        print("   • Diversity and inclusion factors")
        print("   • Market context and opportunities")
        
        ai_result = ai_manager.generate_internship_recommendation(
            candidate_data, internship_data, scores
        )
        
        print_subsection("Step 3: AI Analysis Results")
        
        print(f"🎯 AI Recommendation: {ai_result.get('recommendation', 'N/A')}")
        print(f"📝 Detailed Reasoning:")
        reasoning = ai_result.get('reasoning', 'No reasoning provided')
        # Format reasoning for better readability
        lines = reasoning.split('. ')
        for line in lines:
            if line.strip():
                print(f"   • {line.strip()}.")
        
        print(f"📈 Confidence Score: {ai_result.get('confidence_score', 'N/A')}")
        
        if 'skills_gap_analysis' in ai_result:
            print(f"🔍 Skills Gap: {ai_result['skills_gap_analysis']}")
        
        if 'career_impact' in ai_result:
            print(f"🚀 Career Impact: {ai_result['career_impact']}")
        
        return ai_result
        
    except Exception as e:
        print(f"❌ AI Integration Error: {e}")
        return None

def demo_end_to_end_api():
    """Demonstrate the complete API workflow"""
    print_section("🌐 END-TO-END API DEMO - Complete Application Flow")
    
    base_url = "http://localhost:8001"
    
    print("🔍 Testing if backend is running...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
        else:
            print("❌ Backend not responding properly")
            return
    except:
        print("❌ Backend is not running. Please start it first:")
        print("   Run: python backend/main_simple.py")
        return
    
    print_subsection("Step 1: Create Candidate Profile")
    
    candidate_data = {
        "name": "Arjun Patel",
        "email": "arjun.patel@email.com",
        "skills": ["Python", "Django", "React", "PostgreSQL"],
        "location": "Ahmedabad",
        "social_category": "OC",
        "area_type": "URBAN"
    }
    
    response = requests.post(f"{base_url}/candidates/", json=candidate_data)
    if response.status_code == 200:
        print("✅ Candidate created successfully")
        candidate_result = response.json()
        print(f"   Candidate: {candidate_data['name']}")
        print(f"   Skills: {candidate_data['skills']}")
    else:
        print(f"❌ Failed to create candidate: {response.text}")
        return
    
    print_subsection("Step 2: Create Internship Posting")
    
    internship_data = {
        "title": "Full Stack Developer Intern",
        "company_name": "StartupXYZ",
        "description": "Build web applications using modern technologies",
        "required_skills": ["Python", "React", "JavaScript", "Database"],
        "location": "Ahmedabad",
        "duration_months": 6,
        "stipend": 20000
    }
    
    response = requests.post(f"{base_url}/internships/", json=internship_data)
    if response.status_code == 200:
        print("✅ Internship created successfully")
        internship_result = response.json()
        print(f"   Position: {internship_data['title']}")
        print(f"   Company: {internship_data['company_name']}")
        print(f"   Required Skills: {internship_data['required_skills']}")
    else:
        print(f"❌ Failed to create internship: {response.text}")
        return
    
    print_subsection("Step 3: Generate AI-Powered Match")
    
    match_request = {
        "candidate_skills": candidate_data["skills"],
        "candidate_location": candidate_data["location"],
        "candidate_category": candidate_data["social_category"],
        "internship_title": internship_data["title"],
        "internship_skills": internship_data["required_skills"],
        "internship_location": internship_data["location"]
    }
    
    response = requests.post(f"{base_url}/match/", json=match_request)
    if response.status_code == 200:
        print("✅ Match analysis completed")
        match_result = response.json()
        
        scores = match_result["match_scores"]
        ai_recommendation = match_result["ai_recommendation"]
        
        print(f"📊 Match Analysis:")
        print(f"   • Skill Similarity: {scores['skill_similarity']:.3f}")
        print(f"   • Location Match: {scores['location_match']:.3f}")
        print(f"   • Overall Score: {scores['overall_score']:.3f}")
        
        print(f"🤖 AI Recommendation: {ai_recommendation.get('recommendation', 'N/A')}")
        
        reasoning = ai_recommendation.get('reasoning', '')
        if reasoning:
            print(f"📝 AI Reasoning: {reasoning[:200]}...")
        
    else:
        print(f"❌ Failed to generate match: {response.text}")

def main():
    """Run the complete demo"""
    print("🎯 INTERNSHIP MATCHING SYSTEM - COMPLETE DEMO")
    print("Demonstrating embeddings, matching algorithm, AI integration, and API flow")
    print("=" * 80)
    
    # Demo 1: Embeddings
    embedding_data = demo_embeddings()
    
    # Demo 2: Matching Algorithm
    matching_data = demo_matching_algorithm(embedding_data)
    
    # Demo 3: AI Integration
    ai_result = demo_ai_integration(matching_data)
    
    # Demo 4: End-to-End API
    demo_end_to_end_api()
    
    print_section("🎉 DEMO COMPLETE - System Overview")
    
    print("🔧 Technical Architecture:")
    print("   1. 🧠 Embeddings: sentence-transformers for semantic skill matching")
    print("   2. ⚖️  Affirmative Action: Fair representation algorithms")
    print("   3. 🎯 Matching: Multi-factor scoring (skills, location, qualifications, diversity)")
    print("   4. 🤖 AI: Groq API with Llama 3.1 for intelligent recommendations")
    print("   5. 🌐 API: FastAPI backend with comprehensive endpoints")
    print("   6. 💾 Database: SQLAlchemy models with embedding storage")
    
    print("\n🚀 Key Features:")
    print("   ✅ Semantic skill matching using AI embeddings")
    print("   ✅ Affirmative action for SC/ST/BC/OC categories")
    print("   ✅ Rural area representation (30% target)")
    print("   ✅ First-generation graduate support")
    print("   ✅ AI-powered recommendation explanations")
    print("   ✅ Real-time matching and scoring")
    print("   ✅ Comprehensive diversity analytics")
    
    print("\n📈 Next Steps:")
    print("   1. View API docs: http://localhost:8001/docs")
    print("   2. Start frontend: streamlit run frontend/app.py")
    print("   3. Test the complete application!")

if __name__ == "__main__":
    main()
