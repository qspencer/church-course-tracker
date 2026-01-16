# Planning Center Support Request - Registration API Access

## Issue
Unable to fetch registrations for a Calendar event via Planning Center API. All API endpoints return 404.

## Event Details
- **Calendar Event ID**: `16425231`
- **Event Name**: "The Practicing the Way Course - Wilson"
- **Registration URL**: `https://eastgatechurchnc.churchcenter.com/registrations/events/3070694`
- **Registration Event ID** (from URL): `3070694`
- **Number of Event Instances**: 16
- **Expected Registrations**: 15 people are registered for this event

## API Endpoints Attempted (All Return 404)

### 1. Check-Ins API
- `GET /check-ins/v2/events/16425231/event_times?include=event_time_registrations.person`
- Result: 401 Unauthorized

### 2. Events API
- `GET /events/v2/events/16425231/registrations?include=person`
- Result: 404 Not Found

### 3. Registrations API - Event-specific
- `GET /registrations/v2/events/16425231/registrations?include=person`
- Result: 404 Not Found
- `GET /registrations/v2/events/3070694/registrations?include=person` (using ID from registration_url)
- Result: 404 Not Found

### 4. Calendar API
- `GET /calendar/v2/events/16425231/registrations?include=person`
- Result: 404 Not Found
- `GET /calendar/v2/events/16425231/event_instances?include=signups.person`
- Result: 200 OK (16 instances found, but no signups in included data)
- `GET /calendar/v2/event_instances/{instance_id}/signups?include=person`
- Result: 404 Not Found (tried 3 instances)

### 5. Query-based Approaches
- `GET /registrations/v2/registrations?where[event_id]=16425231&include=person,event`
- Result: 404 Not Found (tried with various archived parameters)

### 6. General API Access Test
- `GET /registrations/v2/registrations?per_page=10&include=person,event`
- Result: 404 Not Found

## Observations

1. **Registration URL Structure**: The `registration_url` field in the Calendar event points to `churchcenter.com` (public-facing site), not `planningcenteronline.com` (API). This suggests registrations might be stored in a different system.

2. **Event Instances**: The Calendar event has 16 instances, but none of them have accessible signups via the API.

3. **No Count Attributes**: Event instances don't have `signup_count` or `registration_count` attributes that would indicate registrations exist.

## Questions for Planning Center Support

1. Are registrations for Calendar events accessible via the Planning Center API?
2. Is there a different API endpoint or method to access registrations for Calendar events?
3. Does the `registration_url` field (pointing to `churchcenter.com`) indicate that registrations are stored in a different system?
4. Is there a mapping between Calendar event IDs and Registration event IDs that we should use?
5. Are there specific permissions or API scopes required to access registration data?
6. Should we be using the Events API, Check-Ins API, or Registrations API for Calendar event registrations?

## Code Implementation

We've implemented comprehensive fallback logic that tries multiple API endpoints:
- Check-Ins API (with archived support)
- Events API (with archived support)
- Registrations API (with archived support)
- Calendar API (event instances and signups)
- Query-based searches with various archived parameters

All approaches result in 404 responses, suggesting the registrations may not be accessible via the API, or require a different access method.

## Environment
- Planning Center API Base URL: `https://api.planningcenteronline.com`
- Authentication: Using Application ID and Secret (HTTP Basic Auth)
- API Access: Working for events, people, and other resources


