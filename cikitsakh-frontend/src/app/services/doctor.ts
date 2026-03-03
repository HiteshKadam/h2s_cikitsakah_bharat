import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { Doctor } from '../models/doctor.model';

@Injectable({
  providedIn: 'root'
})
export class DoctorService {

  private doctors: Doctor[] = [
    {
      id: 1,
      name: 'Dr. Rahul Sharma',
      age: 45,
      gender: 'Male',
      specialty: 'Pediatrician',
      address: 'Andheri West, Mumbai',
      experience: 18
    },
    {
      id: 2,
      name: 'Dr. Neha Mehta',
      age: 38,
      gender: 'Female',
      specialty: 'Physiotherapist',
      address: 'Bandra East, Mumbai',
      experience: 12
    }
  ];

  searchDoctors(range: string, specialty: string): Observable<Doctor[]> {
    const filtered = this.doctors.filter(d =>
      (!specialty || d.specialty === specialty)
    );

    return of(filtered).pipe(delay(1500)); // simulate loader
  }
}