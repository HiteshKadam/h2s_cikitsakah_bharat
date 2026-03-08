from django.contrib import admin
from .models import (
    HumanDoctor, VetDoctor, Patient, Animal, Owner,
    Address, Gender, HumanAppointment, AnimalAppointment
)


@admin.register(HumanDoctor)
class HumanDoctorAdmin(admin.ModelAdmin):
    list_display = ['doctor_id', 'first_name', 'last_name', 'specialization', 'status']
    list_filter = ['specialization', 'status']
    search_fields = ['first_name', 'last_name', 'specialization']


@admin.register(VetDoctor)
class VetDoctorAdmin(admin.ModelAdmin):
    list_display = ['doctor_id', 'name', 'specialty', 'clinic_name']
    list_filter = ['specialty']
    search_fields = ['name', 'specialty', 'clinic_name']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'first_name', 'last_name', 'contact_number']
    search_fields = ['first_name', 'last_name', 'email_id']


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['animal_id', 'animal_name', 'species', 'breed', 'owner']
    list_filter = ['species']
    search_fields = ['animal_name', 'species', 'breed']


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['owner_id', 'owner_name', 'phone', 'email']
    search_fields = ['owner_name', 'email']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['address_id', 'city', 'state']
    list_filter = ['state', 'city']
    search_fields = ['city', 'state']


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ['gender_id', 'name']


@admin.register(HumanAppointment)
class HumanAppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'scheduling_date', 'status']
    list_filter = ['status', 'scheduling_date']
    search_fields = ['patient__first_name', 'doctor__first_name']


@admin.register(AnimalAppointment)
class AnimalAppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'animal', 'doctor', 'appointment_date', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['animal__animal_name', 'doctor__name']
