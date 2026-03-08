import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Doctor, HumanDoctor, VetDoctor } from '../models/doctor.model';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class DoctorService {

  constructor(private apiService: ApiService) { }

  searchHumanDoctors(
    specialization?: string,
    city?: string
  ): Observable<HumanDoctor[]> {
    return this.apiService.getHumanDoctors({
      specialization,
      city
    }).pipe(
      map(response => this.mapHumanDoctors(response))
    );
  }

  searchVetDoctors(
    specialty?: string
  ): Observable<VetDoctor[]> {
    return this.apiService.getVetDoctors({
      specialty
    }).pipe(
      map(response => this.mapVetDoctors(response))
    );
  }

  getNearbyHumanDoctors(
    latitude: number,
    longitude: number,
    radius: number = 10,
    specialization?: string
  ): Observable<HumanDoctor[]> {
    return this.apiService.getNearbyDoctors(
      latitude,
      longitude,
      radius,
      'human',
      specialization
    ).pipe(
      map(response => this.mapHumanDoctors(response))
    );
  }

  getNearbyVetDoctors(
    latitude: number,
    longitude: number,
    radius: number = 10,
    specialty?: string
  ): Observable<VetDoctor[]> {
    return this.apiService.getNearbyDoctors(
      latitude,
      longitude,
      radius,
      'pet',
      specialty
    ).pipe(
      map(response => this.mapVetDoctors(response))
    );
  }

  searchBySymptoms(
    symptoms: string,
    patientType: 'human' | 'pet',
    latitude: number,
    longitude: number,
    radius: number = 10
  ): Observable<{ analysis: any; doctors: any[] }> {
    return this.apiService.searchDoctorsBySymptoms(
      symptoms,
      patientType,
      latitude,
      longitude,
      radius
    ).pipe(
      map(response => ({
        analysis: response.analysis,
        doctors: patientType === 'human' 
          ? this.mapHumanDoctors(response.doctors)
          : this.mapVetDoctors(response.doctors)
      }))
    );
  }

  private mapHumanDoctors(data: any[]): HumanDoctor[] {
    return data.map(doc => ({
      ...doc,
      id: doc.doctor_id,
      name: `Dr. ${doc.first_name} ${doc.last_name}`,
      experience: doc.yoe,
      rating: 4.5 // Default rating since not in DB
    }));
  }

  private mapVetDoctors(data: any[]): VetDoctor[] {
    return data.map(doc => ({
      ...doc,
      id: doc.doctor_id,
      name: doc.name,
      specialization: doc.specialty,
      rating: 4.5 // Default rating since not in DB
    }));
  }
}