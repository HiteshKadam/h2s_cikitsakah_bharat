import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-doctor-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor-login.html',
  styleUrls: ['./doctor-login.scss']
})
export class DoctorLoginComponent {
  loginData = {
    email: '',
    password: '',
    doctorType: 'human' as 'human' | 'vet'
  };
  errorMessage = '';
  isLoading = false;
  isRedirecting = false;
  showToast = false;

  constructor(
    private apiService: ApiService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  onLogin() {
    this.isLoading = true;
    this.errorMessage = '';
    this.isRedirecting = false;
    this.showToast = false;
    this.cdr.detectChanges();

    this.apiService.doctorLogin(this.loginData).subscribe({
      next: (response) => {
        this.isLoading = false;
        localStorage.setItem('doctorToken', response.token);
        localStorage.setItem('doctorType', this.loginData.doctorType);
        localStorage.setItem('doctorId', response.doctor_id);
        this.router.navigate(['/doctor-dashboard']);
      },
      error: (error) => {
        console.log('Login error:', error);
        this.isLoading = false;
        
        // Extract error message
        const errorData = error.error || {};
        const errorType = errorData.errorType || '';
        const errorMsg = errorData.error || errorData.message || error.message || 'Login failed. Please check credentials.';
        
        this.errorMessage = errorMsg;
        
        // Trigger change detection and show toast
        setTimeout(() => {
          this.showToast = true;
          this.cdr.detectChanges();
        }, 10);
        
        // Handle specific error types
        if (errorType === 'USER_NOT_FOUND') {
          this.isRedirecting = true;
          this.cdr.detectChanges();
          
          // Show error for 3 seconds then redirect
          setTimeout(() => {
            this.showToast = false;
            this.cdr.detectChanges();
            
            setTimeout(() => {
              this.errorMessage = '';
              this.isRedirecting = false;
              this.router.navigate(['/doctor-register']);
            }, 300);
          }, 3000);
        } else {
          // Clear error after 3 seconds for other errors
          setTimeout(() => {
            this.showToast = false;
            this.cdr.detectChanges();
            
            setTimeout(() => {
              this.errorMessage = '';
              this.cdr.detectChanges();
            }, 300);
          }, 3000);
        }
      }
    });
  }

  goToRegister() {
    this.router.navigate(['/doctor-register']);
  }

  goBack() {
    this.router.navigate(['/']);
  }
}
