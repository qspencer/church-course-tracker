import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import {
  AuditLog,
  formatAuditTimestamp,
  getActionColor,
  getActionDisplayName,
  getActionIcon,
  getTableDisplayName
} from '../../../models';

export interface AuditDetailsDialogData {
  log: AuditLog;
  userName?: string;
}

interface AuditChangeEntry {
  key: string;
  oldValue: unknown;
  newValue: unknown;
}

@Component({
    selector: 'app-audit-details-dialog',
    templateUrl: './audit-details-dialog.component.html',
    styleUrls: ['./audit-details-dialog.component.scss'],
    standalone: false
})
export class AuditDetailsDialogComponent {
  readonly log: AuditLog;
  readonly userName: string;
  readonly changeEntries: AuditChangeEntry[];

  constructor(
    public dialogRef: MatDialogRef<AuditDetailsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: AuditDetailsDialogData
  ) {
    this.log = data.log;
    this.userName = data.userName || 'System';
    this.changeEntries = this.buildChangeEntries(this.log);
  }

  get actionLabel(): string {
    return getActionDisplayName(this.log.action);
  }

  get actionIcon(): string {
    return getActionIcon(this.log.action);
  }

  get actionColor(): string {
    return getActionColor(this.log.action);
  }

  get tableDisplayName(): string {
    return getTableDisplayName(this.log.table_name);
  }

  get formattedTimestamp(): string {
    return formatAuditTimestamp(this.log.changed_at);
  }

  close(): void {
    this.dialogRef.close();
  }

  formatValue(value: unknown): string {
    if (value === null || value === undefined || value === '') {
      return '—';
    }

    if (typeof value === 'object') {
      try {
        return JSON.stringify(value, null, 2);
      } catch (error) {
        return String(value);
      }
    }

    return String(value);
  }

  private buildChangeEntries(log: AuditLog): AuditChangeEntry[] {
    const oldValues = log.old_values || {};
    const newValues = log.new_values || {};
    const keys = new Set<string>([
      ...Object.keys(oldValues),
      ...Object.keys(newValues)
    ]);

    return Array.from(keys)
      .sort((a, b) => a.localeCompare(b))
      .map(key => ({
        key,
        oldValue: oldValues[key],
        newValue: newValues[key]
      }));
  }
}



