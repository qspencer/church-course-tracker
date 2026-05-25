import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

// Angular Material
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';

import { AttributeMappingDialogComponent, AttributeMappingDialogData, AttributeMappingReview, AttributeMappingMatch } from './attribute-mapping-dialog.component';
import { environment } from '../../../../environments/environment';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('AttributeMappingDialogComponent', () => {
  let component: AttributeMappingDialogComponent;
  let fixture: ComponentFixture<AttributeMappingDialogComponent>;
  let httpMock: HttpTestingController;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<AttributeMappingDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockDialogData: AttributeMappingDialogData = {
    source_type: 'event',
    source_id: '123',
    target_type: 'course',
    target_id: 1
  };

  const mockMatch: AttributeMappingMatch = {
    pc_attribute: 'first_name',
    local_attribute: 'first_name',
    similarity_score: 0.95,
    is_predefined: true,
    match_status: 'matched'
  };

  const mockReview: AttributeMappingReview = {
    source_type: 'event',
    source_id: '123',
    target_type: 'course',
    target_id: 1,
    pc_attributes: {
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com'
    },
    local_attributes: ['first_name', 'last_name', 'email', 'phone'],
    matches: [
      mockMatch,
      {
        pc_attribute: 'phone',
        local_attribute: null,
        similarity_score: 0.3,
        is_predefined: false,
        match_status: 'unmatched'
      }
    ]
  };

  beforeEach(async () => {
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
    declarations: [AttributeMappingDialogComponent],
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        HttpClientTestingModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatCardModule
    ],
    providers: [
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

    fixture = TestBed.createComponent(AttributeMappingDialogComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<AttributeMappingDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Initialization', () => {
    it('should load attribute mappings on init', () => {
      fixture.detectChanges();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockReview);

      expect(component.review).toEqual(mockReview);
      expect(component.isLoading).toBe(false);
    });

    it('should initialize forms for each match', () => {
      fixture.detectChanges();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.flush(mockReview);

      expect(Object.keys(component.attributeForms).length).toBe(2);
      expect(component.attributeForms['first_name']).toBeDefined();
    });

    it('should set default action to accept for matched', () => {
      fixture.detectChanges();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.flush(mockReview);

      const matchedForm = component.attributeForms['first_name'];
      expect(matchedForm.get('action')?.value).toBe('accept');
    });

    it('should set default action to ignore for unmatched', () => {
      fixture.detectChanges();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.flush(mockReview);

      const unmatchedForm = component.attributeForms['phone'];
      expect(unmatchedForm.get('action')?.value).toBe('ignore');
    });

    it('should handle error loading mappings', () => {
      fixture.detectChanges();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.error(new ErrorEvent('Network error'));

      expect(component.isLoading).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Failed to load attribute mappings', 'Close', { duration: 3000 });
    });
  });

  describe('Form validation', () => {
    beforeEach(() => {
      fixture.detectChanges();
      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.flush(mockReview);
    });

    it('should require local_attribute for accept action', () => {
      const form = component.attributeForms['first_name'];
      form.patchValue({ action: 'accept', local_attribute: '' });
      form.get('local_attribute')?.markAsTouched();

      expect(form.get('local_attribute')?.hasError('required')).toBe(true);
    });

    it('should require local_attribute for rematch action', () => {
      const form = component.attributeForms['first_name'];
      form.patchValue({ action: 'rematch', local_attribute: '' });
      form.get('local_attribute')?.markAsTouched();

      expect(form.get('local_attribute')?.hasError('required')).toBe(true);
    });

    it('should require custom_attribute_name for custom action', () => {
      const form = component.attributeForms['phone'];
      form.patchValue({ action: 'custom', custom_attribute_name: '' });
      form.get('custom_attribute_name')?.markAsTouched();

      expect(form.get('custom_attribute_name')?.hasError('required')).toBe(true);
    });

    it('should clear validators for ignore action', () => {
      const form = component.attributeForms['phone'];
      form.patchValue({ action: 'ignore' });

      expect(form.get('local_attribute')?.hasError('required')).toBe(false);
      expect(form.get('custom_attribute_name')?.hasError('required')).toBe(false);
    });
  });

  describe('getAvailableActions', () => {
    beforeEach(() => {
      fixture.detectChanges();
      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.flush(mockReview);
    });

    it('should return all actions for matched status', () => {
      const actions = component.getAvailableActions(mockMatch);
      expect(actions.length).toBeGreaterThan(0);
    });

    it('should filter actions by match status', () => {
      const unmatchedMatch: AttributeMappingMatch = {
        pc_attribute: 'phone',
        local_attribute: null,
        similarity_score: 0.3,
        is_predefined: false,
        match_status: 'unmatched'
      };
      const actions = component.getAvailableActions(unmatchedMatch);
      expect(actions.length).toBeGreaterThan(0);
    });
  });

  describe('Helper methods', () => {
    beforeEach(() => {
      fixture.detectChanges();
      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.flush(mockReview);
    });

    it('should get local attribute options', () => {
      const options = component.getLocalAttributeOptions();
      expect(options).toEqual(mockReview.local_attributes);
    });

    it('should get attribute value', () => {
      const value = component.getAttributeValue('first_name');
      expect(value).toBe('John');
    });

    it('should get attribute type for string', () => {
      expect(component.getAttributeType('test')).toBe('string');
    });

    it('should get attribute type for number', () => {
      expect(component.getAttributeType(123)).toBe('number');
    });

    it('should get attribute type for boolean', () => {
      expect(component.getAttributeType(true)).toBe('boolean');
    });

    it('should get attribute type for date', () => {
      expect(component.getAttributeType('2023-01-15')).toBe('date');
    });

    it('should get attribute type for null', () => {
      expect(component.getAttributeType(null)).toBe('null');
    });

    it('should format attribute value for string', () => {
      expect(component.formatAttributeValue('test')).toBe('test');
    });

    it('should format attribute value for boolean', () => {
      expect(component.formatAttributeValue(true)).toBe('Yes');
      expect(component.formatAttributeValue(false)).toBe('No');
    });

    it('should format attribute value for null', () => {
      expect(component.formatAttributeValue(null)).toBe('(empty)');
    });

    it('should truncate long strings', () => {
      const longString = 'a'.repeat(100);
      const formatted = component.formatAttributeValue(longString);
      expect(formatted.length).toBeLessThanOrEqual(53); // 50 + '...'
      expect(formatted).toContain('...');
    });

    it('should get match status icon for matched predefined', () => {
      expect(component.getMatchStatusIcon(mockMatch)).toBe('verified');
    });

    it('should get match status icon for matched non-predefined', () => {
      const match = { ...mockMatch, is_predefined: false };
      expect(component.getMatchStatusIcon(match)).toBe('auto_awesome');
    });

    it('should get match status icon for unmatched', () => {
      const unmatchedMatch: AttributeMappingMatch = {
        pc_attribute: 'phone',
        local_attribute: null,
        similarity_score: 0.3,
        is_predefined: false,
        match_status: 'unmatched'
      };
      expect(component.getMatchStatusIcon(unmatchedMatch)).toBe('help_outline');
    });

    it('should get match status color for matched predefined', () => {
      expect(component.getMatchStatusColor(mockMatch)).toBe('primary');
    });

    it('should get match status color for matched non-predefined', () => {
      const match = { ...mockMatch, is_predefined: false };
      expect(component.getMatchStatusColor(match)).toBe('accent');
    });

    it('should get match status color for unmatched', () => {
      const unmatchedMatch: AttributeMappingMatch = {
        pc_attribute: 'phone',
        local_attribute: null,
        similarity_score: 0.3,
        is_predefined: false,
        match_status: 'unmatched'
      };
      expect(component.getMatchStatusColor(unmatchedMatch)).toBe('warn');
    });
  });

  describe('onSubmit', () => {
    beforeEach(() => {
      fixture.detectChanges();
      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings?source_type=event&source_id=123&target_type=course&target_id=1`);
      req.flush(mockReview);
    });

    it('should not submit if review is null', () => {
      component.review = null;
      component.onSubmit();

      // Verify no HTTP request was made
      httpMock.expectNone(`${environment.apiUrl}/planning-center/attribute-mappings/decisions`);
      expect(component.isSaving).toBe(false);
    });

    it('should not submit if forms are invalid', () => {
      const form = component.attributeForms['first_name'];
      form.patchValue({ action: 'accept', local_attribute: '' });
      form.get('local_attribute')?.markAsTouched();

      component.onSubmit();

      expect(snackBarSpy.open).toHaveBeenCalledWith('Please complete all attribute mappings', 'Close', { duration: 3000 });
    });

    it('should submit valid decisions', () => {
      component.onSubmit();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings/decisions`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toBeDefined();
      req.flush({ success: true });

      expect(snackBarSpy.open).toHaveBeenCalledWith('Attribute mappings saved successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalled();
    });

    it('should build decisions correctly for accept action', () => {
      const form = component.attributeForms['first_name'];
      form.patchValue({ action: 'accept', local_attribute: 'first_name' });

      component.onSubmit();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings/decisions`);
      const decisions = req.request.body.decisions;
      const acceptDecision = decisions.find((d: any) => d.pc_attribute === 'first_name');
      expect(acceptDecision.action).toBe('accept');
      expect(acceptDecision.local_attribute).toBe('first_name');
      req.flush({ success: true });
    });

    it('should build decisions correctly for custom action', () => {
      const form = component.attributeForms['phone'];
      form.patchValue({ action: 'custom', custom_attribute_name: 'custom_phone' });

      component.onSubmit();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings/decisions`);
      const decisions = req.request.body.decisions;
      const customDecision = decisions.find((d: any) => d.pc_attribute === 'phone');
      expect(customDecision.action).toBe('custom');
      expect(customDecision.custom_attribute_name).toBe('custom_phone');
      req.flush({ success: true });
    });

    it('should handle submit error', () => {
      component.onSubmit();

      const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/attribute-mappings/decisions`);
      req.error(new ErrorEvent('Network error'));

      expect(component.isSaving).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Failed to save attribute mappings', 'Close', { duration: 3000 });
    });
  });

  describe('onCancel', () => {
    it('should close dialog with null', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalledWith(null);
    });
  });
});
