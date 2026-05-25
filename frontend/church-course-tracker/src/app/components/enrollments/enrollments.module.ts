import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
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

import { EnrollmentsComponent } from './enrollments.component';
import { EnrollmentDialogComponent } from './enrollment-dialog/enrollment-dialog.component';
import { BulkEnrollmentDialogModule } from './bulk-enrollment-dialog.module';

const routes: Routes = [
  { path: '', component: EnrollmentsComponent }
];

@NgModule({
    imports: [
        CommonModule,
        ReactiveFormsModule,
        RouterModule.forChild(routes),
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatTableModule,
        MatPaginatorModule,
        MatSortModule,
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
        BulkEnrollmentDialogModule,
        EnrollmentsComponent,
        EnrollmentDialogComponent
        // BulkEnrollmentDialogComponent is now in BulkEnrollmentDialogModule
    ],
    exports: [
        BulkEnrollmentDialogModule
    ]
})
export class EnrollmentsModule { }
