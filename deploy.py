#!/usr/bin/env python
"""
Deployment helper script for Railway
This script helps prepare your Django project for Railway deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_file_exists(filepath):
    """Check if a file exists"""
    return Path(filepath).exists()

def main():
    print("🚀 Railway Deployment Preparation Script")
    print("=" * 50)
    
    # Check required files
    required_files = [
        'Procfile',
        'requirements.txt',
        'runtime.txt',
        'railway.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all Railway configuration files are present.")
        return False
    
    print("✅ All required Railway configuration files are present")
    
    # Check if .env file exists for local development
    if not check_file_exists('.env'):
        print("⚠️  No .env file found. Creating .env.template for reference...")
        env_template = """# Copy this file to .env and fill in your values
# This file is for local development only

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for local development - SQLite will be used by default)
# DATABASE_URL=postgresql://username:password@host:port/database

# Email Configuration (Optional)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# CORS Settings (for local development)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080

# CSRF Settings (for local development)
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080
"""
        with open('.env.template', 'w') as f:
            f.write(env_template)
        print("✅ Created .env.template")
    
    # Check if staticfiles directory exists
    if not check_file_exists('staticfiles'):
        print("🔄 Creating staticfiles directory...")
        os.makedirs('staticfiles', exist_ok=True)
        print("✅ Created staticfiles directory")
    
    # Check if media directory exists
    if not check_file_exists('media'):
        print("🔄 Creating media directory...")
        os.makedirs('media', exist_ok=True)
        print("✅ Created media directory")
    
    # Collect static files
    result = run_command("python manage.py collectstatic --noinput", "Collecting static files")
    if result is None:
        print("❌ Failed to collect static files. Please check your Django installation.")
        return False
    
    # Check database migrations
    result = run_command("python manage.py showmigrations", "Checking database migrations")
    if result is None:
        print("❌ Failed to check migrations. Please check your Django installation.")
        return False
    
    print("\n🎉 Deployment preparation completed successfully!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your GitHub repository to Railway")
    print("3. Add a PostgreSQL database in Railway")
    print("4. Set environment variables in Railway dashboard")
    print("5. Deploy!")
    print("\n📖 See RAILWAY_DEPLOYMENT.md for detailed instructions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
