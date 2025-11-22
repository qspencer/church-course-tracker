import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BulkEnrollmentDialogComponent } from './bulk-enrollment-dialog.component';

describe('BulkEnrollmentDialogComponent', () => {
  let component: BulkEnrollmentDialogComponent;
  let fixture: ComponentFixture<BulkEnrollmentDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BulkEnrollmentDialogComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BulkEnrollmentDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
