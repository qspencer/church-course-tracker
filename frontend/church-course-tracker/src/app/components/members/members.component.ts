import { Component, OnInit, viewChild, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MemberService } from '../../services/member.service';
import { LoggerService } from '../../services/logger.service';
import { Person } from '../../models';
import { MemberDialogComponent } from './member-dialog/member-dialog.component';
import { MemberEnrollmentsDialogComponent } from './member-enrollments-dialog/member-enrollments-dialog.component';
import { MemberImportDialogComponent } from './member-import-dialog/member-import-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent } from '@angular/material/card';
import { MatFormField, MatLabel, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatTooltip } from '@angular/material/tooltip';
import { DatePipe } from '@angular/common';

@Component({
    selector: 'app-members',
    templateUrl: './members.component.html',
    styleUrls: ['./members.component.scss'],
    imports: [MatButton, MatIcon, MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent, MatFormField, MatLabel, MatInput, MatSuffix, MatProgressSpinner, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, MatIconButton, MatTooltip, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator, DatePipe]
})
export class MembersComponent implements OnInit {
  private memberService = inject(MemberService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private logger = inject(LoggerService);

  displayedColumns: string[] = ['full_name', 'email', 'phone', 'created_at', 'actions'];
  dataSource = new MatTableDataSource<Person>();
  isLoading = true;

  readonly paginator = viewChild(MatPaginator);
  readonly sort = viewChild(MatSort);

  ngOnInit(): void {
    this.loadMembers();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator();
    this.dataSource.sort = this.sort();
  }

  loadMembers(): void {
    this.isLoading = true;
    this.memberService.getMembers().subscribe({
      next: (members) => {
        // Add full_name property for display
        const membersWithFullName = members.map(member => ({
          ...member,
          full_name: `${member.first_name} ${member.last_name}`
        }));
        this.dataSource.data = membersWithFullName;
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading members', error);
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

  openMemberDialog(member?: Person): void {
    const dialogRef = this.dialog.open(MemberDialogComponent, {
      width: '500px',
      data: { member: member || null }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadMembers();
      }
    });
  }

  openImportDialog(): void {
    const dialogRef = this.dialog.open(MemberImportDialogComponent, {
      width: '600px',
      maxWidth: '95vw'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadMembers();
      }
    });
  }

  editMember(member: Person): void {
    this.openMemberDialog(member);
  }

  deleteMember(member: Person): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Member',
        message: `Are you sure you want to delete "${member.first_name} ${member.last_name}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.memberService.deleteMember(member.id).subscribe({
          next: () => {
            this.snackBar.open('Member deleted successfully', 'Close', { duration: 3000 });
            this.loadMembers();
          },
          error: (error) => {
            this.logger.error('Error deleting member', error);
          }
        });
      }
    });
  }

  viewMemberDetails(member: Person): void {
    // Fetch full member details and open in view mode
    this.memberService.getMember(member.id).subscribe({
      next: (fullMember) => {
        this.dialog.open(MemberDialogComponent, {
          width: '700px',
          maxWidth: '90vw',
          maxHeight: '90vh',
          data: {
            member: fullMember,
            viewMode: true
          }
        });
      },
      error: (error) => {
        this.logger.error('Error loading member details', error);
        this.snackBar.open('Failed to load member details', 'Close', { duration: 3000 });
      }
    });
  }

  viewMemberEnrollments(member: Person): void {
    this.memberService.getMemberEnrollments(member.id).subscribe({
      next: (enrollments) => {
        this.dialog.open(MemberEnrollmentsDialogComponent, {
          width: '600px',
          maxWidth: '90vw',
          maxHeight: '90vh',
          data: {
            member: member,
            enrollments: enrollments
          }
        });
      },
      error: (error) => {
        this.logger.error('Error loading member enrollments', error);
        this.snackBar.open('Failed to load member enrollments', 'Close', { duration: 3000 });
      }
    });
  }
}
