import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ReportService } from '../../services/report.service';
import { CourseService } from '../../services/course.service';
import { DashboardStats, ProgressReport, Course, ReportFilters } from '../../models';
import { ChartConfiguration, ChartData } from 'chart.js';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss']
})
export class ReportsComponent implements OnInit {
  dashboardStats: DashboardStats | null = null;
  progressReport: ProgressReport | null = null;
  courses: Course[] = [];
  isLoading = true;
  isGeneratingReport = false;

  filterForm: FormGroup;

  // Chart data
  courseCompletionData: ChartData<'bar'> = {
    labels: [],
    datasets: [{
      label: 'Completion Rate (%)',
      data: [],
      backgroundColor: '#2196F3',
      borderColor: '#1976D2',
      borderWidth: 1
    }]
  };

  courseCompletionOptions: ChartConfiguration['options'] = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      title: {
        display: true,
        text: 'Course Completion Rates'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  enrollmentTrendsData: ChartData<'line'> = {
    labels: [],
    datasets: [{
      label: 'New Enrollments',
      data: [],
      borderColor: '#4CAF50',
      backgroundColor: 'rgba(76, 175, 80, 0.1)',
      tension: 0.4,
      fill: true
    }, {
      label: 'Completions',
      data: [],
      borderColor: '#FF9800',
      backgroundColor: 'rgba(255, 152, 0, 0.1)',
      tension: 0.4,
      fill: true
    }]
  };

  enrollmentTrendsOptions: ChartConfiguration['options'] = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      title: {
        display: true,
        text: 'Enrollment and Completion Trends'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  constructor(
    private fb: FormBuilder,
    private reportService: ReportService,
    private courseService: CourseService,
    private snackBar: MatSnackBar
  ) {
    this.filterForm = this.fb.group({
      start_date: [''],
      end_date: [''],
      course_ids: [[]],
      status: ['']
    });
  }

  ngOnInit(): void {
    this.loadInitialData();
  }

  loadInitialData(): void {
    this.isLoading = true;

    // Load dashboard stats
    this.reportService.getDashboardStats().subscribe({
      next: (stats) => {
        this.dashboardStats = stats;
      },
      error: (error) => {
        console.error('Error loading dashboard stats:', error);
      }
    });

    // Load courses for filter
    this.courseService.getCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
      },
      error: (error) => {
        console.error('Error loading courses:', error);
      }
    });

    // Load initial progress report
    this.generateReport();
  }

  generateReport(): void {
    this.isGeneratingReport = true;
    const filters: ReportFilters = this.filterForm.value;

    this.reportService.getProgressReport(filters).subscribe({
      next: (report) => {
        this.progressReport = report;
        this.updateChartData(report);
        this.isGeneratingReport = false;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error generating report:', error);
        this.isGeneratingReport = false;
        this.isLoading = false;
      }
    });
  }

  updateChartData(report: ProgressReport): void {
    // Update course completion chart
    if (report.course_stats) {
      this.courseCompletionData = {
        labels: report.course_stats.map(stat => stat.course_title),
        datasets: [{
          label: 'Completion Rate (%)',
          data: report.course_stats.map(stat => stat.completion_rate),
          backgroundColor: '#2196F3',
          borderColor: '#1976D2',
          borderWidth: 1
        }]
      };
    }

    // Update enrollment trends chart
    if (report.completion_trends) {
      this.enrollmentTrendsData = {
        labels: report.completion_trends.map(trend => new Date(trend.date).toLocaleDateString()),
        datasets: [{
          label: 'New Enrollments',
          data: report.completion_trends.map(trend => trend.enrollments),
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        }, {
          label: 'Completions',
          data: report.completion_trends.map(trend => trend.completions),
          borderColor: '#FF9800',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          tension: 0.4,
          fill: true
        }]
      };
    }
  }

  exportReport(format: string): void {
    const filters: ReportFilters = this.filterForm.value;
    
    this.reportService.exportReport(format, filters).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `progress-report-${new Date().toISOString().split('T')[0]}.${format}`;
        link.click();
        window.URL.revokeObjectURL(url);
        
        this.snackBar.open(`Report exported as ${format.toUpperCase()}`, 'Close', { duration: 3000 });
      },
      error: (error) => {
        console.error('Error exporting report:', error);
        this.snackBar.open('Error exporting report', 'Close', { duration: 3000 });
      }
    });
  }

  clearFilters(): void {
    this.filterForm.reset();
    this.generateReport();
  }

  getCompletionRateColor(rate: number): string {
    if (rate >= 80) return '#4CAF50';
    if (rate >= 60) return '#FF9800';
    return '#F44336';
  }

  getProgressColor(progress: number): string {
    if (progress >= 80) return '#4CAF50';
    if (progress >= 60) return '#FF9800';
    return '#F44336';
  }
}
