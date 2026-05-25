import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { User, UserCreate, UserUpdate } from '../../models';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { MatDialog } from '@angular/material/dialog';
import { UserDialogComponent } from './user-dialog/user-dialog.component';
import { UserImportDialogComponent } from './user-import-dialog/user-import-dialog.component';
import { ResetPasswordDialogComponent } from './reset-password-dialog/reset-password-dialog.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LoggerService } from '../../services/logger.service';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { NgClass, TitleCasePipe } from '@angular/common';
import { MatChip } from '@angular/material/chips';
import { MatMenuTrigger, MatMenu, MatMenuContent, MatMenuItem } from '@angular/material/menu';

export interface PCUserImportData {
  planning_center_person_id: string;
  role: string;
}

@Component({
    selector: 'app-users',
    templateUrl: './users.component.html',
    styleUrls: ['./users.component.scss'],
    imports: [MatButton, MatIcon, MatProgressSpinner, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, NgClass, MatChip, MatIconButton, MatMenuTrigger, MatMenu, MatMenuContent, MatMenuItem, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, TitleCasePipe]
})
export class UsersComponent implements OnInit {
  private userService = inject(UserService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private logger = inject(LoggerService);

  users: User[] = [];
  isLoading = true;
  displayedColumns: string[] = ['full_name', 'email', 'username', 'role', 'is_active', 'created_at', 'actions'];

  ngOnInit(): void {
    // Double-check admin access (additional security layer)
    if (!this.authService.isAdmin()) {
      this.snackBar.open('Access denied. Admin privileges required.', 'Close', { duration: 3000 });
      this.router.navigate(['/dashboard']);
      return;
    }
    
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;
    this.userService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading users', error);
        this.snackBar.open('Error loading users', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(UserDialogComponent, {
      width: '500px',
      data: { mode: 'create' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadUsers();
      }
    });
  }

  openImportDialog(): void {
    const dialogRef = this.dialog.open(UserImportDialogComponent, {
      width: '600px',
      maxWidth: '95vw'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Import the user from Planning Center
        this.importUserFromPC(result);
      }
    });
  }

  importUserFromPC(importData: PCUserImportData): void {
    this.userService.importUserFromPlanningCenter(importData.planning_center_person_id, importData.role).subscribe({
      next: (user) => {
        this.snackBar.open(`User "${user.full_name}" imported successfully. A temporary password has been generated and the user will need to reset it on first login.`, 'Close', { duration: 5000 });
        this.loadUsers();
      },
      error: (error) => {
        this.logger.error('Error importing user', error);
        const errorMsg = error?.error?.detail || 'Error importing user from Planning Center';
        this.snackBar.open(errorMsg, 'Close', { duration: 5000 });
      }
    });
  }

  openEditDialog(user: User): void {
    const dialogRef = this.dialog.open(UserDialogComponent, {
      width: '500px',
      data: { mode: 'edit', user: user }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadUsers();
      }
    });
  }

  openResetPasswordDialog(user: User): void {
    this.dialog.open(ResetPasswordDialogComponent, {
      width: '450px',
      data: { user: user }
    });
  }

  deleteUser(user: User): void {
    if (confirm(`Are you sure you want to delete user "${user.full_name}"?`)) {
      this.userService.deleteUser(user.id).subscribe({
        next: () => {
          this.snackBar.open('User deleted successfully', 'Close', { duration: 3000 });
          this.loadUsers();
        },
        error: (error) => {
          this.logger.error('Error deleting user', error);
          this.snackBar.open('Error deleting user', 'Close', { duration: 3000 });
        }
      });
    }
  }

  toggleUserStatus(user: User): void {
    const update: UserUpdate = {
      is_active: !user.is_active
    };

    this.userService.updateUser(user.id, update).subscribe({
      next: () => {
        this.snackBar.open(`User ${user.is_active ? 'deactivated' : 'activated'} successfully`, 'Close', { duration: 3000 });
        this.loadUsers();
      },
      error: (error) => {
        this.logger.error('Error updating user', error);
        this.snackBar.open('Error updating user', 'Close', { duration: 3000 });
      }
    });
  }

  getRoleBadgeClass(role: string): string {
    switch (role) {
      case 'admin':
        return 'badge-danger';
      case 'staff':
        return 'badge-primary';
      case 'viewer':
        return 'badge-secondary';
      default:
        return 'badge-secondary';
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }
}
