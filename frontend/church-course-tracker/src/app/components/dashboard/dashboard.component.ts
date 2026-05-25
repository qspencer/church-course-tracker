import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Router, RouterLink } from '@angular/router';
import { ReportService } from '../../services/report.service';
import { CourseService } from '../../services/course.service';
import { EnrollmentService } from '../../services/enrollment.service';
import { ProgramService } from '../../services/program.service';
import { LoggerService } from '../../services/logger.service';
import { DashboardStats, ProgramStats, Course, Enrollment, Program, ProgramParticipant, ProgramPairing, ProgramSession, CompletionTrendsResponse } from '../../models';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { MatButtonToggleGroup, MatButtonToggle } from '@angular/material/button-toggle';
import { MatIcon } from '@angular/material/icon';
import { MatButton } from '@angular/material/button';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatCard, MatCardContent, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardActions } from '@angular/material/card';
import { NgChartsModule } from 'ng2-charts';
import { MatChip } from '@angular/material/chips';
import { MatProgressBar } from '@angular/material/progress-bar';
import { SlicePipe, DecimalPipe, DatePipe } from '@angular/common';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss'],
    imports: [MatButtonToggleGroup, MatButtonToggle, MatIcon, MatButton, MatProgressSpinner, MatCard, MatCardContent, MatCardHeader, MatCardTitle, NgChartsModule, MatCardSubtitle, MatChip, MatCardActions, RouterLink, MatProgressBar, SlicePipe, DecimalPipe, DatePipe]
})
export class DashboardComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  viewMode: 'courses' | 'programs' = 'courses';
  stats: DashboardStats | null = null;
  programStats: ProgramStats | null = null;
  recentCourses: Course[] = [];
  recentEnrollments: Enrollment[] = [];
  recentPrograms: Program[] = [];
  recentParticipants: ProgramParticipant[] = [];
  isLoading = true;

  // Chart configurations
  completionChartData: ChartData<'doughnut'> = {
    labels: ['Completed', 'In Progress', 'Not Started'],
    datasets: [{
      data: [0, 0, 0],
      backgroundColor: ['#4CAF50', '#FF9800', '#F44336'],
      hoverBackgroundColor: ['#45a049', '#e68900', '#da190b']
    }]
  };

  completionChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom'
      },
      title: {
        display: true,
        text: 'Course Completion Overview'
      }
    }
  };

  programCompletionChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom'
      },
      title: {
        display: true,
        text: 'Program Completion Overview'
      }
    }
  };

  enrollmentTrendsData: ChartData<'line'> = {
    labels: [],
    datasets: [
      {
        label: 'New Enrollments',
        data: [],
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4
      },
      {
        label: 'Completions',
        data: [],
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        borderDash: [5, 5],
        tension: 0.4
      }
    ]
  };

  enrollmentTrendsOptions: ChartConfiguration['options'] = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
      },
      title: {
        display: true,
        text: 'Enrollment Trends (Last 30 Days)'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  programTrendsOptions: ChartConfiguration['options'] = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
      },
      title: {
        display: true,
        text: 'Program Activity Trends (Last 30 Days)'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  programTrendsData: ChartData<'line'> = {
    labels: [],
    datasets: [
      {
        label: 'New Participants',
        data: [],
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4
      },
      {
        label: 'New Pairings',
        data: [],
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        borderDash: [5, 5],
        tension: 0.4
      }
    ]
  };

  constructor(
    private router: Router,
    private reportService: ReportService,
    private courseService: CourseService,
    private enrollmentService: EnrollmentService,
    private programService: ProgramService,
    private logger: LoggerService
  ) {}

  ngOnInit(): void {
    // Load dashboard data on initialization
    this.loadDashboardData();
  }

  onViewModeChange(mode: 'courses' | 'programs'): void {
    this.viewMode = mode;
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoading = true;
    
    if (this.viewMode === 'courses') {
      this.loadCoursesData();
    } else {
      this.loadProgramsData();
    }
  }

  loadCoursesData(): void {
    // Load dashboard stats
    this.reportService.getDashboardStats().pipe(takeUntil(this.destroy$)).subscribe({
      next: (stats) => {
        this.stats = stats;
        this.updateCompletionChart(stats);
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading dashboard stats', error);
        this.isLoading = false;
      }
    });

    // Load recent courses
    this.courseService.getCourses({ limit: 5, sort: 'created_at', order: 'desc' }).pipe(takeUntil(this.destroy$)).subscribe({
      next: (courses) => {
        this.recentCourses = courses;
      },
      error: (error) => {
        this.logger.error('Error loading recent courses', error);
      }
    });

    // Load recent enrollments
    this.enrollmentService.getEnrollments({ limit: 5 }).pipe(takeUntil(this.destroy$)).subscribe({
      next: (enrollments) => {
        this.recentEnrollments = enrollments;
      },
      error: (error) => {
        this.logger.error('Error loading recent enrollments', error);
      }
    });

    // Load completion trends
    this.loadCompletionTrends();
  }

  loadProgramsData(): void {
    // Load all programs to calculate stats
    this.programService.getPrograms().subscribe({
      next: (programs) => {
        this.calculateProgramStats(programs);
        this.recentPrograms = programs
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 5);
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading programs', error);
        this.isLoading = false;
      }
    });

    // Load program participants for all programs
    this.loadProgramParticipants();
  }

  private calculateProgramStats(programs: Program[]): void {
    const totalPrograms = programs.length;
    const activePrograms = programs.filter(p => p.is_active).length;
    
    // We'll need to load participants, pairings, and sessions to get accurate stats
    // For now, we'll set placeholders and load them separately
    this.programStats = {
      total_programs: totalPrograms,
      active_programs: activePrograms,
      total_participants: 0,
      active_participants: 0,
      total_pairings: 0,
      active_pairings: 0,
      total_sessions: 0,
      completion_rate: 0
    };

    // Load detailed stats
    this.loadDetailedProgramStats(programs);
  }

  private loadDetailedProgramStats(programs: Program[]): void {
    let participantsCount = 0;
    let activeParticipantsCount = 0;
    let pairingsCount = 0;
    let activePairingsCount = 0;
    let sessionsCount = 0;
    let completedParticipants = 0;
    let loadedCount = 0;
    const totalPrograms = programs.length;

    if (totalPrograms === 0) {
      if (this.programStats) {
        this.updateProgramStats(0, 0, 0, 0, 0, 0);
      }
      return;
    }

    const expectedCalls = totalPrograms * 3;
    let hasUpdated = false;

    programs.forEach(program => {
      // Load participants
      this.programService.getProgramParticipants(program.id).subscribe({
        next: (participants) => {
          participantsCount += participants.length;
          activeParticipantsCount += participants.filter(p => p.status === 'active').length;
          completedParticipants += participants.filter(p => p.progress_percentage >= 100).length;
          
          loadedCount++;
          if (loadedCount === expectedCalls && !hasUpdated) {
            hasUpdated = true;
            this.updateProgramStats(participantsCount, activeParticipantsCount, pairingsCount, activePairingsCount, sessionsCount, completedParticipants);
          }
        },
        error: (error) => {
          this.logger.error('Error loading participants for program', error, { component: 'DashboardComponent', action: 'loadDetailedProgramStats', programId: program.id });
          loadedCount++;
          if (loadedCount === expectedCalls && !hasUpdated) {
            hasUpdated = true;
            this.updateProgramStats(participantsCount, activeParticipantsCount, pairingsCount, activePairingsCount, sessionsCount, completedParticipants);
          }
        }
      });

      // Load pairings
      this.programService.getProgramPairings(program.id).subscribe({
        next: (pairings) => {
          pairingsCount += pairings.length;
          activePairingsCount += pairings.filter(p => p.status === 'active').length;
          
          loadedCount++;
          if (loadedCount === expectedCalls && !hasUpdated) {
            hasUpdated = true;
            this.updateProgramStats(participantsCount, activeParticipantsCount, pairingsCount, activePairingsCount, sessionsCount, completedParticipants);
          }
        },
        error: (error) => {
          this.logger.error(`Error loading pairings for program ${program.id}`, error);
          loadedCount++;
          if (loadedCount === expectedCalls && !hasUpdated) {
            hasUpdated = true;
            this.updateProgramStats(participantsCount, activeParticipantsCount, pairingsCount, activePairingsCount, sessionsCount, completedParticipants);
          }
        }
      });

      // Load sessions
      this.programService.getProgramSessions(program.id).subscribe({
        next: (sessions) => {
          sessionsCount += sessions.length;
          
          loadedCount++;
          if (loadedCount === expectedCalls && !hasUpdated) {
            hasUpdated = true;
            this.updateProgramStats(participantsCount, activeParticipantsCount, pairingsCount, activePairingsCount, sessionsCount, completedParticipants);
          }
        },
        error: (error) => {
          this.logger.error(`Error loading sessions for program ${program.id}`, error);
          loadedCount++;
          if (loadedCount === expectedCalls && !hasUpdated) {
            hasUpdated = true;
            this.updateProgramStats(participantsCount, activeParticipantsCount, pairingsCount, activePairingsCount, sessionsCount, completedParticipants);
          }
        }
      });
    });
  }

  private updateProgramStats(
    totalParticipants: number,
    activeParticipants: number,
    totalPairings: number,
    activePairings: number,
    totalSessions: number,
    completedParticipants: number
  ): void {
    if (this.programStats) {
      this.programStats.total_participants = totalParticipants;
      this.programStats.active_participants = activeParticipants;
      this.programStats.total_pairings = totalPairings;
      this.programStats.active_pairings = activePairings;
      this.programStats.total_sessions = totalSessions;
      this.programStats.completion_rate = totalParticipants > 0 
        ? (completedParticipants / totalParticipants) * 100 
        : 0;
      
      this.updateProgramCompletionChart();
    }
  }

  private loadProgramParticipants(): void {
    // Load participants from all programs for recent activity
    this.programService.getPrograms().subscribe({
      next: (programs) => {
        const allParticipants: Array<{participant: ProgramParticipant, programTitle: string}> = [];
        let loadedCount = 0;
        const totalPrograms = programs.length;
        
        if (totalPrograms === 0) {
          this.recentParticipants = [];
          return;
        }

        let hasUpdated = false;
        programs.forEach(program => {
          this.programService.getProgramParticipants(program.id).subscribe({
            next: (participants) => {
              participants.forEach(p => {
                allParticipants.push({ participant: p, programTitle: program.title });
              });
              
              loadedCount++;
              if (loadedCount === totalPrograms && !hasUpdated) {
                hasUpdated = true;
                this.recentParticipants = allParticipants
                  .sort((a, b) => new Date(b.participant.created_at).getTime() - new Date(a.participant.created_at).getTime())
                  .slice(0, 5)
                  .map(item => item.participant);
              }
            },
            error: (error) => {
              this.logger.error(`Error loading participants for program ${program.id}`, error);
              loadedCount++;
              if (loadedCount === totalPrograms && !hasUpdated) {
                hasUpdated = true;
                this.recentParticipants = allParticipants
                  .sort((a, b) => new Date(b.participant.created_at).getTime() - new Date(a.participant.created_at).getTime())
                  .slice(0, 5)
                  .map(item => item.participant);
              }
            }
          });
        });
      },
      error: (error) => {
        this.logger.error('Error loading programs for participants', error);
        this.recentParticipants = [];
      }
    });
  }

  private updateCompletionChart(stats: DashboardStats): void {
    const completed = stats.completed_enrollments;
    const inProgress = stats.total_enrollments - stats.completed_enrollments;
    const notStarted = Math.max(0, stats.total_courses * 10 - stats.total_enrollments); // Estimated

    this.completionChartData = {
      ...this.completionChartData,
      datasets: [{
        ...this.completionChartData.datasets[0],
        data: [completed, inProgress, notStarted]
      }]
    };
  }

  private updateProgramCompletionChart(): void {
    if (!this.programStats) return;
    
    const completed = this.programStats.total_participants > 0 
      ? Math.round((this.programStats.completion_rate / 100) * this.programStats.total_participants)
      : 0;
    const inProgress = this.programStats.active_participants - completed;
    const notStarted = Math.max(0, this.programStats.total_participants - this.programStats.active_participants);

    this.completionChartData = {
      ...this.completionChartData,
      labels: ['Completed', 'In Progress', 'Not Started'],
      datasets: [{
        ...this.completionChartData.datasets[0],
        data: [completed, inProgress, notStarted]
      }]
    };
  }

  private loadCompletionTrends(): void {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 30);
    
    this.reportService.getCompletionTrends({ 
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    }).subscribe({
      next: (response: CompletionTrendsResponse) => {
        const trends = response.trends || [];
        const labels = trends.map(t => new Date(t.date).toLocaleDateString());
        const enrollmentData = trends.map(t => t.enrollments);
        const completionData = trends.map(t => t.completions ?? 0);
        
        this.enrollmentTrendsData = {
          labels,
          datasets: [
            {
              ...this.enrollmentTrendsData.datasets[0],
              data: enrollmentData
            },
            {
              ...this.enrollmentTrendsData.datasets[1],
              data: completionData
            }
          ]
        };
      },
      error: (error) => {
        this.logger.error('Error loading completion trends', error);
      }
    });
  }

  getCompletionRate(): number {
    if (this.viewMode === 'courses') {
      return this.stats?.completion_rate || 0;
    } else {
      return this.programStats?.completion_rate || 0;
    }
  }

  getCompletionRateColor(): string {
    const rate = this.getCompletionRate();
    if (rate >= 80) return '#4CAF50';
    if (rate >= 60) return '#FF9800';
    return '#F44336';
  }

  refreshDashboard(): void {
    this.loadDashboardData();
  }

  getEnrollmentMemberName(enrollment: Enrollment): string {
    const person = enrollment.person || enrollment.people;
    if (person) {
      const first = person.first_name ?? '';
      const last = person.last_name ?? '';
      const full = `${first} ${last}`.trim();
      if (full) {
        return full;
      }
    }
    const fallbackId =
      enrollment.person_id ??
      enrollment.people?.id ??
      enrollment.person?.id ??
      enrollment.people_id ?? // legacy compat if backend ever sends
      enrollment.id;
    return `Member #${fallbackId}`;
  }

  navigateToCourses(): void {
    this.router.navigate(['/courses']);
  }

  navigateToEnrollments(): void {
    this.router.navigate(['/enrollments']);
  }

  navigateToMembers(): void {
    this.router.navigate(['/members']);
  }

  navigateToPrograms(): void {
    this.router.navigate(['/programs']);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
