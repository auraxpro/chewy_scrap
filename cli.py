#!/usr/bin/env python3
"""
Convenient CLI wrapper for the Dog Food Scoring API.

This script can be run from the api/ directory and automatically handles
the Python path setup.

Usage:
    python cli.py [command] [options]

Examples:
    python cli.py --help
    python cli.py --stats
    python cli.py --scrape --details
    python cli.py --process
    python cli.py --score
    python cli.py --all
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main CLI
from scripts.main import main

if __name__ == "__main__":
    main()
