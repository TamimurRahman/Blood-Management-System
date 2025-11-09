"""
Django management command to create sample data for testing
Usage: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from blood_management.models import BloodBank, BloodInventory


class Command(BaseCommand):
    help = 'Creates sample blood banks and inventory data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...\n')
        
        # Sample Blood Banks
        sample_banks = [
            {
                'name': 'City General Hospital Blood Bank',
                'address': '123 Main Street, Medical Center',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
                'phone_number': '(555) 123-4567',
                'email': 'bloodbank@citygeneral.com'
            },
            {
                'name': 'Regional Medical Center Blood Bank',
                'address': '456 Oak Avenue, Building A',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90001',
                'phone_number': '(555) 234-5678',
                'email': 'bloodbank@regionalmed.com'
            },
            {
                'name': 'Community Health Center Blood Bank',
                'address': '789 Pine Road',
                'city': 'Chicago',
                'state': 'IL',
                'zip_code': '60601',
                'phone_number': '(555) 345-6789',
                'email': 'bloodbank@communityhealth.org'
            },
            {
                'name': 'Memorial Hospital Blood Services',
                'address': '321 Elm Street, Suite 200',
                'city': 'Houston',
                'state': 'TX',
                'zip_code': '77001',
                'phone_number': '(555) 456-7890',
                'email': 'bloodservices@memorialhospital.com'
            },
            {
                'name': 'University Medical Center Blood Bank',
                'address': '654 Maple Drive, Medical Complex',
                'city': 'Phoenix',
                'state': 'AZ',
                'zip_code': '85001',
                'phone_number': '(555) 567-8901',
                'email': 'bloodbank@universitymed.edu'
            },
            {
                'name': 'Metro Blood Center',
                'address': '987 Cedar Lane',
                'city': 'Miami',
                'state': 'FL',
                'zip_code': '33101',
                'phone_number': '(555) 678-9012',
                'email': 'info@metrobloodcenter.com'
            },
            {
                'name': 'Central Blood Bank',
                'address': '147 Birch Boulevard',
                'city': 'Seattle',
                'state': 'WA',
                'zip_code': '98101',
                'phone_number': '(555) 789-0123',
                'email': 'contact@centralbloodbank.org'
            },
            {
                'name': 'Pacific Coast Blood Services',
                'address': '258 Willow Way',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94101',
                'phone_number': '(555) 890-1234',
                'email': 'donate@pacificblood.org'
            }
        ]
        
        # Create blood banks
        created_count = 0
        for bank_data in sample_banks:
            bank, created = BloodBank.objects.get_or_create(
                name=bank_data['name'],
                defaults=bank_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Created: {bank.name}')
                )
                created_count += 1
                
                # Create sample inventory for each blood group
                blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
                for bg in blood_groups:
                    # Random sample inventory (0-50 units)
                    import random
                    units = random.randint(0, 50)
                    BloodInventory.objects.create(
                        blood_bank=bank,
                        blood_group=bg,
                        units_available=units
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'[SKIP] Already exists: {bank.name}')
                )
        
        self.stdout.write(f'\n[SUCCESS] Created {created_count} new blood banks')
        self.stdout.write(f'[INFO] Total blood banks: {BloodBank.objects.count()}')
        self.stdout.write(f'[INFO] Total inventory entries: {BloodInventory.objects.count()}')
        self.stdout.write('\n[COMPLETE] Sample data creation finished!')

