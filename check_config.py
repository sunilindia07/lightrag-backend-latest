#!/usr/bin/env python3
"""
Configuration Checker for LightRAG Backend
Run this script to validate your environment configuration before starting the server.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from lightrag.utils import validate_configuration, print_configuration_report


def main():
    """Main function to check configuration"""
    print("\n" + "=" * 70)
    print("🔧 LightRAG Backend Configuration Checker")
    print("=" * 70)
    print("\nThis script will validate your environment configuration.")
    print("Make sure you have created a .env file from .env.example\n")
    
    try:
        results = validate_configuration()
        is_valid = print_configuration_report(results)
        
        if is_valid:
            print("✅ Your configuration is valid! You can start the server.")
            print("\nTo start the server, run:")
            print("  python -m lightrag.api.lightrag_server")
            return 0
        else:
            print("❌ Configuration validation failed.")
            print("\nPlease fix the errors above before starting the server.")
            print("See SETUP_GUIDE.md for detailed instructions.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
