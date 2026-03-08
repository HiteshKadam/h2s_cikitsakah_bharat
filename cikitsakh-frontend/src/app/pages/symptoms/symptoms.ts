import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CareSelectionService } from '../../services/care-selection';
import { ApiService } from '../../services/api.service';
import { LocationService } from '../../services/location';
import { Router } from '@angular/router';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './symptoms.html',
  styleUrls: ['./symptoms.scss']
})
export class SymptomsComponent implements OnInit {
  webkitSpeechRecognition: any;
  recognition: any;
  careType: 'human' | 'pet' | null = null;
  symptoms: string = '';
  severity: string = '';
  loading: boolean = false;
  analysisResult: any = null;
  recommendedDoctors: any[] = [];
  showResults: boolean = false;
  Object = Object; // Make Object available in template
  
  // Voice recording properties
  isRecording: boolean = false;
  selectedLanguage: string = 'hi-IN'; // Default to Hindi
  translationInProgress: boolean = false;
  originalText: string = '';
  detectedLanguage: string = '';

  constructor(
    private careService: CareSelectionService,
    private apiService: ApiService,
    private locationService: LocationService,
    private router: Router
  ) { }

  ngOnInit() {
    this.careType = this.careService.getCareType() as 'human' | 'pet';
    if (!this.careType) {
      this.router.navigate(['/']);
    }
  }

  goBack() {
    this.router.navigate(['/']);
  }

  setLanguage(lang: string) {
    this.selectedLanguage = lang;
  }

  startListening() {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (this.isRecording) {
      // Stop recording
      this.recognition?.stop();
      this.isRecording = false;
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.lang = this.selectedLanguage; // Use selected language
    this.recognition.interimResults = false;
    this.recognition.continuous = false;

    this.isRecording = true;
    this.recognition.start();

    this.recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      this.originalText = transcript;
      
      // If language is Marathi or Hindi, translate to English
      if (this.selectedLanguage === 'hi-IN' || this.selectedLanguage === 'mr-IN') {
        this.translateAndSetSymptoms(transcript);
      } else {
        // English - use directly
        this.symptoms = transcript;
        this.isRecording = false;
      }
    };

    this.recognition.onerror = (event: any) => {
      console.error('Speech recognition error', event);
      this.isRecording = false;
      alert('Error recognizing speech. Please try again.');
    };

    this.recognition.onend = () => {
      this.isRecording = false;
    };
  }

  translateAndSetSymptoms(text: string) {
    this.translationInProgress = true;
    
    // Determine source language
    const sourceLanguage = this.selectedLanguage === 'mr-IN' ? 'marathi' : 'hindi';
    
    this.apiService.translateSymptoms(text, sourceLanguage).subscribe({
      next: (response) => {
        console.log('Translation response:', response);
        
        if (response.success && response.translation) {
          this.symptoms = response.translation.translated_text;
          this.detectedLanguage = response.translation.detected_language;
          
          // Show success message
          alert(`Translated from ${this.detectedLanguage} to English successfully!`);
        } else {
          alert('Translation failed. Using original text.');
          this.symptoms = text;
        }
        
        this.translationInProgress = false;
        this.isRecording = false;
      },
      error: (error) => {
        console.error('Translation error:', error);
        alert('Translation service unavailable. Using original text.');
        this.symptoms = text;
        this.translationInProgress = false;
        this.isRecording = false;
      }
    });
  }

  analyzeAndSearch() {
    if (!this.symptoms || !this.careType) {
      alert('Please enter symptoms');
      return;
    }

    this.loading = true;
    this.showResults = false;

    this.locationService.getCurrentLocation()
      .then((location) => {
        if (!this.careType) return;

        this.apiService.searchDoctorsBySymptoms(
          this.symptoms,
          this.careType,
          location.latitude,
          location.longitude,
          10
        ).subscribe({
          next: (response) => {
            console.log('AI Analysis Response:', response);
            
            this.analysisResult = response.analysis;
            this.severity = response.analysis.severity;
            
            // Show search expansion message if applicable
            if (response.search_expanded) {
              console.log(`Search expanded from ${response.initial_radius}km to ${response.search_radius}km`);
            }
            
            if (response.city_based_search) {
              alert(`No doctors found nearby. Showing doctors from nearest cities within ${response.search_radius}km.`);
            }
            
            // Map doctors with AI match scores
            this.recommendedDoctors = response.doctors.map((doc: any) => ({
              ...doc,
              name: doc.name || `Dr. ${doc.first_name} ${doc.last_name}`,
              image: 'https://via.placeholder.com/300x220',
              hospital: doc.clinic_name || doc.address_details?.city || 'N/A',
              location: doc.address_details 
                ? `${doc.address_details.city}, ${doc.address_details.state}` 
                : doc.address || 'N/A',
              experience: `${doc.yoe || doc.experience || 0} years experience`,
              rating: doc.rating || 4.5,
              match_score: doc.match_score || 0,
              match_reason: doc.match_reason || 'Recommended specialist',
              search_info: response.search_expanded 
                ? `Found within ${response.search_radius}km` 
                : `Within ${response.initial_radius}km`
            }));
            
            if (this.recommendedDoctors.length === 0) {
              alert('No doctors found matching your symptoms. Please try different symptoms or consult a general practitioner.');
            }
            
            this.showResults = true;
            this.loading = false;
          },
          error: (error: any) => {
            console.error('Search error', error);
            alert('Error searching for doctors. Please try again.');
            this.loading = false;
          }
        });
      })
      .catch((error: any) => {
        console.error('Location error', error);
        alert('Please enable location services');
        this.loading = false;
      });
  }

  bookAppointment(doctorId: number) {
    this.router.navigate(['/appointment', doctorId]);
  }
}