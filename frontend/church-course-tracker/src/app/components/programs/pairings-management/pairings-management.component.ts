import { Component, OnInit, viewChild, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
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
import { MatIconButton, MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatFormField, MatLabel, MatSuffix } from '@angular/material/form-field';
import { MatSelect, MatOption } from '@angular/material/select';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatInput } from '@angular/material/input';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatChip } from '@angular/material/chips';
import { MatTooltip } from '@angular/material/tooltip';
import { TitleCasePipe, DatePipe } from '@angular/common';

@Component({
    selector: 'app-pairings-management',
    templateUrl: './pairings-management.component.html',
    styleUrls: ['./pairings-management.component.scss'],
    imports: [MatIconButton, MatIcon, MatButton, MatFormField, MatLabel, MatSelect, ReactiveFormsModule, FormsModule, MatOption, MatInput, MatSuffix, MatProgressSpinner, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, MatChip, MatTooltip, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator, TitleCasePipe, DatePipe]
})
export class PairingsManagementComponent implements OnInit {
  private dialogRef = inject<MatDialogRef<PairingsManagementComponent>>(MatDialogRef);
  data = inject<{
    program: Program;
}>(MAT_DIALOG_DATA);
  private programService = inject(ProgramService);
  private memberService = inject(MemberService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private searchFilterService = inject(SearchFilterService);
  private logger = inject(LoggerService);

  displayedColumns: string[] = ['primary_participant', 'secondary_participant', 'status', 'start_date', 'actions'];
  dataSource = new MatTableDataSource<ProgramPairing>();
  isLoading = true;
  program: Program;
  pairings: ProgramPairing[] = [];
  participants: ProgramParticipant[] = [];
  members: Person[] = [];
  statusFilter: string = '';
  searchFilter: string = '';

  readonly paginator = viewChild(MatPaginator);
  readonly sort = viewChild(MatSort);

  constructor() {
    const data = this.data;

    this.program = data.program;
  }

  ngOnInit(): void {
    this.loadData();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator();
    this.dataSource.sort = this.sort();
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


