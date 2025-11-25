import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../services/program.service';
import { AuthService } from '../../services/auth.service';
import { Program } from '../../models/program.model';
import { ProgramDialogComponent } from './program-dialog/program-dialog.component';
import { ParticipantsManagementComponent } from './participants-management/participants-management.component';
import { PairingsManagementComponent } from './pairings-management/pairings-management.component';
import { SessionsManagementComponent } from './sessions-management/sessions-management.component';
import { ProgressManagementComponent } from './progress-management/progress-management.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';
import { BulkEnrollmentDialogComponent } from '../enrollments/bulk-enrollment-dialog/bulk-enrollment-dialog.component';

@Component({
  selector: 'app-programs',
  templateUrl: './programs.component.html',
  styleUrls: ['./programs.component.scss']
})
export class ProgramsComponent implements OnInit {
  displayedColumns: string[] = ['title', 'description', 'is_active', 'created_at', 'actions'];
  dataSource = new MatTableDataSource<Program>();
  isLoading = true;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private programService: ProgramService,
    private authService: AuthService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadPrograms();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
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
        console.error('Error loading programs:', error);
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

  openProgramDialog(program?: Program): void {
    const dialogRef = this.dialog.open(ProgramDialogComponent, {
      width: '1000px',
      maxWidth: '95vw',
      data: { program: program || null }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadPrograms();
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
        console.error('Error updating program status:', error);
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
            console.error('Error deleting program:', error);
            this.snackBar.open('Error deleting program', 'Close', { duration: 3000 });
          }
        });
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

