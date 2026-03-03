import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NearbyDoctors } from './nearby-doctors';

describe('NearbyDoctors', () => {
  let component: NearbyDoctors;
  let fixture: ComponentFixture<NearbyDoctors>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NearbyDoctors],
    }).compileComponents();

    fixture = TestBed.createComponent(NearbyDoctors);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
