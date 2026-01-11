import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface ConfirmWithOptionDialogData {
  title: string;
  message: string;
  optionLabel?: string;
  optionChecked?: boolean;
  confirmText?: string;
  cancelText?: string;
}

@Component({
  selector: 'app-confirm-with-option-dialog',
  templateUrl: './confirm-with-option-dialog.component.html',
  styleUrls: ['./confirm-with-option-dialog.component.scss']
})
export class ConfirmWithOptionDialogComponent {
  optionChecked: boolean;

  constructor(
    public dialogRef: MatDialogRef<ConfirmWithOptionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmWithOptionDialogData
  ) {
    // Set default texts if not provided
    this.data.confirmText = this.data.confirmText || 'Confirm';
    this.data.cancelText = this.data.cancelText || 'Cancel';
    this.optionChecked = this.data.optionChecked || false;
  }

  onCancel(): void {
    this.dialogRef.close({ confirmed: false, optionChecked: false });
  }

  onConfirm(): void {
    this.dialogRef.close({ confirmed: true, optionChecked: this.optionChecked });
  }
}




