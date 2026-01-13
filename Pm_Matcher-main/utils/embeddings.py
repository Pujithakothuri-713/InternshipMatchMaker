from sentence_transformers.SentenceTransformer import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager with a pre-trained sentence transformer model
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def generate_skills_embedding(self, skills: List[str]) -> List[float]:
        """
        Generate embedding for a list of skills
        
        Args:
            skills: List of skill strings
            
        Returns:
            List of float values representing the embedding
        """
        if not skills:
            dim = self.model.get_sentence_embedding_dimension()
            if dim is None or not isinstance(dim, int):
                dim = 384  # Default dimension for all-MiniLM-L6-v2
            return [0.0] * dim
        
        # Combine skills into a single text for embedding
        skills_text = ", ".join(skills)
        
        try:
            embedding = self.model.encode(skills_text)
            if isinstance(embedding, list):
                # If encode returns a list (batch mode), take the first element
                embedding = embedding[0]
            return np.array(embedding).tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding for skills: {e}")
            dim = self.model.get_sentence_embedding_dimension()
            if dim is None or not isinstance(dim, int):
                dim = 384  # Default dimension for all-MiniLM-L6-v2
            return [0.0] * dim
    
    def generate_job_requirements_embedding(self, 
                                          title: str, 
                                          description: str, 
                                          required_skills: List[str]) -> List[float]:
        """
        Generate embedding for job requirements including title, description, and skills
        
        Args:
            title: Job title
            description: Job description
            required_skills: List of required skills
            
        Returns:
            List of float values representing the embedding
        """
        # Combine all job information into a comprehensive text
        job_text_parts = [title, description]
        if required_skills:
            job_text_parts.append("Required skills: " + ", ".join(required_skills))
        
        job_text = ". ".join(job_text_parts)
        
        try:
            embedding = self.model.encode(job_text)
            if isinstance(embedding, list):
                # If encode returns a list (batch mode), take the first element
                embedding = embedding[0]
            return np.array(embedding).tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding for job requirements: {e}")
            dim = self.model.get_sentence_embedding_dimension()
            if dim is None or not isinstance(dim, int):
                dim = 384  # Default dimension for all-MiniLM-L6-v2
            return [0.0] * dim
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            # Convert to numpy arrays and reshape for sklearn
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(emb1, emb2)[0][0]
            
            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_best_matches(self, 
                         candidate_embedding: List[float], 
                         job_embeddings: List[Tuple[int, List[float]]], 
                         top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Find the best matching jobs for a candidate based on embeddings
        
        Args:
            candidate_embedding: Candidate's skills embedding
            job_embeddings: List of tuples (job_id, job_embedding)
            top_k: Number of top matches to return
            
        Returns:
            List of tuples (job_id, similarity_score) sorted by similarity
        """
        if not candidate_embedding or not job_embeddings:
            return []
        
        similarities = []
        
        for job_id, job_embedding in job_embeddings:
            similarity = self.calculate_similarity(candidate_embedding, job_embedding)
            similarities.append((job_id, similarity))
        
        # Sort by similarity score in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]

# Global embedding manager instance
embedding_manager = None

def get_embedding_manager() -> EmbeddingManager:
    """Get or create global embedding manager instance"""
    global embedding_manager
    if embedding_manager is None:
        embedding_manager = EmbeddingManager()
    return embedding_manager

def preprocess_skills(skills: List[str]) -> List[str]:
    """
    Preprocess and normalize skills list
    
    Args:
        skills: Raw list of skills
        
    Returns:
        Cleaned and normalized skills list
    """
    if not skills:
        return []
    
    # Clean and normalize skills
    cleaned_skills = []
    for skill in skills:
        if isinstance(skill, str) and skill.strip():
            # Convert to lowercase and strip whitespace
            cleaned_skill = skill.strip().lower()
            if cleaned_skill not in cleaned_skills:
                cleaned_skills.append(cleaned_skill)
    
    return cleaned_skills

def expand_skills_with_synonyms(skills: List[str]) -> List[str]:
    """
    Expand skills list with common synonyms and related terms
    
    Args:
        skills: Original skills list
        
    Returns:
        Expanded skills list with synonyms
    """
    # Common skill synonyms mapping
    skill_synonyms = {
        "python": ["python programming", "python development"],
        "javascript": ["js", "javascript programming", "node.js"],
        "java": ["java programming", "java development"],
        "react": ["reactjs", "react.js", "react development"],
        "sql": ["database", "mysql", "postgresql", "sql queries"],
        "machine learning": ["ml", "artificial intelligence", "ai", "data science"],
        "html": ["html5", "web markup"],
        "css": ["css3", "styling", "web design"],
        "git": ["version control", "github", "gitlab"],
        "docker": ["containerization", "container technology"],
        "aws": ["amazon web services", "cloud computing"],
        "linux": ["unix", "command line", "bash"],
    }
    
    expanded_skills = skills.copy()
    
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in skill_synonyms:
            expanded_skills.extend(skill_synonyms[skill_lower])
    
    return list(set(expanded_skills))  # Remove duplicates
