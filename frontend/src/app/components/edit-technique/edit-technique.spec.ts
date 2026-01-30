import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditTechnique } from './edit-technique';

describe('EditTechnique', () => {
  let component: EditTechnique;
  let fixture: ComponentFixture<EditTechnique>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditTechnique]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditTechnique);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
