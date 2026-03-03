from django.db import models

class Doctor(models.Model):
    PATIENT_TYPE = (
        ('human', 'Human'),
        ('pet', 'Pet'),
    )

    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    patient_type = models.CharField(max_length=10, choices=PATIENT_TYPE)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    rating = models.FloatField()

    def __str__(self):
        return self.name