import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CareSelectionService {

  private careType: 'human' | 'pet' | null = null;

  setCareType(type: 'human' | 'pet') {
    this.careType = type;
  }

  getCareType() {
    return this.careType;
  }
}