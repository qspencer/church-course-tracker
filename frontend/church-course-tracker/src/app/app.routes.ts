import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { adminGuard } from './guards/admin.guard';
import { AdminLayoutComponent } from './components/admin-layout/admin-layout.component';
import { AccountLayoutComponent } from './components/account-layout/account-layout.component';

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
    canActivate: [authGuard],
  },
  {
    path: 'courses',
    loadComponent: () =>
      import('./components/courses/courses.component').then(m => m.CoursesComponent),
    canActivate: [authGuard],
  },
  {
    path: 'programs',
    loadComponent: () =>
      import('./components/programs/programs.component').then(m => m.ProgramsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'courses/:courseId/content',
    loadComponent: () =>
      import('./components/course-content/course-content.component').then(
        m => m.CourseContentComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'programs/:programId/content',
    loadComponent: () =>
      import('./components/program-content/program-content.component').then(
        m => m.ProgramContentComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'enrollments',
    loadComponent: () =>
      import('./components/enrollments/enrollments.component').then(m => m.EnrollmentsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'progress',
    loadComponent: () =>
      import('./components/progress/progress.component').then(m => m.ProgressComponent),
    canActivate: [authGuard],
  },
  {
    path: 'reports',
    loadComponent: () =>
      import('./components/reports/reports.component').then(m => m.ReportsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'members',
    loadComponent: () =>
      import('./components/members/members.component').then(m => m.MembersComponent),
    canActivate: [authGuard],
  },
  {
    path: 'admin',
    component: AdminLayoutComponent,
    canActivate: [authGuard, adminGuard],
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
    component: AccountLayoutComponent,
    canActivate: [authGuard],
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
