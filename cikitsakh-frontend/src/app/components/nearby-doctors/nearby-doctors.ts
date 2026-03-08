import { Component, OnInit, inject, PLATFORM_ID, ChangeDetectorRef } from '@angular/core';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { CareSelectionService } from '../../services/care-selection';
import { DoctorService } from '../../services/doctor';
import { LocationService } from '../../services/location';
import { Router } from '@angular/router';

@Component({
  standalone: true,
  selector: 'nearby-doctors',
  templateUrl: './nearby-doctors.html',
  styleUrls: ['./nearby-doctors.scss'],
  imports: [CommonModule, HttpClientModule]
})
export class NearbyDoctorsComponent implements OnInit {

  doctors: any[] = [];
  allDoctors: any[] = [];
  loading = true;

  specializations: string[] = [];
  selectedFilters: string[] = [];
  selectedSpeciality: string = '';
  selectedRating: number | null = null;
  selectedDistance: number | null = null;
  petOnly: boolean = false;

  private platformId = inject(PLATFORM_ID);
  private careType: 'human' | 'pet' | null = null;

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
    private careService: CareSelectionService,
    private doctorService: DoctorService,
    private locationService: LocationService,
    private router: Router
  ) { }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.careType = this.careService.getCareType() as 'human' | 'pet';
      this.getLocationAndLoadDoctors();
    }
  }

  getLocationAndLoadDoctors() {
    this.locationService.getCurrentLocation()
      .then((location) => {
        this.loadDoctors(location.latitude, location.longitude);
      })
      .catch((error) => {
        console.error('Geolocation error:', error);
        this.loadDoctors();
      });
  }

  loadDoctors(latitude?: number, longitude?: number) {
    if (latitude && longitude) {
      if (this.careType === 'pet') {
        this.doctorService.getNearbyVetDoctors(latitude, longitude, 10).subscribe({
          next: (data: any[]) => {
            this.allDoctors = data.map((doc: any) => ({
              ...doc,
              name: doc.name,
              image: 'https://via.placeholder.com/300x220',
              hospital: doc.clinic_name || 'N/A',
              location: doc.address || 'N/A',
              experience: `${doc.experience || 0} years experience`,
              rating: doc.rating || 4.5,
              distance: doc.distance ? `${doc.distance} km` : 'N/A',
              specialization: doc.specialty
            }));
            this.doctors = [...this.allDoctors];
            this.extractSpecializations();
            this.loading = false;
            this.cdr.detectChanges();
          },
          error: (err: any) => {
            console.error('Failed to load doctors from API', err);
            this.loading = false;
            this.cdr.detectChanges();
          }
        });
      } else {
        this.doctorService.getNearbyHumanDoctors(latitude, longitude, 100).subscribe({
          next: (data: any[]) => {
            this.allDoctors = data.map((doc: any) => ({
              ...doc,
              name: `Dr. ${doc.first_name} ${doc.last_name}`,
              image: 'https://via.placeholder.com/300x220',
              hospital: doc.address_details?.city || 'N/A',
              location: doc.address_details ? `${doc.address_details.city}, ${doc.address_details.state}` : 'N/A',
              experience: `${doc.yoe || 0} years experience`,
              rating: doc.rating || 4.5,
              distance: doc.distance ? `${doc.distance} km` : 'N/A',
              specialization: doc.specialization
            }));
            this.doctors = [...this.allDoctors];
            this.extractSpecializations();
            this.loading = false;
            this.cdr.detectChanges();
          },
          error: (err: any) => {
            console.error('Failed to load doctors from API', err);
            this.loading = false;
            this.cdr.detectChanges();
          }
        });
      }
    } else {
      this.loading = false;
    }
  }

  extractSpecializations() {
    const specs = this.allDoctors.map(doc => doc.specialization);
    this.specializations = [...new Set(specs)];
  }

  toggleFilter(spec: string) {
    if (this.selectedFilters.includes(spec)) {
      this.selectedFilters = this.selectedFilters.filter(s => s !== spec);
    } else {
      this.selectedFilters.push(spec);
    }
    this.applyAdvancedFilters();
  }

  applyAdvancedFilters() {
    this.doctors = this.allDoctors.filter(doc => {
      const matchSpeciality =
        !this.selectedSpeciality ||
        doc.specialization === this.selectedSpeciality;

      const matchRating =
        !this.selectedRating ||
        doc.rating >= this.selectedRating;

      const matchDistance =
        !this.selectedDistance ||
        (doc.distance && parseFloat(doc.distance) <= this.selectedDistance);

      const matchPet =
        !this.petOnly ||
        doc.petFriendly === true;

      return matchSpeciality && matchRating && matchDistance && matchPet;
    });

    this.doctors = [...this.doctors];
  }

  isSelected(spec: string): boolean {
    return this.selectedFilters.includes(spec);
  }

  sortDoctors(event: any) {
    const value = event.target.value;

    if (value === 'distance') {
      this.doctors.sort((a, b) => {
        const distA = parseFloat(a.distance) || 999;
        const distB = parseFloat(b.distance) || 999;
        return distA - distB;
      });
    }

    if (value === 'rating') {
      this.doctors.sort((a, b) => b.rating - a.rating);
    }

    if (value === 'experience') {
      this.doctors.sort((a, b) => {
        const expA = parseInt(a.experience) || 0;
        const expB = parseInt(b.experience) || 0;
        return expB - expA;
      });
    }

    this.doctors = [...this.doctors];
  }

  onSpecialityChange(event: any) {
    this.selectedSpeciality = event.target.value;
    this.applyAdvancedFilters();
  }

  onRatingChange(event: any) {
    this.selectedRating = event.target.value ? +event.target.value : null;
    this.applyAdvancedFilters();
  }

  onDistanceChange(event: any) {
    this.selectedDistance = event.target.value ? +event.target.value : null;
    this.applyAdvancedFilters();
  }

  onPetToggle(event: any) {
    this.petOnly = event.target.checked;
    this.applyAdvancedFilters();
  }

  bookAppointment(doctorId: number) {
    this.router.navigate(['/appointment', doctorId]);
  }
}