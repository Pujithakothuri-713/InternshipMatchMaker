#!/usr/bin/env python3
"""
Test the improved matching algorithm
"""

import requests
import json

def test_matching_improvements():
    """Test that the improved matching algorithm filters out irrelevant matches"""
    
    print("🧪 Testing improved matching algorithm...\n")
    
    # Test with a tech candidate (should get mostly tech internships)
    candidate_data = {
        "email": "test.tech@example.com",
        "name": "Tech Test Candidate",
        "phone": "+91 9876543210",
        "education_level": "Bachelor",
        "field_of_study": "Computer Science",
        "cgpa": "8.5",
        "graduation_year": 2024,
        "institution": "Test University",
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "SQL", "Git", 
            "Docker", "AWS", "Machine Learning", "Data Science",
            "HTML", "CSS", "MongoDB", "PostgreSQL", "Flask", "Django"
        ],
        "experience_months": 6,
        "projects": [],
        "preferred_locations": ["Mumbai", "Bangalore", "Pune"],
        "current_location": "Mumbai, Maharashtra",
        "willing_to_relocate": True,
        "social_category": "OC",
        "area_type": "URBAN",
        "state": "Maharashtra",
        "district": "Mumbai",
        "is_first_generation_graduate": False,
        "family_income_annual": None,
        "previous_internships_count": 0,
        "previous_internship_companies": []
    }
    
    # Register candidate
    print("📝 Registering test candidate...")
    response = requests.post("http://localhost:8002/candidates/", json=candidate_data)
    
    if response.status_code == 200:
        result = response.json()
        candidate_id = result['candidate_id']
        print(f"✅ Candidate registered with ID: {candidate_id}")
        
        # Get matches
        print(f"🔍 Finding matches for candidate {candidate_id}...")
        matches_response = requests.get(f"http://localhost:8002/matches/candidate/{candidate_id}")
        
        if matches_response.status_code == 200:
            matches_data = matches_response.json()
            
            print(f"📊 Match Results:")
            print(f"   Status: {matches_data.get('status', 'Unknown')}")
            print(f"   Total matches: {matches_data.get('total_matches_found', 0)}")
            print(f"   Relevant matches: {matches_data.get('relevant_matches_count', 0)}")
            print(f"   Threshold used: {matches_data.get('skill_match_threshold', 0)}")
            
            matches = matches_data.get('matches', [])
            
            if matches:
                print(f"\n🎯 Top matches:")
                for i, match in enumerate(matches[:5], 1):
                    internship = match['internship']
                    similarity = match.get('embedding_similarity', 0)
                    match_pct = match.get('match_percentage', 0)
                    
                    print(f"   {i}. {internship['title']} at {internship['company_name']}")
                    print(f"      Industry: {internship['industry']}")
                    print(f"      Skills similarity: {similarity:.3f}")
                    print(f"      Match: {match_pct}%")
                    print(f"      Required skills: {', '.join(internship['required_skills'][:3])}...")
                    print()
                
                # Check if we're getting irrelevant matches
                irrelevant_matches = []
                for match in matches:
                    internship = match['internship']
                    industry = internship['industry'].lower()
                    if any(word in industry for word in ['agriculture', 'culinary', 'music', 'sports']):
                        irrelevant_matches.append(internship['title'])
                
                if irrelevant_matches:
                    print(f"⚠️  WARNING: Still getting irrelevant matches:")
                    for title in irrelevant_matches:
                        print(f"   - {title}")
                else:
                    print("✅ Good! No irrelevant matches found.")
                    
        else:
            print(f"❌ Failed to get matches: {matches_response.status_code}")
            print(matches_response.text)
            
    else:
        print(f"❌ Failed to register candidate: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_matching_improvements()
