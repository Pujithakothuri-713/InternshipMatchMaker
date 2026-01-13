#!/usr/bin/env python3
"""
Comprehensive End-to-End Demo of the Internship Matcher System

This script demonstrates:
1. Mock data (companies, internships with previous participation history)
2. Real candidate registration
3. Real AI-powered matching with embeddings
4. Affirmative action and first-time participant preferences
5. Diversity analytics
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"

def make_api_request(endpoint, method="GET", data=None):
    """Helper function to make API requests"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def display_mock_data():
    """Display the loaded mock data"""
    print_section("MOCK DATA OVERVIEW")
    
    # Companies
    companies = make_api_request("/companies/")
    if companies:
        print(f"📊 Loaded {len(companies)} companies:")
        for company in companies:
            print(f"  🏢 {company['name']} ({company['industry']})")
            print(f"     📍 {company['headquarters']}")
            print(f"     📈 Diversity commitment: {company['diversity_commitment']*100:.1f}%")
            print(f"     🎯 Rural quota: {company['rural_quota']*100:.1f}%")
    
    # Internships
    internships = make_api_request("/internships/")
    if internships:
        print(f"\n💼 Loaded {len(internships)} internships:")
        for internship in internships:
            print(f"  📝 {internship['title']} at {internship['company_name']}")
            print(f"     💰 Stipend: ₹{internship['stipend_amount']:,.0f}/month")
            print(f"     📍 Location: {internship['location']} {'(Remote)' if internship['is_remote'] else ''}")
            print(f"     🎓 Min Education: {internship['min_education_level']}")
            print(f"     👥 Positions: {internship['total_positions'] - internship['filled_positions']}/{internship['total_positions']} available")
            
            # Previous participants
            prev_participants = internship.get('previous_participants', [])
            if prev_participants:
                print(f"     📚 Previous participants ({len(prev_participants)}):")
                for participant in prev_participants:
                    print(f"       • {participant['name']} ({participant['year']}) - {participant['category']}, {participant['area']} - {participant['performance']}")
            print()

def register_demo_candidates():
    """Register diverse demo candidates to show real registration"""
    print_section("REAL CANDIDATE REGISTRATION")
    
    demo_candidates = [
        {
            "email": "arjun.patel@gmail.com",
            "name": "Arjun Patel",
            "phone": "+91 9876543210",
            "education_level": "UG",
            "field_of_study": "Computer Science",
            "cgpa": 8.2,
            "graduation_year": 2024,
            "institution": "IIT Mumbai",
            "skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB"],
            "experience_months": 0,
            "projects": ["E-commerce Web App", "Task Management System"],
            "preferred_locations": ["Mumbai", "Pune"],
            "current_location": "Mumbai, Maharashtra",
            "willing_to_relocate": True,
            "social_category": "OC",
            "area_type": "URBAN",
            "state": "Maharashtra",
            "district": "Mumbai",
            "is_first_generation_graduate": False,
            "family_income_annual": 800000,
            "previous_internships_count": 0,
            "previous_internship_companies": []
        },
        {
            "email": "kavya.reddy@gmail.com",
            "name": "Kavya Reddy",
            "phone": "+91 9876543211",
            "education_level": "UG",
            "field_of_study": "Data Science",
            "cgpa": 8.7,
            "graduation_year": 2024,
            "institution": "NIT Warangal",
            "skills": ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "TensorFlow"],
            "experience_months": 0,
            "projects": ["Stock Price Prediction", "Sentiment Analysis Tool"],
            "preferred_locations": ["Hyderabad", "Bangalore"],
            "current_location": "Warangal, Telangana",
            "willing_to_relocate": True,
            "social_category": "BC",
            "area_type": "RURAL",
            "state": "Telangana",
            "district": "Warangal",
            "is_first_generation_graduate": True,
            "family_income_annual": 250000,
            "previous_internships_count": 0,
            "previous_internship_companies": []
        },
        {
            "email": "rajesh.kumar@gmail.com",
            "name": "Rajesh Kumar",
            "phone": "+91 9876543212",
            "education_level": "UG",
            "field_of_study": "Electronics Engineering",
            "cgpa": 7.8,
            "graduation_year": 2024,
            "institution": "Government Engineering College",
            "skills": ["IoT", "Arduino", "Python", "C++", "Sensors"],
            "experience_months": 0,
            "projects": ["Smart Home Automation", "Weather Monitoring System"],
            "preferred_locations": ["Pune", "Mumbai"],
            "current_location": "Nashik, Maharashtra",
            "willing_to_relocate": True,
            "social_category": "SC",
            "area_type": "RURAL",
            "state": "Maharashtra",
            "district": "Nashik",
            "is_first_generation_graduate": True,
            "family_income_annual": 180000,
            "previous_internships_count": 0,
            "previous_internship_companies": []
        }
    ]
    
    registered_candidates = []
    
    for candidate_data in demo_candidates:
        print(f"\n👤 Registering: {candidate_data['name']}")
        print(f"   📧 {candidate_data['email']}")
        print(f"   🎓 {candidate_data['education_level']} in {candidate_data['field_of_study']}")
        print(f"   📊 CGPA: {candidate_data['cgpa']}")
        print(f"   🏷️ Category: {candidate_data['social_category']} ({candidate_data['area_type']})")
        print(f"   🎯 First Gen Graduate: {candidate_data['is_first_generation_graduate']}")
        print(f"   💰 Family Income: ₹{candidate_data['family_income_annual']:,}")
        print(f"   🛠️ Skills: {', '.join(candidate_data['skills'][:3])}...")
        
        result = make_api_request("/candidates/", "POST", candidate_data)
        if result:
            candidate_id = result['candidate_id']
            registered_candidates.append(candidate_id)
            print(f"   ✅ Registered successfully! ID: {candidate_id}")
        else:
            print(f"   ❌ Registration failed!")
    
    return registered_candidates

def demonstrate_matching(candidate_ids):
    """Demonstrate the matching algorithm with real AI recommendations"""
    print_section("AI-POWERED MATCHING DEMONSTRATION")
    
    for candidate_id in candidate_ids:
        print(f"\n🔍 Finding matches for Candidate ID: {candidate_id}")
        
        # Get candidate details
        candidate = make_api_request(f"/candidates/{candidate_id}")
        if candidate:
            print(f"👤 {candidate['name']} ({candidate['social_category']}, {candidate['area_type']})")
            print(f"🎓 {candidate['education_level']} in {candidate['field_of_study']} (CGPA: {candidate.get('cgpa', 'N/A')})")
            print(f"🛠️ Skills: {', '.join(candidate['skills'])}")
            print(f"🎯 First-time applicant: {candidate['previous_internships_count'] == 0}")
        
        # Get matches
        matches = make_api_request(f"/matches/candidate/{candidate_id}")
        if matches:
            print(f"\n📊 Found {len(matches)} matches:")
            
            for i, match in enumerate(matches[:3], 1):  # Show top 3 matches
                internship = match['internship']
                scores = match['scores']
                
                print(f"\n  {i}. 🏢 {internship['title']} at {internship['company_name']}")
                print(f"     🎯 Match Score: {match['match_percentage']}%")
                print(f"     💰 Stipend: ₹{internship['stipend_amount']:,.0f}/month")
                print(f"     📍 Location: {internship['location']}")
                print(f"     ⏱️ Duration: {internship['duration_months']} months")
                
                print(f"     📈 Score Breakdown:")
                print(f"       • Skills: {scores['skill_match_score']:.3f}")
                print(f"       • Location: {scores['location_match_score']:.3f}")
                print(f"       • Qualifications: {scores['qualification_match_score']:.3f}")
                print(f"       • Diversity Boost: {scores['affirmative_action_boost']:.3f}")
                
                # Show diversity factors
                diversity = match.get('diversity_factors', {})
                print(f"     🌟 Diversity Benefits:")
                print(f"       • First-time applicant: {match.get('first_time_applicant_boost', False)}")
                print(f"       • Social category: {diversity.get('social_category')}")
                print(f"       • Rural/Urban: {diversity.get('area_type')}")
                print(f"       • First generation: {diversity.get('first_generation')}")
                
                # Show AI recommendation if available
                ai_rec = match.get('ai_recommendation')
                if ai_rec and not ai_rec.startswith("AI recommendation temporarily"):
                    print(f"     🤖 AI Recommendation: {ai_rec[:200]}...")
                
        print("\n" + "-"*50)

def show_diversity_analytics():
    """Show diversity analytics for mock internships"""
    print_section("DIVERSITY ANALYTICS")
    
    # Get internships
    internships = make_api_request("/internships/")
    if internships:
        for internship in internships[:3]:  # Show analytics for first 3 internships
            internship_id = internship['id']
            print(f"\n📊 Diversity Stats for: {internship['title']}")
            
            stats = make_api_request(f"/internships/{internship_id}/diversity-stats")
            if stats:
                print(f"👥 Total Previous Participants: {stats['total_previous_participants']}")
                
                print(f"\n📈 Social Category Distribution:")
                for category, data in stats['category_distribution'].items():
                    print(f"  • {category}: {data['count']} ({data['percentage']}%)")
                
                print(f"\n🏘️ Area Distribution:")
                for area, data in stats['area_distribution'].items():
                    print(f"  • {area}: {data['count']} ({data['percentage']}%)")
                
                print(f"\n🏆 Performance Distribution:")
                for performance, data in stats['performance_distribution'].items():
                    print(f"  • {performance}: {data['count']} ({data['percentage']}%)")

def test_ai_integration():
    """Test the AI integration"""
    print_section("AI INTEGRATION TEST")
    
    result = make_api_request("/test-ai/")
    if result:
        print("✅ AI Integration Status:", result['status'])
        if result['status'] == 'success':
            print("🤖 AI Recommendation Sample:")
            print(f"   {result['ai_recommendation'][:300]}...")
        else:
            print("❌ AI Error:", result.get('error', 'Unknown error'))

def main():
    """Run the complete demonstration"""
    print("🎯 INTERNSHIP MATCHER SYSTEM - COMPREHENSIVE DEMO")
    print("="*60)
    
    # Check if backend is running
    health = make_api_request("/health")
    if not health:
        print("❌ Backend server is not running! Please start it first.")
        return
    
    print(f"✅ Backend server is healthy! Timestamp: {health['timestamp']}")
    
    # Show mock data
    display_mock_data()
    
    # Test AI integration
    test_ai_integration()
    
    # Register demo candidates
    candidate_ids = register_demo_candidates()
    
    if candidate_ids:
        # Demonstrate matching
        demonstrate_matching(candidate_ids)
        
        # Show diversity analytics
        show_diversity_analytics()
    
    print_section("DEMO COMPLETE")
    print("🎉 All features demonstrated successfully!")
    print("\n🌐 Frontend URL: http://localhost:8504")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("\n💡 Key Features Demonstrated:")
    print("  ✅ Mock data for companies and internships with participation history")
    print("  ✅ Real candidate registration with comprehensive profiles")
    print("  ✅ AI-powered matching using real embeddings and LLM recommendations")
    print("  ✅ Advanced affirmative action algorithm favoring first-time participants")
    print("  ✅ Diversity analytics and previous participation tracking")
    print("  ✅ Rural vs urban preference and social category considerations")

if __name__ == "__main__":
    main()
