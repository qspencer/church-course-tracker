import { Component, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { MatIcon } from '@angular/material/icon';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatButton } from '@angular/material/button';

export interface EmbeddedContentViewerData {
  title: string;
  content: string;
}

@Component({
    selector: 'app-embedded-content-viewer',
    templateUrl: './embedded-content-viewer.component.html',
    styleUrls: ['./embedded-content-viewer.component.scss'],
    imports: [MatDialogTitle, MatIcon, CdkScrollable, MatDialogContent, MatDialogActions, MatButton]
})
export class EmbeddedContentViewerComponent {
  dialogRef = inject<MatDialogRef<EmbeddedContentViewerComponent>>(MatDialogRef);
  data = inject<EmbeddedContentViewerData>(MAT_DIALOG_DATA);
  private sanitizer = inject(DomSanitizer);

  // Database-stored content is rendered into a sandboxed <iframe srcdoc>
  // rather than the app's own DOM. The iframe's sandbox has no
  // allow-same-origin, so the content runs in an opaque origin and cannot
  // reach the parent's localStorage (where the auth token lives), cookies,
  // or DOM - a malicious content record can no longer exfiltrate tokens.
  // bypassSecurityTrustHtml is still required to bind arbitrary HTML to
  // [srcdoc], but the sandbox is what contains it.
  safeContent: SafeHtml;

  constructor() {
    this.safeContent = this.sanitizer.bypassSecurityTrustHtml(this.data.content);
  }

  onClose(): void {
    this.dialogRef.close();
  }

  getSafeHtml(): SafeHtml {
    return this.safeContent;
  }
}
