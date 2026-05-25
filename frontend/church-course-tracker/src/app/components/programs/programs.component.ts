import { Component, OnInit, viewChild, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../services/program.service';
import { AuthService } from '../../services/auth.service';
import { LoggerService } from '../../services/logger.service';
import { Program } from '../../models/program.model';
import { PlanningCenterImportData } from '../../models';
import { ProgramDialogComponent } from './program-dialog/program-dialog.component';
import { ParticipantsManagementComponent } from './participants-management/participants-management.component';
import { PairingsManagementComponent } from './pairings-management/pairings-management.component';
import { SessionsManagementComponent } from './sessions-management/sessions-management.component';
import { ProgressManagementComponent } from './progress-management/progress-management.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';
import { BulkEnrollmentDialogComponent } from '../enrollments/bulk-enrollment-dialog/bulk-enrollment-dialog.component';
import { PCImportDialogComponent, PCImportDialogData } from '../courses/pc-import-dialog/pc-import-dialog.component';
import { CustomTabConfigDialogComponent } from './custom-tab-config-dialog/custom-tab-config-dialog.component';
import { CustomTabImportDialogComponent } from './custom-tab-import-dialog/custom-tab-import-dialog.component';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent } from '@angular/material/card';
import { MatFormField, MatLabel, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatChip } from '@angular/material/chips';
import { MatTooltip } from '@angular/material/tooltip';
import { SlicePipe, DatePipe } from '@angular/common';

@Component({
    selector: 'app-programs',
    templateUrl: './programs.component.html',
    styleUrls: ['./programs.component.scss'],
    imports: [MatButton, MatIcon, MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent, MatFormField, MatLabel, MatInput, MatSuffix, MatProgressSpinner, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, MatChip, MatIconButton, MatTooltip, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator, SlicePipe, DatePipe]
})
export class ProgramsComponent implements OnInit {
  private programService = inject(ProgramService);
  private authService = inject(AuthService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private logger = inject(LoggerService);

  displayedColumns: string[] = ['title', 'description', 'is_active', 'created_at', 'actions'];
  dataSource = new MatTableDataSource<Program>();
  isLoading = true;

  readonly paginator = viewChild(MatPaginator);
  readonly sort = viewChild(MatSort);

  ngOnInit(): void {
    // Removed console.log statements - use logger if needed
    this.loadPrograms();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator();
    this.dataSource.sort = this.sort();
  }

  loadPrograms(): void {
    this.isLoading = true;
    // Only load active programs by default (soft-deleted programs have is_active=false)
    this.programService.getPrograms({ is_active: true }).subscribe({
      next: (programs) => {
        this.dataSource.data = programs;
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading programs', error);
        this.snackBar.open('Error loading programs', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  openProgramDialog(program?: Program, importData?: PlanningCenterImportData): void {
    const dialogRef = this.dialog.open(ProgramDialogComponent, {
      width: '1000px',
      maxWidth: '95vw',
      data: { program: program || null, importData: importData || null }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadPrograms();
      }
    });
  }

  openImportDialog(): void {
    const dialogRef = this.dialog.open(PCImportDialogComponent, {
      width: '700px',
      data: { entityType: 'program' } as PCImportDialogData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Open program dialog with import data
        this.openProgramDialog(undefined, result);
      }
    });
  }

  openBulkImportDialog(): void {
    const dialogRef = this.dialog.open(BulkEnrollmentDialogComponent, {
      width: '600px',
      data: { targetType: 'program' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadPrograms();
      }
    });
  }

  viewProgramDetails(program: Program): void {
    this.dialog.open(ProgramDialogComponent, {
      width: '1000px',
      maxWidth: '95vw',
      data: { 
        program: program,
        viewMode: true 
      }
    });
  }

  manageParticipants(program: Program): void {
    this.dialog.open(ParticipantsManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: program }
    });
  }

  managePairings(program: Program): void {
    this.dialog.open(PairingsManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: program }
    });
  }

  manageSessions(program: Program): void {
    this.dialog.open(SessionsManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: program }
    });
  }

  manageProgress(program: Program): void {
    this.dialog.open(ProgressManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: program }
    });
  }

  editProgram(program: Program): void {
    this.openProgramDialog(program);
  }

  toggleProgramStatus(program: Program): void {
    const newStatus = !program.is_active;
    this.programService.updateProgram(program.id, { is_active: newStatus }).subscribe({
      next: () => {
        this.snackBar.open(
          `Program ${newStatus ? 'activated' : 'deactivated'} successfully`,
          'Close',
          { duration: 3000 }
        );
        this.loadPrograms();
      },
      error: (error) => {
        this.logger.error('Error updating program status', error);
        this.snackBar.open('Error updating program status', 'Close', { duration: 3000 });
      }
    });
  }

  deleteProgram(program: Program): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Program',
        message: `Are you sure you want to delete "${program.title}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.programService.deleteProgram(program.id).subscribe({
          next: () => {
            this.snackBar.open('Program deleted successfully', 'Close', { duration: 3000 });
            this.loadPrograms();
          },
          error: (error) => {
            this.logger.error('Error deleting program', error);
            this.snackBar.open('Error deleting program', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  configureCustomTab(program: Program): void {
    const dialogRef = this.dialog.open(CustomTabConfigDialogComponent, {
      width: '900px',
      maxWidth: '95vw',
      maxHeight: '90vh',
      data: {
        programId: program.id,
        currentConfig: program.planning_center_tab_config
      }
    });

    dialogRef.afterClosed().subscribe(config => {
      if (config) {
        this.programService.updateProgram(program.id, {
          planning_center_tab_config: config
        }).subscribe({
          next: () => {
            this.snackBar.open('Custom tab configuration saved successfully', 'Close', { duration: 3000 });
            this.loadPrograms();
          },
          error: (error) => {
            this.logger.error('Error saving custom tab configuration', error);
            this.snackBar.open('Error saving configuration', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  importFromCustomTab(program: Program): void {
    const dialogRef = this.dialog.open(CustomTabImportDialogComponent, {
      width: '700px',
      maxWidth: '95vw',
      data: { program }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadPrograms();
      }
    });
  }

  getStatusColor(isActive: boolean): string {
    return isActive ? 'primary' : 'warn';
  }

  getStatusText(isActive: boolean): string {
    return isActive ? 'Active' : 'Inactive';
  }

  canCreateProgram(): boolean {
    return this.authService.isAdmin() || this.authService.hasRole('admin');
  }

  canEditProgram(): boolean {
    return this.authService.isAdmin() || this.authService.hasRole('admin');
  }

  canDeleteProgram(): boolean {
    return this.authService.isAdmin() || this.authService.hasRole('admin');
  }

  canToggleProgramStatus(): boolean {
    return this.authService.isAdmin() || this.authService.hasRole('admin');
  }
}

