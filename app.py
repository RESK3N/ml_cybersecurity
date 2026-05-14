import os
import sys
import subprocess
import shutil

def check_requirements():
    print("🔍 Checking and installing requirements from requirements.txt...")
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print(f"⚠️ Warning: {req_file} not found in the current directory.")
        return
        
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("✅ All dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def setup_env():
    print("⚙️ Checking environment variables...")
    env_file = os.path.join("backend", ".env")
    if not os.path.exists(env_file):
        print("📝 No .env file found. Creating a default one for Demo Mode...")
        with open(env_file, "w") as f:
            f.write("FLASK_ENV=development\n")
            f.write("DEBUG=True\n")
            f.write("DEMO_MODE=True\n")
            f.write("PORT=8000\n")
        print("✅ Created default .env file.")
    else:
        print("✅ .env file exists.")

def run_app():
    print("🚀 Starting the Intrusion Detection System in DEMO MODE...")
    
    # We must run the application from within the backend directory 
    # so that it can find its relative models and CSV files.
    backend_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "backend")
    
    if not os.path.exists(backend_dir):
        print(f"❌ Error: 'backend' directory not found at {backend_dir}.")
        sys.exit(1)
        
    os.chdir(backend_dir)
    
    try:
        # Launch the backend app
        subprocess.check_call([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Shutting down demo...")
    except Exception as e:
        print(f"\n❌ Application crashed: {e}")

if __name__ == "__main__":
    print("========================================")
    print("   CIC-IDS2017 DASHBOARD - DEMO MODE    ")
    print("========================================\n")
    check_requirements()
    print("-" * 40)
    setup_env()
    print("-" * 40)
    run_app()
