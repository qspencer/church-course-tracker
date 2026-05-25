import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';
import { BrowserModule } from '@angular/platform-browser';

import { EmbeddedContentViewerComponent, EmbeddedContentViewerData } from './embedded-content-viewer.component';

describe('EmbeddedContentViewerComponent', () => {
  let component: EmbeddedContentViewerComponent;
  let fixture: ComponentFixture<EmbeddedContentViewerComponent>;
  let dialogRef: jasmine.SpyObj<MatDialogRef<EmbeddedContentViewerComponent>>;
  let sanitizer: DomSanitizer;

  const mockDialogData: EmbeddedContentViewerData = {
    title: 'Test Embedded Content',
    content: '<iframe src="https://example.com"></iframe>'
  };

  beforeEach(async () => {
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);

    await TestBed.configureTestingModule({
    imports: [
        BrowserModule,
        MatDialogModule,
        MatButtonModule,
        MatIconModule,
        EmbeddedContentViewerComponent
    ],
    providers: [
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData }
    ]
}).compileComponents();

    fixture = TestBed.createComponent(EmbeddedContentViewerComponent);
    component = fixture.componentInstance;
    dialogRef = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<EmbeddedContentViewerComponent>>;
    sanitizer = TestBed.inject(DomSanitizer);
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should sanitize embedded content on init', () => {
      fixture.detectChanges();
      expect(component.safeContent).toBeDefined();
    });

    it('should store dialog data', () => {
      expect(component.data.title).toBe('Test Embedded Content');
      expect(component.data.content).toBe('<iframe src="https://example.com"></iframe>');
    });
  });

  describe('Content Sanitization', () => {
    it('should use bypassSecurityTrustHtml for iframe content', () => {
      const spy = spyOn(sanitizer, 'bypassSecurityTrustHtml').and.returnValue(
        sanitizer.bypassSecurityTrustHtml(mockDialogData.content)
      );
      
      fixture.detectChanges();
      
      expect(spy).toHaveBeenCalledWith(mockDialogData.content);
    });

    it('should return safe HTML from getSafeHtml', () => {
      fixture.detectChanges();
      const safeHtml = component.getSafeHtml();
      expect(safeHtml).toBeDefined();
    });
  });

  describe('Dialog Actions', () => {
    it('should close dialog on close', () => {
      component.onClose();
      expect(dialogRef.close).toHaveBeenCalled();
    });
  });

  describe('Different Content Types', () => {
    it('should handle YouTube embed', () => {
      const youtubeData: EmbeddedContentViewerData = {
        title: 'YouTube Video',
        content: '<iframe src="https://www.youtube.com/embed/VIDEO_ID"></iframe>'
      };
      
      component.data = youtubeData;
      fixture.detectChanges();
      
      expect(component.safeContent).toBeDefined();
      expect(component.data.content).toContain('youtube.com');
    });

    it('should handle Vimeo embed', () => {
      const vimeoData: EmbeddedContentViewerData = {
        title: 'Vimeo Video',
        content: '<iframe src="https://player.vimeo.com/video/VIDEO_ID"></iframe>'
      };
      
      component.data = vimeoData;
      fixture.detectChanges();
      
      expect(component.safeContent).toBeDefined();
      expect(component.data.content).toContain('vimeo.com');
    });

    it('should handle plain HTML content', () => {
      const htmlData: EmbeddedContentViewerData = {
        title: 'HTML Content',
        content: '<div><p>Some HTML content</p></div>'
      };
      
      component.data = htmlData;
      fixture.detectChanges();
      
      expect(component.safeContent).toBeDefined();
    });
  });
});


