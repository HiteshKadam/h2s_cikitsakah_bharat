
  
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-doctor-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor-dashboard.html',
  styleUrls: ['./doctor-dashboard.scss']
})
export class DoctorDashboardComponent implements OnInit {
  doctorType: 'human' | 'vet' = 'human';
  doctorId: string = '';
  appointments: any[] = [];
  isLoading = true;
  errorMessage = '';
  showEditPanel = false;
  isSaving = false;
  successMessage = '';
  showSuccessToast = false;
  selectedTab: 'upcoming' | 'past' = 'upcoming';
  
  profileData = {
    address: '',
    city: '',
    state: '',
    openTime1: '',
    closeTime1: '',
    openTime2: '',
    closeTime2: '',
    isActive: true
  };

  constructor(
    private apiService: ApiService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const token = localStorage.getItem('doctorToken');
    if (!token) {
      this.router.navigate(['/doctor-login']);
      return;
    }

    this.doctorType = (localStorage.getItem('doctorType') as 'human' | 'vet') || 'human';
    this.doctorId = localStorage.getItem('doctorId') || '';

    this.loadAppointments('upcoming');
    this.loadDoctorProfile();
  }

  loadAppointments(tab: 'upcoming' | 'past') {
    this.isLoading = true;
    this.selectedTab = tab;
    this.appointments = [];
    this.apiService.getDoctorAppointments(this.doctorId, this.doctorType, tab).subscribe({
      next: (response) => {
        this.appointments = response.appointments || [];
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = 'Failed to load appointments';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  loadDoctorProfile() {
    this.apiService.getDoctorProfile(this.doctorId, this.doctorType).subscribe({
      next: (response) => {
        const profile = response.profile || {};
        this.profileData = {
          address: profile.address || '',
          city: profile.city || '',
          state: profile.state || '',
          openTime1: profile.open_time_1 || '',
          closeTime1: profile.close_time_1 || '',
          openTime2: profile.open_time_2 || '',
          closeTime2: profile.close_time_2 || '',
          isActive: profile.status === 'Active' || profile.status === 'active'
        };
      },
      error: (error) => {
        console.error('Failed to load profile', error);
      }
    });
  }
onStatusChange(appointment: any, newStatus: string): void {
    const apptType = this.doctorType === 'human' ? 'human' : 'vet';
    this.apiService.updateAppointmentStatus(appointment.appointment_id, newStatus, apptType).subscribe({
      next: (_res: any) => {
        this.loadAppointments(this.selectedTab); // Refresh list
      },
      error: (_err: any) => {
        this.errorMessage = 'Failed to update status';
        this.cdr.detectChanges();
      }
    });
  }
  
  toggleEditProfile() {
    this.showEditPanel = !this.showEditPanel;
    this.successMessage = '';
    this.errorMessage = '';
  }

  saveProfile() {
    this.isSaving = true;
    this.successMessage = '';
    this.errorMessage = '';
    this.showSuccessToast = false;
    this.cdr.detectChanges();

    const updateData = {
      ...this.profileData,
      status: this.profileData.isActive ? 'Active' : 'Inactive'
    };

    this.apiService.updateDoctorProfile(this.doctorId, this.doctorType, updateData).subscribe({
      next: (response) => {
        console.log('Profile update success:', response);
        this.isSaving = false;
        
        // Close panel immediately
        this.showEditPanel = false;
        this.cdr.detectChanges();
        
        // Show success toast after panel closes
        setTimeout(() => {
          this.showSuccessToast = true;
          this.successMessage = 'Profile updated successfully!';
          this.cdr.detectChanges();
          
          // Hide toast after 3 seconds
          setTimeout(() => {
            this.showSuccessToast = false;
            this.cdr.detectChanges();
            setTimeout(() => {
              this.successMessage = '';
              this.cdr.detectChanges();
            }, 300);
          }, 3000);
        }, 300);
      },
      error: (error) => {
        console.error('Profile update error:', error);
        this.isSaving = false;
        this.errorMessage = error.error?.error || 'Failed to update profile';
        this.cdr.detectChanges();
        
        // Clear error after 3 seconds
        setTimeout(() => {
          this.errorMessage = '';
          this.cdr.detectChanges();
        }, 3000);
      }
    });
  }

  logout() {
    localStorage.removeItem('doctorToken');
    localStorage.removeItem('doctorType');
    localStorage.removeItem('doctorId');
    this.router.navigate(['/']);
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  }

  formatTime(time: string): string {
    if (!time) return '';
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  }
}
