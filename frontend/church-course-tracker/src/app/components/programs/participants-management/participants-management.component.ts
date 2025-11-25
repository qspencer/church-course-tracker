import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { Program, ProgramParticipant } from '../../../models/program.model';
import { Person } from '../../../models';
import { ParticipantDialogComponent } from '../participant-dialog/participant-dialog.component';
import { PairingsManagementComponent } from '../pairings-management/pairings-management.component';
import { ConfirmDialogComponent } from '../../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-participants-management',
  templateUrl: './participants-management.component.html',
  styleUrls: ['./participants-management.component.scss']
})
export class ParticipantsManagementComponent implements OnInit {
  displayedColumns: string[] = ['member_name', 'role_name', 'status', 'progress_percentage', 'start_date', 'actions'];
  dataSource = new MatTableDataSource<ProgramParticipant>();
  isLoading = true;
  program: Program;
  participants: ProgramParticipant[] = [];
  members: Person[] = [];
  roleFilter: string = '';
  statusFilter: string = '';

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private dialogRef: MatDialogRef<ParticipantsManagementComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { program: Program },
    private programService: ProgramService,
    private memberService: MemberService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {
    this.program = data.program;
  }

  ngOnInit(): void {
    this.loadParticipants();
    this.loadMembers();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadParticipants(): void {
    this.isLoading = true;
    this.programService.getProgramParticipants(this.program.id).subscribe({
      next: (participants) => {
        this.participants = participants;
        this.dataSource.data = participants;
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading participants:', error);
        this.snackBar.open('Error loading participants', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  loadMembers(): void {
    this.memberService.getMembers().subscribe({
      next: (members) => {
        this.members = members;
      },
      error: (error) => {
        console.error('Error loading members:', error);
      }
    });
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    // Custom filter function to search by member name and email
    this.dataSource.filterPredicate = (data: ProgramParticipant, filter: string) => {
      const memberName = this.getMemberName(data.people_id).toLowerCase();
      const memberEmail = this.getMemberEmail(data.people_id).toLowerCase();
      const searchText = filter.toLowerCase();
      return memberName.includes(searchText) || memberEmail.includes(searchText);
    };
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  applyFilters(): void {
    let filteredData = [...this.participants];

    if (this.roleFilter) {
      filteredData = filteredData.filter(p => p.role_name === this.roleFilter);
    }

    if (this.statusFilter) {
      filteredData = filteredData.filter(p => p.status === this.statusFilter);
    }

    this.dataSource.data = filteredData;
  }

  onRoleFilterChange(): void {
    this.applyFilters();
  }

  onStatusFilterChange(): void {
    this.applyFilters();
  }

  getRoleOptions(): string[] {
    if (this.program.role_definitions && this.program.role_definitions.length > 0) {
      return this.program.role_definitions.map(r => r.name);
    }
    return [];
  }

  getMemberName(peopleId: number): string {
    const member = this.members.find(m => m.id === peopleId);
    if (member) {
      return `${member.first_name} ${member.last_name}`;
    }
    return 'Unknown';
  }

  getMemberEmail(peopleId: number): string {
    const member = this.members.find(m => m.id === peopleId);
    return member?.email || '';
  }

  openParticipantDialog(participant?: ProgramParticipant): void {
    const dialogRef = this.dialog.open(ParticipantDialogComponent, {
      width: '600px',
      data: {
        participant: participant || null,
        program: this.program
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadParticipants();
      }
    });
  }

  viewParticipant(participant: ProgramParticipant): void {
    this.dialog.open(ParticipantDialogComponent, {
      width: '600px',
      data: {
        participant: participant,
        program: this.program,
        viewMode: true
      }
    });
  }

  editParticipant(participant: ProgramParticipant): void {
    this.openParticipantDialog(participant);
  }

  deleteParticipant(participant: ProgramParticipant): void {
    const memberName = this.getMemberName(participant.people_id);
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Remove Participant',
        message: `Are you sure you want to remove "${memberName}" from this program?`,
        confirmText: 'Remove',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.programService.removeProgramParticipant(participant.id).subscribe({
          next: () => {
            this.snackBar.open('Participant removed successfully', 'Close', { duration: 3000 });
            this.loadParticipants();
          },
          error: (error) => {
            console.error('Error removing participant:', error);
            this.snackBar.open('Error removing participant', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'active':
        return 'primary';
      case 'paused':
        return 'warn';
      case 'completed':
        return 'accent';
      case 'ended':
        return '';
      default:
        return '';
    }
  }

  getRoleColor(roleName: string): string {
    const roleDef = this.program.role_definitions?.find(r => r.name === roleName);
    if (roleDef?.is_primary) {
      return 'primary';
    }
    return 'accent';
  }

  onClose(): void {
    this.dialogRef.close();
  }

  managePairings(): void {
    this.dialog.open(PairingsManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: this.program }
    });
  }
}

