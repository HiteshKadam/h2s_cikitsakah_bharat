from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_add_doctor_auth_fields'),
    ]

    operations = [
        # No-op migration - doctor_id is already an identity column
        migrations.RunSQL(
            "SELECT 1;",  # Do nothing
            reverse_sql="SELECT 1;"
        ),
    ]
