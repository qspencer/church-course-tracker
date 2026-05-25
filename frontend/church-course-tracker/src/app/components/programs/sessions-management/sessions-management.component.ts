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
import { Program, ProgramSession, ProgramPairing, ProgramParticipant } from '../../../models/program.model';
import { Person } from '../../../models';
import { SessionDialogComponent } from '../session-dialog/session-dialog.component';
import { ConfirmDialogComponent } from '../../../shared/confirm-dialog/confirm-dialog.component';
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
    selector: 'app-sessions-management',
    templateUrl: './sessions-management.component.html',
    styleUrls: ['./sessions-management.component.scss'],
    imports: [MatIconButton, MatIcon, MatButton, MatFormField, MatLabel, MatSelect, ReactiveFormsModule, FormsModule, MatOption, MatInput, MatSuffix, MatProgressSpinner, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, MatChip, MatTooltip, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator, TitleCasePipe, DatePipe]
})
export class SessionsManagementComponent implements OnInit {
  private dialogRef = inject<MatDialogRef<SessionsManagementComponent>>(MatDialogRef);
  data = inject<{
    program: Program;
}>(MAT_DIALOG_DATA);
  private programService = inject(ProgramService);
  private memberService = inject(MemberService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private logger = inject(LoggerService);

  displayedColumns: string[] = ['session_date', 'duration', 'location', 'session_type', 'participants', 'actions'];
  dataSource = new MatTableDataSource<ProgramSession>();
  isLoading = true;
  program: Program;
  sessions: ProgramSession[] = [];
  pairings: ProgramPairing[] = [];
  participants: ProgramParticipant[] = [];
  members: Person[] = [];
  pairingFilter: number | null = null;

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
      sessions: this.programService.getProgramSessions(this.program.id),
      pairings: this.programService.getProgramPairings(this.program.id),
      participants: this.programService.getProgramParticipants(this.program.id),
      members: this.memberService.getMembers()
    }).subscribe({
      next: (data) => {
        this.sessions = data.sessions;
        this.pairings = data.pairings;
        this.participants = data.participants;
        this.members = data.members;
        this.dataSource.data = this.sessions;
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading data', error, { component: 'SessionsManagementComponent', action: 'loadData', programId: this.program.id });
        this.snackBar.open('Error loading sessions', 'Close', { duration: 3000 });
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

  applyFilters(): void {
    let filteredData = [...this.sessions];

    if (this.pairingFilter !== null) {
      filteredData = filteredData.filter(s => s.pairing_id === this.pairingFilter);
    }

    this.dataSource.data = filteredData;
  }

  onPairingFilterChange(): void {
    this.applyFilters();
  }

  getParticipantNames(participantIds: number[] | undefined): string {
    if (!participantIds || participantIds.length === 0) {
      return 'None';
    }
    return participantIds.map(id => {
      const participant = this.participants.find(p => p.id === id);
      if (participant) {
        const member = this.members.find(m => m.id === participant.people_id);
        if (member) {
          return `${member.first_name} ${member.last_name}`;
        }
      }
      return `Participant #${id}`;
    }).join(', ');
  }

  getPairingDisplay(pairingId: number | undefined): string {
    if (!pairingId) return 'No pairing';
    const pairing = this.pairings.find(p => p.id === pairingId);
    if (pairing) {
      const primary = this.participants.find(p => p.id === pairing.primary_participant_id);
      const secondary = this.participants.find(p => p.id === pairing.secondary_participant_id);
      if (primary && secondary) {
        const primaryMember = this.members.find(m => m.id === primary.people_id);
        const secondaryMember = this.members.find(m => m.id === secondary.people_id);
        if (primaryMember && secondaryMember) {
          return `${primaryMember.first_name} ${primaryMember.last_name} ↔ ${secondaryMember.first_name} ${secondaryMember.last_name}`;
        }
      }
      return `Pairing #${pairingId}`;
    }
    return 'Unknown pairing';
  }

  openSessionDialog(session?: ProgramSession): void {
    const dialogRef = this.dialog.open(SessionDialogComponent, {
      width: '700px',
      data: {
        session: session || null,
        program: this.program,
        pairings: this.pairings,
        participants: this.participants
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  viewSession(session: ProgramSession): void {
    this.dialog.open(SessionDialogComponent, {
      width: '700px',
      data: {
        session: session,
        program: this.program,
        pairings: this.pairings,
        participants: this.participants,
        viewMode: true
      }
    });
  }

  editSession(session: ProgramSession): void {
    this.openSessionDialog(session);
  }

  deleteSession(session: ProgramSession): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Session',
        message: `Are you sure you want to delete this session?`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.programService.deleteProgramSession(session.id).subscribe({
          next: () => {
            this.snackBar.open('Session deleted successfully', 'Close', { duration: 3000 });
            this.loadData();
          },
          error: (error) => {
            this.logger.error('Error deleting session', error, { component: 'SessionsManagementComponent', action: 'deleteSession', sessionId: session.id, programId: this.program.id });
            this.snackBar.open('Error deleting session', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  onClose(): void {
    this.dialogRef.close();
  }
}

