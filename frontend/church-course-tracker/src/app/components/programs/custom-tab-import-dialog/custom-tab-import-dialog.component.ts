import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../../services/program.service';
import { Program } from '../../../models/program.model';

export interface CustomTabImportDialogData {
  program: Program;
}

@Component({
  selector: 'app-custom-tab-import-dialog',
  templateUrl: './custom-tab-import-dialog.component.html',
  styleUrls: ['./custom-tab-import-dialog.component.scss']
})
export class CustomTabImportDialogComponent implements OnInit {
  loading = false;
  listId = '';
  defaultRole = '';

  // Import results
  importing = false;
  importComplete = false;
  importResults?: {
    imported: Array<{
      person_name: string;
      pc_person_id: string;
      role_name?: string;
      status: string;
    }>;
    errors: Array<{
      person_name: string;
      pc_person_id: string;
      error: string;
    }>;
  };

  constructor(
    public dialogRef: MatDialogRef<CustomTabImportDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CustomTabImportDialogData,
    private programService: ProgramService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    // Set default role from program if available
    if (this.data.program.role_definitions && this.data.program.role_definitions.length > 0) {
      this.defaultRole = this.data.program.role_definitions[0].name;
    }
  }

  get hasConfig(): boolean {
    return !!this.data.program.planning_center_tab_config?.enabled;
  }

  get configTabName(): string {
    return this.data.program.planning_center_tab_config?.tab_name || '';
  }

  startImport(): void {
    if (!this.listId.trim()) {
      this.snackBar.open('Please enter a Planning Center List ID', 'Close', { duration: 3000 });
      return;
    }

    if (!this.hasConfig) {
      this.snackBar.open('Program does not have custom tab configuration', 'Close', { duration: 3000 });
      return;
    }

    this.importing = true;
    this.programService.bulkImportParticipantsFromPCListWithTabs(
      this.data.program.id,
      {
        list_id: this.listId.trim(),
        role_name: this.defaultRole || undefined
      }
    ).subscribe({
      next: (results) => {
        this.importResults = results;
        this.importComplete = true;
        this.importing = false;

        const successCount = results.imported.length;
        const errorCount = results.errors.length;

        if (errorCount === 0) {
          this.snackBar.open(
            `Successfully imported ${successCount} participant(s)!`,
            'Close',
            { duration: 5000 }
          );
        } else {
          this.snackBar.open(
            `Imported ${successCount} participant(s) with ${errorCount} error(s)`,
            'Close',
            { duration: 5000 }
          );
        }
      },
      error: (error) => {
        console.error('Import error:', error);
        this.snackBar.open(
          error.error?.detail || 'Import failed. Please check your configuration and try again.',
          'Close',
          { duration: 5000 }
        );
        this.importing = false;
      }
    });
  }

  close(): void {
    this.dialogRef.close(this.importComplete);
  }

  reset(): void {
    this.listId = '';
    this.importComplete = false;
    this.importResults = undefined;
  }
}
