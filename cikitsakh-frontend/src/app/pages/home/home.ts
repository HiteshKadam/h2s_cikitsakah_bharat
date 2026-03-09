import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CareSelectionService } from '../../services/care-selection';
import { AppMarqueeComponent } from '../../components/app-marquee/app-marquee';

@Component({
  standalone: true,
  selector: 'app-home',
  templateUrl: './home.html',
  styleUrls: ['./home.scss'],
  imports: [AppMarqueeComponent],
})
export class HomeComponent {

  constructor(
    private router: Router,
    private careService: CareSelectionService
  ) { }

  selectCare(type: 'human' | 'pet') {
    this.careService.setCareType(type);
    this.router.navigate(['/symptoms']);
  }

  goToDoctorLogin() {
    this.router.navigate(['/doctor-login']);
  }

  goToDoctorRegister() {
    this.router.navigate(['/doctor-register']);
  }
}