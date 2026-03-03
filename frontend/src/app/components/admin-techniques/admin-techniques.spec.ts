import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminTechniques } from './admin-techniques';

describe('AdminTechniques', () => {
  let component: AdminTechniques;
  let fixture: ComponentFixture<AdminTechniques>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminTechniques]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminTechniques);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
