import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';

const routes: Routes = [
  {
    path: '',
    redirectTo: '/churchcoursetracker/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'churchcoursetracker',
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'auth',
        loadChildren: () => import('./components/auth/auth.module').then(m => m.AuthModule)
      },
      {
        path: 'dashboard',
        loadChildren: () => import('./components/dashboard/dashboard.module').then(m => m.DashboardModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'courses',
        loadChildren: () => import('./components/courses/courses.module').then(m => m.CoursesModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'programs',
        loadChildren: () => import('./components/programs/programs.module').then(m => m.ProgramsModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'courses/:courseId/content',
        loadChildren: () => import('./components/course-content/course-content.module').then(m => m.CourseContentModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'programs/:programId/content',
        loadChildren: () => import('./components/program-content/program-content.module').then(m => m.ProgramContentModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'enrollments',
        loadChildren: () => import('./components/enrollments/enrollments.module').then(m => m.EnrollmentsModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'progress',
        loadChildren: () => import('./components/progress/progress.module').then(m => m.ProgressModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'reports',
        loadChildren: () => import('./components/reports/reports.module').then(m => m.ReportsModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'members',
        loadChildren: () => import('./components/members/members.module').then(m => m.MembersModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'users',
        loadChildren: () => import('./components/users/users.module').then(m => m.UsersModule),
        canActivate: [AuthGuard, AdminGuard]
      },
      {
        path: 'audit',
        loadChildren: () => import('./components/audit/audit.module').then(m => m.AuditModule),
        canActivate: [AuthGuard, AdminGuard]
      },
      {
        path: 'settings',
        loadChildren: () => import('./components/settings/settings.module').then(m => m.SettingsModule),
        canActivate: [AuthGuard, AdminGuard]
      },
      {
        path: 'profile',
        loadChildren: () => import('./components/profile/profile.module').then(m => m.ProfileModule),
        canActivate: [AuthGuard]
      },
      {
        path: 'activity-logs',
        loadChildren: () => import('./components/activity-logs/activity-logs.module').then(m => m.ActivityLogsModule),
        canActivate: [AuthGuard]
      },
      {
        path: '404',
        loadChildren: () => import('./components/not-found/not-found.module').then(m => m.NotFoundModule)
      },
      {
        path: '**',
        loadChildren: () => import('./components/not-found/not-found.module').then(m => m.NotFoundModule)
      }
    ]
  },
  // Legacy routes retained for backward compatibility and deep links without the application slug.
  {
    path: 'auth',
    loadChildren: () => import('./components/auth/auth.module').then(m => m.AuthModule)
  },
  {
    path: 'dashboard',
    loadChildren: () => import('./components/dashboard/dashboard.module').then(m => m.DashboardModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'courses',
    loadChildren: () => import('./components/courses/courses.module').then(m => m.CoursesModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'programs',
    loadChildren: () => import('./components/programs/programs.module').then(m => m.ProgramsModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'courses/:courseId/content',
    loadChildren: () => import('./components/course-content/course-content.module').then(m => m.CourseContentModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'enrollments',
    loadChildren: () => import('./components/enrollments/enrollments.module').then(m => m.EnrollmentsModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'progress',
    loadChildren: () => import('./components/progress/progress.module').then(m => m.ProgressModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'reports',
    loadChildren: () => import('./components/reports/reports.module').then(m => m.ReportsModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'members',
    loadChildren: () => import('./components/members/members.module').then(m => m.MembersModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'users',
    loadChildren: () => import('./components/users/users.module').then(m => m.UsersModule),
    canActivate: [AuthGuard, AdminGuard]
  },
      {
        path: 'audit',
        loadChildren: () => import('./components/audit/audit.module').then(m => m.AuditModule),
        canActivate: [AuthGuard, AdminGuard]
      },
      {
        path: 'profile',
        loadChildren: () => import('./components/profile/profile.module').then(m => m.ProfileModule),
        canActivate: [AuthGuard]
      },
      {
        path: '**',
        redirectTo: '/churchcoursetracker/dashboard'
      }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
