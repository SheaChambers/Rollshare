import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GymReviewForm } from './gym-review-form';

describe('GymReviewForm', () => {
  let component: GymReviewForm;
  let fixture: ComponentFixture<GymReviewForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GymReviewForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GymReviewForm);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
