import { Component, OnInit, OnDestroy } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subject, takeUntil } from 'rxjs';

import { AuditService } from '../../services/audit.service';
import { AuthService } from '../../services/auth.service';
import { UserService } from '../../services/user.service';
import { 
  AuditLog, 
  AuditLogFilters, 
  AuditSummary, 
  AuditExportOptions,
  getActionDisplayName,
  getActionIcon,
  getActionColor,
  formatAuditTimestamp,
  getTableDisplayName,
  formatAuditValues
} from '../../models';

@Component({
  selector: 'app-audit',
  templateUrl: './audit.component.html',
  styleUrls: ['./audit.component.scss']
})
export class AuditComponent implements OnInit, OnDestroy {
  auditLogs: AuditLog[] = [];
  summary: AuditSummary | null = null;
  isLoading = false;
  totalCount = 0;
  currentPage = 0;
  pageSize = 50;
  
  // Filters
  filters: AuditLogFilters = {
    skip: 0,
    limit: this.pageSize
  };
  
  // Available filter options
  availableTables: string[] = [];
  availableActions: string[] = ['insert', 'update', 'delete'];
  availableUsers: any[] = [];
  
  // Utility functions for template
  getActionDisplayName = getActionDisplayName;
  getActionIcon = getActionIcon;
  getActionColor = getActionColor;
  formatAuditTimestamp = formatAuditTimestamp;
  getTableDisplayName = getTableDisplayName;
  formatAuditValues = formatAuditValues;
  
  private destroy$ = new Subject<void>();

  constructor(
    private auditService: AuditService,
    private authService: AuthService,
    private userService: UserService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadAuditLogs();
    this.loadSummary();
    this.loadFilterOptions();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadAuditLogs(): void {
    this.isLoading = true;
    
    this.auditService.getAuditLogs(this.filters).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (logs) => {
        this.auditLogs = logs;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading audit logs:', error);
        this.snackBar.open('Error loading audit logs', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  loadSummary(): void {
    this.auditService.getAuditSummary(
      this.filters.start_date,
      this.filters.end_date
    ).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (summary) => {
        this.summary = summary;
        this.totalCount = summary.total_logs;
      },
      error: (error) => {
        console.error('Error loading audit summary:', error);
      }
    });
  }

  loadFilterOptions(): void {
    // Load users for filter dropdown
    this.userService.getUsers().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (users) => {
        this.availableUsers = users;
      },
      error: (error) => {
        console.error('Error loading users:', error);
      }
    });
  }

  onFilterChange(): void {
    this.filters.skip = 0;
    this.currentPage = 0;
    this.loadAuditLogs();
    this.loadSummary();
  }

  onPageChange(event: any): void {
    this.currentPage = event.pageIndex;
    this.filters.skip = event.pageIndex * event.pageSize;
    this.filters.limit = event.pageSize;
    this.loadAuditLogs();
  }

  clearFilters(): void {
    this.filters = {
      skip: 0,
      limit: this.pageSize
    };
    this.currentPage = 0;
    this.loadAuditLogs();
    this.loadSummary();
  }

  exportAuditLogs(format: 'csv' | 'json'): void {
    const options: AuditExportOptions = {
      format,
      start_date: this.filters.start_date,
      end_date: this.filters.end_date,
      table_name: this.filters.table_name
    };
    
    this.auditService.downloadAuditLogs(options);
    this.snackBar.open(`Audit logs exported as ${format.toUpperCase()}`, 'Close', { duration: 3000 });
  }

  viewAuditDetails(log: AuditLog): void {
    // TODO: Implement audit detail dialog
    console.log('View audit details:', log);
  }

  getUserName(userId: number): string {
    const user = this.availableUsers.find(u => u.id === userId);
    return user ? user.full_name : `User ${userId}`;
  }

  getTableIcon(tableName: string): string {
    switch (tableName) {
      case 'users': return 'people';
      case 'courses': return 'school';
      case 'course_content': return 'description';
      case 'course_modules': return 'folder';
      case 'enrollments': return 'assignment';
      case 'audit_log': return 'history';
      default: return 'table_chart';
    }
  }
}


