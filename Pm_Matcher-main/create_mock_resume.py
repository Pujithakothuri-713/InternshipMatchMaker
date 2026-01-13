#!/usr/bin/env python3
"""
Create a mock resume PDF for testing the internship matcher upload functionality
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_mock_resume():
    # Create the PDF document
    filename = "mock_resume_rahul_sharma.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get sample styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue,
        borderWidth=1,
        borderColor=colors.darkblue,
        borderPadding=5
    )
    
    # Name and Header
    name = Paragraph("RAHUL SHARMA", title_style)
    elements.append(name)
    
    # Contact Information
    contact_info = Paragraph("""
    <para align=center>
    Email: rahul.sharma@email.com | Phone: +91 9876543210<br/>
    Location: Mumbai, Maharashtra | LinkedIn: linkedin.com/in/rahulsharma
    </para>
    """, styles['Normal'])
    elements.append(contact_info)
    elements.append(Spacer(1, 20))
    
    # Education Section
    education_heading = Paragraph("EDUCATION", heading_style)
    elements.append(education_heading)
    
    education_content = Paragraph("""
    <b>Bachelor of Technology in Computer Science</b><br/>
    Indian Institute of Technology, Mumbai<br/>
    CGPA: 8.5/10.0 | Graduation Year: 2024<br/>
    Relevant Coursework: Data Structures, Algorithms, Machine Learning, Database Systems
    """, styles['Normal'])
    elements.append(education_content)
    elements.append(Spacer(1, 15))
    
    # Skills Section
    skills_heading = Paragraph("TECHNICAL SKILLS", heading_style)
    elements.append(skills_heading)
    
    skills_content = Paragraph("""
    <b>Programming Languages:</b> Python, Java, JavaScript, C++, SQL<br/>
    <b>Web Technologies:</b> React, Angular, HTML, CSS, Bootstrap, NodeJS<br/>
    <b>Databases:</b> MySQL, PostgreSQL, MongoDB<br/>
    <b>Tools & Technologies:</b> Git, Docker, AWS, Machine Learning, Data Science<br/>
    <b>Frameworks:</b> Django, Flask, Express, Spring Boot<br/>
    <b>Other:</b> RESTful APIs, Microservices, DevOps, CI/CD
    """, styles['Normal'])
    elements.append(skills_content)
    elements.append(Spacer(1, 15))
    
    # Experience Section
    experience_heading = Paragraph("EXPERIENCE", heading_style)
    elements.append(experience_heading)
    
    experience_content = Paragraph("""
    <b>Software Development Intern</b> | Tech Solutions Pvt Ltd | Jun 2023 - Aug 2023<br/>
    • Developed web applications using React and Node.js<br/>
    • Implemented RESTful APIs for data management<br/>
    • Collaborated with cross-functional teams using Agile methodologies<br/>
    • Gained experience in database design and optimization
    """, styles['Normal'])
    elements.append(experience_content)
    elements.append(Spacer(1, 15))
    
    # Projects Section
    projects_heading = Paragraph("PROJECTS", heading_style)
    elements.append(projects_heading)
    
    projects_content = Paragraph("""
    <b>E-Commerce Web Application</b><br/>
    • Built a full-stack e-commerce platform using React, Node.js, and MongoDB<br/>
    • Implemented user authentication, payment gateway integration<br/>
    • Technologies: React, Express, MongoDB, JWT Authentication<br/><br/>
    
    <b>Machine Learning Price Predictor</b><br/>
    • Developed a machine learning model to predict house prices<br/>
    • Used Python, Pandas, NumPy, and Scikit-learn<br/>
    • Achieved 85% accuracy in price predictions
    """, styles['Normal'])
    elements.append(projects_content)
    elements.append(Spacer(1, 15))
    
    # Achievements Section
    achievements_heading = Paragraph("ACHIEVEMENTS & CERTIFICATIONS", heading_style)
    elements.append(achievements_heading)
    
    achievements_content = Paragraph("""
    • AWS Certified Solutions Architect Associate<br/>
    • Winner of College Hackathon 2023<br/>
    • Published research paper on Machine Learning algorithms<br/>
    • Active contributor to open-source projects on GitHub<br/>
    • Completed online courses in Data Science and AI
    """, styles['Normal'])
    elements.append(achievements_content)
    
    # Build PDF
    doc.build(elements)
    print(f"✅ Mock resume created successfully: {filename}")
    return filename

if __name__ == "__main__":
    create_mock_resume()
