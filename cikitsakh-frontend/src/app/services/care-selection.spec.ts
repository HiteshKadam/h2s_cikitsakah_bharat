import { TestBed } from '@angular/core/testing';

import { CareSelection } from './care-selection';

describe('CareSelection', () => {
  let service: CareSelection;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CareSelection);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
