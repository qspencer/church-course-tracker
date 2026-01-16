# Planning Center API: Registrations Issue - Multiple People Per Registration

## Issue Summary

We are successfully fetching registrations for a Planning Center Calendar event, but are only receiving the primary registrant (10 people) when there should be 15 total people registered. Some registrations include multiple people (e.g., when a wife registers herself and her husband), but the API only returns one person per registration.

## Current Situation

### What's Working
- ✅ Event is successfully found via Calendar API: Event ID `16425231`
- ✅ Registration URL is successfully extracted: `3070694` (signup ID)
- ✅ Registrations endpoint returns 10 registrations: `/registrations/v2/signups/3070694/registrations`
- ✅ Each registration includes `registrant_contact` (the person who submitted the registration)
- ✅ API reports `total_count: 10` in metadata

### What's Not Working
- ❌ Only 10 people are returned, but Planning Center UI shows 15 people registered
- ❌ Multiple people registered under the same registration ID (group/family registrations) are not accessible via API
- ❌ The `/registrants` endpoint does not exist or is not accessible (returns 404)

## Expected vs. Actual

### Expected (from Planning Center UI)
- **10 unique registration IDs**
- **15 total people** registered
- Some registration IDs appear multiple times with different people:
  - `69520367`: David Barefoot AND Teresa Barefoot
  - `69498554`: Janice Chamberlain AND Ron Chamberlain  
  - `69473637`: William McMurray AND Jennifer McMurray
  - `68894976`: Keegan Sullinger AND Mikaela Sullinger
  - `69517898`: Samara Batts AND Quentin Spencer

### Actual (from API)
- ✅ 10 unique registration IDs returned
- ❌ Only 10 people (one per registration - the `registrant_contact`)
- ❌ The 5 additional people from group registrations are not accessible

## API Endpoints Attempted

### 1. Fetching Registrations by Signup ✅ WORKS
```
GET /registrations/v2/signups/3070694/registrations
Params:
  - per_page: 100
  - offset: 0
  - include: registrant_contact,registrants.person
  - include_archived: true
```
**Result:** Returns 10 registrations, each with only `registrant_contact` relationship. No `registrants` relationship present.

### 2. Fetching Registrants for a Registration ❌ 404 NOT FOUND
```
GET /registrations/v2/signups/3070694/registrations/{registration_id}/registrants
Params:
  - include: person
  - include_archived: true
```
**Result:** 404 Not Found

### 3. Alternative Registrants Endpoint ❌ 404 NOT FOUND
```
GET /registrations/v2/registrations/{registration_id}/registrants
Params:
  - include: person
  - include_archived: true
```
**Result:** 404 Not Found

## Code Implementation

### Current Code Location
`backend/app/services/planning_center_sync_service.py` - `get_event_registrations()` method

### Current Behavior
1. Fetches event from Calendar API to get `registration_url`
2. Extracts signup ID (`3070694`) from `registration_url`
3. Queries `/registrations/v2/signups/{signup_id}/registrations`
4. Attempts to fetch registrants via `/registrants` endpoints (all fail with 404)
5. Falls back to using only `registrant_contact` (one person per registration)

### Log Output Example
```
INFO: Found signup with ID '3070694', now fetching its registrations
INFO: Page 1: Found 10 registrations (total_count from meta: 10)
INFO: Pagination metadata: meta={'total_count': 10, 'count': 10, 'can_include': ['created_by', 'registrant_contact'], ...}
INFO: Included data types in page 1: {'Person': 10}
INFO: Registration 69520367: falling back to registrant_contact (only 1 person)
INFO: Returning 10 registrations from signup ID 3070694
```

## Questions for Planning Center Support

1. **How do we access all individual registrants for a registration that includes multiple people?**

2. **Is there a different endpoint or parameter we should use to fetch registrants?**

3. **Does the API support fetching registrants, or is this only available in the Planning Center UI?**

4. **Are registrants stored differently in the API structure than we're expecting?**

5. **Do we need different API credentials/permissions to access registrant data?**

6. **When a registration includes multiple people (e.g., family registration), how should we access each individual person's information via the API?**

## Technical Details

### Event Information
- **Calendar Event ID:** `16425231`
- **Event Name:** "The Practicing the Way Course - Wilson"
- **Signup ID (from registration_url):** `3070694`
- **Registration URL:** `https://eastgatechurchnc.churchcenter.com/registrations/events/3070694`

### Registration IDs Returned
1. `68894976` - Keegan Sullinger (but UI shows also Mikaela Sullinger)
2. `69429683` - Larry Arthur
3. `69473637` - William McMurray (but UI shows also Jennifer McMurray)
4. `69498554` - Janice Chamberlain (but UI shows also Ron Chamberlain)
5. `69517891` - Stefania Blevins
6. `69517898` - Samara Batts (but UI shows also Quentin Spencer)
7. `69520367` - David Barefoot (but UI shows also Teresa Barefoot)
8. `69614278` - Tevin Jordan
9. `69884085` - Alan Huff
10. `69901166` - Kimberly Vasquez

### Sample Registration Structure
```json
{
  "type": "Registration",
  "id": "69520367",
  "attributes": {
    "created_at": "2025-09-02T13:34:52Z",
    "updated_at": "2025-09-02T13:34:52Z"
  },
  "relationships": {
    "registrant_contact": {
      "data": {
        "type": "Person",
        "id": "146684602"
      },
      "links": {
        "related": "https://api.planningcenteronline.com/registrations/v2/signups/3070694/registrations/69520367/registrant_contact"
      }
    }
  }
}
```

**Note:** No `registrants` relationship is present in the response.

## Workaround (Current)

Currently, the system only imports the primary registrant (`registrant_contact`) for each registration. This means:
- ✅ 10 people are imported (the person who submitted each registration)
- ❌ 5 additional people are missing (secondary registrants in group registrations)

## Next Steps

1. **Contact Planning Center Support** with this document
2. **Wait for guidance** on how to access all registrants via API
3. **Update implementation** once the correct endpoint/approach is identified
4. **Re-import registrations** to capture all 15 people

---

**Document Created:** 2025-01-01  
**Last Updated:** 2025-01-01  
**Status:** Waiting on Planning Center Support response

