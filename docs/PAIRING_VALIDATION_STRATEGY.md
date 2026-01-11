# Pairing Constraint Validation Strategy

## Recommended Approach: Hybrid (Proactive + Reactive)

### Strategy Overview
Use a **multi-layered validation approach** that combines:
1. **Proactive Prevention** - Filter options to prevent obvious violations
2. **Real-time Feedback** - Show warnings and constraint information as user selects
3. **Submit-time Validation** - Final validation with clear error messages

## Implementation Plan

### Layer 1: Proactive Prevention (Prevent Bad Data Entry)

#### A. Filter Secondary Participants Dropdown
When a primary participant is selected:
- **If `allow_multiple_secondary = false`**: 
  - Filter out secondary participants who are already paired with the selected primary
  - Show message: "This primary already has a secondary participant"
  
- **If `max_secondary_per_primary` is set**:
  - Count existing active pairings for the selected primary
  - If at max, disable secondary dropdown and show: "Maximum {{ max }} secondary participants reached for this primary"
  - If near max, show warning: "{{ remaining }} more secondary participant(s) allowed for this primary"

#### B. Visual Indicators
- Show count badge next to primary participants: "3/3 secondaries" (when at max)
- Gray out or disable primary participants who are at capacity
- Show tooltip explaining why a participant is disabled

#### C. Dynamic Secondary List Updates
- As primary participant changes, immediately update available secondary participants
- Show count: "{{ availableCount }} secondary participants available"

### Layer 2: Real-time Feedback (Inform User)

#### A. Constraint Display
- Show current constraint status in the dialog:
  ```
  Current Pairings for [Primary Name]:
  - [Secondary 1 Name]
  - [Secondary 2 Name]
  - [Secondary 3 Name] (MAX REACHED)
  ```

#### B. Warning Messages
- When selecting a secondary that would violate constraints:
  - Show inline warning: "⚠️ This would exceed the maximum of {{ max }} secondaries per primary"
  - Highlight the constraint in the info box
  - Disable submit button until resolved

#### C. Live Validation
- Validate constraints as user makes selections (not just on submit)
- Show error messages immediately when constraint would be violated
- Use Angular reactive forms validators for real-time feedback

### Layer 3: Submit-time Validation (Final Check)

#### A. Backend Validation
- Always validate on backend (server is source of truth)
- Return clear, actionable error messages:
  - "Cannot create pairing: Primary participant 'John Doe' already has the maximum of 3 secondary participants"
  - "Cannot create pairing: Multiple secondary participants not allowed for this program"

#### B. Frontend Pre-submit Check
- Before calling API, do a final validation check
- Show error summary if violations found
- Prevent API call if validation fails

#### C. Error Display
- Show errors in a clear, non-blocking way:
  - Use `mat-error` for field-level errors
  - Use snackbar for general constraint violations
  - Use info box with error styling for constraint violations

## Implementation Details

### 1. Update Pairing Dialog Component

```typescript
// Add methods to check constraints
checkPrimaryCapacity(primaryId: number): {
  current: number;
  max: number | null;
  atCapacity: boolean;
  remaining: number;
}

getAvailableSecondaries(primaryId: number): ProgramParticipant[] {
  // Filter based on:
  // - allow_multiple_secondary
  // - max_secondary_per_primary
  // - Existing pairings
}

// Watch for primary selection changes
this.pairingForm.get('primary_participant_id')?.valueChanges.subscribe(primaryId => {
  this.updateAvailableSecondaries(primaryId);
  this.checkConstraints();
});
```

### 2. Add Custom Validators

```typescript
// Custom validator for pairing constraints
pairingConstraintValidator(program: Program, existingPairings: ProgramPairing[]) {
  return (control: AbstractControl): ValidationErrors | null => {
    const primaryId = control.parent?.get('primary_participant_id')?.value;
    const secondaryId = control.value;
    
    if (!primaryId || !secondaryId) return null;
    
    // Check constraints
    const config = program.relationship_config;
    const existingCount = existingPairings.filter(
      p => p.primary_participant_id === primaryId && p.status === 'active'
    ).length;
    
    if (!config.allow_multiple_secondary && existingCount > 0) {
      return { multipleNotAllowed: true };
    }
    
    if (config.max_secondary_per_primary && existingCount >= config.max_secondary_per_primary) {
      return { maxReached: { max: config.max_secondary_per_primary } };
    }
    
    return null;
  };
}
```

### 3. Update UI Components

#### A. Enhanced Info Box
```html
<div class="constraint-status" *ngIf="selectedPrimary">
  <mat-icon [color]="isAtCapacity ? 'warn' : 'primary'">info</mat-icon>
  <div>
    <strong>Current Pairings:</strong>
    <ul>
      <li *ngFor="let pairing of existingPairings">
        {{ getSecondaryName(pairing.secondary_participant_id) }}
      </li>
      <li *ngIf="isAtCapacity" class="at-capacity">
        ⚠️ Maximum capacity reached
      </li>
    </ul>
    <p *ngIf="!isAtCapacity">
      {{ remainingSlots }} more secondary participant(s) allowed
    </p>
  </div>
</div>
```

#### B. Filtered Dropdown with Indicators
```html
<mat-select formControlName="secondary_participant_id">
  <mat-option 
    *ngFor="let participant of availableSecondaries" 
    [value]="participant.id"
    [disabled]="isParticipantDisabled(participant)">
    {{ getParticipantDisplay(participant) }}
    <span *ngIf="isParticipantDisabled(participant)" class="disabled-reason">
      (Already paired with this primary)
    </span>
  </mat-option>
  <mat-option *ngIf="availableSecondaries.length === 0" disabled>
    No available secondary participants (constraints limit reached)
  </mat-option>
</mat-select>
```

### 4. Backend Error Messages

Ensure backend returns user-friendly error messages:
```python
# In program_service.py validate_pairing_constraints
if existing_pairings >= max_secondary:
    return (
        False,
        f"Primary participant already has {existing_pairings} secondary participant(s). "
        f"Maximum allowed is {max_secondary}. Please remove an existing pairing first."
    )
```

## User Experience Flow

### Scenario 1: User selects primary at capacity
1. User selects primary participant
2. System checks existing pairings
3. **Proactive**: Secondary dropdown shows only available participants (or empty if none)
4. **Feedback**: Info box shows "Maximum capacity reached (3/3)"
5. **Prevention**: Submit button disabled with tooltip explaining why

### Scenario 2: User selects primary near capacity
1. User selects primary with 2/3 secondaries
2. **Feedback**: Info box shows "1 more secondary participant allowed"
3. **Proactive**: Secondary dropdown shows all available secondaries
4. User can proceed normally

### Scenario 3: User tries to add when not allowed
1. User selects primary
2. System detects `allow_multiple_secondary = false` and primary already has a secondary
3. **Proactive**: Secondary dropdown is empty with message "This primary already has a secondary participant"
4. **Feedback**: Info box explains the constraint
5. **Prevention**: Submit button disabled

### Scenario 4: Constraint violation on submit
1. User somehow bypasses frontend validation (edge case)
2. **Reactive**: Backend validates and returns error
3. **Feedback**: Snackbar shows clear error message
4. **Action**: User can see what went wrong and fix it

## Benefits of This Approach

1. **Prevents Most Errors**: Proactive filtering prevents 90% of constraint violations
2. **Clear Communication**: Users understand constraints before they try to violate them
3. **Flexible**: Still allows edge cases to be handled gracefully
4. **User-Friendly**: No frustrating "try and fail" experiences
5. **Maintainable**: Clear separation of concerns (UI validation + backend validation)

## Implementation Priority

### Phase 1 (High Priority - Immediate Value):
1. Add constraint checking when primary is selected
2. Filter secondary participants dropdown based on constraints
3. Show constraint status in info box
4. Disable submit button when constraints would be violated

### Phase 2 (Medium Priority - Enhanced UX):
1. Add visual indicators (badges, counts) on primary participants
2. Real-time validation with custom validators
3. Enhanced error messages with actionable guidance

### Phase 3 (Low Priority - Polish):
1. Tooltips explaining constraints
2. Constraint summary in pairing management list
3. Bulk validation for multiple pairings

## Code Changes Required

1. **Frontend**:
   - `pairing-dialog.component.ts`: Add constraint checking logic
   - `pairing-dialog.component.html`: Update UI with constraint feedback
   - Add custom validators for pairing constraints
   - Load existing pairings when dialog opens

2. **Backend** (Already mostly done):
   - Ensure `validate_pairing_constraints` returns clear error messages
   - Consider adding endpoint to get pairing count for a primary participant

3. **Services**:
   - Add method to get existing pairings for a primary participant
   - Add method to check if pairing would violate constraints

## Example Error Messages

**Proactive (Before Submit):**
- "This primary participant already has the maximum of 3 secondary participants. Please select a different primary or remove an existing pairing."
- "Multiple secondary participants are not allowed for this program. This primary already has 1 secondary participant."

**Reactive (On Submit):**
- "Cannot create pairing: Primary participant 'John Doe' already has 3 secondary participants (maximum allowed)."
- "Cannot create pairing: This program does not allow multiple secondary participants per primary."

