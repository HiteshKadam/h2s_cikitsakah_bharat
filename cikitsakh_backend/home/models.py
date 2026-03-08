from django.db import models


class Gender(models.Model):
    gender_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'gender'
        managed = False

    def __str__(self):
        return self.name


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'address'
        managed = False

    def __str__(self):
        return f"{self.city}, {self.state}"


class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)
    email_id = models.EmailField(null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, db_column='gender_id')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, db_column='address_id')

    class Meta:
        db_table = 'patients'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class HumanDoctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, db_column='gender_id')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, db_column='address_id')
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    years_experience = models.IntegerField(null=True, blank=True)  # years of experience
    status = models.CharField(max_length=50, null=True, blank=True)
    open_time_1 = models.TimeField(null=True, blank=True)
    close_time_1 = models.TimeField(null=True, blank=True)
    open_time_2 = models.TimeField(null=True, blank=True)
    # close_time_2 = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'human_doctors'
        managed = False

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"


class Owner(models.Model):
    owner_id = models.AutoField(primary_key=True)
    owner_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'owner'
        managed = False

    def __str__(self):
        return self.owner_name


class Animal(models.Model):
    animal_id = models.AutoField(primary_key=True)
    animal_name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, null=True, blank=True)
    breed = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, db_column='owner_id')

    class Meta:
        db_table = 'animal'
        managed = False

    def __str__(self):
        return self.animal_name


class VetDoctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100, null=True, blank=True)
    clinic_name = models.CharField(max_length=200, null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    license_number = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    open_time_1 = models.TimeField(null=True, blank=True)
    open_time_2 = models.TimeField(null=True, blank=True)
    close_time_1 = models.TimeField(null=True, blank=True)
    close_time_2 = models.TimeField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'doctor'
        managed = False

    def __str__(self):
        return self.name


class HumanAppointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    doctor = models.ForeignKey(HumanDoctor, on_delete=models.CASCADE, db_column='doctor_id')
    scheduling_date = models.DateField()
    scheduling_time = models.TimeField()
    scheduling_interval = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    check_in_time = models.TimeField(null=True, blank=True)
    appointment_duration = models.IntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    waiting_timr = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'appointment'
        managed = False

    def __str__(self):
        return f"Appointment {self.appointment_id}"


class AnimalAppointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(VetDoctor, on_delete=models.CASCADE, db_column='doctor_id')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, db_column='animal_id')
    appointment_date = models.DateField()
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'appointment'
        managed = False

    def __str__(self):
        return f"Vet Appointment {self.appointment_id}"