import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { of, throwError } from 'rxjs';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { UsersComponent } from './users.component';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models';

describe('UsersComponent', () => {
  let component: UsersComponent;
  let fixture: ComponentFixture<UsersComponent>;
  let userService: jasmine.SpyObj<UserService>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let dialog: jasmine.SpyObj<MatDialog>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;

  const mockUsers: User[] = [
    {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      full_name: 'Admin User',
      role: 'admin',
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    },
    {
      id: 2,
      username: 'staff',
      email: 'staff@example.com',
      full_name: 'Staff User',
      role: 'staff',
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    }
  ];

  const mockAdminUser: User = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: 'Admin User',
    role: 'admin',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(async () => {
    const userServiceSpy = jasmine.createSpyObj('UserService', [
      'getUsers', 'deleteUser', 'updateUser'
    ]);
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['isAdmin']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      imports: [
        NoopAnimationsModule,
        MatTableModule,
        MatButtonModule,
        MatIconModule,
        MatChipsModule,
        MatProgressSpinnerModule
      ],
      declarations: [UsersComponent],
      providers: [
        { provide: UserService, useValue: userServiceSpy },
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy },
        { provide: MatDialog, useValue: dialogSpy },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(UsersComponent);
    component = fixture.componentInstance;
    userService = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    dialog = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should load users when user is admin', () => {
      authService.isAdmin.and.returnValue(true);
      userService.getUsers.and.returnValue(of(mockUsers));

      component.ngOnInit();

      expect(authService.isAdmin).toHaveBeenCalled();
      expect(userService.getUsers).toHaveBeenCalled();
      expect(router.navigate).not.toHaveBeenCalled();
    });

    it('should redirect to dashboard when user is not admin', () => {
      authService.isAdmin.and.returnValue(false);

      component.ngOnInit();

      expect(authService.isAdmin).toHaveBeenCalled();
      expect(snackBar.open).toHaveBeenCalledWith(
        'Access denied. Admin privileges required.',
        'Close',
        { duration: 3000 }
      );
      expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
      expect(userService.getUsers).not.toHaveBeenCalled();
    });
  });

  describe('loadUsers', () => {
    beforeEach(() => {
      authService.isAdmin.and.returnValue(true);
    });

    it('should load users successfully', () => {
      userService.getUsers.and.returnValue(of(mockUsers));

      component.loadUsers();

      expect(component.users).toEqual(mockUsers);
      expect(component.isLoading).toBe(false);
    });

    it('should handle error when loading users fails', () => {
      const error = new Error('Failed to load users');
      userService.getUsers.and.returnValue(throwError(() => error));

      component.loadUsers();

      expect(snackBar.open).toHaveBeenCalledWith(
        'Error loading users',
        'Close',
        { duration: 3000 }
      );
      expect(component.isLoading).toBe(false);
    });
  });

  describe('openCreateDialog', () => {
    it('should open create user dialog', () => {
      const dialogRef = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRef.afterClosed.and.returnValue(of(true));
      dialog.open.and.returnValue(dialogRef);

      component.openCreateDialog();

      expect(dialog.open).toHaveBeenCalledWith(
        jasmine.any(Function),
        {
          width: '500px',
          data: { mode: 'create' }
        }
      );
    });
  });

  describe('openEditDialog', () => {
    it('should open edit user dialog', () => {
      const dialogRef = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRef.afterClosed.and.returnValue(of(true));
      dialog.open.and.returnValue(dialogRef);

      component.openEditDialog(mockUsers[0]);

      expect(dialog.open).toHaveBeenCalledWith(
        jasmine.any(Function),
        {
          width: '500px',
          data: { mode: 'edit', user: mockUsers[0] }
        }
      );
    });
  });

  describe('deleteUser', () => {
    it('should delete user when confirmed', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      userService.deleteUser.and.returnValue(of({}));

      component.deleteUser(mockUsers[0]);

      expect(window.confirm).toHaveBeenCalledWith(
        `Are you sure you want to delete user "${mockUsers[0].full_name}"?`
      );
      expect(userService.deleteUser).toHaveBeenCalledWith(mockUsers[0].id);
      expect(snackBar.open).toHaveBeenCalledWith(
        'User deleted successfully',
        'Close',
        { duration: 3000 }
      );
    });

    it('should not delete user when not confirmed', () => {
      spyOn(window, 'confirm').and.returnValue(false);

      component.deleteUser(mockUsers[0]);

      expect(window.confirm).toHaveBeenCalled();
      expect(userService.deleteUser).not.toHaveBeenCalled();
    });

    it('should handle error when deleting user fails', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      const error = new Error('Failed to delete user');
      userService.deleteUser.and.returnValue(throwError(() => error));

      component.deleteUser(mockUsers[0]);

      expect(snackBar.open).toHaveBeenCalledWith(
        'Error deleting user',
        'Close',
        { duration: 3000 }
      );
    });
  });

  describe('toggleUserStatus', () => {
    it('should toggle user status from active to inactive', () => {
      const updatedUser = { ...mockUsers[0], is_active: false };
      userService.updateUser.and.returnValue(of(updatedUser));

      component.toggleUserStatus(mockUsers[0]);

      expect(userService.updateUser).toHaveBeenCalledWith(mockUsers[0].id, {
        is_active: false
      });
      expect(snackBar.open).toHaveBeenCalledWith(
        'User deactivated successfully',
        'Close',
        { duration: 3000 }
      );
    });

    it('should toggle user status from inactive to active', () => {
      const inactiveUser = { ...mockUsers[0], is_active: false };
      const updatedUser = { ...inactiveUser, is_active: true };
      userService.updateUser.and.returnValue(of(updatedUser));

      component.toggleUserStatus(inactiveUser);

      expect(userService.updateUser).toHaveBeenCalledWith(inactiveUser.id, {
        is_active: true
      });
      expect(snackBar.open).toHaveBeenCalledWith(
        'User activated successfully',
        'Close',
        { duration: 3000 }
      );
    });

    it('should handle error when updating user status fails', () => {
      const error = new Error('Failed to update user');
      userService.updateUser.and.returnValue(throwError(() => error));

      component.toggleUserStatus(mockUsers[0]);

      expect(snackBar.open).toHaveBeenCalledWith(
        'Error updating user',
        'Close',
        { duration: 3000 }
      );
    });
  });

  describe('getRoleBadgeClass', () => {
    it('should return correct badge class for admin role', () => {
      expect(component.getRoleBadgeClass('admin')).toBe('badge-danger');
    });

    it('should return correct badge class for staff role', () => {
      expect(component.getRoleBadgeClass('staff')).toBe('badge-primary');
    });

    it('should return correct badge class for viewer role', () => {
      expect(component.getRoleBadgeClass('viewer')).toBe('badge-secondary');
    });

    it('should return default badge class for unknown role', () => {
      expect(component.getRoleBadgeClass('unknown')).toBe('badge-secondary');
    });
  });

  describe('formatDate', () => {
    it('should format date string correctly', () => {
      const dateString = '2023-01-01T00:00:00Z';
      const formatted = component.formatDate(dateString);
      
      expect(formatted).toBe('1/1/2023');
    });
  });
});
