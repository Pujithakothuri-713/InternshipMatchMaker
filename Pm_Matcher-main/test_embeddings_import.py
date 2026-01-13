#!/usr/bin/env python3
"""
Test embeddings import separately
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_embeddings_import():
    """Test the embeddings import that matching algorithm uses"""
    
    try:
        print("Testing embeddings import...")
        from utils.embeddings import get_embedding_manager
        print("✅ get_embedding_manager imported successfully")
        
        print("Creating embedding manager...")
        manager = get_embedding_manager()
        print("✅ Embedding manager created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Embeddings error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_embeddings_import()
