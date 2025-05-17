#!/usr/bin/env python3
"""
Setup script for Blockchain Tweet Bot.
Creates a virtual environment and installs dependencies.
"""
import os
import subprocess
import platform
import shutil


def main():
    print("🚀 Setting up Blockchain Tweet Bot")

    # Check if Python is installed
    try:
        python_version = subprocess.check_output(
            ["python", "--version"], stderr=subprocess.STDOUT, universal_newlines=True
        )
        print(f"Found {python_version.strip()}")
    except:
        print("❌ Python not found. Please install Python 3.10+ and try again.")
        return

    # Create virtual environment
    if not os.path.exists(".venv"):
        print("Creating virtual environment...")
        subprocess.call(["python", "-m", "venv", ".venv"])

    # Activate and install dependencies
    print("Installing dependencies...")

    if platform.system() == "Windows":
        pip_path = os.path.join(".venv", "Scripts", "pip")
    else:
        pip_path = os.path.join(".venv", "bin", "pip")

    subprocess.call([pip_path, "install", "-U", "-r", "requirements.txt"])

    # Create .env from template if it doesn't exist
    if not os.path.exists(".env") and os.path.exists("env.template"):
        print("Creating .env file from template...")
        shutil.copy("env.template", ".env")
        print(
            "⚠️ Remember to update the .env file with your Twitter API credentials and Groq API key!"
        )

    print("\n✅ Setup complete!")
    print("To get started:")

    if platform.system() == "Windows":
        print("   1. Run: .venv\\Scripts\\activate")
    else:
        print("   1. Run: source .venv/bin/activate")

    print("   2. Edit .env with your API credentials")
    print("   3. Run: python tweet_bot.py")


if __name__ == "__main__":
    main()
