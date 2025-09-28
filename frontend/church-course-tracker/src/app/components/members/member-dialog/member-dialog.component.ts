import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MemberService } from '../../../services/member.service';
import { Person } from '../../../models';

export interface MemberDialogData {
  member: Person | null;
}

@Component({
  selector: 'app-member-dialog',
  templateUrl: './member-dialog.component.html',
  styleUrls: ['./member-dialog.component.scss']
})
export class MemberDialogComponent implements OnInit {
  memberForm: FormGroup;
  isEditing: boolean;
  isLoading = false;

         constructor(
           private fb: FormBuilder,
           private memberService: MemberService,
           private snackBar: MatSnackBar,
           public dialogRef: MatDialogRef<MemberDialogComponent>,
           @Inject(MAT_DIALOG_DATA) public data: MemberDialogData
         ) {
           this.isEditing = !!data.member;
           
           this.memberForm = this.fb.group({
             first_name: ['', [Validators.required, Validators.minLength(2)]],
             last_name: ['', [Validators.required, Validators.minLength(2)]],
             email: ['', [Validators.email]],
             phone: [''],
             planning_center_id: ['']
           });
         }

         ngOnInit(): void {
           // Initialize form values if editing
           if (this.isEditing && this.data.member) {
             this.memberForm.patchValue({
               first_name: this.data.member.first_name,
               last_name: this.data.member.last_name,
               email: this.data.member.email,
               phone: this.data.member.phone,
               planning_center_id: this.data.member.planning_center_id
             });
           }
         }

  onSubmit(): void {
    if (this.memberForm.valid) {
      this.isLoading = true;
      const formValue = this.memberForm.value;

      if (this.isEditing && this.data.member) {
        // Update existing member
        this.memberService.updateMember(this.data.member.id, formValue).subscribe({
          next: (member) => {
            this.isLoading = false;
            this.snackBar.open('Member updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(member);
          },
          error: (error) => {
            this.isLoading = false;
            console.error('Error updating member:', error);
          }
        });
      } else {
        // Create new member
        this.memberService.createMember(formValue).subscribe({
          next: (member) => {
            this.isLoading = false;
            this.snackBar.open('Member created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(member);
          },
          error: (error) => {
            this.isLoading = false;
            console.error('Error creating member:', error);
          }
        });
      }
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  getErrorMessage(fieldName: string): string {
    const field = this.memberForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName.replace('_', ' ')} is required`;
    }
    if (field?.hasError('minlength')) {
      return `${fieldName.replace('_', ' ')} must be at least ${field.errors?.['minlength'].requiredLength} characters`;
    }
    if (field?.hasError('email')) {
      return 'Please enter a valid email address';
    }
    return '';
  }
}
