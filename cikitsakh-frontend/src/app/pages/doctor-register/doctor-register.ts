import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-doctor-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor-register.html',
  styleUrls: ['./doctor-register.scss']
})
export class DoctorRegisterComponent {
  registerData = {
    doctorType: 'human' as 'human' | 'vet',
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phoneNumber: '',
    gender: '',
    age: null as number | null,
    specialization: '',
    yearsExperience: null as number | null,
    registrationNumber: '',
    passoutDate: '',
    clinicName: '',
    address: '',
    city: '',
    state: ''
  };
  
  errorMessage = '';
  successMessage = '';
  isLoading = false;

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  onRegister() {
    // Validate passwords match
    if (this.registerData.password !== this.registerData.confirmPassword) {
      this.errorMessage = 'Passwords do not match';
      return;
    }

    // Validate phone number (10 digits)
    const phoneRegex = /^[0-9]{10}$/;
    if (!phoneRegex.test(this.registerData.phoneNumber)) {
      this.errorMessage = 'Phone number must be exactly 10 digits';
      return;
    }

    // Validate age > years of experience
    if (this.registerData.age && this.registerData.yearsExperience) {
      if (this.registerData.age <= this.registerData.yearsExperience) {
        this.errorMessage = 'Age must be greater than years of experience';
        return;
      }
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    // Add +91 prefix to phone number
    const dataToSend = {
      ...this.registerData,
      phoneNumber: '+91' + this.registerData.phoneNumber
    };

    this.apiService.doctorRegister(dataToSend).subscribe({
      next: (response) => {
        this.successMessage = 'Registration successful! Redirecting to login...';
        setTimeout(() => {
          this.router.navigate(['/doctor-login']);
        }, 2000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || error.error?.message || 'Registration failed. Please try again.';
        this.isLoading = false;
      }
    });
  }

  goToLogin() {
    this.router.navigate(['/doctor-login']);
  }

  goBack() {
    this.router.navigate(['/']);
  }
}
