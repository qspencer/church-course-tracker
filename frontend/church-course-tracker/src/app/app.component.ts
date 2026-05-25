import { Component, OnInit, OnDestroy, viewChild, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth.service';
import { InactivityService } from './services/inactivity.service';
import { MatSidenav, MatSidenavContainer, MatSidenavContent } from '@angular/material/sidenav';
import { environment } from '../environments/environment';
import { MatToolbar } from '@angular/material/toolbar';
import { MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatNavList, MatListItem, MatListItemIcon, MatListItemTitle, MatDivider } from '@angular/material/list';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    imports: [MatToolbar, MatIconButton, MatIcon, MatSidenavContainer, MatSidenav, MatNavList, MatListItem, RouterLink, RouterLinkActive, MatListItemIcon, MatListItemTitle, MatDivider, MatSidenavContent, RouterOutlet]
})
export class AppComponent implements OnInit, OnDestroy {
  private authService = inject(AuthService);
  private router = inject(Router);
  private inactivityService = inject(InactivityService);

  readonly sidenav = viewChild<MatSidenav>('sidenav');
  title = 'Church Course Tracker'; // Triggering frontend tests
  appVersion = environment.version || '0.01';
  isAuthenticated = false;
  currentUser: any = null;

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe(isAuth => {
      this.isAuthenticated = isAuth;
    });

    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    // Start inactivity monitoring
    this.inactivityService.startMonitoring();
  }

  ngOnDestroy(): void {
    this.inactivityService.stopMonitoring();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isStaffOrAdmin(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }
}
