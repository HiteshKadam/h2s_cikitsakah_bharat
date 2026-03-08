import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { DoctorService } from '../../services/doctor';
import { CareSelectionService } from '../../services/care-selection';
import { LocationService } from '../../services/location';

@Component({
  selector: 'app-doctor-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor-list.html',
  styleUrls: ['./doctor-list.scss']
})
export class DoctorListComponent implements OnInit {

  range: string = '';
  specialty: string = '';
  doctors: any[] = [];
  loading: boolean = false;
  careType: 'human' | 'pet' | null = null;

  constructor(
    private doctorService: DoctorService,
    private careService: CareSelectionService,
    private locationService: LocationService,
    private router: Router
  ) { }

  ngOnInit() {
    this.careType = this.careService.getCareType() as 'human' | 'pet';
    if (!this.careType) {
      this.router.navigate(['/']);
    }
  }

  search() {
    if (!this.careType) return;

    this.loading = true;

    this.locationService.getCurrentLocation()
      .then((location) => {
        const radius = this.range ? parseFloat(this.range) : 10;

        if (this.careType === 'pet') {
          this.doctorService.getNearbyVetDoctors(
            location.latitude,
            location.longitude,
            radius,
            this.specialty
          ).subscribe({
            next: (data: any[]) => {
              this.doctors = data.map((doc: any) => ({
                id: doc.doctor_id || doc.id,
                name: doc.name,
                age: doc.age || 'N/A',
                gender: doc.gender || 'N/A',
                specialty: doc.specialty,
                experience: doc.experience || 0,
                address: doc.address || 'N/A'
              }));
              this.loading = false;
            },
            error: (error: any) => {
              console.error('Search error', error);
              this.loading = false;
            }
          });
        } else {
          this.doctorService.getNearbyHumanDoctors(
            location.latitude,
            location.longitude,
            radius,
            this.specialty
          ).subscribe({
            next: (data: any[]) => {
              this.doctors = data.map((doc: any) => ({
                id: doc.doctor_id || doc.id,
                name: `Dr. ${doc.first_name} ${doc.last_name}`,
                age: doc.age || 'N/A',
                gender: doc.gender_name || 'N/A',
                specialty: doc.specialization,
                experience: doc.yoe || 0,
                address: doc.address_details 
                  ? `${doc.address_details.city}, ${doc.address_details.state}`
                  : 'N/A'
              }));
              this.loading = false;
            },
            error: (error: any) => {
              console.error('Search error', error);
              this.loading = false;
            }
          });
        }
      })
      .catch((error: any) => {
        console.error('Location error', error);
        alert('Please enable location services');
        this.loading = false;
      });
  }

  goToAppointment(doctorId: number) {
    this.router.navigate(['/appointment', doctorId]);
  }
}
