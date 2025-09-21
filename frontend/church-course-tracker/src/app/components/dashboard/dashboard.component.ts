import { Component, OnInit } from '@angular/core';
import { ReportService } from '../../services/report.service';
import { CourseService } from '../../services/course.service';
import { EnrollmentService } from '../../services/enrollment.service';
import { DashboardStats, Course, Enrollment } from '../../models';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  stats: DashboardStats | null = null;
  recentCourses: Course[] = [];
  recentEnrollments: Enrollment[] = [];
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

  enrollmentTrendsData: ChartData<'line'> = {
    labels: [],
    datasets: [{
      label: 'New Enrollments',
      data: [],
      borderColor: '#2196F3',
      backgroundColor: 'rgba(33, 150, 243, 0.1)',
      tension: 0.4
    }]
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

  constructor(
    private reportService: ReportService,
    private courseService: CourseService,
    private enrollmentService: EnrollmentService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoading = true;
    
    // Load dashboard stats
    this.reportService.getDashboardStats().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.updateCompletionChart(stats);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading dashboard stats:', error);
        this.isLoading = false;
      }
    });

    // Load recent courses
    this.courseService.getCourses({ limit: 5, sort: 'created_at', order: 'desc' }).subscribe({
      next: (courses) => {
        this.recentCourses = courses;
      },
      error: (error) => {
        console.error('Error loading recent courses:', error);
      }
    });

    // Load recent enrollments
    this.enrollmentService.getEnrollments({ limit: 5, sort: 'enrolled_at', order: 'desc' }).subscribe({
      next: (enrollments) => {
        this.recentEnrollments = enrollments;
      },
      error: (error) => {
        console.error('Error loading recent enrollments:', error);
      }
    });

    // Load completion trends
    this.loadCompletionTrends();
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

  private loadCompletionTrends(): void {
    this.reportService.getCompletionTrends({ days: 30 }).subscribe({
      next: (trends) => {
        const labels = trends.map(t => new Date(t.date).toLocaleDateString());
        const data = trends.map(t => t.enrollments);
        
        this.enrollmentTrendsData = {
          ...this.enrollmentTrendsData,
          labels: labels,
          datasets: [{
            ...this.enrollmentTrendsData.datasets[0],
            data: data
          }]
        };
      },
      error: (error) => {
        console.error('Error loading completion trends:', error);
      }
    });
  }

  getCompletionRate(): number {
    return this.stats?.completion_rate || 0;
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
}
