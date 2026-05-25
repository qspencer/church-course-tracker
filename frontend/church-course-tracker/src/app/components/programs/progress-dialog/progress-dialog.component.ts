import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../../services/program.service';
import { LoggerService } from '../../../services/logger.service';
import { Program, ProgramProgress, ProgramProgressCreate, ProgramProgressUpdate, ProgramParticipant, ProgramSession } from '../../../models/program.model';

export interface ProgressDialogData {
  progress: ProgramProgress | null;
  program: Program;
  participant: ProgramParticipant;
  sessions?: ProgramSession[];
  viewMode?: boolean;
}

@Component({
    selector: 'app-progress-dialog',
    templateUrl: './progress-dialog.component.html',
    styleUrls: ['./progress-dialog.component.scss'],
    standalone: false
})
export class ProgressDialogComponent implements OnInit {
  progressForm: FormGroup;
  isEditing: boolean;
  viewMode = false;
  isLoading = false;
  isSubmitted = false; // Track if form has been submitted
  program: Program;
  participant: ProgramParticipant;
  sessions: ProgramSession[] = [];
  progressTypeOptions = [
    { value: 'content_completion', label: 'Content Completion' },
    { value: 'session_completion', label: 'Session Completion' },
    { value: 'milestone', label: 'Milestone' }
  ];

  constructor(
    private fb: FormBuilder,
    private programService: ProgramService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<ProgressDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ProgressDialogData,
    private logger: LoggerService
  ) {
    this.viewMode = !!data.viewMode;
    this.isEditing = !this.viewMode && !!data.progress;
    this.program = data.program;
    this.participant = data.participant;
    this.sessions = data.sessions || [];
    
    this.progressForm = this.fb.group({
      progress_type: ['content_completion', [Validators.required]],
      content_id: [null],
      completion_date: [new Date()],
      completion_percentage: [100, [Validators.min(0), Validators.max(100)]],
      session_id: [null],
      milestone_name: [''],
      milestone_description: [''],
      notes: ['']
    });

    if (this.viewMode) {
      this.progressForm.disable();
    }

    // Watch for progress type changes to show/hide relevant fields
    this.progressForm.get('progress_type')?.valueChanges.subscribe(type => {
      this.updateFormValidation(type);
    });
  }

  ngOnInit(): void {
    if (!this.viewMode) {
      if (this.isEditing && this.data.progress) {
        const progress = this.data.progress;
        const completionDate = progress.completion_date 
          ? new Date(progress.completion_date) 
          : new Date();
        
        this.progressForm.patchValue({
          progress_type: progress.progress_type,
          content_id: progress.content_id || null,
          completion_date: completionDate,
          completion_percentage: progress.completion_percentage || 100,
          session_id: progress.session_id || null,
          milestone_name: progress.milestone_name || '',
          milestone_description: progress.milestone_description || '',
          notes: progress.notes || ''
        });
      } else {
        // Default to today's date
        this.progressForm.patchValue({
          completion_date: new Date()
        });
      }
    } else if (this.data.progress) {
      const progress = this.data.progress;
      const completionDate = progress.completion_date 
        ? new Date(progress.completion_date) 
        : new Date();
      
      this.progressForm.patchValue({
        progress_type: progress.progress_type,
        content_id: progress.content_id || null,
        completion_date: completionDate,
        completion_percentage: progress.completion_percentage || 100,
        session_id: progress.session_id || null,
        milestone_name: progress.milestone_name || '',
        milestone_description: progress.milestone_description || '',
        notes: progress.notes || ''
      });
    }

    // Set initial validation
    const progressType = this.progressForm.get('progress_type')?.value || 'content_completion';
    this.updateFormValidation(progressType);
  }

  updateFormValidation(progressType: string): void {
    const contentIdControl = this.progressForm.get('content_id');
    const sessionIdControl = this.progressForm.get('session_id');
    const milestoneNameControl = this.progressForm.get('milestone_name');

    // Reset validators
    contentIdControl?.clearValidators();
    sessionIdControl?.clearValidators();
    milestoneNameControl?.clearValidators();

    // Add validators based on type
    if (progressType === 'content_completion') {
      contentIdControl?.setValidators([Validators.required]);
    } else if (progressType === 'session_completion') {
      sessionIdControl?.setValidators([Validators.required]);
    } else if (progressType === 'milestone') {
      milestoneNameControl?.setValidators([Validators.required]);
    }

    // Update validity
    contentIdControl?.updateValueAndValidity();
    sessionIdControl?.updateValueAndValidity();
    milestoneNameControl?.updateValueAndValidity();
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;
    
    if (this.progressForm.invalid || this.viewMode || this.isLoading) {
      return;
    }

    this.isLoading = true;

    const formValue = this.progressForm.value;
    const completionDate = formValue.completion_date instanceof Date 
      ? formValue.completion_date.toISOString() 
      : formValue.completion_date;

    if (this.isEditing && this.data.progress) {
      const updateData: ProgramProgressUpdate = {
        progress_type: formValue.progress_type,
        content_id: formValue.content_id || null,
        completion_date: completionDate,
        completion_percentage: formValue.completion_percentage || null,
        session_id: formValue.session_id || null,
        milestone_name: formValue.milestone_name || null,
        milestone_description: formValue.milestone_description || null,
        notes: formValue.notes || null
      };

      this.programService.updateProgramProgress(this.data.progress.id, updateData).subscribe({
        next: () => {
          this.snackBar.open('Progress updated successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.logger.error('Error updating progress', error, { component: 'ProgressDialogComponent', action: 'updateProgress', progressId: this.data.progress?.id, programId: this.program.id });
          const errorMsg = error?.error?.detail || 'Error updating progress';
          this.snackBar.open(errorMsg, 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
    } else {
      const createData: ProgramProgressCreate = {
        program_id: this.program.id,
        participant_id: this.participant.id,
        progress_type: formValue.progress_type,
        content_id: formValue.content_id || null,
        completion_date: completionDate,
        completion_percentage: formValue.completion_percentage || null,
        session_id: formValue.session_id || null,
        milestone_name: formValue.milestone_name || null,
        milestone_description: formValue.milestone_description || null,
        notes: formValue.notes || null
      };

      this.programService.createProgramProgress(this.program.id, createData).subscribe({
        next: () => {
          this.snackBar.open('Progress recorded successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.logger.error('Error creating progress', error, { component: 'ProgressDialogComponent', action: 'createProgress', programId: this.program.id, participantId: this.participant.id });
          const errorMsg = error?.error?.detail || 'Error creating progress';
          this.snackBar.open(errorMsg, 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  getSessionDisplay(sessionId: number | undefined): string {
    if (!sessionId) return 'N/A';
    const session = this.sessions.find(s => s.id === sessionId);
    if (session) {
      const date = new Date(session.session_date);
      return date.toLocaleString();
    }
    return `Session #${sessionId}`;
  }

  shouldShowError(fieldName: string): boolean {
    const field = this.progressForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}

