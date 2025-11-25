import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../../services/program.service';
import { Program, ProgramSession, ProgramSessionCreate, ProgramSessionUpdate, ProgramPairing, ProgramParticipant } from '../../../models/program.model';

export interface SessionDialogData {
  session: ProgramSession | null;
  program: Program;
  pairings: ProgramPairing[];
  participants: ProgramParticipant[];
  viewMode?: boolean;
}

@Component({
  selector: 'app-session-dialog',
  templateUrl: './session-dialog.component.html',
  styleUrls: ['./session-dialog.component.scss']
})
export class SessionDialogComponent implements OnInit {
  sessionForm: FormGroup;
  isEditing: boolean;
  viewMode = false;
  isLoading = false;
  isSubmitted = false; // Track if form has been submitted
  program: Program;
  pairings: ProgramPairing[] = [];
  participants: ProgramParticipant[] = [];
  sessionTypeOptions = [
    { value: 'in_person', label: 'In Person' },
    { value: 'online', label: 'Online' },
    { value: 'phone', label: 'Phone' },
    { value: 'video_call', label: 'Video Call' },
    { value: 'hybrid', label: 'Hybrid' }
  ];

  constructor(
    private fb: FormBuilder,
    private programService: ProgramService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<SessionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SessionDialogData
  ) {
    this.viewMode = !!data.viewMode;
    this.isEditing = !this.viewMode && !!data.session;
    this.program = data.program;
    this.pairings = data.pairings || [];
    this.participants = data.participants || [];
    
    this.sessionForm = this.fb.group({
      pairing_id: [null],
      session_date: [new Date(), [Validators.required]],
      duration_minutes: [null],
      location: [''],
      session_type: ['in_person'],
      participant_ids: [[]],
      topics_covered: [''],
      notes: [''],
      content_completed: [[]],
      milestones_achieved: [[]]
    });

    if (this.viewMode) {
      this.sessionForm.disable();
    }
  }

  ngOnInit(): void {
    if (!this.viewMode) {
      if (this.isEditing && this.data.session) {
        const session = this.data.session;
        this.sessionForm.patchValue({
          pairing_id: session.pairing_id || null,
          session_date: new Date(session.session_date),
          duration_minutes: session.duration_minutes || null,
          location: session.location || '',
          session_type: session.session_type || 'in_person',
          participant_ids: session.participant_ids || [],
          topics_covered: session.topics_covered || '',
          notes: session.notes || '',
          content_completed: session.content_completed || [],
          milestones_achieved: session.milestones_achieved || []
        });
      } else {
        // Default to today's date
        this.sessionForm.patchValue({
          session_date: new Date()
        });
      }
    } else if (this.data.session) {
      const session = this.data.session;
      this.sessionForm.patchValue({
        pairing_id: session.pairing_id || null,
        session_date: new Date(session.session_date),
        duration_minutes: session.duration_minutes || null,
        location: session.location || '',
        session_type: session.session_type || 'in_person',
        participant_ids: session.participant_ids || [],
        topics_covered: session.topics_covered || '',
        notes: session.notes || '',
        content_completed: session.content_completed || [],
        milestones_achieved: session.milestones_achieved || []
      });
    }
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;
    
    if (this.sessionForm.invalid || this.viewMode || this.isLoading) {
      return;
    }

    this.isLoading = true;

    const formValue = this.sessionForm.value;
    const sessionDate = formValue.session_date instanceof Date 
      ? formValue.session_date.toISOString() 
      : formValue.session_date;

    if (this.isEditing && this.data.session) {
      const updateData: ProgramSessionUpdate = {
        session_date: sessionDate,
        duration_minutes: formValue.duration_minutes || null,
        location: formValue.location || null,
        session_type: formValue.session_type || null,
        participant_ids: formValue.participant_ids || [],
        topics_covered: formValue.topics_covered || null,
        notes: formValue.notes || null,
        content_completed: formValue.content_completed || [],
        milestones_achieved: formValue.milestones_achieved || []
      };

      this.programService.updateProgramSession(this.data.session.id, updateData).subscribe({
        next: () => {
          this.snackBar.open('Session updated successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          console.error('Error updating session:', error);
          const errorMsg = error?.error?.detail || 'Error updating session';
          this.snackBar.open(errorMsg, 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
    } else {
      const createData: ProgramSessionCreate = {
        program_id: this.program.id,
        pairing_id: formValue.pairing_id || null,
        session_date: sessionDate,
        duration_minutes: formValue.duration_minutes || null,
        location: formValue.location || null,
        session_type: formValue.session_type || null,
        participant_ids: formValue.participant_ids || [],
        topics_covered: formValue.topics_covered || null,
        notes: formValue.notes || null,
        content_completed: formValue.content_completed || [],
        milestones_achieved: formValue.milestones_achieved || []
      };

      this.programService.createProgramSession(this.program.id, createData).subscribe({
        next: () => {
          this.snackBar.open('Session logged successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          console.error('Error creating session:', error);
          const errorMsg = error?.error?.detail || 'Error creating session';
          this.snackBar.open(errorMsg, 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  getPairingDisplay(pairing: ProgramPairing): string {
    // This would need participant names - simplified for now
    return `Pairing #${pairing.id}`;
  }

  getParticipantDisplay(participant: ProgramParticipant): string {
    return `${participant.role_name} #${participant.id}`;
  }

  shouldShowError(fieldName: string): boolean {
    const field = this.sessionForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}

