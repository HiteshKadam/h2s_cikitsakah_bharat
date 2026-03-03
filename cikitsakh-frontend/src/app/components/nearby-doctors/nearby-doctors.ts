import { Component, OnInit, inject, PLATFORM_ID, ChangeDetectorRef } from '@angular/core';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule, isPlatformBrowser } from '@angular/common';

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

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) { }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.getLocation();
      this.loadDoctors();
    }
  }

  // ✅ Proper Geolocation Code
  getLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('Latitude:', position.coords.latitude);
          console.log('Longitude:', position.coords.longitude);
        },
        (error) => {
          console.error('Geolocation error:', error);
        }
      );
    } else {
      console.log('Geolocation not supported');
    }
  }

  // ✅ Load JSON
  loadDoctors() {
    this.http.get<any[]>('assets/data/doctors.json')
      .subscribe({
        next: (data) => {
          console.log('Doctors loaded:', data);

          this.allDoctors = data;
          this.doctors = [...data];   // 👈 important
          this.extractSpecializations();
          this.loading = false;

          this.cdr.detectChanges();   // 👈 force UI update
        },
        error: (err) => {
          console.error('Failed to load doctors.json', err);
          this.loading = false;
          this.cdr.detectChanges();
        }
      });
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
        doc.distance <= this.selectedDistance;

      const matchPet =
        !this.petOnly ||
        doc.petFriendly === true;

      return matchSpeciality && matchRating && matchDistance && matchPet;
    });

    this.doctors = [...this.doctors]; // trigger change detection
  }

  isSelected(spec: string): boolean {
    return this.selectedFilters.includes(spec);
  }

  sortDoctors(event: any) {
    const value = event.target.value;

    if (value === 'distance') {
      this.doctors.sort((a, b) => a.distance - b.distance);
    }

    if (value === 'rating') {
      this.doctors.sort((a, b) => b.rating - a.rating);
    }

    if (value === 'experience') {
      this.doctors.sort((a, b) => b.experience - a.experience);
    }

    this.doctors = [...this.doctors]; // trigger UI update
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
}