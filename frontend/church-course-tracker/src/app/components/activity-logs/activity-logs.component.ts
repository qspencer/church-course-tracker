import { Component, OnInit, inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PageEvent, MatPaginator } from '@angular/material/paginator';
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
import { MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent } from '@angular/material/card';
import { MatIcon } from '@angular/material/icon';
import { MatFormField, MatLabel, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatDatepickerInput, MatDatepickerToggle, MatDatepicker } from '@angular/material/datepicker';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { MatChip } from '@angular/material/chips';

@Component({
    selector: 'app-activity-logs',
    templateUrl: './activity-logs.component.html',
    styleUrls: ['./activity-logs.component.scss'],
    imports: [MatCard, MatCardHeader, MatCardTitle, MatIcon, MatCardSubtitle, MatCardContent, MatFormField, MatLabel, MatInput, MatDatepickerInput, ReactiveFormsModule, FormsModule, MatDatepickerToggle, MatSuffix, MatDatepicker, MatButton, MatProgressSpinner, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatChip, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class ActivityLogsComponent implements OnInit {
  private auditService = inject(AuditService);
  private authService = inject(AuthService);
  private snackBar = inject(MatSnackBar);
  private logger = inject(LoggerService);

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

