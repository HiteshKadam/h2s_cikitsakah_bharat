import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { CareSelectionService } from '../../services/care-selection';

@Component({
  selector: 'app-appointment',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './appointment.html',
  styleUrl: './appointment.scss',
})
export class Appointment implements OnInit {

  doctorId: number | null = null;
  doctor: any = null;
  loading: boolean = true;
  submitting: boolean = false;
  careType: 'human' | 'pet' | null = null;
  currentStep: number = 1;
  totalSteps: number = 3;

  // Form validation errors
  errors: { [key: string]: string } = {};

  // Human patient fields
  patientFirstName: string = '';
  patientLastName: string = '';
  contactNumber: string = '';
  email: string = '';
  dateOfBirth: string = '';
  age: number | null = null;

  // Pet fields
  ownerName: string = '';
  ownerPhone: string = '';
  ownerEmail: string = '';
  animalName: string = '';
  species: string = '';
  breed: string = '';
  animalAge: number | null = null;
  animalGender: string = '';
  weight: number | null = null;

  // Common fields
  appointmentDate: string = '';
  appointmentTime: string = '';
  reason: string = '';

  // Available slots
  availableSlots: any[] = [];
  loadingSlots: boolean = false;

  // Species options
  speciesOptions: string[] = [
    'Dog', 'Cat', 'Bird', 'Rabbit', 'Hamster', 'Guinea Pig',
    'Fish', 'Reptile', 'Horse', 'Other'
  ];

  // Gender options
  genderOptions: string[] = ['Male', 'Female'];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private careService: CareSelectionService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    console.log('Appointment component ngOnInit called');
    this.careType = this.careService.getCareType() as 'human' | 'pet';
    console.log('Care type from service:', this.careType);

    // If care type is not set, try to determine it from localStorage
    if (!this.careType) {
      const storedCareType = localStorage.getItem('careType');
      if (storedCareType === 'human' || storedCareType === 'pet') {
        this.careType = storedCareType;
        this.careService.setCareType(this.careType);
        console.log('Care type restored from localStorage:', this.careType);
      } else {
        // If still no care type, redirect to home
        console.error('No care type found, redirecting to home');
        this.router.navigate(['/']);
        return;
      }
    }

    this.route.params.subscribe(params => {
      const doctorId = +params['id'];
      console.log('Doctor ID from route params:', doctorId);
      
      if (doctorId && doctorId !== this.doctorId) {
        console.log('New doctor ID detected, loading doctor details');
        this.doctorId = doctorId;
        this.loadDoctorDetails();
      } else if (doctorId && !this.doctor) {
        console.log('Same doctor ID, but no doctor data loaded yet');
        this.doctorId = doctorId;
        this.loadDoctorDetails();
      }
    });

    // Set minimum date to today
    this.setMinDate();
  }

  loadDoctorDetails() {
    console.log('loadDoctorDetails called with:', { doctorId: this.doctorId, careType: this.careType });
    if (!this.doctorId || !this.careType) {
      console.error('Missing doctorId or careType:', { doctorId: this.doctorId, careType: this.careType });
      this.loading = false;
      this.errors['general'] = 'Missing required information. Please go back and select a care type.';
      return;
    }

    this.loading = true;
    console.log('Making API call to getDoctorDetails...');

    this.apiService.getDoctorDetails(this.doctorId, this.careType).subscribe({
      next: (response) => {
        console.log('API call successful, response:', response);
        console.log('Setting doctor data:', response.doctor);
        this.doctor = response.doctor;
        this.loading = false;
        console.log('Loading set to false, doctor data set');
        console.log('Current state - loading:', this.loading, 'doctor:', !!this.doctor);
        console.log('Doctor object keys:', Object.keys(this.doctor || {}));
        console.log('Doctor first_name:', this.doctor?.first_name);
        console.log('Doctor specialization:', this.doctor?.specialization);

        // Force change detection
        this.cdr.detectChanges();

        // Load available slots for today
        if (this.appointmentDate) {
          this.loadAvailableSlots();
        }
      },
      error: (error) => {
        console.error('API call failed:', error);
        this.loading = false;
        this.errors['general'] = 'Failed to load doctor details. Please try again.';
      }
    });
  }

  onDateChange() {
    if (this.appointmentDate && this.doctorId) {
      this.loadAvailableSlots();
    }
    // Clear time selection when date changes
    this.appointmentTime = '';
    this.availableSlots = [];
  }

  loadAvailableSlots() {
    if (!this.doctorId || !this.appointmentDate || !this.careType) return;

    this.loadingSlots = true;
    this.apiService.getAvailableSlots(this.doctorId, this.appointmentDate, this.careType).subscribe({
      next: (response) => {
        this.availableSlots = response.slots || [];
        this.loadingSlots = false;
      },
      error: (error) => {
        console.error('Error loading slots:', error);
        this.loadingSlots = false;
        // Generate default slots if API fails
        this.generateDefaultSlots();
      }
    });
  }

  generateDefaultSlots() {
    const slots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
    ];

    this.availableSlots = slots.map(time => ({
      time: time,
      display: this.formatTime(time),
      available: true
    }));
  }

  formatTime(time: string): string {
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
    return `${displayHour}:${minutes} ${ampm}`;
  }

  // Step navigation
  nextStep() {
    if (this.validateCurrentStep()) {
      this.currentStep++;
      this.clearStepErrors();
    }
  }

  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.clearStepErrors();
    }
  }

  validateCurrentStep(): boolean {
    this.clearStepErrors();

    switch (this.currentStep) {
      case 1:
        return this.validatePatientInfo();
      case 2:
        return this.validateAppointmentDetails();
      case 3:
        return this.validateConfirmation();
      default:
        return false;
    }
  }

  validatePatientInfo(): boolean {
    let isValid = true;

    if (this.careType === 'human') {
      if (!this.patientFirstName.trim()) {
        this.errors['patientFirstName'] = 'First name is required';
        isValid = false;
      }
      if (!this.patientLastName.trim()) {
        this.errors['patientLastName'] = 'Last name is required';
        isValid = false;
      }
      if (!this.contactNumber.trim()) {
        this.errors['contactNumber'] = 'Contact number is required';
        isValid = false;
      } else if (!this.isValidPhoneNumber(this.contactNumber)) {
        this.errors['contactNumber'] = 'Please enter a valid phone number';
        isValid = false;
      }
      if (this.email && !this.isValidEmail(this.email)) {
        this.errors['email'] = 'Please enter a valid email address';
        isValid = false;
      }
    } else {
      if (!this.ownerName.trim()) {
        this.errors['ownerName'] = 'Owner name is required';
        isValid = false;
      }
      if (!this.ownerPhone.trim()) {
        this.errors['ownerPhone'] = 'Owner phone is required';
        isValid = false;
      } else if (!this.isValidPhoneNumber(this.ownerPhone)) {
        this.errors['ownerPhone'] = 'Please enter a valid phone number';
        isValid = false;
      }
      if (this.ownerEmail && !this.isValidEmail(this.ownerEmail)) {
        this.errors['ownerEmail'] = 'Please enter a valid email address';
        isValid = false;
      }
      if (!this.animalName.trim()) {
        this.errors['animalName'] = 'Pet name is required';
        isValid = false;
      }
      if (!this.species) {
        this.errors['species'] = 'Species is required';
        isValid = false;
      }
    }

    return isValid;
  }

  validateAppointmentDetails(): boolean {
    let isValid = true;

    if (!this.appointmentDate) {
      this.errors['appointmentDate'] = 'Please select an appointment date';
      isValid = false;
    } else if (this.isPastDate(this.appointmentDate)) {
      this.errors['appointmentDate'] = 'Please select a future date';
      isValid = false;
    }

    if (!this.appointmentTime) {
      this.errors['appointmentTime'] = 'Please select an appointment time';
      isValid = false;
    }

    if (!this.reason.trim()) {
      this.errors['reason'] = 'Please provide a reason for the appointment';
      isValid = false;
    }

    return isValid;
  }

  validateConfirmation(): boolean {
    // All validations should be done in previous steps
    return true;
  }

  clearStepErrors() {
    // Clear errors for current step fields
    const stepFields = this.getStepFields(this.currentStep);
    stepFields.forEach(field => {
      delete this.errors[field];
    });
  }

  getStepFields(step: number): string[] {
    switch (step) {
      case 1:
        return this.careType === 'human'
          ? ['patientFirstName', 'patientLastName', 'contactNumber', 'email']
          : ['ownerName', 'ownerPhone', 'ownerEmail', 'animalName', 'species'];
      case 2:
        return ['appointmentDate', 'appointmentTime', 'reason'];
      default:
        return [];
    }
  }

  // Validation helpers
  isValidPhoneNumber(phone: string): boolean {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
  }

  isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  isPastDate(dateString: string): boolean {
    const selectedDate = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return selectedDate < today;
  }

  setMinDate() {
    const today = new Date();
    const minDate = today.toISOString().split('T')[0];
    // Set min attribute on date input
    const dateInput = document.getElementById('appointmentDate') as HTMLInputElement;
    if (dateInput) {
      dateInput.min = minDate;
    }
  }

  getMinDate(): string {
    const today = new Date();
    return today.toISOString().split('T')[0];
  }

  // Form submission
  confirmBooking() {
    if (!this.validateForm()) {
      this.currentStep = 1; // Go back to first invalid step
      return;
    }

    this.submitting = true;

    if (this.careType === 'human') {
      this.bookHumanAppointment();
    } else {
      this.bookAnimalAppointment();
    }
  }

  validateForm(): boolean {
    // Run all validations
    const step1Valid = this.validatePatientInfo();
    const step2Valid = this.validateAppointmentDetails();
    const step3Valid = this.validateConfirmation();

    return step1Valid && step2Valid && step3Valid;
  }

  bookHumanAppointment() {
    if (!this.doctorId) return;

    const appointmentData = {
      doctor_id: this.doctorId,
      patient_first_name: this.patientFirstName,
      patient_last_name: this.patientLastName,
      contact_number: this.contactNumber,
      email_id: this.email,
      date_of_birth: this.dateOfBirth || undefined,
      scheduling_date: this.appointmentDate,
      scheduling_time: this.appointmentTime,
      reason: this.reason,
      age: this.age || undefined
    };

    this.apiService.createHumanAppointment(appointmentData).subscribe({
      next: (response) => {
        console.log('Appointment created:', response);

        const message = `✅ Appointment Booked Successfully!\n\n` +
          `Appointment ID: ${response.appointment_id}\n` +
          `Doctor: ${response.booking_details?.doctor_name}\n` +
          `Patient: ${response.booking_details?.patient_name}\n` +
          `Date: ${response.booking_details?.date}\n` +
          `Time: ${response.booking_details?.time}\n\n` +
          `Please arrive 10 minutes before your appointment time.`;

        alert(message);
        this.submitting = false;
        this.router.navigate(['/']);
      },
      error: (error) => {
        console.error('Booking error:', error);
        this.submitting = false;

        if (error.status === 409) {
          // Slot conflict
          this.errors['general'] = error.error.message || 'This time slot is already booked. Please select a different time slot.';
          this.currentStep = 2; // Go back to appointment details step
          // Reload slots to show updated availability
          this.loadAvailableSlots();
        } else if (error.error?.details) {
          this.errors['general'] = `Failed to book appointment: ${JSON.stringify(error.error.details)}`;
        } else {
          this.errors['general'] = 'Failed to book appointment. Please try again.';
        }
      }
    });
  }

  bookAnimalAppointment() {
    if (!this.doctorId) return;

    const appointmentData = {
      doctor_id: this.doctorId,
      owner_name: this.ownerName,
      owner_phone: this.ownerPhone,
      owner_email: this.ownerEmail,
      animal_name: this.animalName,
      species: this.species,
      breed: this.breed,
      age: this.animalAge || undefined,
      gender: this.animalGender,
      weight: this.weight || undefined,
      appointment_date: this.appointmentDate,
      reason: this.reason
    };

    this.apiService.createAnimalAppointment(appointmentData).subscribe({
      next: (response) => {
        console.log('Appointment created:', response);

        const message = `✅ Appointment Booked Successfully!\n\n` +
          `Appointment ID: ${response.appointment_id}\n` +
          `Doctor: ${response.booking_details?.doctor_name}\n` +
          `Pet: ${response.booking_details?.animal_name}\n` +
          `Owner: ${response.booking_details?.owner_name}\n` +
          `Date: ${response.booking_details?.date}\n` +
          `Clinic: ${response.booking_details?.clinic}\n\n` +
          `Please bring your pet's medical records if available.`;

        alert(message);
        this.submitting = false;
        this.router.navigate(['/']);
      },
      error: (error) => {
        console.error('Booking error:', error);
        this.submitting = false;

        if (error.status === 409) {
          // Slot conflict
          this.errors['general'] = error.error.message || 'This date is already booked. Please select a different date.';
          this.currentStep = 2; // Go back to appointment details step
          // Reload slots to show updated availability
          this.loadAvailableSlots();
        } else if (error.error?.details) {
          this.errors['general'] = `Failed to book appointment: ${JSON.stringify(error.error.details)}`;
        } else {
          this.errors['general'] = 'Failed to book appointment. Please try again.';
        }
      }
    });
  }

  goBack() {
    this.router.navigate(['/symptoms']);
  }

  get isLoading(): boolean {
    return this.loading;
  }

  get hasDoctor(): boolean {
    return !!this.doctor;
  }

  get doctorData(): any {
    return this.doctor;
  }

  // Helper methods for template
  isStepActive(step: number): boolean {
    return this.currentStep === step;
  }

  isStepCompleted(step: number): boolean {
    return this.currentStep > step;
  }

  getStepTitle(): string {
    switch (this.currentStep) {
      case 1:
        return this.careType === 'human' ? 'Patient Information' : 'Pet & Owner Information';
      case 2:
        return 'Appointment Details';
      case 3:
        return 'Confirmation';
      default:
        return '';
    }
  }

  getStepIcon(): string {
    switch (this.currentStep) {
      case 1:
        return this.careType === 'human' ? 'fas fa-user' : 'fas fa-paw';
      case 2:
        return 'fas fa-calendar-alt';
      case 3:
        return 'fas fa-check-circle';
      default:
        return '';
    }
  }

  getAvailableSlotsCount(): number {
    return this.availableSlots.filter(slot => slot.available).length;
  }

  ngOnDestroy() {
    console.log('Appointment component destroyed');
  }
}

