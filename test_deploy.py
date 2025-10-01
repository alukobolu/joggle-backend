#!/usr/bin/env python
"""
Simple test script to verify Django can start
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joggle.settings')

try:
    django.setup()
    print("✅ Django setup successful!")
    
    # Test basic imports
    from django.conf import settings
    print(f"✅ Settings loaded: DEBUG={settings.DEBUG}")
    print(f"✅ Database: {settings.DATABASES['default']['ENGINE']}")
    print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")
    
    # Test URL patterns
    from django.urls import reverse
    from django.test import Client
    client = Client()
    
    print("✅ Django test client created")
    print("✅ All basic Django components working!")
    
except Exception as e:
    print(f"❌ Django setup failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
