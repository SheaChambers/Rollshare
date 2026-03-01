import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GymCard } from './gym-card';

describe('GymCard', () => {
  let component: GymCard;
  let fixture: ComponentFixture<GymCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GymCard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GymCard);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
