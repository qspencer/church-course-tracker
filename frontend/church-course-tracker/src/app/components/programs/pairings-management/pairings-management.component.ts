import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { forkJoin } from 'rxjs';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { LoggerService } from '../../../services/logger.service';
import { Program, ProgramPairing, ProgramParticipant } from '../../../models/program.model';
import { Person } from '../../../models';
import { PairingDialogComponent } from '../pairing-dialog/pairing-dialog.component';
import { ConfirmDialogComponent } from '../../../shared/confirm-dialog/confirm-dialog.component';
import { SearchFilterService } from '../../../shared/search-filter.service';

@Component({
  selector: 'app-pairings-management',
  templateUrl: './pairings-management.component.html',
  styleUrls: ['./pairings-management.component.scss']
})
export class PairingsManagementComponent implements OnInit {
  displayedColumns: string[] = ['primary_participant', 'secondary_participant', 'status', 'start_date', 'actions'];
  dataSource = new MatTableDataSource<ProgramPairing>();
  isLoading = true;
  program: Program;
  pairings: ProgramPairing[] = [];
  participants: ProgramParticipant[] = [];
  members: Person[] = [];
  statusFilter: string = '';
  searchFilter: string = '';

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private dialogRef: MatDialogRef<PairingsManagementComponent>,
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
    this.loadData();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadData(): void {
    this.isLoading = true;
    
    forkJoin({
      pairings: this.programService.getProgramPairings(this.program.id),
      participants: this.programService.getProgramParticipants(this.program.id),
      members: this.memberService.getMembers()
    }).subscribe({
      next: (data) => {
        this.pairings = data.pairings;
        this.participants = data.participants;
        this.members = data.members;
        this.dataSource.data = this.pairings;
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading data', error, { component: 'PairingsManagementComponent', action: 'loadData', programId: this.program.id });
        this.snackBar.open('Error loading pairings', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.searchFilter = filterValue.trim();
    this.applyFilters();
  }

  applyFilters(): void {
    let filteredData = [...this.pairings];

    // Apply status filter first
    if (this.statusFilter) {
      filteredData = filteredData.filter(p => p.status === this.statusFilter);
    }

    // Apply search filter using centralized search service
    if (this.searchFilter) {
      filteredData = this.searchFilterService.filterByParticipantNames(
        filteredData,
        this.members,
        this.participants,
        this.searchFilter,
        true // include email search
      );
    }

    this.dataSource.data = filteredData;

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  onStatusFilterChange(): void {
    this.applyFilters();
  }

  getParticipantName(participantId: number): string {
    const participant = this.participants.find(p => p.id === participantId);
    if (participant) {
      const member = this.members.find(m => m.id === participant.people_id);
      if (member) {
        return `${member.first_name} ${member.last_name}`;
      }
      return `Participant #${participant.id}`;
    }
    return 'Unknown';
  }

  getParticipantRole(participantId: number): string {
    const participant = this.participants.find(p => p.id === participantId);
    return participant?.role_name || 'Unknown';
  }

  openPairingDialog(pairing?: ProgramPairing): void {
    const dialogRef = this.dialog.open(PairingDialogComponent, {
      width: '600px',
      data: {
        pairing: pairing || null,
        program: this.program,
        participants: this.participants
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  viewPairing(pairing: ProgramPairing): void {
    this.dialog.open(PairingDialogComponent, {
      width: '600px',
      data: {
        pairing: pairing,
        program: this.program,
        participants: this.participants,
        viewMode: true
      }
    });
  }

  editPairing(pairing: ProgramPairing): void {
    this.openPairingDialog(pairing);
  }

  deletePairing(pairing: ProgramPairing): void {
    const primaryName = this.getParticipantName(pairing.primary_participant_id);
    const secondaryName = this.getParticipantName(pairing.secondary_participant_id);
    
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Remove Pairing',
        message: `Are you sure you want to remove the pairing between "${primaryName}" and "${secondaryName}"?`,
        confirmText: 'Remove',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.programService.removeProgramPairing(pairing.id).subscribe({
          next: () => {
            this.snackBar.open('Pairing removed successfully', 'Close', { duration: 3000 });
            this.loadData();
          },
          error: (error) => {
            this.logger.error('Error removing pairing', error, { component: 'PairingsManagementComponent', action: 'deletePairing', pairingId: pairing.id, programId: this.program.id });
            this.snackBar.open('Error removing pairing', 'Close', { duration: 3000 });
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

  canCreatePairing(): boolean {
    // Check if we have both primary and secondary participants
    const roleDefinitions = this.program.role_definitions || [];
    const primaryRoleNames = roleDefinitions.filter(r => r.is_primary).map(r => r.name);
    const secondaryRoleNames = roleDefinitions.filter(r => !r.is_primary).map(r => r.name);
    
    const hasPrimary = this.participants.some(p => 
      primaryRoleNames.includes(p.role_name) && p.status === 'active'
    );
    const hasSecondary = this.participants.some(p => 
      secondaryRoleNames.includes(p.role_name) && p.status === 'active'
    );
    
    return hasPrimary && hasSecondary;
  }

  onClose(): void {
    this.dialogRef.close();
  }
}


