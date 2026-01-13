#!/usr/bin/env python3
"""
Simplified Demo: How the Internship Matching System Works
Focus on the working API and show the end-to-end flow
"""

import requests
import json
import time

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_subsection(title):
    print(f"\n{'─'*40}")
    print(f"  {title}")
    print('─'*40)

def demo_api_workflow():
    """Demonstrate the complete API workflow with real backend"""
    print_section("🌐 COMPLETE SYSTEM DEMO - End-to-End Workflow")
    
    base_url = "http://localhost:8001"
    
    print("🔍 Testing backend connection...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is running!")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
        else:
            print("❌ Backend not responding properly")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        print("💡 Make sure to start the backend first:")
        print("   Run: python backend/main_simple.py")
        return False
    
    print_subsection("Step 1: Test AI Integration")
    
    try:
        response = requests.get(f"{base_url}/test-ai", timeout=15)
        if response.status_code == 200:
            ai_test = response.json()
            print("✅ AI Integration working!")
            print(f"   Status: {ai_test.get('status', 'unknown')}")
            
            if 'ai_recommendation' in ai_test:
                ai_rec = ai_test['ai_recommendation']
                print(f"   🤖 AI Response: {ai_rec.get('recommendation', 'N/A')}")
                
                reasoning = ai_rec.get('reasoning', '')
                if reasoning:
                    # Show first part of reasoning
                    lines = reasoning.split('.')[:3]
                    for line in lines:
                        if line.strip():
                            print(f"      • {line.strip()}.")
        else:
            print(f"❌ AI test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI test error: {e}")
        return False
    
    print_subsection("Step 2: Create Sample Candidates")
    
    candidates = [
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@email.com",
            "skills": ["Python", "Machine Learning", "Data Science", "Pandas", "Scikit-learn"],
            "location": "Mumbai",
            "social_category": "BC",
            "area_type": "RURAL"
        },
        {
            "name": "Arjun Reddy",
            "email": "arjun.reddy@email.com", 
            "skills": ["Java", "Spring Boot", "Microservices", "AWS", "Docker"],
            "location": "Hyderabad",
            "social_category": "OC",
            "area_type": "URBAN"
        },
        {
            "name": "Sunita Kumari",
            "email": "sunita.kumari@email.com",
            "skills": ["React", "JavaScript", "Node.js", "MongoDB", "Express"],
            "location": "Patna",
            "social_category": "SC", 
            "area_type": "RURAL"
        }
    ]
    
    created_candidates = []
    for candidate in candidates:
        try:
            response = requests.post(f"{base_url}/candidates/", json=candidate)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created candidate: {candidate['name']}")
                print(f"   Skills: {candidate['skills'][:3]}... ({len(candidate['skills'])} total)")
                print(f"   Location: {candidate['location']}")
                print(f"   Category: {candidate['social_category']} ({candidate['area_type']})")
                created_candidates.append(candidate)
            else:
                print(f"❌ Failed to create {candidate['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating {candidate['name']}: {e}")
    
    print_subsection("Step 3: Create Sample Internships")
    
    internships = [
        {
            "title": "Data Science Intern",
            "company_name": "TechCorp India",
            "description": "Work on machine learning projects using Python and AI frameworks",
            "required_skills": ["Python", "Machine Learning", "Data Analysis", "TensorFlow"],
            "location": "Mumbai",
            "duration_months": 6,
            "stipend": 25000
        },
        {
            "title": "Backend Developer Intern", 
            "company_name": "StartupXYZ",
            "description": "Build scalable backend systems using Java and cloud technologies",
            "required_skills": ["Java", "Spring Boot", "REST API", "Database"],
            "location": "Bangalore",
            "duration_months": 4,
            "stipend": 20000
        },
        {
            "title": "Frontend Developer Intern",
            "company_name": "WebTech Solutions",
            "description": "Create responsive web applications using React and modern JavaScript",
            "required_skills": ["React", "JavaScript", "HTML", "CSS", "Redux"],
            "location": "Pune",
            "duration_months": 3,
            "stipend": 18000
        }
    ]
    
    created_internships = []
    for internship in internships:
        try:
            response = requests.post(f"{base_url}/internships/", json=internship)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created internship: {internship['title']}")
                print(f"   Company: {internship['company_name']}")
                print(f"   Skills: {internship['required_skills'][:3]}... ({len(internship['required_skills'])} total)")
                print(f"   Location: {internship['location']}")
                print(f"   Stipend: ₹{internship['stipend']:,}/month")
                created_internships.append(internship)
            else:
                print(f"❌ Failed to create {internship['title']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating {internship['title']}: {e}")
    
    print_subsection("Step 4: Generate AI-Powered Matches")
    
    if not created_candidates or not created_internships:
        print("❌ Cannot generate matches without candidates and internships")
        return False
    
    # Test different combinations to show how the system works
    match_combinations = [
        # Perfect match: Data Science candidate + Data Science internship
        (created_candidates[0], created_internships[0], "Perfect Skills + Location Match"),
        # Good match: Java developer + Backend internship  
        (created_candidates[1], created_internships[1], "Good Skills Match, Different Location"),
        # Moderate match: Frontend candidate + Frontend internship
        (created_candidates[2], created_internships[2], "Skills Match, Different Location"),
        # Cross-domain match: Data Science candidate + Frontend internship
        (created_candidates[0], created_internships[2], "Cross-Domain Skills Test")
    ]
    
    for i, (candidate, internship, scenario) in enumerate(match_combinations, 1):
        print(f"\n🔍 Match Scenario {i}: {scenario}")
        print(f"   Candidate: {candidate['name']} ({candidate['social_category']}, {candidate['area_type']})")
        print(f"   Internship: {internship['title']} at {internship['company_name']}")
        
        match_request = {
            "candidate_skills": candidate["skills"],
            "candidate_location": candidate["location"],
            "candidate_category": candidate["social_category"],
            "internship_title": internship["title"],
            "internship_skills": internship["required_skills"],
            "internship_location": internship["location"]
        }
        
        try:
            response = requests.post(f"{base_url}/match/", json=match_request, timeout=20)
            if response.status_code == 200:
                match_result = response.json()
                
                scores = match_result["match_scores"]
                ai_recommendation = match_result["ai_recommendation"]
                
                print(f"   📊 Match Analysis:")
                print(f"      • Skill Similarity: {scores['skill_similarity']:.3f} ({scores['skill_similarity']*100:.1f}%)")
                print(f"      • Location Match: {scores['location_match']:.3f}")
                print(f"      • Overall Score: {scores['overall_score']:.3f} ({scores['overall_score']*100:.1f}%)")
                
                # Determine match quality
                overall_pct = scores['overall_score'] * 100
                if overall_pct >= 80:
                    quality = "🟢 EXCELLENT"
                elif overall_pct >= 65:
                    quality = "🟡 GOOD"
                elif overall_pct >= 50:
                    quality = "🟠 MODERATE"
                else:
                    quality = "🔴 POOR"
                
                print(f"      • Match Quality: {quality}")
                
                # Show AI recommendation
                ai_rec = ai_recommendation.get('recommendation', 'N/A')
                print(f"   🤖 AI Recommendation: {ai_rec}")
                
                # Show key reasoning points
                reasoning = ai_recommendation.get('reasoning', '')
                if reasoning:
                    lines = reasoning.split('.')[:2]  # First 2 sentences
                    for line in lines:
                        if line.strip():
                            print(f"      💡 {line.strip()}.")
                
            else:
                print(f"   ❌ Match generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error generating match: {e}")
    
    print_subsection("Step 5: View All Data")
    
    # Show summary of created data
    try:
        candidates_response = requests.get(f"{base_url}/candidates/")
        internships_response = requests.get(f"{base_url}/internships/")
        
        if candidates_response.status_code == 200 and internships_response.status_code == 200:
            candidates_data = candidates_response.json()
            internships_data = internships_response.json()
            
            print(f"📊 System Summary:")
            print(f"   • Total Candidates: {candidates_data.get('total', 0)}")
            print(f"   • Total Internships: {internships_data.get('total', 0)}")
            
            # Diversity breakdown
            categories = {}
            areas = {}
            for candidate in candidates_data.get('candidates', []):
                cat = candidate.get('social_category', 'Unknown')
                area = candidate.get('area_type', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
                areas[area] = areas.get(area, 0) + 1
            
            print(f"   • Social Categories: {categories}")
            print(f"   • Area Types: {areas}")
            
        else:
            print("❌ Failed to retrieve summary data")
            
    except Exception as e:
        print(f"❌ Error retrieving summary: {e}")
    
    return True

def explain_system_architecture():
    """Explain how the system works technically"""
    print_section("🏗️ SYSTEM ARCHITECTURE - How It All Works Together")
    
    print("🔧 Technical Components:")
    print("   1. 🧠 Embeddings (sentence-transformers)")
    print("      • Converts skills to 384-dimensional vectors")
    print("      • Enables semantic similarity matching")
    print("      • Example: 'Python' and 'Machine Learning' = high similarity")
    
    print("   2. ⚖️ Affirmative Action Calculator")
    print("      • Ensures fair representation across social categories")
    print("      • Targets: SC(15%), ST(7.5%), BC(27%), OC(50.5%)")
    print("      • Rural area representation: 30% target")
    print("      • First-generation graduate support")
    
    print("   3. 🎯 Matching Algorithm")
    print("      • Multi-factor scoring system:")
    print("        - Skills similarity: 40% weight")
    print("        - Location match: 20% weight") 
    print("        - Qualifications: 25% weight")
    print("        - Diversity boost: 15% weight")
    
    print("   4. 🤖 AI Integration (Groq + Llama 3.1)")
    print("      • Analyzes match context and provides explanations")
    print("      • Considers career progression potential")
    print("      • Accounts for diversity and inclusion factors")
    print("      • Generates human-readable recommendations")
    
    print("   5. 🌐 FastAPI Backend")
    print("      • RESTful API with comprehensive endpoints")
    print("      • Real-time matching and scoring")
    print("      • CRUD operations for candidates and internships")
    print("      • Analytics and diversity tracking")
    
    print("\n🔄 Processing Flow:")
    print("   Input → Embeddings → Matching → AI Analysis → Recommendation")
    print("   1. Skills converted to vectors using transformer models")
    print("   2. Cosine similarity calculated between candidate and job vectors")
    print("   3. Location, qualifications, and diversity factors scored")
    print("   4. Combined score sent to AI for contextual analysis")
    print("   5. AI generates explanation and final recommendation")

def main():
    """Run the complete demonstration"""
    print("🎯 INTERNSHIP MATCHING SYSTEM - COMPREHENSIVE DEMO")
    print("Demonstrating embeddings, matching, AI integration, and complete workflow")
    print("=" * 80)
    
    # Explain the system first
    explain_system_architecture()
    
    # Run the actual demo
    success = demo_api_workflow()
    
    if success:
        print_section("🎉 DEMO COMPLETED SUCCESSFULLY!")
        
        print("✅ What You Just Saw:")
        print("   • Semantic skill matching using AI embeddings")
        print("   • Multi-factor scoring with affirmative action")
        print("   • AI-powered recommendation generation")
        print("   • Real-time API processing")
        print("   • Diversity and inclusion tracking")
        
        print("\n🚀 Next Steps:")
        print("   1. 📖 View API Documentation: http://localhost:8001/docs")
        print("   2. 🎨 Start Streamlit Frontend: streamlit run frontend/app.py")
        print("   3. 🔧 Explore the codebase and modify algorithms")
        print("   4. 📊 Add more sophisticated analytics")
        
        print("\n💡 Key Insights:")
        print("   • The system balances merit with diversity")
        print("   • Embeddings enable semantic understanding of skills")
        print("   • AI provides explainable recommendations")
        print("   • Real-time processing enables instant matching")
        
    else:
        print_section("⚠️ DEMO INCOMPLETE")
        print("Some components failed. Please check:")
        print("   1. Backend server is running (python backend/main_simple.py)")
        print("   2. All dependencies are installed")
        print("   3. Groq API key is properly configured")

if __name__ == "__main__":
    main()
