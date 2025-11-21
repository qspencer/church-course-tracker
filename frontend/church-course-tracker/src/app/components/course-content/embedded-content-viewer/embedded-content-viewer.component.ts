import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

export interface EmbeddedContentViewerData {
  title: string;
  content: string;
}

@Component({
  selector: 'app-embedded-content-viewer',
  templateUrl: './embedded-content-viewer.component.html',
  styleUrls: ['./embedded-content-viewer.component.scss']
})
export class EmbeddedContentViewerComponent {
  safeContent: SafeHtml;

  constructor(
    public dialogRef: MatDialogRef<EmbeddedContentViewerComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EmbeddedContentViewerData,
    private sanitizer: DomSanitizer
  ) {
    // Sanitize the embedded content to prevent XSS attacks
    this.safeContent = this.sanitizer.sanitize(1, data.content) || '';
  }

  onClose(): void {
    this.dialogRef.close();
  }

  getSafeHtml(): SafeHtml {
    return this.safeContent;
  }
}

