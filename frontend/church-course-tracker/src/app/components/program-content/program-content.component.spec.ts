import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { ProgramContentComponent } from './program-content.component';
import { ProgramContentService } from '../../services/program-content.service';
import { ProgramService } from '../../services/program.service';
import { AuthService } from '../../services/auth.service';
import {
  ProgramModule, ProgramContent, ContentType
} from '../../models/program-content.model';
import { Program } from '../../models/program.model';

describe('ProgramContentComponent', () => {
  let component: ProgramContentComponent;
  let fixture: ComponentFixture<ProgramContentComponent>;
  let programContentService: jasmine.SpyObj<ProgramContentService>;
  let programService: jasmine.SpyObj<ProgramService>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let dialog: jasmine.SpyObj<MatDialog>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let activatedRoute: jasmine.SpyObj<ActivatedRoute>;

  const mockProgram: Program = {
    id: 1,
    title: 'Test Program',
    description: 'Test Description',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 1,
    updated_by: 1
  };

  const mockModule: ProgramModule = {
    id: 1,
    program_id: 1,
    title: 'Category 1',
    description: 'First category',
    order_index: 1,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 1,
    updated_by: 1,
    content_items: []
  };

  const mockContent: ProgramContent = {
    id: 1,
    program_id: 1,
    module_id: 1,
    title: 'Lesson 1',
    description: 'First lesson',
    content_type: ContentType.DOCUMENT,
    order_index: 1,
    download_count: 0,
    view_count: 0,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 1,
    updated_by: 1
  };

  beforeEach(async () => {
    const programContentServiceSpy = jasmine.createSpyObj('ProgramContentService', [
      'getProgramModules',
      'getProgramContent',
      'createModule',
      'createContent',
      'updateModule',
      'updateContent',
      'deleteModule',
      'deleteContent'
    ]);
    const programServiceSpy = jasmine.createSpyObj('ProgramService', ['getProgram']);
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['hasAnyRole', 'isAdmin']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const activatedRouteSpy = {
      snapshot: {
        paramMap: {
          get: jasmine.createSpy('get').and.returnValue('1')
        }
      }
    };

    await TestBed.configureTestingModule({
      declarations: [ProgramContentComponent],
      imports: [
        MatTabsModule,
        MatIconModule,
        MatButtonModule,
        MatProgressSpinnerModule,
        NoopAnimationsModule
      ],
      providers: [
        { provide: ProgramContentService, useValue: programContentServiceSpy },
        { provide: ProgramService, useValue: programServiceSpy },
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy },
        { provide: MatDialog, useValue: dialogSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        { provide: ActivatedRoute, useValue: activatedRouteSpy }
      ]
    }).compileComponents();

    programContentService = TestBed.inject(ProgramContentService) as jasmine.SpyObj<ProgramContentService>;
    programService = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    dialog = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    activatedRoute = TestBed.inject(ActivatedRoute) as jasmine.SpyObj<ActivatedRoute>;

    // Setup default return values
    programService.getProgram.and.returnValue(of(mockProgram));
    programContentService.getProgramModules.and.returnValue(of([mockModule]));
    programContentService.getProgramContent.and.returnValue(of([mockContent]));
    authService.hasAnyRole.and.returnValue(true);
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProgramContentComponent);
    component = fixture.componentInstance;
    component.programId = 1;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load program, modules, and content on init', () => {
    expect(programService.getProgram).toHaveBeenCalledWith(1);
    expect(programContentService.getProgramModules).toHaveBeenCalledWith(1);
    expect(programContentService.getProgramContent).toHaveBeenCalledWith(1);
  });

  it('should display program title', () => {
    component.program = mockProgram;
    fixture.detectChanges();
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('h1').textContent).toContain('Test Program');
  });

  it('should create module when createModule is called', () => {
    const dialogRef = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
    dialogRef.afterClosed.and.returnValue(of(mockModule));
    dialog.open.and.returnValue(dialogRef);

    component.createModule();

    expect(dialog.open).toHaveBeenCalled();
  });

  it('should create content when createContent is called', () => {
    const dialogRef = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
    dialogRef.afterClosed.and.returnValue(of(mockContent));
    dialog.open.and.returnValue(dialogRef);

    component.createContent();

    expect(dialog.open).toHaveBeenCalled();
  });

  it('should get content for module', () => {
    component.contentItems = [mockContent];
    const content = component.getContentForModule(1);
    expect(content.length).toBe(1);
    expect(content[0].module_id).toBe(1);
  });

  it('should get module title', () => {
    component.modules = [mockModule];
    const title = component.getModuleTitle(1);
    expect(title).toBe('Category 1');
  });

  it('should format file size correctly', () => {
    const formatted = component.formatFileSize(1024);
    expect(formatted).toContain('KB');
  });

  it('should format duration correctly', () => {
    const formatted = component.formatDuration(3661); // 1 hour, 1 minute, 1 second
    expect(formatted).toContain(':');
  });

  it('should check if content is external', () => {
    const externalContent: ProgramContent = {
      ...mockContent,
      content_type: ContentType.EXTERNAL_LINK
    };
    expect(component.isExternalContent(externalContent)).toBe(true);
  });

  it('should check if content is file content', () => {
    expect(component.isFileContent(mockContent)).toBe(true);
  });

  it('should delete module after confirmation', () => {
    const dialogRef = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
    dialogRef.afterClosed.and.returnValue(of(true));
    dialog.open.and.returnValue(dialogRef);
    programContentService.deleteModule.and.returnValue(of(void 0));
    programContentService.getProgramModules.and.returnValue(of([]));
    programContentService.getProgramContent.and.returnValue(of([]));

    component.deleteModule(mockModule);

    expect(dialog.open).toHaveBeenCalled();
    expect(programContentService.deleteModule).toHaveBeenCalledWith(1);
  });

  it('should delete content after confirmation', () => {
    const dialogRef = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
    dialogRef.afterClosed.and.returnValue(of(true));
    dialog.open.and.returnValue(dialogRef);
    programContentService.deleteContent.and.returnValue(of(void 0));
    programContentService.getProgramModules.and.returnValue(of([]));
    programContentService.getProgramContent.and.returnValue(of([]));

    component.deleteContent(mockContent);

    expect(dialog.open).toHaveBeenCalled();
    expect(programContentService.deleteContent).toHaveBeenCalledWith(1);
  });
});


