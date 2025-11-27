import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
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
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatAutocompleteModule } from '@angular/material/autocomplete';

import { ProgramsComponent } from './programs.component';
import { ProgramDialogComponent } from './program-dialog/program-dialog.component';
import { ParticipantDialogComponent } from './participant-dialog/participant-dialog.component';
import { ParticipantsManagementComponent } from './participants-management/participants-management.component';
import { PairingDialogComponent } from './pairing-dialog/pairing-dialog.component';
import { PairingsManagementComponent } from './pairings-management/pairings-management.component';
import { SessionDialogComponent } from './session-dialog/session-dialog.component';
import { SessionsManagementComponent } from './sessions-management/sessions-management.component';
import { ProgressDialogComponent } from './progress-dialog/progress-dialog.component';
import { ProgressManagementComponent } from './progress-management/progress-management.component';
import { SharedModule } from '../../shared/shared.module';

const routes: Routes = [
  { path: '', component: ProgramsComponent }
];

@NgModule({
  declarations: [
    ProgramsComponent,
    ProgramDialogComponent,
    ParticipantDialogComponent,
    ParticipantsManagementComponent,
    PairingDialogComponent,
    PairingsManagementComponent,
    SessionDialogComponent,
    SessionsManagementComponent,
    ProgressDialogComponent,
    ProgressManagementComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule.forChild(routes),
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatFormFieldModule,
    MatInputModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTooltipModule,
    MatSelectModule,
    MatCheckboxModule,
    MatSnackBarModule,
    MatChipsModule,
    MatProgressBarModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatAutocompleteModule,
    SharedModule
  ]
})
export class ProgramsModule { }

