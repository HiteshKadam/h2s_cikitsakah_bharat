from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE human_doctors 
            ADD COLUMN IF NOT EXISTS email VARCHAR(255),
            ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
            ADD COLUMN IF NOT EXISTS age INTEGER,
            ADD COLUMN IF NOT EXISTS passout_date DATE;
            """,
            reverse_sql="""
            ALTER TABLE human_doctors 
            DROP COLUMN IF EXISTS email,
            DROP COLUMN IF EXISTS password_hash,
            DROP COLUMN IF EXISTS age,
            DROP COLUMN IF EXISTS passout_date;
            """
        ),
        migrations.RunSQL(
            """
            ALTER TABLE animal_doctors 
            ADD COLUMN IF NOT EXISTS email VARCHAR(255),
            ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
            ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
            ADD COLUMN IF NOT EXISTS age INTEGER,
            ADD COLUMN IF NOT EXISTS passout_date DATE,
            ADD COLUMN IF NOT EXISTS registration_number VARCHAR(100),
            ADD COLUMN IF NOT EXISTS city VARCHAR(100),
            ADD COLUMN IF NOT EXISTS state VARCHAR(100);
            """,
            reverse_sql="""
            ALTER TABLE animal_doctors 
            DROP COLUMN IF EXISTS email,
            DROP COLUMN IF EXISTS password_hash,
            DROP COLUMN IF EXISTS phone,
            DROP COLUMN IF EXISTS age,
            DROP COLUMN IF EXISTS passout_date,
            DROP COLUMN IF EXISTS registration_number,
            DROP COLUMN IF EXISTS city,
            DROP COLUMN IF EXISTS state;
            """
        ),
    ]
