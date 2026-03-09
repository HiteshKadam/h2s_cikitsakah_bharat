import { Routes } from '@angular/router';
import { SymptomsComponent } from './pages/symptoms/symptoms';
import { HomeComponent } from './pages/home/home';
import { DoctorListComponent } from './pages/doctor-list/doctor-list';
import { Appointment } from './pages/appointment/appointment';
import { DoctorLoginComponent } from './pages/doctor-login/doctor-login';
import { DoctorRegisterComponent } from './pages/doctor-register/doctor-register';
import { DoctorDashboardComponent } from './pages/doctor-dashboard/doctor-dashboard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'symptoms', component: SymptomsComponent },
  { path: 'doctors', component: DoctorListComponent },
  { path: 'appointment/:id', component: Appointment },
  { path: 'doctor-login', component: DoctorLoginComponent },
  { path: 'doctor-register', component: DoctorRegisterComponent },
  { path: 'doctor-dashboard', component: DoctorDashboardComponent },
];