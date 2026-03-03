import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CareSelectionService } from '../../services/care-selection';
import { Router } from '@angular/router';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './symptoms.html'
})
export class SymptomsComponent implements OnInit {
  webkitSpeechRecognition: any;
  recognition: any;
  careType: string | null = null;
  symptoms: string = '';
  severity: string = '';
  loading: boolean = false;

  constructor(private careService: CareSelectionService,
    private router: Router
  ) { }



  ngOnInit() {
    this.careType = this.careService.getCareType();
  }

  goBack() {
    this.router.navigate(['/']);
  }

  startListening() {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    this.recognition = new SpeechRecognition();
    this.recognition.lang = 'en-IN'; // Default language
    this.recognition.interimResults = false;

    this.recognition.start();

    this.recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      this.processWithLLM(transcript);
    };

    this.recognition.onerror = (event: any) => {
      console.error('Speech recognition error', event);
    };
  }

    processWithLLM(transcript: string) {

      this.loading = true;

      fetch('http://localhost:3000/process-symptoms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: transcript
        })
      })
        .then(res => res.json())
        .then(data => {
          this.symptoms = data.cleanedSymptoms;
          this.loading = false;
        });
    }

  }