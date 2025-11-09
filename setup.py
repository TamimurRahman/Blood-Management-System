"""
Setup script for Blood Management System
Run this script to initialize the database and create a superuser
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_management_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from blood_management.models import BloodBank, BloodGroup

User = get_user_model()

def create_blood_groups():
    """Create blood group entries"""
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    for bg in blood_groups:
        BloodGroup.objects.get_or_create(name=bg)
    print("✓ Blood groups created")

def create_sample_data():
    """Create sample blood banks"""
    sample_banks = [
        {
            'name': 'City General Hospital Blood Bank',
            'address': '123 Main Street',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001',
            'phone_number': '555-0101',
            'email': 'bloodbank1@hospital.com'
        },
        {
            'name': 'Regional Medical Center',
            'address': '456 Oak Avenue',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip_code': '90001',
            'phone_number': '555-0202',
            'email': 'bloodbank2@hospital.com'
        },
        {
            'name': 'Community Health Center',
            'address': '789 Pine Road',
            'city': 'Chicago',
            'state': 'IL',
            'zip_code': '60601',
            'phone_number': '555-0303',
            'email': 'bloodbank3@hospital.com'
        },
    ]
    
    for bank_data in sample_banks:
        BloodBank.objects.get_or_create(
            name=bank_data['name'],
            defaults=bank_data
        )
    print("✓ Sample blood banks created")

if __name__ == '__main__':
    print("Setting up Blood Management System...")
    create_blood_groups()
    create_sample_data()
    print("\n✓ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python manage.py migrate")
    print("2. Run: python manage.py createsuperuser (optional)")
    print("3. Run: python manage.py runserver")
    print("4. Visit: http://127.0.0.1:8000/")

