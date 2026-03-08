from rest_framework import serializers
from .models import (
    HumanDoctor, VetDoctor, Patient, Animal, 
    Address, Gender, HumanAppointment, AnimalAppointment, Owner
)


class AddressSerializer(serializers.ModelSerializer):
    address_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Address
        fields = ['address_id', 'address', 'city', 'state']


class GenderSerializer(serializers.ModelSerializer):
    gender_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Gender
        fields = ['gender_id', 'name']


class HumanDoctorSerializer(serializers.ModelSerializer):
    address_details = serializers.SerializerMethodField()
    gender_name = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = HumanDoctor
        fields = [
            'doctor_id', 'first_name', 'last_name', 'specialization',
            'phone_number', 'years_experience', 'status', 'registration_number',
            'open_time_1', 'close_time_1', 'open_time_2',
            'gender_name', 'address_details', 'distance'
        ]
    
    def get_address_details(self, obj):
        if obj.address:
            try:
                return {
                    'address_id': str(obj.address.address_id),
                    'address': obj.address.address,
                    'city': obj.address.city,
                    'state': obj.address.state
                }
            except:
                return None
        return None
    
    def get_gender_name(self, obj):
        if obj.gender:
            try:
                return obj.gender.name
            except:
                return None
        return None


class VetDoctorSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True)
    
    class Meta:
        model = VetDoctor
        fields = [
            'doctor_id', 'name', 'specialty', 'clinic_name', 'experience',
            'license_number', 'gender', 'address',
            'open_time_1', 'close_time_1', 'open_time_2', 'close_time_2',
            'distance'
        ]


class PatientSerializer(serializers.ModelSerializer):
    address_details = serializers.SerializerMethodField()
    gender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'patient_id', 'first_name', 'last_name', 'date_of_birth',
            'contact_number', 'email_id', 'registration_date',
            'gender_name', 'address_details'
        ]
    
    def get_address_details(self, obj):
        if obj.address:
            try:
                return {
                    'address_id': str(obj.address.address_id),
                    'address': obj.address.address,
                    'city': obj.address.city,
                    'state': obj.address.state
                }
            except:
                return None
        return None
    
    def get_gender_name(self, obj):
        if obj.gender:
            try:
                return obj.gender.name
            except:
                return None
        return None


class AnimalSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.owner_name', read_only=True)
    
    class Meta:
        model = Animal
        fields = [
            'animal_id', 'animal_name', 'species', 'breed',
            'age', 'gender', 'weight', 'owner_name'
        ]


class HumanAppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = HumanAppointment
        fields = [
            'appointment_id', 'scheduling_date', 'scheduling_time',
            'status', 'check_in_time', 'appointment_duration',
            'start_time', 'end_time', 'patient_name', 'doctor_name'
        ]
    
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.first_name} {obj.doctor.last_name}"


class AnimalAppointmentSerializer(serializers.ModelSerializer):
    animal_name = serializers.CharField(source='animal.animal_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    
    class Meta:
        model = AnimalAppointment
        fields = [
            'appointment_id', 'appointment_date', 'status',
            'animal_name', 'doctor_name'
        ]



class CreateHumanAppointmentSerializer(serializers.Serializer):
    """Serializer for creating human appointments"""
    doctor_id = serializers.IntegerField(required=True)
    patient_first_name = serializers.CharField(max_length=100, required=True)
    patient_last_name = serializers.CharField(max_length=100, required=True)
    contact_number = serializers.CharField(max_length=20, required=True)
    email_id = serializers.EmailField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender_id = serializers.IntegerField(required=False, allow_null=True)
    scheduling_date = serializers.DateField(required=True)
    scheduling_time = serializers.TimeField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    age = serializers.IntegerField(required=False, allow_null=True)


class CreateAnimalAppointmentSerializer(serializers.Serializer):
    """Serializer for creating animal appointments"""
    doctor_id = serializers.CharField(max_length=50, required=True)
    owner_name = serializers.CharField(max_length=100, required=True)
    owner_phone = serializers.CharField(max_length=20, required=True)
    owner_email = serializers.EmailField(required=False, allow_blank=True)
    animal_name = serializers.CharField(max_length=100, required=True)
    species = serializers.CharField(max_length=100, required=True)
    breed = serializers.CharField(max_length=100, required=False, allow_blank=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=20, required=False, allow_blank=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    appointment_date = serializers.DateField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Detailed appointment information for confirmation"""
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = HumanDoctorSerializer(source='doctor', read_only=True)
    
    class Meta:
        model = HumanAppointment
        fields = [
            'appointment_id', 'scheduling_date', 'scheduling_time',
            'status', 'patient_details', 'doctor_details'
        ]
