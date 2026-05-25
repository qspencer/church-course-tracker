import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';
import { InactivityService } from './services/inactivity.service';
import { MatSidenav } from '@angular/material/sidenav';
import { environment } from '../environments/environment';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    standalone: false
})
export class AppComponent implements OnInit, OnDestroy {
  @ViewChild('sidenav') sidenav!: MatSidenav;
  title = 'Church Course Tracker'; // Triggering frontend tests
  appVersion = environment.version || '0.01';
  isAuthenticated = false;
  currentUser: any = null;

  constructor(
    private authService: AuthService,
    private router: Router,
    private inactivityService: InactivityService
  ) {}

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
