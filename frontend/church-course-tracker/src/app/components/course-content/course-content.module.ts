import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

// Angular Material Modules
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatListModule } from '@angular/material/list';
import { MatDialogModule } from '@angular/material/dialog';

// Components and Routing
import { CourseContentComponent } from './course-content.component';
import { ContentDialogComponent } from './content-dialog/content-dialog.component';
import { ModuleDialogComponent } from './module-dialog/module-dialog.component';
import { EmbeddedContentViewerComponent } from './embedded-content-viewer/embedded-content-viewer.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';
import { CourseContentRoutingModule } from './course-content-routing.module';

@NgModule({
  declarations: [
    CourseContentComponent,
    ContentDialogComponent,
    ModuleDialogComponent,
    EmbeddedContentViewerComponent,
    ConfirmDialogComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CourseContentRoutingModule,
    
    // Angular Material
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatSnackBarModule,
    MatListModule,
    MatDialogModule
  ],
  exports: [
    CourseContentComponent
  ]
})
export class CourseContentModule { }
