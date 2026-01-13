#!/usr/bin/env python3
"""
Test script to verify PDF parsing functionality with the mock resume
"""

import PyPDF2
import re
from io import BytesIO

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_skills_from_text(text):
    """Extract skills from text"""
    # Define comprehensive skill keywords
    technical_skills = [
        'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css', 'react', 'angular',
        'nodejs', 'django', 'flask', 'spring', 'mysql', 'postgresql', 'mongodb',
        'git', 'docker', 'aws', 'machine learning', 'data science', 'devops',
        'restful apis', 'microservices', 'ci/cd', 'bootstrap', 'express',
        'jwt', 'pandas', 'numpy', 'scikit-learn', 'github'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in technical_skills:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates

def extract_education_from_text(text):
    """Extract education information from text"""
    education_patterns = [
        r'bachelor.*?technology',
        r'b\.?tech',
        r'bachelor.*?engineering',
        r'b\.?e\.',
        r'master.*?technology',
        r'm\.?tech',
        r'bachelor.*?science',
        r'b\.?sc',
        r'master.*?science',
        r'm\.?sc',
        r'bachelor.*?computer.*?science',
        r'bachelor.*?information.*?technology'
    ]
    
    text_lower = text.lower()
    for pattern in education_patterns:
        if re.search(pattern, text_lower):
            return pattern.replace('.*?', ' ').replace('\\', '').title()
    
    return "Not specified"

def extract_contact_info_from_text(text):
    """Extract contact information from text"""
    contact_info = {}
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['email'] = emails[0]
    
    # Phone pattern (Indian format)
    phone_pattern = r'(?:\+91|91)?\s*[6-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    if phones:
        contact_info['phone'] = phones[0]
    
    # Name extraction (first line that looks like a name)
    lines = text.split('\n')
    for line in lines[:3]:  # Check first 3 lines
        line = line.strip()
        if len(line) > 2 and len(line) < 50 and line.isalpha():
            contact_info['name'] = line.title()
            break
    
    return contact_info

def test_pdf_parsing():
    """Test the PDF parsing with the mock resume"""
    print("🧪 Testing PDF parsing functionality with mock resume...\n")
    
    # Read the PDF file
    with open('mock_resume_rahul_sharma.pdf', 'rb') as file:
        # Extract text
        text = extract_text_from_pdf(file)
        print("📄 Extracted Text Preview:")
        print(text[:500] + "..." if len(text) > 500 else text)
        print("\n" + "="*60 + "\n")
        
        # Test skill extraction
        skills = extract_skills_from_text(text)
        print("🔧 Extracted Skills:")
        for skill in skills:
            print(f"  • {skill}")
        print(f"\nTotal skills found: {len(skills)}\n")
        
        # Test education extraction
        education = extract_education_from_text(text)
        print(f"🎓 Extracted Education: {education}\n")
        
        # Test contact info extraction
        contact_info = extract_contact_info_from_text(text)
        print("📞 Extracted Contact Information:")
        for key, value in contact_info.items():
            print(f"  • {key.title()}: {value}")
        
        print("\n✅ PDF parsing test completed successfully!")

if __name__ == "__main__":
    test_pdf_parsing()
