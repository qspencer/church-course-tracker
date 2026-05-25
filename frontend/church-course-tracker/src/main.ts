import { provideZoneChangeDetection, ErrorHandler, importProvidersFrom } from "@angular/core";
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { environment } from './environments/environment';
import '@angular/compiler';
import * as Sentry from '@sentry/angular';
import { AuthService } from "./app/services/auth.service";
import { InactivityService } from "./app/services/inactivity.service";
import { CourseService } from "./app/services/course.service";
import { EnrollmentService } from "./app/services/enrollment.service";
import { ProgressService } from "./app/services/progress.service";
import { ReportService } from "./app/services/report.service";
import { MemberService } from "./app/services/member.service";
import { LoggerService } from "./app/services/logger.service";
import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi } from "@angular/common/http";
import { AuthInterceptor } from "./app/interceptors/auth.interceptor";
import { ErrorInterceptor } from "./app/interceptors/error.interceptor";
import { BrowserModule, bootstrapApplication } from "@angular/platform-browser";
import { AppRoutingModule } from "./app/app-routing.module";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatListModule } from "@angular/material/list";
import { MatIconModule } from "@angular/material/icon";
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from "@angular/material/card";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatTableModule } from "@angular/material/table";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatSortModule } from "@angular/material/sort";
import { MatDialogModule } from "@angular/material/dialog";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatChipsModule } from "@angular/material/chips";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MatTabsModule } from "@angular/material/tabs";
import { MatExpansionModule } from "@angular/material/expansion";
import { MatDividerModule } from "@angular/material/divider";
import { AppComponent } from "./app/app.component";

// Initialize Sentry for production error tracking
if (environment.production && environment.enableErrorReporting) {
  Sentry.init({
    dsn: environment.sentry.dsn,
    environment: environment.sentry.environment,
    integrations: [
      Sentry.browserTracingIntegration(),
    ],
    tracePropagationTargets: environment.sentry.tracePropagationTargets,
    tracesSampleRate: environment.sentry.tracesSampleRate,
    beforeSend(event) {
      // Filter out sensitive data
      if (event.request?.headers) {
        delete event.request.headers['Authorization'];
      }
      return event;
    },
  });
}

bootstrapApplication(AppComponent, {
    providers: [
        importProvidersFrom(BrowserModule, AppRoutingModule, BrowserAnimationsModule, ReactiveFormsModule, FormsModule, 
        // Angular Material
        MatToolbarModule, MatSidenavModule, MatListModule, MatIconModule, MatButtonModule, MatCardModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatTableModule, MatPaginatorModule, MatSortModule, MatDialogModule, MatSnackBarModule, MatProgressSpinnerModule, MatChipsModule, MatDatepickerModule, MatNativeDateModule, MatTabsModule, MatExpansionModule, MatDividerModule),
        AuthService,
        InactivityService,
        CourseService,
        EnrollmentService,
        ProgressService,
        ReportService,
        MemberService,
        LoggerService,
        {
            provide: HTTP_INTERCEPTORS,
            useClass: AuthInterceptor,
            multi: true
        },
        {
            provide: HTTP_INTERCEPTORS,
            useClass: ErrorInterceptor,
            multi: true
        },
        {
            provide: ErrorHandler,
            useValue: environment.production && environment.enableErrorReporting
                ? Sentry.createErrorHandler({ showDialog: false })
                : new ErrorHandler()
        },
        provideHttpClient(withInterceptorsFromDi())
    ]
})
  .catch(err => console.error(err));
