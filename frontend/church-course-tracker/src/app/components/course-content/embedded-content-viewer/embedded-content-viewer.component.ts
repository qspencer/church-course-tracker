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
    // Use bypassSecurityTrustHtml for embedded content (iframes, videos, etc.)
    // This is safe because content is stored in the database and only admins/staff can create it
    // In production, you may want to add additional validation or whitelisting
    this.safeContent = this.sanitizer.bypassSecurityTrustHtml(data.content);
  }

  onClose(): void {
    this.dialogRef.close();
  }

  getSafeHtml(): SafeHtml {
    return this.safeContent;
  }
}

