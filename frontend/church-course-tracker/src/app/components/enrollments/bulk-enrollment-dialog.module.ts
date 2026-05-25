import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatRadioModule } from '@angular/material/radio';
import { MatButtonToggleModule } from '@angular/material/button-toggle';

import { BulkEnrollmentDialogComponent } from './bulk-enrollment-dialog/bulk-enrollment-dialog.component';

/**
 * Standalone module for BulkEnrollmentDialogComponent
 * This module does NOT include routing, so it can be safely imported
 * by other modules without causing route conflicts.
 */
@NgModule({
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatFormFieldModule,
        MatInputModule,
        MatSelectModule,
        MatDialogModule,
        MatProgressSpinnerModule,
        MatProgressBarModule,
        MatChipsModule,
        MatTooltipModule,
        MatCheckboxModule,
        MatRadioModule,
        MatButtonToggleModule,
        BulkEnrollmentDialogComponent
    ],
    exports: [
        BulkEnrollmentDialogComponent
    ]
})
export class BulkEnrollmentDialogModule { }

