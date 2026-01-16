import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { LoggerService } from '../../../services/logger.service';
import { Program, ProgramPairing, ProgramPairingCreate, ProgramPairingUpdate, ProgramParticipant } from '../../../models/program.model';
import { Person } from '../../../models';

export interface PairingDialogData {
  pairing: ProgramPairing | null;
  program: Program;
  participants: ProgramParticipant[];
  viewMode?: boolean;
}

@Component({
  selector: 'app-pairing-dialog',
  templateUrl: './pairing-dialog.component.html',
  styleUrls: ['./pairing-dialog.component.scss']
})
export class PairingDialogComponent implements OnInit {
  pairingForm: FormGroup;
  isEditing: boolean;
  viewMode = false;
  isLoading = false;
  isSubmitted = false; // Track if form has been submitted
  program: Program;
  participants: ProgramParticipant[] = [];
  members: Person[] = [];
  primaryParticipants: ProgramParticipant[] = [];
  secondaryParticipants: ProgramParticipant[] = [];
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
    public dialogRef: MatDialogRef<PairingDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: PairingDialogData,
    private logger: LoggerService
  ) {
    this.viewMode = !!data.viewMode;
    this.isEditing = !this.viewMode && !!data.pairing;
    this.program = data.program;
    this.participants = data.participants || [];
    
    // Filter participants by role (primary vs secondary)
    this.updateParticipantLists();
    
    this.pairingForm = this.fb.group({
      primary_participant_id: ['', [Validators.required]],
      secondary_participant_id: ['', [Validators.required]],
      status: ['active', [Validators.required]],
      notes: ['']
    });

    if (this.viewMode) {
      this.pairingForm.disable();
    }
  }

  ngOnInit(): void {
    if (!this.viewMode) {
      if (this.isEditing && this.data.pairing) {
        this.pairingForm.patchValue({
          primary_participant_id: this.data.pairing.primary_participant_id,
          secondary_participant_id: this.data.pairing.secondary_participant_id,
          status: this.data.pairing.status,
          notes: this.data.pairing.notes || ''
        });
      }
    } else if (this.data.pairing) {
      // View mode - just populate for display
      this.pairingForm.patchValue({
        primary_participant_id: this.data.pairing.primary_participant_id,
        secondary_participant_id: this.data.pairing.secondary_participant_id,
        status: this.data.pairing.status,
        notes: this.data.pairing.notes || ''
      });
    }

    // Watch for primary participant changes to update secondary list
    this.pairingForm.get('primary_participant_id')?.valueChanges.subscribe(() => {
      this.updateSecondaryParticipants();
    });

    // Load members for display
    this.loadMembers();
  }

  loadMembers(): void {
    this.memberService.getMembers().subscribe({
      next: (members) => {
        this.members = members;
      },
      error: (error) => {
        this.logger.error('Error loading members', error, { component: 'PairingDialogComponent', action: 'loadMembers' });
      }
    });
  }

  updateParticipantLists(): void {
    // Get role definitions to determine primary vs secondary
    const roleDefinitions = this.program.role_definitions || [];
    const primaryRoleNames = roleDefinitions
      .filter(r => r.is_primary)
      .map(r => r.name);
    const secondaryRoleNames = roleDefinitions
      .filter(r => !r.is_primary)
      .map(r => r.name);

    this.primaryParticipants = this.participants.filter(p => 
      primaryRoleNames.includes(p.role_name) && p.status === 'active'
    );
    this.secondaryParticipants = this.participants.filter(p => 
      secondaryRoleNames.includes(p.role_name) && p.status === 'active'
    );
  }

  updateSecondaryParticipants(): void {
    // If a primary participant is selected, we might want to filter secondary participants
    // For now, we'll show all secondary participants
    // This could be enhanced to show only available secondary participants
    this.updateParticipantLists();
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;
    
    if (this.pairingForm.invalid || this.viewMode || this.isLoading) {
      return;
    }

    // Validate that primary and secondary are different
    if (this.pairingForm.value.primary_participant_id === this.pairingForm.value.secondary_participant_id) {
      this.snackBar.open('Primary and secondary participants must be different', 'Close', { duration: 3000 });
      return;
    }

    this.isLoading = true;

    if (this.isEditing && this.data.pairing) {
      const updateData: ProgramPairingUpdate = {
        status: this.pairingForm.value.status,
        notes: this.pairingForm.value.notes
      };

      this.programService.updateProgramPairing(this.data.pairing.id, updateData).subscribe({
        next: () => {
          this.snackBar.open('Pairing updated successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.logger.error('Error updating pairing', error, { component: 'PairingDialogComponent', action: 'updatePairing', pairingId: this.data.pairing?.id, programId: this.program.id });
          const errorMsg = error?.error?.detail || 'Error updating pairing';
          this.snackBar.open(errorMsg, 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
    } else {
      const createData: ProgramPairingCreate = {
        program_id: this.program.id,
        primary_participant_id: this.pairingForm.value.primary_participant_id,
        secondary_participant_id: this.pairingForm.value.secondary_participant_id,
        status: this.pairingForm.value.status,
        notes: this.pairingForm.value.notes
      };

      this.programService.createProgramPairing(this.program.id, createData).subscribe({
        next: () => {
          this.snackBar.open('Pairing created successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.logger.error('Error creating pairing', error, { component: 'PairingDialogComponent', action: 'createPairing', programId: this.program.id });
          const errorMsg = error?.error?.detail || 'Error creating pairing';
          this.snackBar.open(errorMsg, 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  getParticipantName(participantId: number): string {
    const participant = this.participants.find(p => p.id === participantId);
    if (participant) {
      const member = this.members.find(m => m.id === participant.people_id);
      if (member) {
        return `${member.first_name} ${member.last_name}`;
      }
      return `Participant #${participant.id}`;
    }
    return 'Unknown';
  }

  getParticipantDisplay(participant: ProgramParticipant): string {
    const member = this.members.find(m => m.id === participant.people_id);
    if (member) {
      return `${member.first_name} ${member.last_name} (${participant.role_name})`;
    }
    return `${participant.role_name} #${participant.id}`;
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
    const field = this.pairingForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}

