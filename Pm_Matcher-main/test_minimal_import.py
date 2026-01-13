#!/usr/bin/env python3
"""
Test minimal import for matching algorithm
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_minimal_import():
    """Test just importing the module without specific classes"""
    
    try:
        print("Importing matching_algorithm module...")
        import utils.matching_algorithm as ma
        print("✅ Module imported")
        
        print("Checking available attributes...")
        attributes = [attr for attr in dir(ma) if not attr.startswith('_')]
        print(f"Available: {attributes}")
        
        if hasattr(ma, 'InternshipMatcher'):
            print("✅ InternshipMatcher found in module")
            return True
        else:
            print("❌ InternshipMatcher not found in module")
            return False
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_minimal_import()
