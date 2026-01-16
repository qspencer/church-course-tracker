import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PlanningCenterService, PlanningCenterPerson } from '../../../services/planning-center.service';
import { UserService } from '../../../services/user.service';
import { LoggerService } from '../../../services/logger.service';
import { Observable, of } from 'rxjs';
import { map, startWith, debounceTime, distinctUntilChanged, switchMap, catchError } from 'rxjs/operators';

@Component({
  selector: 'app-user-import-dialog',
  templateUrl: './user-import-dialog.component.html',
  styleUrls: ['./user-import-dialog.component.scss']
})
export class UserImportDialogComponent implements OnInit {
  searchForm: FormGroup;
  searchControl: FormControl;
  searchResults: PlanningCenterPerson[] = [];
  isLoading = false;
  selectedPerson: PlanningCenterPerson | null = null;
  roleControl: FormControl;
  
  // Filtered results for autocomplete
  filteredResults!: Observable<PlanningCenterPerson[]>;

  constructor(
    private fb: FormBuilder,
    private planningCenterService: PlanningCenterService,
    private userService: UserService,
    private logger: LoggerService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<UserImportDialogComponent>
  ) {
    this.searchControl = new FormControl('', [Validators.required]);
    this.roleControl = new FormControl('instructor', [Validators.required]);
    
    this.searchForm = this.fb.group({
      search: this.searchControl,
      role: this.roleControl
    });
  }

  ngOnInit(): void {
    // Set up autocomplete with debounced search
    this.filteredResults = this.searchControl.valueChanges.pipe(
      startWith(''),
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(value => {
        if (!value || value.length < 2) {
          return of([]);
        }
        this.isLoading = true;
        return this.planningCenterService.searchPeople(value, 20).pipe(
          catchError(error => {
            this.logger.error('Error searching Planning Center', error);
            this.snackBar.open('Error searching Planning Center', 'Close', { duration: 3000 });
            return of([]);
          })
        );
      }),
      map(results => {
        this.isLoading = false;
        this.searchResults = results;
        return results;
      })
    );
  }

  displayPerson(person: PlanningCenterPerson | null): string {
    if (!person) return '';
    const attrs = person.attributes || {};
    const name = `${attrs.first_name || ''} ${attrs.last_name || ''}`.trim();
    const email = attrs.email || '';
    return email ? `${name} (${email})` : name;
  }

  onPersonSelected(person: PlanningCenterPerson): void {
    this.selectedPerson = person;
  }

  onImport(): void {
    if (!this.selectedPerson) {
      this.snackBar.open('Please select a person to import', 'Close', { duration: 3000 });
      return;
    }

    const attrs = this.selectedPerson.attributes || {};
    const firstName = attrs.first_name || '';
    const lastName = attrs.last_name || '';
    const fullName = `${firstName} ${lastName}`.trim();
    const email = attrs.email;
    const role = this.roleControl.value;

    if (!email) {
      this.snackBar.open('Selected person does not have an email address', 'Close', { duration: 3000 });
      return;
    }

    // Import the user
    // The backend will handle creating the user from Planning Center data
    // We'll call a new endpoint or use the existing user creation with PC data
    this.dialogRef.close({
      planning_center_person_id: this.selectedPerson.id,
      full_name: fullName,
      email: email,
      role: role
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}

