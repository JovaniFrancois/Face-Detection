#!/usr/bin/env python3
"""
Launcher script for Face Recognition App.
Run this from the project root directory.
"""
import sys
import os

# Add src directory to Python path
# Join the directory containing this file with 'src'
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import main function from src.main module
from main import main

if __name__ == "__main__":
    # Display startup message
    print("Starting Face Recognition App...")
    print("Press Ctrl+C to exit")

    # Launch the main application
    main()