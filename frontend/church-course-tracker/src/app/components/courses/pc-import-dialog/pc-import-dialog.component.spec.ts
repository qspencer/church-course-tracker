import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatRadioModule } from '@angular/material/radio';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { PCImportDialogComponent, PCImportDialogData } from './pc-import-dialog.component';
import { PlanningCenterService, PlanningCenterEvent, PlanningCenterList } from '../../../services/planning-center.service';
import { CourseService } from '../../../services/course.service';
import { ProgramService } from '../../../services/program.service';

describe('PCImportDialogComponent', () => {
  let component: PCImportDialogComponent;
  let fixture: ComponentFixture<PCImportDialogComponent>;
  let mockPlanningCenterService: jasmine.SpyObj<PlanningCenterService>;
  let mockCourseService: jasmine.SpyObj<CourseService>;
  let mockProgramService: jasmine.SpyObj<ProgramService>;
  let mockDialogRef: jasmine.SpyObj<MatDialogRef<PCImportDialogComponent>>;

  const mockEvents: PlanningCenterEvent[] = [
    {
      id: 'pc_event_1',
      type: 'Event',
      attributes: {
        name: 'Test Event 1',
        start_date: '2024-01-15T10:00:00Z',
        end_date: '2024-01-15T12:00:00Z',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        capacity: 50
      },
      relationships: {
        event_type: {
          data: {
            id: 'event_type_1',
            type: 'EventType'
          }
        }
      }
    },
    {
      id: 'pc_event_2',
      type: 'Event',
      attributes: {
        name: 'Test Event 2',
        start_date: '2024-01-20T10:00:00Z',
        end_date: '2024-01-20T12:00:00Z',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        capacity: 30
      },
      relationships: {
        event_type: {
          data: {
            id: 'event_type_2',
            type: 'EventType'
          }
        }
      }
    }
  ];

  const mockLists: PlanningCenterList[] = [
    {
      id: 'pc_list_1',
      type: 'List',
      attributes: {
        name: 'Test List 1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    },
    {
      id: 'pc_list_2',
      type: 'List',
      attributes: {
        name: 'Test List 2',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z'
      }
    }
  ];

  beforeEach(async () => {
    mockPlanningCenterService = jasmine.createSpyObj('PlanningCenterService', [
      'getEvents',
      'getLists',
      'getEvent',
      'getList'
    ]);
    mockCourseService = jasmine.createSpyObj('CourseService', ['getCourses']);
    mockProgramService = jasmine.createSpyObj('ProgramService', ['getPrograms']);
    mockDialogRef = jasmine.createSpyObj('MatDialogRef', ['close']);

    await TestBed.configureTestingModule({
      declarations: [PCImportDialogComponent],
      imports: [
        ReactiveFormsModule,
        MatDialogModule,
        MatSnackBarModule,
        MatSelectModule,
        MatFormFieldModule,
        MatInputModule,
        MatAutocompleteModule,
        MatRadioModule,
        MatProgressSpinnerModule,
        MatIconModule,
        BrowserAnimationsModule
      ],
      providers: [
        FormBuilder,
        { provide: MatDialogRef, useValue: mockDialogRef },
        { provide: MAT_DIALOG_DATA, useValue: { entityType: 'course' } as PCImportDialogData },
        { provide: PlanningCenterService, useValue: mockPlanningCenterService },
        { provide: CourseService, useValue: mockCourseService },
        { provide: ProgramService, useValue: mockProgramService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(PCImportDialogComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load events and lists on init', () => {
    mockPlanningCenterService.getEvents.and.returnValue(of(mockEvents));
    mockPlanningCenterService.getLists.and.returnValue(of(mockLists));

    fixture.detectChanges();

    expect(mockPlanningCenterService.getEvents).toHaveBeenCalled();
    expect(mockPlanningCenterService.getLists).toHaveBeenCalled();
    expect(component.events).toEqual(mockEvents);
    expect(component.lists).toEqual(mockLists);
  });

  it('should handle error loading events', () => {
    mockPlanningCenterService.getEvents.and.returnValue(throwError(() => new Error('Failed')));
    mockPlanningCenterService.getLists.and.returnValue(of(mockLists));

    fixture.detectChanges();

    expect(component.isLoadingEvents).toBe(false);
  });

  it('should handle error loading lists', () => {
    mockPlanningCenterService.getEvents.and.returnValue(of(mockEvents));
    mockPlanningCenterService.getLists.and.returnValue(throwError(() => new Error('Failed')));

    fixture.detectChanges();

    expect(component.isLoadingLists).toBe(false);
  });

  it('should load event details when event is selected', () => {
    mockPlanningCenterService.getEvents.and.returnValue(of(mockEvents));
    mockPlanningCenterService.getLists.and.returnValue(of(mockLists));
    mockPlanningCenterService.getEvent.and.returnValue(of(mockEvents[0]));

    fixture.detectChanges();

    component.importForm.get('pc_event_id')?.setValue('pc_event_1');

    expect(mockPlanningCenterService.getEvent).toHaveBeenCalledWith('pc_event_1');
    expect(component.selectedEvent).toEqual(mockEvents[0]);
    expect(component.previewData).toBeTruthy();
  });

  it('should load list details when list is selected', () => {
    mockPlanningCenterService.getEvents.and.returnValue(of(mockEvents));
    mockPlanningCenterService.getLists.and.returnValue(of(mockLists));
    mockPlanningCenterService.getList.and.returnValue(of(mockLists[0]));

    fixture.detectChanges();

    component.importForm.get('source_type')?.setValue('list');
    component.importForm.get('pc_list_id')?.setValue('pc_list_1');

    expect(mockPlanningCenterService.getList).toHaveBeenCalledWith('pc_list_1');
    expect(component.selectedList).toEqual(mockLists[0]);
    expect(component.previewData).toBeTruthy();
  });

  it('should build preview data from event', () => {
    const preview = component.buildPreviewFromEvent(mockEvents[0]);
    
    expect(preview.title).toBe('Test Event 1');
    expect(preview.planning_center_event_id).toBe('pc_event_1');
    expect(preview.planning_center_event_name).toBe('Test Event 1');
    expect(preview.event_start_date).toBeTruthy();
    expect(preview.event_end_date).toBeTruthy();
    expect(preview.max_capacity).toBe(50);
  });

  it('should build preview data from list', () => {
    const preview = component.buildPreviewFromList(mockLists[0]);
    
    expect(preview.title).toBe('Test List 1');
    expect(preview.planning_center_list_id).toBe('pc_list_1');
    expect(preview.planning_center_list_name).toBe('Test List 1');
  });

  it('should close dialog on cancel', () => {
    component.onCancel();
    expect(mockDialogRef.close).toHaveBeenCalledWith(null);
  });

  it('should close dialog with result on submit', () => {
    mockPlanningCenterService.getEvents.and.returnValue(of(mockEvents));
    mockPlanningCenterService.getLists.and.returnValue(of(mockLists));
    mockPlanningCenterService.getEvent.and.returnValue(of(mockEvents[0]));

    fixture.detectChanges();

    component.importForm.get('pc_event_id')?.setValue('pc_event_1');
    component.onSubmit();

    expect(mockDialogRef.close).toHaveBeenCalled();
    const callArgs = mockDialogRef.close.calls.mostRecent().args[0];
    expect(callArgs.sourceType).toBe('event');
    expect(callArgs.sourceId).toBe('pc_event_1');
    expect(callArgs.previewData).toBeTruthy();
  });

  it('should not submit if form is invalid', () => {
    component.onSubmit();
    expect(mockDialogRef.close).not.toHaveBeenCalled();
  });

  it('should not submit if preview data is not loaded', () => {
    component.importForm.get('source_type')?.setValue('event');
    component.importForm.get('pc_event_id')?.setValue('pc_event_1');
    component.previewData = null;

    component.onSubmit();
    expect(mockDialogRef.close).not.toHaveBeenCalled();
  });
});

