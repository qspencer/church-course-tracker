import { Component, Inject, OnInit, AfterViewInit, ElementRef, viewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatAutocompleteTrigger, MatAutocomplete } from '@angular/material/autocomplete';
import { Observable } from 'rxjs';
import { map, startWith, tap, finalize } from 'rxjs/operators';
import { PlanningCenterService, PlanningCenterEvent, PlanningCenterList } from '../../../services/planning-center.service';
import { CourseService } from '../../../services/course.service';
import { ProgramService } from '../../../services/program.service';
import { LoggerService } from '../../../services/logger.service';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatRadioGroup, MatRadioButton } from '@angular/material/radio';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatSelect, MatOption, MatOptgroup } from '@angular/material/select';
import { MatInput } from '@angular/material/input';
import { MatIcon } from '@angular/material/icon';
import { MatButton } from '@angular/material/button';
import { AsyncPipe, DatePipe } from '@angular/common';

export interface PCImportDialogData {
  entityType: 'course' | 'program';
}

export interface PCImportPreviewData {
  title: string;
  description: string;
  planning_center_event_id?: string;
  planning_center_event_name?: string;
  planning_center_list_id?: string;
  planning_center_list_name?: string;
  event_start_date?: Date | null;
  event_end_date?: Date | null;
  max_capacity?: number | null;
  locations?: string[];
  delivery_modes?: string[];
  duration_weeks?: number | null;
}

export interface GroupedEvent {
  letter: string;
  events: PlanningCenterEvent[];
}

export interface GroupedList {
  letter: string;
  lists: PlanningCenterList[];
}

@Component({
    selector: 'app-pc-import-dialog',
    templateUrl: './pc-import-dialog.component.html',
    styleUrls: ['./pc-import-dialog.component.scss'],
    imports: [MatDialogTitle, CdkScrollable, MatDialogContent, ReactiveFormsModule, MatRadioGroup, MatRadioButton, MatProgressSpinner, MatFormField, MatLabel, MatSelect, MatOption, MatInput, MatAutocompleteTrigger, MatAutocomplete, MatOptgroup, MatError, MatIcon, MatDialogActions, MatButton, AsyncPipe, DatePipe]
})
export class PCImportDialogComponent implements OnInit, AfterViewInit {
  importForm: FormGroup;
  sourceType: 'event' | 'list' = 'event';
  events: PlanningCenterEvent[] = [];
  lists: PlanningCenterList[] = [];
  isLoadingEvents = false;
  isLoadingLists = false;
  isLoadingDetails = false;
  selectedEvent: PlanningCenterEvent | null = null;
  selectedList: PlanningCenterList | null = null;
  previewData: PCImportPreviewData | null = null;

  // For autocomplete mode (when >20 items)
  eventControl = new FormControl('');
  listControl = new FormControl('');
  filteredEvents: Observable<GroupedEvent[]>;
  filteredLists: Observable<GroupedList[]>;
  
  // Threshold for switching between select and autocomplete
  readonly SELECT_THRESHOLD = 20;

  readonly eventAutoTrigger = viewChild<MatAutocompleteTrigger>('eventAutoTrigger');
  readonly listAutoTrigger = viewChild<MatAutocompleteTrigger>('listAutoTrigger');

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<PCImportDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: PCImportDialogData,
    private planningCenterService: PlanningCenterService,
    private courseService: CourseService,
    private logger: LoggerService,
    private programService: ProgramService,
    private snackBar: MatSnackBar
  ) {
    this.importForm = this.fb.group({
      source_type: ['event', Validators.required],
      pc_event_id: ['', Validators.required], // Required initially since event is default
      pc_list_id: [''] // Will be required when list is selected
    });

    // Initialize filtered observables for autocomplete with scroll-to-section
    this.filteredEvents = this.eventControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        // Handle both string and object values (object when event is selected)
        let searchValue: string = '';
        if (typeof value === 'string') {
          searchValue = value;
        } else if (value && typeof value === 'object' && 'attributes' in value) {
          searchValue = (value as any).attributes?.name || '';
        }
        const filtered = this._filterEventGroups(searchValue || '');
        // Scroll to first visible group after DOM updates
        setTimeout(() => this.scrollToFirstVisibleGroup('event'), 150);
        return filtered;
      })
    );

    this.filteredLists = this.listControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        // Handle both string and object values (object when list is selected)
        let searchValue: string = '';
        if (typeof value === 'string') {
          searchValue = value;
        } else if (value && typeof value === 'object' && 'attributes' in value) {
          searchValue = (value as any).attributes?.name || '';
        }
        const filtered = this._filterListGroups(searchValue || '');
        // Scroll to first visible group after DOM updates
        setTimeout(() => this.scrollToFirstVisibleGroup('list'), 150);
        return filtered;
      })
    );
  }

  ngOnInit(): void {
    this.loadEvents();
    this.loadLists();

    // Watch for source type changes
    this.importForm.get('source_type')?.valueChanges.subscribe(type => {
      this.sourceType = type;
      this.selectedEvent = null;
      this.selectedList = null;
      this.previewData = null;
      if (type === 'event') {
        this.importForm.get('pc_list_id')?.clearValidators();
        this.importForm.get('pc_list_id')?.updateValueAndValidity();
        this.importForm.get('pc_event_id')?.setValidators([Validators.required]);
        this.importForm.get('pc_list_id')?.setValue('');
        this.listControl.setValue('');
      } else {
        this.importForm.get('pc_event_id')?.clearValidators();
        this.importForm.get('pc_event_id')?.updateValueAndValidity();
        this.importForm.get('pc_list_id')?.setValidators([Validators.required]);
        this.importForm.get('pc_event_id')?.setValue('');
        this.eventControl.setValue('');
      }
    });

    // Watch for event selection (for mat-select mode)
    this.importForm.get('pc_event_id')?.valueChanges.subscribe(eventId => {
      if (eventId && typeof eventId === 'string') {
        this.loadEventDetails(eventId);
      } else {
        this.selectedEvent = null;
        this.previewData = null;
      }
    });

    // Watch for list selection (for mat-select mode)
    this.importForm.get('pc_list_id')?.valueChanges.subscribe(listId => {
      if (listId && typeof listId === 'string') {
        this.loadListDetails(listId);
      } else {
        this.selectedList = null;
        this.previewData = null;
      }
    });

    // Watch for event selection (for autocomplete mode)
    this.eventControl.valueChanges.subscribe(value => {
      if (value && typeof value === 'object' && 'id' in value) {
        const event = value as PlanningCenterEvent;
        this.importForm.get('pc_event_id')?.setValue(event.id, { emitEvent: false });
        this.loadEventDetails(event.id);
      }
    });

    // Watch for list selection (for autocomplete mode)
    this.listControl.valueChanges.subscribe(value => {
      if (value && typeof value === 'object' && 'id' in value) {
        const list = value as PlanningCenterList;
        this.importForm.get('pc_list_id')?.setValue(list.id, { emitEvent: false });
        this.loadListDetails(list.id);
      }
    });
  }

  // Getter methods to determine UI mode
  get useSelectForEvents(): boolean {
    return this.events.length <= this.SELECT_THRESHOLD;
  }

  get useSelectForLists(): boolean {
    return this.lists.length <= this.SELECT_THRESHOLD;
  }

  // Group events alphabetically
  private _groupEventsAlphabetically(): GroupedEvent[] {
    const groups: { [key: string]: PlanningCenterEvent[] } = {};
    
    this.events.forEach(event => {
      const name = event.attributes?.name || '';
      const firstLetter = name.charAt(0).toUpperCase();
      const letter = /[A-Z]/.test(firstLetter) ? firstLetter : '#';
      
      if (!groups[letter]) {
        groups[letter] = [];
      }
      groups[letter].push(event);
    });

    // Sort groups and items within groups
    return Object.keys(groups)
      .sort()
      .map(letter => ({
        letter,
        events: groups[letter].sort((a, b) => {
          const aName = a.attributes?.name || '';
          const bName = b.attributes?.name || '';
          return aName.localeCompare(bName);
        })
      }));
  }

  // Group lists alphabetically
  private _groupListsAlphabetically(): GroupedList[] {
    const groups: { [key: string]: PlanningCenterList[] } = {};
    
    this.lists.forEach(list => {
      const name = list.attributes?.name || '';
      const firstLetter = name.charAt(0).toUpperCase();
      const letter = /[A-Z]/.test(firstLetter) ? firstLetter : '#';
      
      if (!groups[letter]) {
        groups[letter] = [];
      }
      groups[letter].push(list);
    });

    // Sort groups and items within groups
    return Object.keys(groups)
      .sort()
      .map(letter => ({
        letter,
        lists: groups[letter].sort((a, b) => {
          const aName = a.attributes?.name || '';
          const bName = b.attributes?.name || '';
          return aName.localeCompare(bName);
        })
      }));
  }

  // Filter event groups based on search input
  private _filterEventGroups(searchValue: string | any): GroupedEvent[] {
    // Ensure searchValue is a string
    const searchStr = typeof searchValue === 'string' ? searchValue : (searchValue?.attributes?.name || '');
    const filterValue = searchStr.toLowerCase().trim();
    const allGroups = this._groupEventsAlphabetically();

    if (!filterValue) {
      return allGroups;
    }

    return allGroups
      .map(group => ({
        letter: group.letter,
        events: group.events.filter(event => {
          const name = (event.attributes?.name || '').toLowerCase();
          return name.includes(filterValue);
        })
      }))
      .filter(group => group.events.length > 0);
  }

  // Filter list groups based on search input
  private _filterListGroups(searchValue: string | any): GroupedList[] {
    // Ensure searchValue is a string
    const searchStr = typeof searchValue === 'string' ? searchValue : (searchValue?.attributes?.name || '');
    const filterValue = searchStr.toLowerCase().trim();
    const allGroups = this._groupListsAlphabetically();

    if (!filterValue) {
      return allGroups;
    }

    return allGroups
      .map(group => ({
        letter: group.letter,
        lists: group.lists.filter(list => {
          const name = (list.attributes?.name || '').toLowerCase();
          return name.includes(filterValue);
        })
      }))
      .filter(group => group.lists.length > 0);
  }

  // Display functions for autocomplete
  getEventDate(event: PlanningCenterEvent): Date | null {
    const attrs = event.attributes || {};
    const startDate = attrs.start_date || attrs['starts_at'];
    if (!startDate) return null;
    try {
      return new Date(String(startDate));
    } catch {
      return null;
    }
  }

  getListDate(list: PlanningCenterList): Date | null {
    const attrs = list.attributes || {};
    const date = attrs.created_at || attrs.updated_at;
    if (!date) return null;
    try {
      return new Date(String(date));
    } catch {
      return null;
    }
  }

  displayEventName(event: PlanningCenterEvent | string): string {
    if (typeof event === 'string') {
      return event;
    }
    return event?.attributes?.name || '';
  }

  displayListName(list: PlanningCenterList | string): string {
    if (typeof list === 'string') {
      return list;
    }
    return list?.attributes?.name || '';
  }

  ngAfterViewInit(): void {
    // ViewChild references are available here
  }

  /**
   * Scroll to the first visible optgroup in the autocomplete panel
   * If user typed a letter, scroll to that letter's group
   */
  scrollToFirstVisibleGroup(type: 'event' | 'list'): void {
    try {
      // Get the autocomplete trigger
      const trigger = type === 'event' ? this.eventAutoTrigger() : this.listAutoTrigger();
      
      if (!trigger || !trigger.panelOpen) {
        return;
      }

      // Get the current search value to determine target letter
      const searchValue = type === 'event' ? this.eventControl.value : this.listControl.value;
      const targetLetter = this._getTargetLetter(searchValue);

      // Wait for panel to be fully rendered and DOM to update
      setTimeout(() => {
        // Find the autocomplete panel in the DOM
        // The panel is in an overlay, so we need to find it by class
        const panelSelector = '.mat-mdc-autocomplete-panel';
        const panels = document.querySelectorAll(panelSelector);
        
        // Find the panel that's currently visible (has options)
        let targetPanel: HTMLElement | null = null;
        for (let i = 0; i < panels.length; i++) {
          const panel = panels[i] as HTMLElement;
          const optgroups = panel.querySelectorAll('mat-optgroup');
          const isVisible = window.getComputedStyle(panel).display !== 'none';
          
          if (optgroups.length > 0 && isVisible) {
            targetPanel = panel;
            break;
          }
        }

        if (!targetPanel) {
          return;
        }

        // Find the scrollable container (usually the panel itself or a child)
        const scrollContainer = targetPanel.querySelector('.cdk-virtual-scroll-viewport') || 
                               targetPanel.querySelector('[class*="viewport"]') ||
                               targetPanel;

        // Find all visible optgroups
        const optgroups = Array.from(targetPanel.querySelectorAll('mat-optgroup')) as HTMLElement[];
        
        if (optgroups.length === 0) {
          return;
        }

        // Find target optgroup - either the one matching the letter, or the first one
        let targetOptgroup: HTMLElement | null = null;
        
        if (targetLetter) {
          // Try to find the optgroup with the matching letter using data attribute
          for (const optgroup of optgroups) {
            const groupLetter = optgroup.getAttribute('data-group-letter');
            if (groupLetter === targetLetter) {
              targetOptgroup = optgroup;
              break;
            }
          }
        }
        
        // Fallback to first optgroup if no match found
        if (!targetOptgroup) {
          targetOptgroup = optgroups[0];
        }
        
        if (!targetOptgroup) {
          return;
        }

        // Find the first option in the target group
        const firstOption = targetOptgroup.querySelector('mat-option') as HTMLElement;
        
        if (!firstOption) {
          return;
        }

        // Get positions before scrolling
        const container = scrollContainer as HTMLElement;
        const optionOffsetTop = firstOption.offsetTop;

        // Calculate scroll position to bring the option near the top of the visible area
        const scrollTop = Math.max(0, optionOffsetTop - 10); // 10px padding from top

        // Scroll the container directly
        if (container && container.scrollHeight > container.clientHeight) {
          // Scroll with smooth behavior
          container.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
          });
          
          // Verify scroll completed after animation (smooth scroll takes ~300-500ms)
          // Check multiple times to ensure scroll completes, especially for large scrolls
          const checkScroll = (attempt: number = 1) => {
            setTimeout(() => {
              const finalScrollTop = container.scrollTop;
              
              // If scroll didn't complete (within 100px tolerance), try instant scroll as fallback
              const scrollDiff = Math.abs(finalScrollTop - scrollTop);
              if (scrollDiff > 100 && attempt < 3) {
                checkScroll(attempt + 1);
              } else if (scrollDiff > 100 && attempt === 3) {
                // Use instant scroll as fallback if smooth scroll didn't complete
                container.scrollTop = scrollTop;
              }
            }, attempt === 1 ? 300 : 200); // First check at 300ms, subsequent at 200ms intervals
          };
          
          checkScroll();
        }
      }, 200); // Delay to ensure DOM is ready
    } catch (error) {
      // Silently handle errors to avoid cluttering console
    }
  }

  /**
   * Extract the target letter from search value
   * Returns the uppercase first letter if it's a single letter, null otherwise
   */
  private _getTargetLetter(searchValue: string | PlanningCenterEvent | PlanningCenterList | null): string | null {
    if (!searchValue || typeof searchValue !== 'string') {
      return null;
    }
    
    const trimmed = searchValue.trim();
    if (trimmed.length === 0) {
      return null;
    }
    
    // If it's a single character and a letter, return it uppercase
    if (trimmed.length === 1) {
      const letter = trimmed.toUpperCase();
      if (/[A-Z]/.test(letter)) {
        return letter;
      }
    }
    
    // If it starts with a letter, return that letter
    const firstChar = trimmed[0].toUpperCase();
    if (/[A-Z]/.test(firstChar)) {
      return firstChar;
    }
    
    return null;
  }

  loadEvents(): void {
    this.isLoadingEvents = true;
    this.planningCenterService.getEvents()
      .pipe(finalize(() => this.isLoadingEvents = false))
      .subscribe({
        next: (events) => {
          this.events = events || [];
          if (this.events.length === 0) {
            this.snackBar.open('No events found in Planning Center. Please check your Planning Center configuration.', 'Close', { duration: 5000 });
          }
          // Reset autocomplete control when events are loaded
          if (!this.useSelectForEvents) {
            this.eventControl.setValue('');
          }
        },
        error: (error) => {
          this.logger.error('Error loading events', error, { component: 'PCImportDialogComponent' });
          this.events = [];
          const errorMessage = error?.error?.detail || error?.message || 'Failed to load Planning Center events';
          this.snackBar.open(`Error: ${errorMessage}`, 'Close', { duration: 5000 });
        }
      });
  }

  loadLists(): void {
    this.isLoadingLists = true;
    this.planningCenterService.getLists()
      .pipe(finalize(() => this.isLoadingLists = false))
      .subscribe({
        next: (lists) => {
          this.lists = lists || [];
          if (this.lists.length === 0) {
            this.snackBar.open('No lists found in Planning Center. Please check your Planning Center configuration.', 'Close', { duration: 5000 });
          }
          // Reset autocomplete control when lists are loaded
          if (!this.useSelectForLists) {
            this.listControl.setValue('');
          }
        },
        error: (error) => {
          this.logger.error('Error loading lists', error, { component: 'PCImportDialogComponent' });
          this.lists = [];
          const errorMessage = error?.error?.detail || error?.message || 'Failed to load Planning Center lists';
          this.snackBar.open(`Error: ${errorMessage}`, 'Close', { duration: 5000 });
        }
      });
  }

  loadEventDetails(eventId: string): void {
    this.isLoadingDetails = true;
    this.planningCenterService.getEvent(eventId)
      .pipe(finalize(() => this.isLoadingDetails = false))
      .subscribe({
        next: (event) => {
          this.selectedEvent = event;
          this.previewData = this.buildPreviewFromEvent(event);
        },
        error: (error) => {
          this.logger.error('Error loading event details', error, { component: 'PCImportDialogComponent', eventId });
          this.snackBar.open('Failed to load event details', 'Close', { duration: 3000 });
        }
      });
  }

  loadListDetails(listId: string): void {
    this.isLoadingDetails = true;
    this.planningCenterService.getList(listId)
      .pipe(finalize(() => this.isLoadingDetails = false))
      .subscribe({
        next: (list) => {
          this.selectedList = list;
          this.previewData = this.buildPreviewFromList(list);
        },
        error: (error) => {
          this.logger.error('Error loading list details', error, { component: 'PCImportDialogComponent', listId });
          this.snackBar.open('Failed to load list details', 'Close', { duration: 3000 });
        }
      });
  }

  buildPreviewFromEvent(event: PlanningCenterEvent): PCImportPreviewData {
    const attrs = event.attributes || {};
    // Calendar API uses 'starts_at' and 'ends_at', Check-Ins uses 'start_date' and 'end_date'
    const startDate = attrs.start_date || attrs['starts_at'];
    const endDate = attrs.end_date || attrs['ends_at'];

    return {
      title: String(attrs.name || ''),
      description: String(attrs['description'] || attrs.name || ''),
      planning_center_event_id: event.id,
      planning_center_event_name: String(attrs.name || ''),
      event_start_date: startDate ? new Date(String(startDate)) : null,
      event_end_date: endDate ? new Date(String(endDate)) : null,
      max_capacity: typeof attrs['capacity'] === 'number' ? attrs['capacity'] : (typeof attrs['max_attendees'] === 'number' ? attrs['max_attendees'] : null),
      locations: attrs['location'] || attrs['location_name'] ? [String(attrs['location'] || attrs['location_name'])] : [],
      delivery_modes: [],
      duration_weeks: null
    };
  }

  buildPreviewFromList(list: PlanningCenterList): PCImportPreviewData {
    const attrs = list.attributes || {};
    return {
      title: attrs.name || '',
      description: String(attrs['description'] || attrs.name || ''),
      planning_center_list_id: list.id,
      planning_center_list_name: attrs.name || '',
      locations: [],
      delivery_modes: [],
      duration_weeks: null
    };
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }

  onSubmit(): void {
    if (this.importForm.invalid || !this.previewData) {
      return;
    }

    // Return the preview data so the parent can use it to populate the course/program form
    this.dialogRef.close({
      sourceType: this.sourceType,
      sourceId: this.sourceType === 'event' 
        ? this.importForm.get('pc_event_id')?.value 
        : this.importForm.get('pc_list_id')?.value,
      previewData: this.previewData
    });
  }
}


