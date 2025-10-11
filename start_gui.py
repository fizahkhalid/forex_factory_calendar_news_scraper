#!/usr/bin/env python3
"""
Cross-platform launcher for Forex Factory GUI Scraper
Installs requirements and launches the GUI
"""

import sys
import subprocess
import os

def main():
    print("Installing required Python packages...")
    try:
        # Install requirements
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                              capture_output=True, text=True, check=True)
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install requirements.\n{e.stderr}")
        input("Press Enter to exit...")
        sys.exit(1)

    print("\nStarting Forex Factory GUI Scraper...")
    try:
        # Launch the GUI
        subprocess.run([sys.executable, "gui_scraper.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to launch GUI.\n{e.stderr}")
        input("Press Enter to exit...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGUI closed.")
    except FileNotFoundError:
        print("Error: gui_scraper.py not found in current directory.")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()