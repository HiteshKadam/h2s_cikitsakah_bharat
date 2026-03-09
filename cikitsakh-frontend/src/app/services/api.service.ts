// ...existing code...
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
    updateAppointmentStatus(appointmentId: string, status: string, type: 'human' | 'vet'): Observable<any> {
      return this.http.patch(`${environment.apiUrl}/api/appointments/${appointmentId}/status/`, { status, type });
    }
  private baseUrl = '/api';

  constructor(private http: HttpClient) { }

  translateSymptoms(text: string, sourceLanguage: string = 'auto'): Observable<any> {
    return this.http.post(`${environment.apiUrl}/api/translate-symptoms/`, {
      text,
      source_language: sourceLanguage
    });
  }

  analyzeSymptoms(symptoms: string, patientType: 'human' | 'pet'): Observable<any> {
    return this.http.post(`${environment.apiUrl}/api/analyze-symptoms/`, {
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
    return this.http.post(`${environment.apiUrl}/api/search-doctors/`, {
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
      ? `${environment.apiUrl}/api/vet-doctors/nearby/`
      : `${environment.apiUrl}/api/human-doctors/nearby/`;

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

    return this.http.get(`${environment.apiUrl}/api/doctors/`, { params });
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

    return this.http.get(`${environment.apiUrl}/api/human-doctors/`, { params });
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

    return this.http.get(`${environment.apiUrl}/api/vet-doctors/`, { params });
  }

  // Appointment methods
  getDoctorDetails(doctorId: number, patientType: 'human' | 'pet' = 'human'): Observable<any> {
    return this.http.get(`${environment.apiUrl}/api/doctors/${doctorId}/`, {
      params: { type: patientType }
    });
  }

  getAvailableSlots(doctorId: number, date: string, patientType: 'human' | 'pet' = 'human'): Observable<any> {
    return this.http.get(`${environment.apiUrl}/api/doctors/${doctorId}/slots/`, {
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
    return this.http.post(`${environment.apiUrl}/api/appointments/human/create/`, appointmentData);
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
    return this.http.post(`${environment.apiUrl}/api/appointments/animal/create/`, appointmentData);
  }

  getAppointmentDetails(appointmentId: number, patientType: 'human' | 'pet' = 'human'): Observable<any> {
    return this.http.get(`${environment.apiUrl}/api/appointments/${appointmentId}/`, {
      params: { type: patientType }
    });
  }

  // Doctor authentication methods
  doctorLogin(credentials: { email: string; password: string; doctorType: 'human' | 'vet' }): Observable<any> {
    return this.http.post(`${environment.apiUrl}/api/doctor/login/`, credentials);
  }

  doctorRegister(doctorData: any): Observable<any> {
    return this.http.post(`${environment.apiUrl}/api/doctor/register/`, doctorData);
  }

  getDoctorAppointments(doctorId: string, doctorType: 'human' | 'vet', filter?: 'upcoming' | 'past'): Observable<any> {
    let params: any = { doctor_id: doctorId, type: doctorType };
    if (filter) params.filter = filter;
    return this.http.get(`${environment.apiUrl}/api/doctor/appointments/`, { params });
  }

  getDoctorProfile(doctorId: string, doctorType: 'human' | 'vet'): Observable<any> {
    return this.http.get(`${environment.apiUrl}/api/doctor/profile/`, {
      params: { doctor_id: doctorId, type: doctorType }
    });
  }

  updateDoctorProfile(doctorId: string, doctorType: 'human' | 'vet', profileData: any): Observable<any> {
    return this.http.put(`${environment.apiUrl}/api/doctor/profile/update/`, {
      doctor_id: doctorId,
      type: doctorType,
      ...profileData
    });
  }
}
