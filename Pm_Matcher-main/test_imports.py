#!/usr/bin/env python3
"""
Test matching algorithm imports
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test imports step by step"""
    
    try:
        print("Testing embeddings import...")
        from utils.embeddings import get_embedding_manager
        print("✅ get_embedding_manager imported")
        
        print("Testing matching algorithm import...")
        from utils.matching_algorithm import InternshipMatcher
        print("✅ InternshipMatcher imported")
        
        print("Creating instances...")
        matcher = InternshipMatcher()
        print("✅ InternshipMatcher created")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
