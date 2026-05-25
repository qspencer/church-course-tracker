/**
 * Smoke test for AuditDetailsDialogComponent.
 * Pre-Angular-18→21-migration coverage. This is a dialog with no
 * service dependencies - just MAT_DIALOG_DATA + MatDialogRef.
 */
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

import { AuditDetailsDialogComponent } from './audit-details-dialog.component';

describe('AuditDetailsDialogComponent (smoke)', () => {
  let component: AuditDetailsDialogComponent;
  let fixture: ComponentFixture<AuditDetailsDialogComponent>;

  beforeEach(async () => {
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    // AuditDetailsDialogData is `{ log: AuditLog, userName?: string }` -
    // the constructor calls buildChangeEntries(this.log), so log.old_values
    // and log.new_values must be present (can be null/undefined; not the
    // outer data itself).
    const mockData = {
      log: {
        id: 1,
        action: 'update' as const,
        table_name: 'users',
        record_id: 42,
        changed_by: 1,
        changed_at: '2026-05-25T12:00:00Z',
        old_values: { foo: 'bar' },
        new_values: { foo: 'baz' },
      },
      userName: 'admin',
    };

    await TestBed.configureTestingModule({
      declarations: [AuditDetailsDialogComponent],
      imports: [BrowserAnimationsModule, MatDialogModule],
      schemas: [NO_ERRORS_SCHEMA],
      providers: [
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockData },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AuditDetailsDialogComponent);
    component = fixture.componentInstance;
  });

  it('should construct without throwing', () => {
    expect(component).toBeTruthy();
  });
});
