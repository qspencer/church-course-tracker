# Planning Center Registrations API Limitation

## Issue Summary

When fetching registrations for a Planning Center event, the API returns only the primary registrant for each registration submission, not all individual registrants within group/family registrations.

### Current Behavior
- **Expected**: 15 individual people registered for the event
- **Actual**: 10 registrations returned (one per submission)
- **Missing**: 5 additional people who were registered as part of group registrations

### Example
When a wife registers herself and her husband for a course:
- Planning Center UI shows: 2 people (wife + husband) under one registration ID
- Planning Center API returns: 1 registration with only the `registrant_contact` (wife)
- Missing: The husband's registration data

## Technical Details

### Endpoint Used
```
GET /registrations/v2/signups/{signup_id}/registrations
```

### Parameters Attempted
- `include=registrant_contact,registrants.person` - Attempted to include registrants
- `include_archived=true` - To ensure archived registrations are included
- Pagination handled with `per_page=100` and `offset`

### API Response
- Returns 10 registration records
- Each registration has:
  - `registrant_contact` relationship (the person who submitted the registration)
  - No `registrants` relationship available
- `meta.total_count: 10` - API confirms only 10 registrations exist at this level

### Endpoints Attempted (All Returned 404)
1. `/registrations/v2/registrations/{registration_id}/registrants`
2. `/registrations/v2/signups/{signup_id}/registrations/{registration_id}/registrants`

Both endpoints return `404 Not Found`, indicating these endpoints either:
- Don't exist in the Planning Center API
- Require different authentication/permissions
- Use a different endpoint structure

## What We've Tried

1. ✅ Including `registrants.person` in the initial request - No registrants returned
2. ✅ Fetching registrants via separate endpoint calls - All endpoints return 404
3. ✅ Checking included data for Registrant objects - None found
4. ✅ Pagination handling - Confirmed we're getting all available registrations
5. ✅ Including archived registrations - No change in results

## Current Workaround

The system currently returns only the primary registrant (`registrant_contact`) for each registration. This means:
- Group registrations (e.g., spouse + spouse) only show one person
- The system can import 10 enrollments instead of the expected 15

## Next Steps

1. **Contact Planning Center Support** to ask:
   - How to access all individual registrants within a group registration via the API
   - Whether there's a different endpoint or parameter to fetch all registrants
   - If this requires different API permissions or credentials
   - If this is a known limitation of the Registrations API

2. **Alternative Solutions** (if the API doesn't support this):
   - Accept that we can only import primary registrants
   - Manually add the additional people after import
   - Use a different data source or export method from Planning Center

## Event Details (For Support Reference)

- **Event ID**: `16425231`
- **Event Name**: "The Practicing the Way Course - Wilson"
- **Signup ID** (from registration_url): `3070694`
- **Expected Registrations**: 15 people
- **API Returns**: 10 registrations
- **Registration IDs Returned**: 
  - 69901166, 69884085, 69614278, 69520367, 69517898, 69517891, 69498554, 69473637, 69429683, 68894976

## Code Location

The registration fetching logic is in:
- `backend/app/services/planning_center_sync_service.py`
- Method: `get_event_registrations()`
- Starting around line 1469

## Date Documented
2025-01-XX (Current date)


