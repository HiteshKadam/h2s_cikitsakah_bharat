import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AppMarquee } from './app-marquee';

describe('AppMarquee', () => {
  let component: AppMarquee;
  let fixture: ComponentFixture<AppMarquee>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppMarquee],
    }).compileComponents();

    fixture = TestBed.createComponent(AppMarquee);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
