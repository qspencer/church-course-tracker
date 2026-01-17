import { Component, Inject, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
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
import { SearchFilterService } from '../../../shared/search-filter.service';
import { LoggerService } from '../../../services/logger.service';

@Component({
  selector: 'app-participants-management',
  templateUrl: './participants-management.component.html',
  styleUrls: ['./participants-management.component.scss']
})
export class ParticipantsManagementComponent implements OnInit, AfterViewInit {
  displayedColumns: string[] = ['member_name', 'role_name', 'status', 'progress_percentage', 'start_date', 'actions'];
  dataSource = new MatTableDataSource<ProgramParticipant>();
  isLoading = true;
  program: Program;
  participants: ProgramParticipant[] = [];
  members: Person[] = [];
  roleFilter: string = '';
  statusFilter: string = '';
  searchFilter: string = '';

  // Pagination properties
  totalCount = 0;
  pageSize = 10;
  pageIndex = 0;
  pageSizeOptions = [5, 10, 25, 50, 100];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private dialogRef: MatDialogRef<ParticipantsManagementComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { program: Program },
    private programService: ProgramService,
    private memberService: MemberService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private searchFilterService: SearchFilterService,
    private logger: LoggerService
  ) {
    this.program = data.program;
  }

  ngOnInit(): void {
    // Load ALL members first (no pagination limit), then participants, so member names are available when displaying
    // Use a high limit to get all members in one request
    this.memberService.getMembers({ limit: 10000 }).subscribe({
      next: (members) => {
        this.members = members;
        // Now load participants after members are loaded
        this.loadParticipants();
      },
      error: (error) => {
        this.logger.error('Error loading members', error, {
          component: 'ParticipantsManagementComponent',
          action: 'ngOnInit',
          programId: this.program.id
        });
        this.snackBar.open('Error loading members', 'Close', { duration: 3000 });
        // Still load participants even if members fail
        this.loadParticipants();
      }
    });
  }

  ngAfterViewInit(): void {
    // Set default sort to last name (member_name column) if sort is available
    // Note: Actual sorting is done server-side, this just sets the UI indicator
    if (this.sort) {
      this.dataSource.sort = this.sort;
      this.sort.sort({ id: 'member_name', start: 'asc', disableClear: false });

      // Note: Sort changes are handled server-side via loadParticipants()
      // The MatSort UI will show the sort indicator, but actual sorting happens on backend
      this.sort.sortChange.subscribe(() => {
        this.pageIndex = 0; // Reset to first page when sorting changes
        if (this.paginator) {
          this.paginator.pageIndex = 0;
        }
        // For now, we keep the default backend sort (by last name)
        // Future enhancement: implement server-side sort parameter
        this.loadParticipants();
      });
    }
  }

  onPageChange(event: PageEvent): void {
    // Handle paginator page changes (page navigation or page size change)
    const oldPageSize = this.pageSize;
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    
    // If page size changed, reset to first page
    if (oldPageSize !== event.pageSize) {
      this.pageIndex = 0;
    }
    
    // Reload participants with new pagination
    this.loadParticipants();
  }

  loadParticipants(): void {
    this.isLoading = true;
    const skip = this.pageIndex * this.pageSize;
    const limit = this.pageSize;
    
    // Load participants with pagination and server-side search
    this.programService.getProgramParticipants(
      this.program.id,
      this.statusFilter || undefined,
      skip,
      limit,
      this.searchFilter || undefined
    ).subscribe({
      next: (participants) => {
        this.participants = participants;
        
        // Apply role filter client-side (since backend doesn't support it yet)
        let filteredData = [...participants];
        if (this.roleFilter) {
          filteredData = filteredData.filter(p => p.role_name === this.roleFilter);
        }
        
        this.dataSource.data = filteredData;
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading participants', error, {
          component: 'ParticipantsManagementComponent',
          action: 'loadParticipants',
          programId: this.program.id,
          pageIndex: this.pageIndex,
          pageSize: this.pageSize
        });
        this.snackBar.open('Error loading participants', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });

    // Load total count for paginator (accounts for status and search filters)
    this.programService.getProgramParticipantsCount(
      this.program.id,
      this.statusFilter || undefined,
      this.searchFilter || undefined
    ).subscribe({
      next: (response) => {
        this.totalCount = response.count;
        // Update paginator length
        if (this.paginator) {
          this.paginator.length = this.totalCount;
        }
      },
      error: (error) => {
        this.logger.error('Error loading participant count', error, {
          component: 'ParticipantsManagementComponent',
          action: 'loadParticipants',
          programId: this.program.id
        });
        // Don't show error to user, just log it
      }
    });
  }

  loadMembers(): void {
    this.memberService.getMembers().subscribe({
      next: (members) => {
        this.members = members;
        // Reload participants after members are loaded so names display correctly
        if (this.participants.length > 0) {
          // Update the data source with current participants to refresh displayed names
          this.dataSource.data = [...this.dataSource.data];
        }
      },
      error: (error) => {
        this.logger.error('Error loading members', error, {
          component: 'ParticipantsManagementComponent',
          action: 'loadMembers',
          programId: this.program.id
        });
        this.snackBar.open('Error loading members', 'Close', { duration: 3000 });
      }
    });
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.searchFilter = filterValue.trim();
    
    // Reset to first page when search changes
    this.pageIndex = 0;
    if (this.paginator) {
      this.paginator.pageIndex = 0;
    }
    
    // Reload participants with server-side search
    this.loadParticipants();
  }

  onRoleFilterChange(): void {
    // Reset to first page when filter changes
    this.pageIndex = 0;
    if (this.paginator) {
      this.paginator.pageIndex = 0;
    }
    this.loadParticipants();
  }

  onStatusFilterChange(): void {
    // Reset to first page when filter changes
    this.pageIndex = 0;
    if (this.paginator) {
      this.paginator.pageIndex = 0;
    }
    this.loadParticipants();
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
    // Log warning if member not found (only if members are loaded to avoid noise during initial load)
    if (this.members.length > 0) {
      this.logger.warn(`Member not found for people_id=${peopleId}`, {
        component: 'ParticipantsManagementComponent',
        action: 'getMemberName',
        peopleId,
        totalMembers: this.members.length
      });
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
            // Reset to first page if we're on a page that might now be empty
            if (this.pageIndex > 0 && this.dataSource.data.length === 1) {
              this.pageIndex = 0;
              if (this.paginator) {
                this.paginator.pageIndex = 0;
              }
            }
            this.loadParticipants();
          },
          error: (error) => {
            this.logger.error('Error removing participant', error, {
              component: 'ParticipantsManagementComponent',
              action: 'deleteParticipant',
              participantId: participant.id,
              programId: this.program.id
            });
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

