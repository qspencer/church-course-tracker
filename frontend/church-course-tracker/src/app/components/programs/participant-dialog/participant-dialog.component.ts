import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { forkJoin } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { Program, ProgramParticipant, ProgramParticipantCreate, ProgramParticipantUpdate, RoleDefinition } from '../../../models/program.model';
import { Person } from '../../../models';
import { LoggerService } from '../../../services/logger.service';

export interface ParticipantDialogData {
  participant: ProgramParticipant | null;
  program: Program;
  viewMode?: boolean;
}

@Component({
    selector: 'app-participant-dialog',
    templateUrl: './participant-dialog.component.html',
    styleUrls: ['./participant-dialog.component.scss'],
    standalone: false
})
export class ParticipantDialogComponent implements OnInit {
  participantForm: FormGroup;
  isEditing: boolean;
  viewMode = false;
  isLoading = false;
  isSubmitted = false; // Track if form has been submitted
  members: Person[] = [];
  program: Program;
  roleOptions: string[] = [];
  statusOptions = [
    { value: 'active', label: 'Active' },
    { value: 'paused', label: 'Paused' },
    { value: 'completed', label: 'Completed' },
    { value: 'ended', label: 'Ended' }
  ];

  constructor(
    private fb: FormBuilder,
    private programService: ProgramService,
    private memberService: MemberService,
    private snackBar: MatSnackBar,
    private logger: LoggerService,
    public dialogRef: MatDialogRef<ParticipantDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ParticipantDialogData
  ) {
    this.viewMode = !!data.viewMode;
    this.isEditing = !this.viewMode && !!data.participant;
    this.program = data.program;
    
    // Extract role names from program's role definitions
    if (this.program.role_definitions && this.program.role_definitions.length > 0) {
      this.roleOptions = this.program.role_definitions.map(role => role.name);
    } else {
      this.roleOptions = ['Mentor', 'Mentee']; // Default fallback
    }
    
    this.participantForm = this.fb.group({
      people_id: ['', [Validators.required]],
      role_name: ['', [Validators.required]],
      status: ['active', [Validators.required]],
      notes: [''],
      progress_percentage: [0, [Validators.min(0), Validators.max(100)]]
    });

    if (this.viewMode) {
      this.participantForm.disable();
    }
  }

  ngOnInit(): void {
    if (!this.viewMode) {
      this.loadMembers();

      if (this.isEditing && this.data.participant) {
        this.participantForm.patchValue({
          people_id: this.data.participant.people_id,
          role_name: this.data.participant.role_name,
          status: this.data.participant.status,
          notes: this.data.participant.notes || '',
          progress_percentage: this.data.participant.progress_percentage || 0
        });
      }
    } else if (this.data.participant) {
      // View mode - just populate for display
      this.participantForm.patchValue({
        people_id: this.data.participant.people_id,
        role_name: this.data.participant.role_name,
        status: this.data.participant.status,
        notes: this.data.participant.notes || '',
        progress_percentage: this.data.participant.progress_percentage || 0
      });
    }
  }

  loadMembers(): void {
    this.isLoading = true;
    this.memberService.getMembers()
      .pipe(finalize(() => this.isLoading = false))
      .subscribe({
        next: (members) => {
          this.members = members;
        },
        error: (error) => {
          this.logger.error('Error loading members', error, {
            component: 'ParticipantDialogComponent',
            action: 'loadMembers',
            programId: this.program.id
          });
          this.snackBar.open('Error loading members', 'Close', { duration: 5000 });
        }
      });
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;

    if (this.participantForm.invalid || this.viewMode || this.isLoading) {
      return;
    }

    this.isLoading = true;

    if (this.isEditing && this.data.participant) {
      const updateData: ProgramParticipantUpdate = {
        role_name: this.participantForm.value.role_name,
        status: this.participantForm.value.status,
        notes: this.participantForm.value.notes,
        progress_percentage: this.participantForm.value.progress_percentage
      };

      this.programService.updateProgramParticipant(this.data.participant.id, updateData)
        .pipe(finalize(() => this.isLoading = false))
        .subscribe({
          next: () => {
            this.snackBar.open('Participant updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            this.logger.error('Error updating participant', error, {
              component: 'ParticipantDialogComponent',
              action: 'onSubmit-update',
              participantId: this.data.participant?.id,
              programId: this.program.id
            });
            const errorMsg = error?.error?.detail || 'Error updating participant';
            this.snackBar.open(errorMsg, 'Close', { duration: 5000 });
          }
        });
    } else {
      const createData: ProgramParticipantCreate = {
        program_id: this.program.id,
        people_id: this.participantForm.value.people_id,
        role_name: this.participantForm.value.role_name,
        status: this.participantForm.value.status,
        notes: this.participantForm.value.notes,
        progress_percentage: this.participantForm.value.progress_percentage
      };

      this.programService.addProgramParticipant(this.program.id, createData)
        .pipe(finalize(() => this.isLoading = false))
        .subscribe({
          next: () => {
            this.snackBar.open('Participant added successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            this.logger.error('Error adding participant', error, {
              component: 'ParticipantDialogComponent',
              action: 'onSubmit-create',
              programId: this.program.id,
              peopleId: createData.people_id
            });
            const errorMsg = error?.error?.detail || 'Error adding participant';
            this.snackBar.open(errorMsg, 'Close', { duration: 5000 });
          }
        });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  getMemberName(peopleId: number): string {
    const member = this.members.find(m => m.id === peopleId);
    if (member) {
      return `${member.first_name} ${member.last_name}`;
    }
    return 'Unknown';
  }

  getRoleColor(roleName: string): string {
    // Check if it's a primary role
    const roleDef = this.program.role_definitions?.find(r => r.name === roleName);
    if (roleDef?.is_primary) {
      return 'primary';
    }
    return 'accent';
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'active':
        return 'primary';
      case 'paused':
        return 'warn';
      case 'completed':
        return 'accent';
      case 'ended':
        return '';
      default:
        return '';
    }
  }

  shouldShowError(fieldName: string): boolean {
    const field = this.participantForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}

