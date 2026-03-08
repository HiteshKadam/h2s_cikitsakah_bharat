import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CareSelectionService {

  private careType: 'human' | 'pet' | null = null;

  setCareType(type: 'human' | 'pet') {
    this.careType = type;
    localStorage.setItem('careType', type);
  }

  getCareType() {
    if (!this.careType) {
      const stored = localStorage.getItem('careType');
      if (stored === 'human' || stored === 'pet') {
        this.careType = stored;
      }
    }
    return this.careType;
  }
}