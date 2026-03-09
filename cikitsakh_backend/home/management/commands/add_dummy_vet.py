from django.core.management.base import BaseCommand
from home.models import VetDoctor


class Command(BaseCommand):
    help = 'Add dummy vet doctor for testing'

    def handle(self, *args, **kwargs):
        from django.db import connection
        
        # Get the next available ID number
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(CAST(SUBSTRING(doctor_id FROM 2) AS INTEGER)) FROM animal_doctors WHERE doctor_id ~ '^V[0-9]+$'")
            result = cursor.fetchone()
            next_id = (result[0] or 0) + 1
        
        # Create doctor_id with max 10 characters (e.g., V001, V002, etc.)
        doctor_id = f"V{next_id:03d}"
        
        vet_doctor = VetDoctor(
            doctor_id=doctor_id,
            name="Dr Arvind Verma",
            specialty="Veterinary_surgery",
            clinic_name="Pet Care Clinic",
            experience=5,
            license_number="VET12345",
            gender="Male",
            open_time_1="09:00:00",
            close_time_1="13:00:00",
            open_time_2="15:00:00",
            close_time_2="19:00:00",
            address="123 Main Street, Mumbai, Maharashtra"
        )
        
        vet_doctor.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created vet doctor: {vet_doctor.name} (ID: {doctor_id})'
            )
        )
