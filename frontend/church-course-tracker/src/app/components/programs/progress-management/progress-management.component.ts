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
import { Program, ProgramProgress, ProgramParticipant, ProgramSession } from '../../../models/program.model';
import { Person } from '../../../models';
import { ProgressDialogComponent } from '../progress-dialog/progress-dialog.component';
import { ConfirmDialogComponent } from '../../../shared/confirm-dialog/confirm-dialog.component';

@Component({
    selector: 'app-progress-management',
    templateUrl: './progress-management.component.html',
    styleUrls: ['./progress-management.component.scss'],
    standalone: false
})
export class ProgressManagementComponent implements OnInit {
  displayedColumns: string[] = ['progress_type', 'details', 'completion_date', 'participant', 'actions'];
  dataSource = new MatTableDataSource<ProgramProgress>();
  isLoading = true;
  program: Program;
  progressRecords: ProgramProgress[] = [];
  participants: ProgramParticipant[] = [];
  sessions: ProgramSession[] = [];
  members: Person[] = [];
  participantFilter: number | null = null;
  progressTypeFilter: string = '';

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private dialogRef: MatDialogRef<ProgressManagementComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { program: Program; participant?: ProgramParticipant },
    private programService: ProgramService,
    private memberService: MemberService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private logger: LoggerService
  ) {
    this.program = data.program;
    if (data.participant) {
      this.participantFilter = data.participant.id;
    }
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
      progress: this.programService.getProgramProgress(this.program.id),
      participants: this.programService.getProgramParticipants(this.program.id),
      sessions: this.programService.getProgramSessions(this.program.id),
      members: this.memberService.getMembers()
    }).subscribe({
      next: (data) => {
        this.progressRecords = data.progress;
        this.participants = data.participants;
        this.sessions = data.sessions;
        this.members = data.members;
        this.dataSource.data = this.progressRecords;
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading data', error, { component: 'ProgressManagementComponent', action: 'loadData', programId: this.program.id });
        this.snackBar.open('Error loading progress', 'Close', { duration: 3000 });
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
    let filteredData = [...this.progressRecords];

    if (this.participantFilter !== null) {
      filteredData = filteredData.filter(p => p.participant_id === this.participantFilter);
    }

    if (this.progressTypeFilter) {
      filteredData = filteredData.filter(p => p.progress_type === this.progressTypeFilter);
    }

    this.dataSource.data = filteredData;
  }

  onParticipantFilterChange(): void {
    this.applyFilters();
  }

  onProgressTypeFilterChange(): void {
    this.applyFilters();
  }

  getParticipantName(participantId: number): string {
    const participant = this.participants.find(p => p.id === participantId);
    if (participant) {
      const member = this.members.find(m => m.id === participant.people_id);
      if (member) {
        return `${member.first_name} ${member.last_name}`;
      }
    }
    return 'Unknown';
  }

  getProgressDetails(progress: ProgramProgress): string {
    switch (progress.progress_type) {
      case 'content_completion':
        return `Content ID: ${progress.content_id || 'N/A'} (${progress.completion_percentage || 0}%)`;
      case 'session_completion':
        const session = this.sessions.find(s => s.id === progress.session_id);
        if (session) {
          const date = new Date(session.session_date);
          return `Session: ${date.toLocaleString()}`;
        }
        return `Session ID: ${progress.session_id}`;
      case 'milestone':
        return progress.milestone_name || 'Milestone';
      default:
        return 'N/A';
    }
  }

  openProgressDialog(participant?: ProgramParticipant, progress?: ProgramProgress): void {
    const targetParticipant = participant || this.data.participant;
    if (!targetParticipant) {
      this.snackBar.open('Please select a participant first', 'Close', { duration: 3000 });
      return;
    }

    const dialogRef = this.dialog.open(ProgressDialogComponent, {
      width: '600px',
      data: {
        progress: progress || null,
        program: this.program,
        participant: targetParticipant,
        sessions: this.sessions
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  viewProgress(progress: ProgramProgress): void {
    const participant = this.participants.find(p => p.id === progress.participant_id);
    if (!participant) return;

    this.dialog.open(ProgressDialogComponent, {
      width: '600px',
      data: {
        progress: progress,
        program: this.program,
        participant: participant,
        sessions: this.sessions,
        viewMode: true
      }
    });
  }

  editProgress(progress: ProgramProgress): void {
    const participant = this.participants.find(p => p.id === progress.participant_id);
    if (!participant) return;

    this.openProgressDialog(participant, progress);
  }

  deleteProgress(progress: ProgramProgress): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Progress Record',
        message: `Are you sure you want to delete this progress record?`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.programService.deleteProgramProgress(progress.id).subscribe({
          next: () => {
            this.snackBar.open('Progress record deleted successfully', 'Close', { duration: 3000 });
            this.loadData();
          },
          error: (error) => {
            this.logger.error('Error deleting progress', error, { component: 'ProgressManagementComponent', action: 'deleteProgress', progressId: progress.id, programId: this.program.id });
            this.snackBar.open('Error deleting progress', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  getProgressTypeColor(progressType: string): string {
    switch (progressType) {
      case 'content_completion':
        return 'primary';
      case 'session_completion':
        return 'accent';
      case 'milestone':
        return 'warn';
      default:
        return '';
    }
  }

  onClose(): void {
    this.dialogRef.close();
  }
}

