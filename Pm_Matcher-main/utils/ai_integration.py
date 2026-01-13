import os
import httpx
import re
from groq import Groq
from typing import Dict, List, Optional, Any
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GroqAIManager:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq AI manager
        
        Args:
            api_key: Groq API key (if not provided, will look for GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not provided. Set GROQ_API_KEY environment variable.")
        
        try:
            # Create HTTP client with SSL verification disabled for corporate environments
            http_client = httpx.Client(verify=False)
            self.client = Groq(api_key=self.api_key, http_client=http_client)
            logger.info("Groq AI client initialized successfully with SSL bypass")
        except Exception as e:
            logger.error(f"Failed to initialize Groq AI client: {e}")
            raise
    
    def generate_internship_recommendation(self, 
                                         candidate_data: Dict[str, Any], 
                                         internship_data: Dict[str, Any], 
                                         match_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate AI-powered internship recommendation using Groq's Llama model
        
        Args:
            candidate_data: Dictionary containing candidate information
            internship_data: Dictionary containing internship information
            match_scores: Dictionary containing various matching scores
            
        Returns:
            Dictionary with recommendation, reasoning, and confidence score
        """
        prompt = self._build_recommendation_prompt(candidate_data, internship_data, match_scores)
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Using available Llama 3.1 8B model
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert career counselor and internship matching specialist for India. 
                        You understand the importance of affirmative action, diversity, and fair representation in internships.
                        Provide detailed, thoughtful recommendations that consider both merit and social equity.
                        Always explain your reasoning clearly and provide actionable advice."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,
                top_p=0.9
            )
            
            recommendation_text = response.choices[0].message.content
            
            # Parse the response to extract recommendation, reasoning, and confidence
            result = self._parse_recommendation_response(recommendation_text)
            
            logger.info(f"Generated recommendation for candidate {candidate_data.get('name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}")
            return {
                "recommendation": "Unable to generate AI recommendation at this time.",
                "reasoning": "Technical error occurred during AI processing.",
                "confidence": 0.0,
                "status": "error"
            }
    
    def _build_recommendation_prompt(self, 
                                   candidate_data: Dict[str, Any], 
                                   internship_data: Dict[str, Any], 
                                   match_scores: Dict[str, float]) -> str:
        """Build the prompt for internship recommendation"""
        
        prompt = f"""
        Provide a clear and encouraging explanation of why this internship is (or is not) a good fit for the candidate. 
        Focus on strengths and potential alignment, and give constructive advice if there are gaps.

        CANDIDATE PROFILE:
        - Name: {candidate_data.get('name', 'Unknown')}
        - Education: {candidate_data.get('education_level', 'Unknown')} in {candidate_data.get('field_of_study', 'Unknown')}
        - CGPA: {candidate_data.get('cgpa', 'Not provided')}
        - Skills: {', '.join(candidate_data.get('skills', []))}
        - Location: {candidate_data.get('current_location', 'Unknown')}
        - Willing to Relocate: {candidate_data.get('willing_to_relocate', False)}

        INTERNSHIP DETAILS:
        - Title: {internship_data.get('title', 'Unknown')}
        - Company: {internship_data.get('company_name', 'Unknown')}
        - Industry: {internship_data.get('industry', 'Unknown')}
        - Location: {internship_data.get('location', 'Unknown')}
        - Duration: {internship_data.get('duration_months', 'Unknown')} months
        - Required Skills: {', '.join(internship_data.get('required_skills', []))}
        - Min Education: {internship_data.get('min_education_level', 'Unknown')}
        - Min CGPA: {internship_data.get('min_cgpa', 'Not specified')}
        - Stipend: ₹{internship_data.get('stipend_amount', 0)}/month
        - Remote: {internship_data.get('is_remote', False)}
        - Total Positions: {internship_data.get('total_positions', 'Unknown')}

        MATCHING SCORES:
        - Skill Match: {match_scores.get('skill_similarity', match_scores.get('skill_match_score', 0)):.2f}/1.0
        - Location Match: {match_scores.get('location_match', match_scores.get('location_match_score', 0)):.2f}/1.0
        - Qualification Match: {match_scores.get('qualification_match', match_scores.get('qualification_match_score', 0)):.2f}/1.0
        - Overall Score: {match_scores.get('overall_score', 0):.2f}/1.0

        OUTPUT FORMAT:

        FIT SUMMARY:
        [Write a short, positive summary (3–4 sentences) explaining why this internship is a good fit for the candidate, 
        focusing on alignment between their skills, education, and the role requirements.]

        STRENGTHS:
        [List 2–3 specific points about why the candidate is a strong match, e.g. key skills, relevant education, or location alignment.]

        GROWTH OPPORTUNITIES:
        [Suggest 1–2 areas where the candidate could strengthen their profile for this or future similar roles.]

        OVERALL RECOMMENDATION:
        [HIGH FIT / GOOD FIT / PARTIAL FIT / LOW FIT] – avoid hard rejection unless the mismatch is very strong.

        CONFIDENCE:
        [0.0–1.0, based on match_scores]
        """
        
        return prompt
    
    def _parse_recommendation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response to extract structured information"""
        
        try:
            lines = response_text.strip().split('\n')
            result = {
                "recommendation": "PARTIAL FIT",
                "fit_summary": "",
                "strengths": "",
                "growth_opportunities": "",
                "confidence": 0.5,
                "full_response": response_text
            }
            
            current_section = None
            content_lines = []
            
            for line in lines:
                line = line.strip()
                # Handle both "SECTION:" and "**SECTION:**" formats
                if line.startswith("**FIT SUMMARY:**") or line.startswith("FIT SUMMARY:"):
                    current_section = "fit_summary"
                    content_lines = []
                elif line.startswith("**STRENGTHS:**") or line.startswith("STRENGTHS:"):
                    if current_section == "fit_summary":
                        result["fit_summary"] = '\n'.join(content_lines).strip()
                    current_section = "strengths"
                    content_lines = []
                elif line.startswith("**GROWTH OPPORTUNITIES:**") or line.startswith("GROWTH OPPORTUNITIES:"):
                    if current_section == "strengths":
                        result["strengths"] = '\n'.join(content_lines).strip()
                    current_section = "growth_opportunities"
                    content_lines = []
                elif line.startswith("**OVERALL RECOMMENDATION:**") or line.startswith("OVERALL RECOMMENDATION:"):
                    if current_section == "growth_opportunities":
                        result["growth_opportunities"] = '\n'.join(content_lines).strip()
                    recommendation_line = line.replace("**OVERALL RECOMMENDATION:**", "").replace("OVERALL RECOMMENDATION:", "").strip()
                    result["recommendation"] = recommendation_line.split("–")[0].strip()
                    current_section = None
                elif line.startswith("**CONFIDENCE:**") or line.startswith("CONFIDENCE:"):
                    try:
                        confidence_str = line.replace("**CONFIDENCE:**", "").replace("CONFIDENCE:", "").strip()
                        # Extract just the number part
                        confidence_match = re.search(r'([0-9]+\.?[0-9]*)', confidence_str)
                        if confidence_match:
                            result["confidence"] = float(confidence_match.group(1))
                    except:
                        result["confidence"] = 0.5
                    current_section = None
                elif current_section and line and not line.startswith("**"):
                    content_lines.append(line)
            
            # Handle the last section
            if current_section == "growth_opportunities":
                result["growth_opportunities"] = '\n'.join(content_lines).strip()
            elif current_section == "strengths" and not result["strengths"]:
                result["strengths"] = '\n'.join(content_lines).strip()
            elif current_section == "fit_summary" and not result["fit_summary"]:
                result["fit_summary"] = '\n'.join(content_lines).strip()
            
            # Create a readable reasoning field for backward compatibility
            result["reasoning"] = f"**Summary:** {result['fit_summary']}\n\n**Strengths:** {result['strengths']}\n\n**Growth Areas:** {result['growth_opportunities']}"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse recommendation response: {e}")
            return {
                "recommendation": "PARTIAL FIT",
                "reasoning": "Unable to parse AI response properly.",
                "fit_summary": "This internship could be a good learning opportunity.",
                "strengths": "Candidate shows potential for growth.",
                "growth_opportunities": "Consider developing relevant technical skills.",
                "confidence": 0.3,
                "full_response": response_text
            }
    
    def generate_batch_recommendations(self, 
                                     candidate_internship_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations for multiple candidate-internship pairs
        
        Args:
            candidate_internship_pairs: List of dictionaries containing candidate_data, 
                                      internship_data, and match_scores
            
        Returns:
            List of recommendation results
        """
        results = []
        
        for pair in candidate_internship_pairs:
            try:
                recommendation = self.generate_internship_recommendation(
                    pair['candidate_data'],
                    pair['internship_data'],
                    pair['match_scores']
                )
                results.append({
                    "candidate_id": pair.get('candidate_id'),
                    "internship_id": pair.get('internship_id'),
                    "recommendation": recommendation
                })
            except Exception as e:
                logger.error(f"Failed to generate recommendation for pair: {e}")
                results.append({
                    "candidate_id": pair.get('candidate_id'),
                    "internship_id": pair.get('internship_id'),
                    "recommendation": {
                        "recommendation": "ERROR",
                        "reasoning": "Failed to generate recommendation.",
                        "confidence": 0.0
                    }
                })
        
        return results

# Global AI manager instance
ai_manager = None

def get_ai_manager() -> GroqAIManager:
    """Get or create global AI manager instance"""
    global ai_manager
    if ai_manager is None:
        ai_manager = GroqAIManager()
    return ai_manager
