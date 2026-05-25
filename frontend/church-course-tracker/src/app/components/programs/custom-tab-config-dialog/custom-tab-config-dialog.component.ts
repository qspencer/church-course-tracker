import { Component, OnInit, inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramService } from '../../../services/program.service';
import { PlanningCenterService } from '../../../services/planning-center.service';
import {
  PlanningCenterTabConfig,
  TabFieldMapping,
  TabFieldTargetType,
  MappingRule,
  PlanningCenterTab,
  PlanningCenterFieldDefinition
} from '../../../models/program.model';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatProgressBar } from '@angular/material/progress-bar';
import { MatFormField, MatLabel, MatHint } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatList, MatListItem, MatListItemTitle, MatListItemLine, MatListItemMeta, MatDivider } from '@angular/material/list';
import { MatIcon } from '@angular/material/icon';
import { MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent } from '@angular/material/card';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatChipSet, MatChip } from '@angular/material/chips';
import { MatCheckbox } from '@angular/material/checkbox';

export interface CustomTabConfigDialogData {
  programId: number;
  currentConfig?: PlanningCenterTabConfig;
}

@Component({
    selector: 'app-custom-tab-config-dialog',
    templateUrl: './custom-tab-config-dialog.component.html',
    styleUrls: ['./custom-tab-config-dialog.component.scss'],
    imports: [MatDialogTitle, CdkScrollable, MatDialogContent, MatProgressBar, MatFormField, MatLabel, MatInput, ReactiveFormsModule, FormsModule, MatHint, MatButton, MatList, MatListItem, MatListItemTitle, MatListItemLine, MatIconButton, MatListItemMeta, MatIcon, MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent, MatSelect, MatOption, MatDivider, MatChipSet, MatChip, MatCheckbox, MatDialogActions]
})
export class CustomTabConfigDialogComponent implements OnInit {
  dialogRef = inject<MatDialogRef<CustomTabConfigDialogComponent>>(MatDialogRef);
  data = inject<CustomTabConfigDialogData>(MAT_DIALOG_DATA);
  private programService = inject(ProgramService);
  private pcService = inject(PlanningCenterService);
  private snackBar = inject(MatSnackBar);

  loading = false;
  step: 'discover' | 'select-tab' | 'configure-mappings' | 'review' = 'discover';

  // Discovery
  samplePersonId = '';
  availableTabs: PlanningCenterTab[] = [];
  selectedTab?: PlanningCenterTab;

  // Field configuration
  fieldDefinitions: PlanningCenterFieldDefinition[] = [];
  fieldMappings: TabFieldMapping[] = [];

  // Configuration
  config: PlanningCenterTabConfig = {
    enabled: true,
    tab_slug: '',
    tab_name: '',
    field_mappings: [],
    default_status: 'active',
    update_existing: false,
    sync_on_import: true
  };

  targetTypes: { value: TabFieldTargetType; label: string }[] = [
    { value: 'participant_role', label: 'Participant Role' },
    { value: 'participant_status', label: 'Participant Status' },
    { value: 'participant_start_date', label: 'Start Date' },
    { value: 'participant_end_date', label: 'End Date' },
    { value: 'participant_notes', label: 'Notes' },
    { value: 'participant_progress', label: 'Progress Percentage' },
    { value: 'ignore', label: 'Ignore Field' }
  ];

  constructor() {
    const data = this.data;

    if (data.currentConfig) {
      this.config = { ...data.currentConfig };
      this.step = 'review';
    }
  }

  ngOnInit(): void {}

  discoverTabs(): void {
    if (!this.samplePersonId.trim()) {
      this.snackBar.open('Please enter a Planning Center Person ID', 'Close', { duration: 3000 });
      return;
    }

    this.loading = true;
    this.programService.getPlanningCenterTabs(this.samplePersonId.trim()).subscribe({
      next: (tabs) => {
        this.availableTabs = tabs;
        if (tabs.length === 0) {
          this.snackBar.open('No custom tabs found for this person', 'Close', { duration: 5000 });
        } else {
          this.step = 'select-tab';
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error discovering tabs:', error);
        this.snackBar.open(
          error.error?.detail || 'Failed to discover tabs. Please check the Person ID.',
          'Close',
          { duration: 5000 }
        );
        this.loading = false;
      }
    });
  }

  selectTab(tab: PlanningCenterTab): void {
    this.selectedTab = tab;
    this.config.tab_slug = tab.attributes.slug;
    this.config.tab_name = tab.attributes.name;

    this.loading = true;
    this.programService.getTabFieldDefinitions(tab.id).subscribe({
      next: (fieldDefs) => {
        this.fieldDefinitions = fieldDefs;
        this.generateDefaultMappings();
        this.step = 'configure-mappings';
        this.loading = false;
      },
      error: (error) => {
        console.error('Error fetching field definitions:', error);
        this.snackBar.open('Failed to load field definitions', 'Close', { duration: 5000 });
        this.loading = false;
      }
    });
  }

  generateDefaultMappings(): void {
    this.fieldMappings = this.fieldDefinitions.map(fieldDef => {
      const attrs = fieldDef.attributes;
      const mapping: TabFieldMapping = {
        pc_field_name: attrs.name,
        pc_field_slug: attrs.slug,
        pc_field_type: attrs.data_type,
        target_type: this.suggestTargetType(attrs.name, attrs.data_type),
        mapping_rules: null
      };

      // Generate mapping rules for select fields
      if (attrs.data_type === 'select' && attrs.options && attrs.options.length > 0) {
        if (mapping.target_type === 'participant_role') {
          mapping.mapping_rules = attrs.options.map(option => ({
            when: option,
            assign_role: option
          }));
        } else if (mapping.target_type === 'participant_status') {
          mapping.mapping_rules = attrs.options.map(option => ({
            when: option,
            assign_status: option.toLowerCase()
          }));
        }
      }

      return mapping;
    });
  }

  suggestTargetType(fieldName: string, dataType: string): TabFieldTargetType {
    const lowerName = fieldName.toLowerCase();

    if (lowerName.includes('role')) {
      return 'participant_role';
    } else if (lowerName.includes('status')) {
      return 'participant_status';
    } else if (lowerName.includes('start') && lowerName.includes('date')) {
      return 'participant_start_date';
    } else if (lowerName.includes('end') && lowerName.includes('date')) {
      return 'participant_end_date';
    } else if (lowerName.includes('note') || lowerName.includes('comment')) {
      return 'participant_notes';
    } else if (lowerName.includes('progress') || lowerName.includes('percent')) {
      return 'participant_progress';
    }

    return 'ignore';
  }

  onTargetTypeChange(mapping: TabFieldMapping): void {
    // Clear mapping rules when target type changes
    mapping.mapping_rules = null;

    // For select fields with role/status, regenerate rules
    const fieldDef = this.fieldDefinitions.find(
      f => f.attributes.slug === mapping.pc_field_slug
    );

    if (fieldDef && fieldDef.attributes.data_type === 'select' && fieldDef.attributes.options) {
      if (mapping.target_type === 'participant_role') {
        mapping.mapping_rules = fieldDef.attributes.options.map(option => ({
          when: option,
          assign_role: option
        }));
      } else if (mapping.target_type === 'participant_status') {
        mapping.mapping_rules = fieldDef.attributes.options.map(option => ({
          when: option,
          assign_status: option.toLowerCase()
        }));
      }
    }
  }

  reviewConfiguration(): void {
    this.config.field_mappings = this.fieldMappings;
    this.step = 'review';
  }

  saveConfiguration(): void {
    this.dialogRef.close(this.config);
  }

  cancel(): void {
    this.dialogRef.close();
  }

  goBack(): void {
    if (this.step === 'select-tab') {
      this.step = 'discover';
    } else if (this.step === 'configure-mappings') {
      this.step = 'select-tab';
    } else if (this.step === 'review') {
      this.step = 'configure-mappings';
    }
  }

  addMappingRule(mapping: TabFieldMapping): void {
    if (!mapping.mapping_rules) {
      mapping.mapping_rules = [];
    }

    if (mapping.target_type === 'participant_role') {
      mapping.mapping_rules.push({ when: '', assign_role: '' });
    } else if (mapping.target_type === 'participant_status') {
      mapping.mapping_rules.push({ when: '', assign_status: '' });
    }
  }

  removeMappingRule(mapping: TabFieldMapping, index: number): void {
    if (mapping.mapping_rules) {
      mapping.mapping_rules.splice(index, 1);
    }
  }

  getActiveFieldMappings(): TabFieldMapping[] {
    return this.fieldMappings.filter(m => m.target_type !== 'ignore');
  }

  getIgnoredFieldMappings(): TabFieldMapping[] {
    return this.fieldMappings.filter(m => m.target_type === 'ignore');
  }

  getActiveConfigMappings(): TabFieldMapping[] {
    return this.config.field_mappings.filter(m => m.target_type !== 'ignore');
  }

  getTargetTypeLabel(targetType: TabFieldTargetType): string {
    const type = this.targetTypes.find(t => t.value === targetType);
    return type ? type.label : targetType;
  }
}

