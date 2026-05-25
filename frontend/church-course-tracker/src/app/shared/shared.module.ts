import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { ConfirmDialogComponent } from './confirm-dialog/confirm-dialog.component';
// Import BulkEnrollmentDialogModule (no routing) instead of EnrollmentsModule (has routing)
// This avoids route conflicts
import { BulkEnrollmentDialogModule } from '../components/enrollments/bulk-enrollment-dialog.module';

@NgModule({
    imports: [
        CommonModule,
        MatDialogModule,
        MatButtonModule,
        BulkEnrollmentDialogModule,
        ConfirmDialogComponent
    ],
    exports: [
        ConfirmDialogComponent,
        BulkEnrollmentDialogModule // Re-export so modules importing SharedModule can use BulkEnrollmentDialogComponent
    ]
})
export class SharedModule { }

