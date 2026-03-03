import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Doctor } from '../../models/doctor.model';
import { Router } from '@angular/router';
import { DoctorService } from '../../services/doctor';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor-list.html',
  styleUrls: ['./doctor-list.scss']
})
export class DoctorListComponent {

  range: string = '';
  specialty: string = '';
  doctors: Doctor[] = [];
  loading: boolean = false;

  constructor(
    private doctorService: DoctorService,
    private router: Router
  ) {}

  search() {
    this.loading = true;

    this.doctorService.searchDoctors(this.range, this.specialty)
      .subscribe(data => {
        this.doctors = data;
        this.loading = false;
      });
  }

  goToAppointment(id: number) {
    this.router.navigate(['/appointment', id]);
  }
}