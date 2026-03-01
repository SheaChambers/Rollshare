import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewGym } from './new-gym';

describe('NewGym', () => {
  let component: NewGym;
  let fixture: ComponentFixture<NewGym>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewGym]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewGym);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
