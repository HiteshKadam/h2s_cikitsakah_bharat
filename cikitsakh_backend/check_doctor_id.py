import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cikitsakh_backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check doctor_id column details
    cursor.execute("""
        SELECT column_name, column_default, is_nullable, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'human_doctors' AND column_name = 'doctor_id'
    """)
    print("Human Doctors doctor_id:", cursor.fetchone())
    
    # Check if there's a sequence
    cursor.execute("""
        SELECT pg_get_serial_sequence('human_doctors', 'doctor_id')
    """)
    print("Sequence:", cursor.fetchone())
