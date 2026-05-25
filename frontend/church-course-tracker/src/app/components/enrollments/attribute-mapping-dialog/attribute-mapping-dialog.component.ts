import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { PlanningCenterService } from '../../../services/planning-center.service';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { LoggerService } from '../../../services/logger.service';

export interface AttributeMappingMatch {
  pc_attribute: string;
  local_attribute: string | null;
  similarity_score: number;
  is_predefined: boolean;
  match_status: 'matched' | 'unmatched';
}

export interface AttributeMappingReview {
  source_type: 'event' | 'list';
  source_id: string;
  target_type: 'course' | 'program';
  target_id: number;
  pc_attributes: Record<string, unknown>;
  local_attributes: string[];
  matches: AttributeMappingMatch[];
}

export interface AttributeMappingDecision {
  pc_attribute: string;
  action: 'accept' | 'rematch' | 'custom' | 'ignore';
  local_attribute?: string | null;
  custom_attribute_name?: string | null;
}

export interface AttributeMappingDialogData {
  source_type: 'event' | 'list';
  source_id: string;
  target_type: 'course' | 'program';
  target_id: number;
}

@Component({
    selector: 'app-attribute-mapping-dialog',
    templateUrl: './attribute-mapping-dialog.component.html',
    styleUrls: ['./attribute-mapping-dialog.component.scss'],
    standalone: false
})
export class AttributeMappingDialogComponent implements OnInit {
  review: AttributeMappingReview | null = null;
  isLoading = false;
  isSaving = false;
  
  // Form for each attribute decision
  attributeForms: { [key: string]: FormGroup } = {};
  
  // Available actions for each attribute
  actions = [
    { value: 'accept', label: 'Accept Match', icon: 'check_circle', availableFor: ['matched'] as ('matched' | 'unmatched')[] },
    { value: 'rematch', label: 'Match to Different Attribute', icon: 'swap_horiz', availableFor: ['matched', 'unmatched'] as ('matched' | 'unmatched')[] },
    { value: 'custom', label: 'Save as Custom Attribute', icon: 'add_circle', availableFor: ['matched', 'unmatched'] as ('matched' | 'unmatched')[] },
    { value: 'ignore', label: 'Ignore (Don\'t Import)', icon: 'block', availableFor: ['matched', 'unmatched'] as ('matched' | 'unmatched')[] }
  ];

  constructor(
    private dialogRef: MatDialogRef<AttributeMappingDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: AttributeMappingDialogData,
    private http: HttpClient,
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private logger: LoggerService
  ) {}

  ngOnInit(): void {
    this.loadAttributeMappings();
  }

  loadAttributeMappings(): void {
    this.isLoading = true;
    const params = new HttpParams()
      .set('source_type', this.data.source_type)
      .set('source_id', this.data.source_id)
      .set('target_type', this.data.target_type)
      .set('target_id', this.data.target_id.toString());

    this.http.get<AttributeMappingReview>(`${environment.apiUrl}/planning-center/attribute-mappings`, { params })
      .subscribe({
        next: (review) => {
          this.review = review;
          this.initializeForms();
          this.isLoading = false;
        },
        error: (error) => {
          this.logger.error('Error loading attribute mappings', error, { component: 'AttributeMappingDialogComponent', action: 'loadAttributeMappings', sourceType: this.data.source_type, sourceId: this.data.source_id });
          this.snackBar.open('Failed to load attribute mappings', 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
  }

  initializeForms(): void {
    if (!this.review) return;

    this.review.matches.forEach(match => {
      // Determine default action based on match status
      let defaultAction: string;
      if (match.match_status === 'matched') {
        defaultAction = 'accept';
      } else {
        defaultAction = 'ignore'; // Default to ignore for unmatched
      }

      const form = this.fb.group({
        action: [defaultAction, Validators.required],
        local_attribute: [match.local_attribute || ''],
        custom_attribute_name: ['']
      });

      // Add validators based on action
      form.get('action')?.valueChanges.subscribe(action => {
        if (action === 'accept' || action === 'rematch') {
          form.get('local_attribute')?.setValidators([Validators.required]);
          form.get('custom_attribute_name')?.clearValidators();
        } else if (action === 'custom') {
          form.get('custom_attribute_name')?.setValidators([Validators.required]);
          form.get('local_attribute')?.clearValidators();
        } else {
          form.get('local_attribute')?.clearValidators();
          form.get('custom_attribute_name')?.clearValidators();
        }
        form.get('local_attribute')?.updateValueAndValidity();
        form.get('custom_attribute_name')?.updateValueAndValidity();
      });

      this.attributeForms[match.pc_attribute] = form;
    });
  }

  getAvailableActions(match: AttributeMappingMatch): typeof this.actions {
    return this.actions.filter(action => 
      action.availableFor.includes(match.match_status)
    );
  }

  getLocalAttributeOptions(): string[] {
    return this.review?.local_attributes || [];
  }

  getAttributeValue(pcAttribute: string): unknown {
    return this.review?.pc_attributes[pcAttribute];
  }

  getAttributeType(value: unknown): string {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'boolean') return 'boolean';
    if (typeof value === 'number') return 'number';
    if (value instanceof Date || (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}/.test(value))) return 'date';
    return 'string';
  }

  formatAttributeValue(value: unknown): string {
    if (value === null || value === undefined) return '(empty)';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (value instanceof Date) return value.toLocaleDateString();
    if (typeof value === 'string' && value.length > 50) return value.substring(0, 50) + '...';
    return String(value);
  }

  onSubmit(): void {
    if (!this.review) return;

    // Validate all forms
    const invalidForms = Object.entries(this.attributeForms).filter(([_, form]) => form.invalid);
    if (invalidForms.length > 0) {
      this.snackBar.open('Please complete all attribute mappings', 'Close', { duration: 3000 });
      return;
    }

    // Build decisions
    const decisions: AttributeMappingDecision[] = Object.entries(this.attributeForms).map(([pcAttribute, form]) => {
      const formValue = form.value;
      return {
        pc_attribute: pcAttribute,
        action: formValue.action,
        local_attribute: formValue.action === 'accept' || formValue.action === 'rematch' ? formValue.local_attribute : null,
        custom_attribute_name: formValue.action === 'custom' ? formValue.custom_attribute_name : null
      };
    });

    const mappingDecisions = {
      source_type: this.review.source_type,
      source_id: this.review.source_id,
      target_type: this.review.target_type,
      target_id: this.review.target_id,
      decisions: decisions
    };

    this.isSaving = true;
    this.http.post(`${environment.apiUrl}/planning-center/attribute-mappings/decisions`, mappingDecisions)
      .subscribe({
        next: (result) => {
          this.snackBar.open('Attribute mappings saved successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(mappingDecisions);
          this.isSaving = false;
        },
        error: (error) => {
          this.logger.error('Error saving attribute mappings', error, { component: 'AttributeMappingDialogComponent', action: 'saveAttributeMappings', sourceType: this.data.source_type, sourceId: this.data.source_id });
          this.snackBar.open('Failed to save attribute mappings', 'Close', { duration: 3000 });
          this.isSaving = false;
        }
      });
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }

  getMatchStatusIcon(match: AttributeMappingMatch): string {
    if (match.match_status === 'matched') {
      return match.is_predefined ? 'verified' : 'auto_awesome';
    }
    return 'help_outline';
  }

  getMatchStatusColor(match: AttributeMappingMatch): string {
    if (match.match_status === 'matched') {
      return match.is_predefined ? 'primary' : 'accent';
    }
    return 'warn';
  }
}

