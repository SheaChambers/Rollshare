import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewTechnique } from './new-technique';

describe('NewTechnique', () => {
  let component: NewTechnique;
  let fixture: ComponentFixture<NewTechnique>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewTechnique]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewTechnique);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
