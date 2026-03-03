import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminGyms } from './admin-gyms';

describe('AdminGyms', () => {
  let component: AdminGyms;
  let fixture: ComponentFixture<AdminGyms>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminGyms]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminGyms);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
