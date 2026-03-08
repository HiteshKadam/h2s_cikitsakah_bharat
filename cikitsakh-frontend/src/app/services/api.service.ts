import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = '/api';

  constructor(private http: HttpClient) { }

  translateSymptoms(text: string, sourceLanguage: string = 'auto'): Observable<any> {
    return this.http.post(`${this.baseUrl}/translate-symptoms/`, {
      text,
      source_language: sourceLanguage
    });
  }

  analyzeSymptoms(symptoms: string, patientType: 'human' | 'pet'): Observable<any> {
    return this.http.post(`${this.baseUrl}/analyze-symptoms/`, {
      symptoms,
      patient_type: patientType
    });
  }

  searchDoctorsBySymptoms(
    symptoms: string,
    patientType: 'human' | 'pet',
    latitude: number,
    longitude: number,
    radius: number = 10
  ): Observable<any> {
    return this.http.post(`${this.baseUrl}/search-doctors/`, {
      symptoms,
      patient_type: patientType,
      latitude,
      longitude,
      radius
    });
  }

  getNearbyDoctors(
    latitude: number,
    longitude: number,
    radius: number = 10,
    patientType?: 'human' | 'pet',
    specialization?: string
  ): Observable<any> {
    let params = new HttpParams()
      .set('latitude', latitude.toString())
      .set('longitude', longitude.toString())
      .set('radius', radius.toString());

    if (specialization) {
      params = params.set('specialization', specialization);
    }

    const endpoint = patientType === 'pet' 
      ? `${this.baseUrl}/vet-doctors/nearby/`
      : `${this.baseUrl}/human-doctors/nearby/`;

    return this.http.get(endpoint, { params });
  }

  getDoctors(filters?: {
    patient_type?: 'human' | 'pet';
    specialization?: string;
    city?: string;
    min_rating?: number;
  }): Observable<any> {
    let params = new HttpParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params = params.set(key, value.toString());
        }
      });
    }

    return this.http.get(`${this.baseUrl}/doctors/`, { params });
  }

  getHumanDoctors(filters?: {
    specialization?: string;
    city?: string;
    status?: string;
  }): Observable<any> {
    let params = new HttpParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params = params.set(key, value.toString());
        }
      });
    }

    return this.http.get(`${this.baseUrl}/human-doctors/`, { params });
  }

  getVetDoctors(filters?: {
    specialty?: string;
  }): Observable<any> {
    let params = new HttpParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params = params.set(key, value.toString());
        }
      });
    }

    return this.http.get(`${this.baseUrl}/vet-doctors/`, { params });
  }

  // Appointment methods
  getDoctorDetails(doctorId: number, patientType: 'human' | 'pet' = 'human'): Observable<any> {
    return this.http.get(`${this.baseUrl}/doctors/${doctorId}/`, {
      params: { type: patientType }
    });
  }

  getAvailableSlots(doctorId: number, date: string, patientType: 'human' | 'pet' = 'human'): Observable<any> {
    return this.http.get(`${this.baseUrl}/doctors/${doctorId}/slots/`, {
      params: { date, type: patientType }
    });
  }

  createHumanAppointment(appointmentData: {
    doctor_id: number;
    patient_first_name: string;
    patient_last_name: string;
    contact_number: string;
    email_id?: string;
    date_of_birth?: string;
    gender_id?: number;
    scheduling_date: string;
    scheduling_time: string;
    reason?: string;
    age?: number;
  }): Observable<any> {
    return this.http.post(`${this.baseUrl}/appointments/human/create/`, appointmentData);
  }

  createAnimalAppointment(appointmentData: {
    doctor_id: number;
    owner_name: string;
    owner_phone: string;
    owner_email?: string;
    animal_name: string;
    species: string;
    breed?: string;
    age?: number;
    gender?: string;
    weight?: number;
    appointment_date: string;
    reason?: string;
  }): Observable<any> {
    return this.http.post(`${this.baseUrl}/appointments/animal/create/`, appointmentData);
  }

  getAppointmentDetails(appointmentId: number, patientType: 'human' | 'pet' = 'human'): Observable<any> {
    return this.http.get(`${this.baseUrl}/appointments/${appointmentId}/`, {
      params: { type: patientType }
    });
  }
}
