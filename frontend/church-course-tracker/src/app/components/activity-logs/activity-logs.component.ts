import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PageEvent } from '@angular/material/paginator';
import { AuditService } from '../../services/audit.service';
import { AuthService } from '../../services/auth.service';
import { LoggerService } from '../../services/logger.service';
import { 
  AuditLog, 
  getActionDisplayName,
  getActionIcon,
  getActionColor,
  formatAuditTimestamp,
  getTableDisplayName
} from '../../models';

@Component({
    selector: 'app-activity-logs',
    templateUrl: './activity-logs.component.html',
    styleUrls: ['./activity-logs.component.scss'],
    standalone: false
})
export class ActivityLogsComponent implements OnInit {
  activityLogs: AuditLog[] = [];
  isLoading = false;
  totalCount = 0;
  currentPage = 0;
  pageSize = 50;
  
  startDate: string | null = null;
  endDate: string | null = null;
  
  // Utility functions for template
  getActionDisplayName = getActionDisplayName;
  getActionIcon = getActionIcon;
  getActionColor = getActionColor;
  formatAuditTimestamp = formatAuditTimestamp;
  getTableDisplayName = getTableDisplayName;
  
  displayedColumns: string[] = ['timestamp', 'table', 'action', 'record_id', 'changed_by'];

  constructor(
    private auditService: AuditService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private logger: LoggerService
  ) {}

  ngOnInit(): void {
    // Check if user has permission (staff or admin)
    if (!this.authService.hasAnyRole(['admin', 'staff'])) {
      this.snackBar.open('You do not have permission to view activity logs', 'Close', { duration: 5000 });
      return;
    }
    
    this.loadActivityLogs();
  }

  loadActivityLogs(): void {
    this.isLoading = true;
    
    const skip = this.currentPage * this.pageSize;
    
    this.auditService.getStaffActivityLogs(
      skip,
      this.pageSize,
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (logs) => {
        this.activityLogs = logs;
        this.totalCount = logs.length; // Note: API should return total count
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading activity logs', error, { component: 'ActivityLogsComponent', action: 'loadActivityLogs' });
        this.snackBar.open('Error loading activity logs', 'Close', { duration: 5000 });
        this.isLoading = false;
      }
    });
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadActivityLogs();
  }

  onDateFilterChange(): void {
    this.currentPage = 0;
    this.loadActivityLogs();
  }

  clearFilters(): void {
    this.startDate = null;
    this.endDate = null;
    this.currentPage = 0;
    this.loadActivityLogs();
  }
}

