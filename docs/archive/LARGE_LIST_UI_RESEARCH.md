# Research: UI Options for Handling Large Lists of Events/Lists from Planning Center

## Current Implementation
- Using `mat-select` with `*ngFor` to render all events/lists
- Problem: Performance degrades with large lists (>20 items)
- Current behavior: Backend fetches up to 500 events, frontend renders all in dropdown

## Requirements
- Handle large datasets (>20 items) efficiently
- Maintain good user experience
- Allow users to find specific events/lists quickly
- Work within Angular Material ecosystem

## Research Options

### Option 1: mat-autocomplete with Client-Side Filtering
**Description:** Replace `mat-select` with `mat-autocomplete` that filters locally

**Pros:**
- ✅ Already used in codebase (locations, delivery modes)
- ✅ Users can type to search/filter
- ✅ Good UX for finding items quickly
- ✅ No backend changes needed
- ✅ Works well for 100-500 items

**Cons:**
- ❌ Still loads all items into memory
- ❌ Filtering happens on client-side (can be slow with 500+ items)
- ❌ Initial load time for large datasets

**Performance:** Good for up to ~500 items with client-side filtering

**Implementation Complexity:** Low (autocomplete already used in codebase)

**Example:**
```typescript
// Filter events as user types
filteredEvents$ = this.eventInput.valueChanges.pipe(
  startWith(''),
  map(value => this._filterEvents(value))
);

private _filterEvents(value: string): PlanningCenterEvent[] {
  const filterValue = value.toLowerCase();
  return this.events.filter(event => 
    event.attributes.name.toLowerCase().includes(filterValue)
  );
}
```

---

### Option 2: mat-autocomplete with Server-Side Search
**Description:** Use `mat-autocomplete` with backend search API

**Pros:**
- ✅ Only loads matching results
- ✅ Fast even with thousands of items
- ✅ Reduces bandwidth and memory usage
- ✅ Scales to any dataset size
- ✅ Better user experience (search as you type)

**Cons:**
- ❌ Requires backend search endpoint
- ❌ More complex implementation
- ❌ Network requests on each keystroke (needs debouncing)

**Performance:** Excellent for any dataset size

**Implementation Complexity:** Medium (needs backend search endpoint + debouncing)

**Example:**
```typescript
// Search events on backend as user types
this.eventInput.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(query => 
    query ? this.planningCenterService.searchEvents(query) : of([])
  )
).subscribe(results => this.filteredEvents = results);
```

---

### Option 3: Hybrid Approach - Conditional UI
**Description:** Use `mat-select` for small lists (<20), switch to `mat-autocomplete` for large lists

**Pros:**
- ✅ Best of both worlds
- ✅ Simple dropdown for small lists
- ✅ Searchable autocomplete for large lists
- ✅ Automatically adapts to data size

**Cons:**
- ❌ Slightly more complex conditional logic
- ❌ Two different UI patterns

**Performance:** Optimal for all scenarios

**Implementation Complexity:** Low-Medium

**Example:**
```html
<!-- Small list: mat-select -->
<mat-select *ngIf="events.length <= 20" formControlName="pc_event_id">
  <mat-option *ngFor="let event of events" [value]="event.id">
    {{ event.attributes.name }}
  </mat-option>
</mat-select>

<!-- Large list: mat-autocomplete -->
<mat-autocomplete *ngIf="events.length > 20" #eventAuto="matAutocomplete">
  <mat-option *ngFor="let event of filteredEvents" [value]="event.id">
    {{ event.attributes.name }}
  </mat-option>
</mat-autocomplete>
```

---

### Option 4: CDK Virtual Scrolling with mat-select
**Description:** Use Angular CDK Virtual Scrolling inside mat-select

**Pros:**
- ✅ Only renders visible items in DOM
- ✅ Smooth scrolling performance
- ✅ Familiar dropdown UI

**Cons:**
- ❌ Complex implementation
- ❌ Not natively supported by mat-select
- ❌ Requires custom wrapper component
- ❌ Still loads all data into memory

**Performance:** Good for rendering, but still loads all data

**Implementation Complexity:** High

**Status:** Not recommended - mat-select doesn't support virtual scrolling well

---

### Option 5: Paginated Selection Dialog
**Description:** Open a dialog with a searchable, paginated table/list

**Pros:**
- ✅ Handles very large datasets
- ✅ Full control over UI/UX
- ✅ Can show more details (dates, descriptions)
- ✅ Familiar table/pagination pattern

**Cons:**
- ❌ More clicks to select (opens dialog)
- ❌ More complex implementation
- ❌ Different UX pattern

**Performance:** Excellent for any dataset size

**Implementation Complexity:** Medium-High

**Example:**
- Click button → Opens dialog with searchable table
- User searches/filters
- User clicks row to select
- Dialog closes, selection populated

---

### Option 6: mat-autocomplete with Virtual Scrolling (CDK)
**Description:** Combine autocomplete with CDK virtual scrolling

**Pros:**
- ✅ Search/filter functionality
- ✅ Efficient rendering for large results
- ✅ Scales well

**Cons:**
- ❌ Complex implementation
- ❌ Requires CDK ScrollingModule
- ❌ Still needs client-side or server-side filtering

**Performance:** Excellent

**Implementation Complexity:** Medium-High

---

## Recommendation Matrix

| Option | Dataset Size | Implementation | UX | Performance | Recommendation |
|--------|-------------|----------------|-----|-------------|----------------|
| 1. Client-side autocomplete | <500 items | Low | Good | Good | ⭐⭐⭐ Best for current needs |
| 2. Server-side search | Any size | Medium | Excellent | Excellent | ⭐⭐⭐⭐ Best long-term |
| 3. Hybrid approach | Any size | Low-Medium | Excellent | Excellent | ⭐⭐⭐⭐⭐ **BEST OVERALL** |
| 4. Virtual scroll select | Large | High | Good | Good | ⭐ Not recommended |
| 5. Selection dialog | Any size | Medium-High | Good | Excellent | ⭐⭐⭐ If you want richer UI |
| 6. Autocomplete + virtual | Large | Medium-High | Excellent | Excellent | ⭐⭐⭐⭐ If needed later |

## Recommended Approach

### **Hybrid Approach (Option 3)** is the best balance:

1. **For small lists (≤20 items):** Keep `mat-select` - simple, fast, familiar
2. **For large lists (>20 items):** Switch to `mat-autocomplete` with client-side filtering
3. **Future enhancement:** Add server-side search if datasets grow very large

### Implementation Strategy:

```typescript
// Component logic
hasLargeList = this.events.length > 20;

// For autocomplete
filteredEvents$ = this.searchInput.valueChanges.pipe(
  startWith(''),
  map(value => this._filterEvents(value))
);
```

### Benefits:
- ✅ Minimal code changes
- ✅ Leverages existing autocomplete patterns in codebase
- ✅ Excellent user experience for both small and large lists
- ✅ Can be enhanced later with server-side search
- ✅ No backend changes required initially

---

## Additional Considerations

### Performance Optimization:
1. **Debounce search input** (300ms) to reduce filtering operations
2. **Limit initial display** (show first 50 matches)
3. **Lazy load** if needed (load more on scroll)

### User Experience Enhancements:
1. **Show count**: "Showing 25 of 500 events"
2. **Highlight search terms** in results
3. **Keyboard navigation** (already in mat-autocomplete)
4. **Recent/favorites** section at top

### Backend Optimization (Future):
1. Add search endpoint: `GET /planning-center/events/search?q=...`
2. Server-side filtering reduces bandwidth
3. Can add pagination support

---

## Next Steps

1. **Implement hybrid approach** (Option 3)
2. **Test with large datasets** to verify performance
3. **Monitor user feedback**
4. **Consider server-side search** if datasets exceed 1000+ items



