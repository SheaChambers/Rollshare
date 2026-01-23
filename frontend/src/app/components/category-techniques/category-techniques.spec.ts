import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CategoryTechniques } from './category-techniques';

describe('CategoryTechniques', () => {
  let component: CategoryTechniques;
  let fixture: ComponentFixture<CategoryTechniques>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CategoryTechniques]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CategoryTechniques);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
