#!/usr/bin/env python
"""
Test script to verify that all dependencies can be imported.
"""

def test_imports():
    """Test that all dependencies can be imported."""
    imports = [
        # Core dependencies
        "numpy",
        "pandas",
        "yaml",  # PyYAML
        "dateutil",
        "pytz",
        "jsonschema",
        
        # Excel reporting
        "xlsxwriter",
        "openpyxl",
        
        # Technical analysis
        "ta",
        
        # Visualization
        "matplotlib",
        
        # Reporting
        "tabulate",
        
        # Performance optimization
        "numba",
        
        # Logging and CLI
        "rich",
        "argparse",
    ]
    
    failed_imports = []
    
    for module in imports:
        try:
            __import__(module)
            print(f"✅ Successfully imported {module}")
        except ImportError:
            failed_imports.append(module)
            print(f"❌ Failed to import {module}")
    
    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} modules: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All dependencies imported successfully!")
        return True

if __name__ == "__main__":
    test_imports()
