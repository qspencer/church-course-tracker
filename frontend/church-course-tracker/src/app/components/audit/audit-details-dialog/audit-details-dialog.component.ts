import { Component, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';

import {
  AuditLog,
  formatAuditTimestamp,
  getActionColor,
  getActionDisplayName,
  getActionIcon,
  getTableDisplayName
} from '../../../models';
import { MatChip, MatChipAvatar } from '@angular/material/chips';
import { MatIcon } from '@angular/material/icon';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatButton } from '@angular/material/button';

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
    imports: [MatDialogTitle, MatChip, MatIcon, MatChipAvatar, CdkScrollable, MatDialogContent, MatDialogActions, MatButton]
})
export class AuditDetailsDialogComponent {
  dialogRef = inject<MatDialogRef<AuditDetailsDialogComponent>>(MatDialogRef);
  data = inject<AuditDetailsDialogData>(MAT_DIALOG_DATA);

  readonly log: AuditLog;
  readonly userName: string;
  readonly changeEntries: AuditChangeEntry[];

  constructor() {
    const data = this.data;

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



