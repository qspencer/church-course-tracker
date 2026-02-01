import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of } from 'rxjs';
import { AppComponent } from './app.component';
import { AuthService } from './services/auth.service';
import { InactivityService } from './services/inactivity.service';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';

const ROUTE_PREFIX = '';

describe('AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let routerSpy: jasmine.SpyObj<Router>;
  let inactivityServiceSpy: jasmine.SpyObj<InactivityService>;

  beforeEach(async () => {
    const authSpy = jasmine.createSpyObj('AuthService', ['logout', 'isAdmin', 'getToken'], {
      isAuthenticated$: of(false),
      currentUser$: of(null)
    });
    const routerSpyObj = jasmine.createSpyObj('Router', ['navigate']);
    const inactivitySpy = jasmine.createSpyObj('InactivityService', ['startMonitoring', 'stopMonitoring']);

    await TestBed.configureTestingModule({
      declarations: [AppComponent],
      imports: [
        RouterTestingModule,
        BrowserAnimationsModule,
        MatToolbarModule,
        MatSidenavModule,
        MatListModule,
        MatIconModule,
        MatButtonModule,
        MatTooltipModule
      ],
      providers: [
        { provide: AuthService, useValue: authSpy },
        { provide: Router, useValue: routerSpyObj },
        { provide: InactivityService, useValue: inactivitySpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    inactivityServiceSpy = TestBed.inject(InactivityService) as jasmine.SpyObj<InactivityService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize and start inactivity monitoring', () => {
    fixture.detectChanges();
    expect(inactivityServiceSpy.startMonitoring).toHaveBeenCalled();
  });

  it('should stop inactivity monitoring on destroy', () => {
    fixture.detectChanges();
    component.ngOnDestroy();
    expect(inactivityServiceSpy.stopMonitoring).toHaveBeenCalled();
  });

  it('should subscribe to authentication state', () => {
    fixture.detectChanges();
    expect(authServiceSpy.isAuthenticated$).toBeDefined();
  });

  it('should subscribe to current user', () => {
    fixture.detectChanges();
    expect(authServiceSpy.currentUser$).toBeDefined();
  });

  it('should logout and navigate to auth', () => {
    component.logout();
    expect(authServiceSpy.logout).toHaveBeenCalled();
    expect(routerSpy.navigate).toHaveBeenCalledWith([`${ROUTE_PREFIX}/auth`]);
  });

  it('should check if user is admin', () => {
    authServiceSpy.isAdmin.and.returnValue(true);
    expect(component.isAdmin()).toBe(true);
    expect(authServiceSpy.isAdmin).toHaveBeenCalled();
  });
});

