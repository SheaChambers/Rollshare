import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Techniques } from './techniques';

describe('Techniques', () => {
  let component: Techniques;
  let fixture: ComponentFixture<Techniques>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Techniques]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Techniques);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
