import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TechniqueCard } from './technique-card';

describe('TechniqueCard', () => {
  let component: TechniqueCard;
  let fixture: ComponentFixture<TechniqueCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TechniqueCard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TechniqueCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
