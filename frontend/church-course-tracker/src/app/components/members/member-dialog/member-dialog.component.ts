import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MemberService } from '../../../services/member.service';
import { Person } from '../../../models';

export interface MemberDialogData {
  member: Person | null;
  viewMode?: boolean;
}

@Component({
  selector: 'app-member-dialog',
  templateUrl: './member-dialog.component.html',
  styleUrls: ['./member-dialog.component.scss']
})
export class MemberDialogComponent implements OnInit {
  memberForm: FormGroup;
  isEditing: boolean;
  viewMode: boolean;
  isLoading = false;
  isSubmitted = false; // Track if form has been submitted
  member: Person | null = null;

         constructor(
           private fb: FormBuilder,
           private memberService: MemberService,
           private snackBar: MatSnackBar,
           public dialogRef: MatDialogRef<MemberDialogComponent>,
           @Inject(MAT_DIALOG_DATA) public data: MemberDialogData
         ) {
           this.viewMode = data.viewMode || false;
           this.isEditing = !!data.member && !this.viewMode;
           this.member = data.member || null;
           
           this.memberForm = this.fb.group({
             first_name: ['', [Validators.required, Validators.minLength(2)]],
             last_name: ['', [Validators.required, Validators.minLength(2)]],
             email: ['', [Validators.email]],
             phone: [''],
             planning_center_id: ['']
           });
         }

         ngOnInit(): void {
           if (this.data.member) {
             if (this.viewMode) {
               // In view mode, just store the member data
               this.member = this.data.member;
             } else {
               // In edit/create mode, populate the form
               this.memberForm.patchValue({
                 first_name: this.data.member.first_name,
                 last_name: this.data.member.last_name,
                 email: this.data.member.email,
                 phone: this.data.member.phone,
                 planning_center_id: this.data.member.planning_center_id
               });
             }
           }
         }

  formatDate(date: string | null | undefined): string {
    if (!date) return 'N/A';
    try {
      const dateObj = new Date(date);
      if (isNaN(dateObj.getTime())) return 'N/A';
      return dateObj.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (e) {
      return 'N/A';
    }
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;
    
    if (this.memberForm.valid) {
      this.isLoading = true;
      const formValue = { ...this.memberForm.value };
      
      // Remove planning_center_id if it's empty (optional field)
      if (!formValue.planning_center_id || formValue.planning_center_id.trim() === '') {
        delete formValue.planning_center_id;
      }

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

  shouldShowError(fieldName: string): boolean {
    const field = this.memberForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}
