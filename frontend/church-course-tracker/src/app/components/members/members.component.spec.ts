import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';

import { MembersComponent } from './members.component';
import { MemberService } from '../../services/member.service';
import { Person } from '../../models';

describe('MembersComponent', () => {
  let component: MembersComponent;
  let fixture: ComponentFixture<MembersComponent>;
  let memberServiceSpy: jasmine.SpyObj<MemberService>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockMembers: Person[] = [
    {
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      phone: '123-456-7890',
      planning_center_id: 'pc123',
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    },
    {
      id: 2,
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane@example.com',
      phone: '098-765-4321',
      created_at: '2023-01-02T00:00:00Z',
      updated_at: '2023-01-02T00:00:00Z'
    }
  ];

  beforeEach(async () => {
    const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers', 'deleteMember', 'getMemberEnrollments']);
    const matDialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [MembersComponent],
      imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatTableModule,
        MatPaginatorModule,
        MatSortModule,
        MatFormFieldModule,
        MatInputModule,
        MatProgressSpinnerModule,
        MatTooltipModule
      ],
      providers: [
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialog, useValue: matDialogSpy },
        { provide: MatSnackBar, useValue: matSnackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MembersComponent);
    component = fixture.componentInstance;
    memberServiceSpy = TestBed.inject(MemberService) as jasmine.SpyObj<MemberService>;
    dialogSpy = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;

    // Setup default return values
    memberServiceSpy.getMembers.and.returnValue(of(mockMembers));
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with loading state', () => {
    expect(component.isLoading).toBe(true);
  });

  describe('ngOnInit', () => {
    it('should load members on init', () => {
      component.ngOnInit();
      expect(memberServiceSpy.getMembers).toHaveBeenCalled();
    });
  });

  describe('loadMembers', () => {
    it('should load members and update data source', () => {
      component.loadMembers();

      expect(memberServiceSpy.getMembers).toHaveBeenCalled();
      expect(component.dataSource.data.length).toBe(2);
      expect(component.dataSource.data[0].full_name).toBe('John Doe');
      expect(component.isLoading).toBe(false);
    });

    it('should handle loading error', () => {
      memberServiceSpy.getMembers.and.returnValue(throwError(() => new Error('Load error')));
      spyOn(console, 'error');

      component.loadMembers();

      expect(console.error).toHaveBeenCalledWith('Error loading members:', jasmine.any(Error));
      expect(component.isLoading).toBe(false);
    });
  });

  describe('applyFilter', () => {
    beforeEach(() => {
      component.dataSource.data = mockMembers.map(member => ({
        ...member,
        full_name: `${member.first_name} ${member.last_name}`
      }));
    });

    it('should filter data source', () => {
      const event = { target: { value: 'John' } } as any;
      
      component.applyFilter(event);

      expect(component.dataSource.filter).toBe('john');
    });
  });

  describe('openMemberDialog', () => {
    it('should open dialog for new member', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      spyOn(component, 'loadMembers');

      component.openMemberDialog();

      expect(dialogSpy.open).toHaveBeenCalled();
      expect(component.loadMembers).toHaveBeenCalled();
    });

    it('should open dialog for existing member', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      spyOn(component, 'loadMembers');

      component.openMemberDialog(mockMembers[0]);

      expect(dialogSpy.open).toHaveBeenCalledWith(jasmine.any(Function), {
        width: '500px',
        data: { member: mockMembers[0] }
      });
    });
  });

  describe('deleteMember', () => {
    it('should delete member after confirmation', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      memberServiceSpy.deleteMember.and.returnValue(of(undefined));
      spyOn(component, 'loadMembers');

      component.deleteMember(mockMembers[0]);

      expect(dialogSpy.open).toHaveBeenCalled();
      expect(memberServiceSpy.deleteMember).toHaveBeenCalledWith(1);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Member deleted successfully', 'Close', { duration: 3000 });
      expect(component.loadMembers).toHaveBeenCalled();
    });

    it('should not delete member if not confirmed', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(false));
      dialogSpy.open.and.returnValue(dialogRefSpy);

      component.deleteMember(mockMembers[0]);

      expect(memberServiceSpy.deleteMember).not.toHaveBeenCalled();
    });

    it('should handle delete error', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      memberServiceSpy.deleteMember.and.returnValue(throwError(() => new Error('Delete error')));
      spyOn(console, 'error');

      component.deleteMember(mockMembers[0]);

      expect(console.error).toHaveBeenCalledWith('Error deleting member:', jasmine.any(Error));
    });
  });

  describe('editMember', () => {
    it('should call openMemberDialog with member', () => {
      spyOn(component, 'openMemberDialog');

      component.editMember(mockMembers[0]);

      expect(component.openMemberDialog).toHaveBeenCalledWith(mockMembers[0]);
    });
  });

  describe('viewMemberDetails', () => {
    it('should log member details', () => {
      spyOn(console, 'log');

      component.viewMemberDetails(mockMembers[0]);

      expect(console.log).toHaveBeenCalledWith('View member details:', mockMembers[0]);
    });
  });

  describe('viewMemberEnrollments', () => {
    it('should fetch and log member enrollments', () => {
      const mockEnrollments = [{ id: 1, course_title: 'Test Course' }];
      memberServiceSpy.getMemberEnrollments.and.returnValue(of(mockEnrollments));
      spyOn(console, 'log');

      component.viewMemberEnrollments(mockMembers[0]);

      expect(memberServiceSpy.getMemberEnrollments).toHaveBeenCalledWith(1);
      expect(console.log).toHaveBeenCalledWith('Member enrollments:', mockEnrollments);
    });

    it('should handle enrollments loading error', () => {
      memberServiceSpy.getMemberEnrollments.and.returnValue(throwError(() => new Error('Enrollments error')));
      spyOn(console, 'error');

      component.viewMemberEnrollments(mockMembers[0]);

      expect(console.error).toHaveBeenCalledWith('Error loading member enrollments:', jasmine.any(Error));
    });
  });

  describe('template rendering', () => {
    beforeEach(() => {
      component.dataSource.data = mockMembers.map(member => ({
        ...member,
        full_name: `${member.first_name} ${member.last_name}`
      }));
      component.isLoading = false;
      fixture.detectChanges();
    });

    it('should display members table', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.members-table')).toBeTruthy();
    });

    it('should display search field', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.search-field')).toBeTruthy();
    });

    it('should display add member button', () => {
      const compiled = fixture.nativeElement;
      const addButton = compiled.querySelector('button[color="primary"]');
      expect(addButton.textContent).toContain('Add New Member');
    });

    it('should show loading spinner when loading', () => {
      component.isLoading = true;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('mat-spinner')).toBeTruthy();
    });

    it('should show no data message when no members', () => {
      component.dataSource.data = [];
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.no-data')).toBeTruthy();
    });
  });
});
