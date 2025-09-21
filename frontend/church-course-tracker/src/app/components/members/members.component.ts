import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MemberService } from '../../services/member.service';
import { Person } from '../../models';
import { MemberDialogComponent } from './member-dialog/member-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-members',
  templateUrl: './members.component.html',
  styleUrls: ['./members.component.scss']
})
export class MembersComponent implements OnInit {
  displayedColumns: string[] = ['full_name', 'email', 'phone', 'created_at', 'actions'];
  dataSource = new MatTableDataSource<Person>();
  isLoading = true;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private memberService: MemberService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadMembers();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
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
        console.error('Error loading members:', error);
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
            console.error('Error deleting member:', error);
          }
        });
      }
    });
  }

  viewMemberDetails(member: Person): void {
    // Navigate to member details page or open detailed dialog
    console.log('View member details:', member);
  }

  viewMemberEnrollments(member: Person): void {
    this.memberService.getMemberEnrollments(member.id).subscribe({
      next: (enrollments) => {
        console.log('Member enrollments:', enrollments);
        // Could open a dialog showing enrollments
      },
      error: (error) => {
        console.error('Error loading member enrollments:', error);
      }
    });
  }
}
