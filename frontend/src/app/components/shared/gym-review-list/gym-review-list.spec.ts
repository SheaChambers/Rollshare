import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GymReviewList } from './gym-review-list';

describe('GymReviewList', () => {
  let component: GymReviewList;
  let fixture: ComponentFixture<GymReviewList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GymReviewList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GymReviewList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
