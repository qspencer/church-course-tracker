import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadComponent: () =>
      import('./components/auth/auth.component').then(m => m.AuthComponent),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'courses',
    loadComponent: () =>
      import('./components/courses/courses.component').then(m => m.CoursesComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'programs',
    loadComponent: () =>
      import('./components/programs/programs.component').then(m => m.ProgramsComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'courses/:courseId/content',
    loadComponent: () =>
      import('./components/course-content/course-content.component').then(
        m => m.CourseContentComponent,
      ),
    canActivate: [AuthGuard],
  },
  {
    path: 'programs/:programId/content',
    loadComponent: () =>
      import('./components/program-content/program-content.component').then(
        m => m.ProgramContentComponent,
      ),
    canActivate: [AuthGuard],
  },
  {
    path: 'enrollments',
    loadComponent: () =>
      import('./components/enrollments/enrollments.component').then(m => m.EnrollmentsComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'progress',
    loadComponent: () =>
      import('./components/progress/progress.component').then(m => m.ProgressComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'reports',
    loadComponent: () =>
      import('./components/reports/reports.component').then(m => m.ReportsComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'members',
    loadComponent: () =>
      import('./components/members/members.component').then(m => m.MembersComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'admin',
    loadComponent: () =>
      import('./components/admin-layout/admin-layout.component').then(
        m => m.AdminLayoutComponent,
      ),
    canActivate: [AuthGuard, AdminGuard],
    canActivateChild: [AuthGuard, AdminGuard],
    children: [
      { path: '', redirectTo: 'users', pathMatch: 'full' },
      {
        path: 'users',
        loadComponent: () =>
          import('./components/users/users.component').then(m => m.UsersComponent),
      },
      {
        path: 'audit',
        loadComponent: () =>
          import('./components/audit/audit.component').then(m => m.AuditComponent),
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./components/settings/settings.component').then(m => m.SettingsComponent),
      },
    ],
  },
  {
    path: 'account',
    loadComponent: () =>
      import('./components/account-layout/account-layout.component').then(
        m => m.AccountLayoutComponent,
      ),
    canActivate: [AuthGuard],
    canActivateChild: [AuthGuard],
    children: [
      { path: '', redirectTo: 'profile', pathMatch: 'full' },
      {
        path: 'profile',
        loadComponent: () =>
          import('./components/profile/profile.component').then(m => m.ProfileComponent),
      },
      {
        path: 'activity-logs',
        loadComponent: () =>
          import('./components/activity-logs/activity-logs.component').then(
            m => m.ActivityLogsComponent,
          ),
      },
    ],
  },
  {
    path: '404',
    loadComponent: () =>
      import('./components/not-found/not-found.component').then(m => m.NotFoundComponent),
  },
  {
    path: '**',
    redirectTo: '/dashboard',
  },
];
