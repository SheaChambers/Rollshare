import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditGym } from './edit-gym';

describe('EditGym', () => {
  let component: EditGym;
  let fixture: ComponentFixture<EditGym>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditGym]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditGym);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
