import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-marquee',
  templateUrl: './app-marquee.html',
  styleUrls: ['./app-marquee.scss'],
  imports: [CommonModule]
})
export class AppMarqueeComponent {

  features = [
    {
      title: 'Voice Based Symptom Input',
      description: 'Describe symptoms naturally using voice for faster diagnosis.'
    },
    {
      title: 'AI Powered Diagnosis',
      description: 'Get instant AI-driven preliminary health insights.'
    },
    {
      title: 'Nearby Doctors & Hospitals',
      description: 'Find trusted specialists near your location.'
    },
    {
      title: 'Instant Appointment Booking',
      description: 'Book appointments in seconds without waiting.'
    }
  ];
}