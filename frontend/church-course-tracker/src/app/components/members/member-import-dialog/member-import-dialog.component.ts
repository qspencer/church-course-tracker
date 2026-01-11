import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PlanningCenterService, PlanningCenterPerson } from '../../../services/planning-center.service';
import { MemberService } from '../../../services/member.service';
import { Observable, of } from 'rxjs';
import { map, startWith, debounceTime, distinctUntilChanged, switchMap, catchError } from 'rxjs/operators';

@Component({
  selector: 'app-member-import-dialog',
  templateUrl: './member-import-dialog.component.html',
  styleUrls: ['./member-import-dialog.component.scss']
})
export class MemberImportDialogComponent implements OnInit {
  searchForm: FormGroup;
  searchControl: FormControl;
  searchResults: PlanningCenterPerson[] = [];
  isLoading = false;
  selectedPerson: PlanningCenterPerson | null = null;
  
  // Filtered results for autocomplete
  filteredResults!: Observable<PlanningCenterPerson[]>;

  constructor(
    private fb: FormBuilder,
    private planningCenterService: PlanningCenterService,
    private memberService: MemberService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<MemberImportDialogComponent>
  ) {
    this.searchControl = new FormControl('', [Validators.required]);
    
    this.searchForm = this.fb.group({
      search: this.searchControl
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
            console.error('Error searching Planning Center:', error);
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

    // Import the member from Planning Center
    this.memberService.importMemberFromPlanningCenter(this.selectedPerson.id).subscribe({
      next: (member) => {
        const fullName = `${member.first_name} ${member.last_name}`.trim();
        this.snackBar.open(`Member "${fullName}" imported successfully`, 'Close', { duration: 3000 });
        this.dialogRef.close(member);
      },
      error: (error) => {
        console.error('Error importing member:', error);
        const errorMsg = error?.error?.detail || 'Error importing member from Planning Center';
        this.snackBar.open(errorMsg, 'Close', { duration: 5000 });
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}

