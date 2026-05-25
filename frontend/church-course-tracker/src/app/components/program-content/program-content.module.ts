import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

// Angular Material Modules
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';

// Components
import { ProgramContentComponent } from './program-content.component';
import { ContentDialogComponent } from './content-dialog/content-dialog.component';
import { ModuleDialogComponent } from './module-dialog/module-dialog.component';

import { ProgramContentRoutingModule } from './program-content-routing.module';

@NgModule({
    imports: [
    CommonModule,
    ReactiveFormsModule,
    ProgramContentRoutingModule,
    // Angular Material
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatSnackBarModule,
    MatDialogModule,
    ProgramContentComponent,
    ContentDialogComponent,
    ModuleDialogComponent
],
    exports: [
        ProgramContentComponent
    ]
})
export class ProgramContentModule { }

