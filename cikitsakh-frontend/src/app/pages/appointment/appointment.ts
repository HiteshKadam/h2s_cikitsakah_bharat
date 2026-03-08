import { Component, OnInit } from '@angular/core';
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

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private careService: CareSelectionService
  ) {}

  ngOnInit() {
    this.careType = this.careService.getCareType() as 'human' | 'pet';
    
    this.route.params.subscribe(params => {
      this.doctorId = +params['id'];
      this.loadDoctorDetails();
    });
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    this.appointmentDate = today;
  }

  loadDoctorDetails() {
    if (!this.doctorId || !this.careType) return;
    
    this.loading = true;
    this.apiService.getDoctorDetails(this.doctorId, this.careType).subscribe({
      next: (response) => {
        this.doctor = response.doctor;
        this.loading = false;
        
        // Load available slots for today
        if (this.appointmentDate) {
          this.loadAvailableSlots();
        }
      },
      error: (error) => {
        console.error('Error loading doctor:', error);
        alert('Failed to load doctor details');
        this.loading = false;
      }
    });
  }

  onDateChange() {
    if (this.appointmentDate && this.doctorId) {
      this.loadAvailableSlots();
    }
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

  confirmBooking() {
    if (!this.validateForm()) {
      alert('Please fill all required fields');
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
    if (!this.doctorId || !this.appointmentDate || !this.appointmentTime) {
      return false;
    }

    if (this.careType === 'human') {
      return !!(this.patientFirstName && this.patientLastName && this.contactNumber);
    } else {
      return !!(this.ownerName && this.ownerPhone && this.animalName && this.species);
    }
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
        alert(`Appointment booked successfully! Your appointment ID is: ${response.appointment_id}`);
        this.submitting = false;
        this.router.navigate(['/symptoms']);
      },
      error: (error) => {
        console.error('Booking error:', error);
        alert('Failed to book appointment. Please try again.');
        this.submitting = false;
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
        alert(`Appointment booked successfully! Your appointment ID is: ${response.appointment_id}`);
        this.submitting = false;
        this.router.navigate(['/symptoms']);
      },
      error: (error) => {
        console.error('Booking error:', error);
        alert('Failed to book appointment. Please try again.');
        this.submitting = false;
      }
    });
  }

  goBack() {
    this.router.navigate(['/symptoms']);
  }
}

