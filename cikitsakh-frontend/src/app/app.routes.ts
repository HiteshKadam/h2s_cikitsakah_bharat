import { Routes } from '@angular/router';
import { SymptomsComponent } from './pages/symptoms/symptoms';
import { HomeComponent } from './pages/home/home';
import { DoctorListComponent } from './pages/doctor-list/doctor-list';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'symptoms', component: SymptomsComponent },
  { path: 'doctors', component: DoctorListComponent },
];