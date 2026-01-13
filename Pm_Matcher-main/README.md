# 🎯 Smart Internship Matcher

An AI-powered internship matching platform that ensures fair representation across social categories while providing intelligent recommendations using embeddings and LLM technology.

## 🌟 Features

### 🤖 AI-Powered Matching
- **Semantic Skill Matching**: Uses sentence-transformers embeddings to match candidate skills with internship requirements
- **LLM Recommendations**: Meta Llama AI via Groq API provides detailed explanations for every match
- **Intelligent Scoring**: Comprehensive scoring algorithm considering skills, qualifications, location, and diversity factors

### ⚖️ Affirmative Action & Diversity
- **Social Category Support**: Handles OC, BC, SC, ST categories with configurable quotas
- **Rural Representation**: Special consideration for rural area candidates
- **First-Generation Graduate Support**: Additional scoring boost for first-generation graduates
- **Economic Background Consideration**: Income-based diversity scoring

### 🎯 Smart Features
- **Location Preference Matching**: Considers candidate location preferences and willingness to relocate
- **Industry-wise Capacity Management**: Tracks and manages internship capacities
- **Real-time Analytics**: Comprehensive diversity and matching analytics
- **Application Tracking**: Complete application lifecycle management

## 🏗️ Architecture

```
Frontend (Streamlit) ←→ Backend (FastAPI) ←→ Database (SQLite)
                                ↓
                      AI Services (Groq + Embeddings)
```

### Technology Stack
- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: Streamlit with modern UI components
- **Database**: SQLite for development, easily scalable to PostgreSQL
- **AI/ML**: 
  - sentence-transformers for embeddings
  - Groq API with Meta Llama for recommendations
- **Analytics**: Plotly for interactive visualizations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (sign up at https://groq.com)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd internship-matcher
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Add your Groq API key to .env file
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Start Backend API
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`

### 4. Start Frontend
```bash
cd frontend
streamlit run app.py
```
The web interface will be available at `http://localhost:8501`

## 📊 Usage Guide

### For Candidates
1. **Register**: Complete your profile with skills, education, and background information
2. **Find Matches**: Get AI-powered internship recommendations
3. **Apply**: Submit applications with cover letters
4. **Track**: Monitor application status and AI feedback

### For Companies
1. **Register Company**: Set up company profile with diversity commitments
2. **Post Internships**: Create detailed internship postings
3. **Review Candidates**: Browse AI-matched candidates
4. **Analytics**: View diversity metrics and application analytics

### For Administrators
- **Platform Analytics**: Monitor overall platform health and diversity metrics
- **Application Management**: Oversee application processes
- **Diversity Reporting**: Generate comprehensive diversity reports

## 🔧 API Documentation

### Key Endpoints

#### Candidates
- `POST /candidates/` - Register new candidate
- `GET /candidates/{id}` - Get candidate profile
- `POST /match/candidate` - Find internship matches

#### Companies & Internships
- `POST /companies/` - Register company
- `POST /internships/` - Post new internship
- `GET /internships/active` - Get active internships

#### Applications
- `POST /applications/` - Submit application (with AI recommendation)
- `GET /applications/candidate/{id}` - Get candidate applications
- `GET /applications/internship/{id}` - Get internship applications

#### Analytics
- `GET /analytics/diversity/{internship_id}` - Get diversity analytics

Full API documentation available at `http://localhost:8000/docs` when backend is running.

## 🎛️ Configuration

### Affirmative Action Settings
```python
# Default quotas (configurable per company)
DEFAULT_CATEGORY_QUOTAS = {
    "SC": 0.15,  # 15% for Scheduled Caste
    "ST": 0.075, # 7.5% for Scheduled Tribe  
    "BC": 0.27,  # 27% for Backward Class
    "OC": 0.505, # 50.5% for Open Category
}

RURAL_REPRESENTATION_TARGET = 0.30  # 30% for rural candidates
```

### Matching Algorithm Weights
```python
# Score weightings
SKILL_WEIGHT = 0.40      # 40% for skill matching
LOCATION_WEIGHT = 0.20   # 20% for location preference
QUALIFICATION_WEIGHT = 0.25  # 25% for qualifications
DIVERSITY_WEIGHT = 0.15  # 15% for affirmative action
```

## 📈 Analytics & Reporting

### Available Metrics
- **Diversity Distribution**: Social category and rural/urban breakdown
- **Skills Analysis**: Most common skills and industry trends
- **Matching Effectiveness**: Success rates and AI recommendation accuracy
- **Application Flow**: Conversion rates from application to selection

### Export Features
- CSV export for all data
- PDF reports for diversity compliance
- Interactive dashboards for real-time monitoring

## 🔒 Security & Privacy

### Data Protection
- All personal data encrypted at rest
- GDPR-compliant data handling
- Secure API authentication
- Audit trails for all operations

### Privacy Features
- Anonymized analytics options
- Consent management
- Data retention policies
- Right to deletion compliance

## 🧪 Development

### Project Structure
```
internship-matcher/
├── backend/
│   ├── main.py              # FastAPI application
│   └── ...
├── frontend/
│   ├── app.py               # Streamlit application
│   └── ...
├── database/
│   ├── models.py            # SQLAlchemy models
│   └── ...
├── utils/
│   ├── embeddings.py        # Embedding utilities
│   ├── ai_integration.py    # Groq AI integration
│   ├── matching_algorithm.py # Matching logic
│   └── ...
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

### Adding New Features
1. **Backend**: Add new endpoints in `backend/main.py`
2. **Frontend**: Add new pages in `frontend/app.py`
3. **Database**: Update models in `database/models.py`
4. **AI**: Extend algorithms in `utils/` directory

### Testing
```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
streamlit run app.py --server.headless true
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Coding Standards
- Follow PEP 8 for Python code
- Use type hints
- Add docstrings for all functions
- Write tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing fast LLM inference
- **Hugging Face** for sentence-transformers models
- **Streamlit** for the amazing web framework
- **FastAPI** for the robust backend framework

## 📞 Support

For support, please:
1. Check the [FAQ](docs/FAQ.md)
2. Search existing [Issues](../../issues)
3. Create a new issue with detailed description

## 🗺️ Roadmap

### Phase 1 ✅ (Current)
- Basic matching algorithm
- Affirmative action support
- Web interface
- AI recommendations

### Phase 2 🚧 (In Progress)
- Advanced analytics
- Email notifications
- Batch processing
- Performance optimization

### Phase 3 📋 (Planned)
- Mobile app
- Integration APIs
- Advanced ML models
- Multi-language support

---<img width="1712" height="773" alt="Screenshot 2025-10-24 161922" src="https://github.com/user-attachments/assets/8477f8b4-3017-4d66-951a-6b02862f9b44" />
<img width="1610" height="720" alt="Screenshot 2025-10-24 161955" src="https://github.com/user-attachments/assets/198c6d03-55f9-4801-9287-5c287d8270ee" />
<img width="1598" height="748" alt="Screenshot 2025-10-24 162019" src="https://github.com/user-attachments/assets/3ac6ada7-1abf-45e4-8c25-bbab465c98b2" />
<img width="1685" height="689" alt="Screenshot 2025-10-24 162052" src="https://github.com/user-attachments/assets/3975af14-f5ee-467f-b15b-4727b414dcba" />




**Built with ❤️ for promoting diversity and fairness in internship opportunities across India.**
