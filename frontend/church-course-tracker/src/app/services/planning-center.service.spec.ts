import { TestBed } from '@angular/core/testing';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

import { PlanningCenterService } from './planning-center.service';
import { environment } from '../../environments/environment';

describe('PlanningCenterService', () => {
  let service: PlanningCenterService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      providers: [
        PlanningCenterService,
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ]
    });
    service = TestBed.inject(PlanningCenterService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get events', () => {
    const mockEvents = [
      {
        id: 'pc_event_1',
        type: 'Event',
        attributes: {
          name: 'Test Event',
          start_date: '2024-01-15T10:00:00Z',
          end_date: '2024-01-15T12:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        relationships: {
          event_type: {
            data: {
              id: 'event_type_1',
              type: 'EventType'
            }
          }
        }
      }
    ];

    service.getEvents().subscribe(events => {
      expect(events.length).toBe(1);
      expect(events[0].id).toBe('pc_event_1');
      expect(events[0].attributes.name).toBe('Test Event');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/events`);
    expect(req.request.method).toBe('GET');
    req.flush(mockEvents);
  });

  it('should get lists', () => {
    const mockLists = [
      {
        id: 'pc_list_1',
        type: 'List',
        attributes: {
          name: 'Test List',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      }
    ];

    service.getLists().subscribe(lists => {
      expect(lists.length).toBe(1);
      expect(lists[0].id).toBe('pc_list_1');
      expect(lists[0].attributes.name).toBe('Test List');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/lists`);
    expect(req.request.method).toBe('GET');
    req.flush(mockLists);
  });

  it('should get a single event', () => {
    const mockEvent = {
      id: 'pc_event_1',
      type: 'Event',
      attributes: {
        name: 'Test Event',
        start_date: '2024-01-15T10:00:00Z',
        end_date: '2024-01-15T12:00:00Z',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      relationships: {
        event_type: {
          data: {
            id: 'event_type_1',
            type: 'EventType'
          }
        }
      }
    };

    service.getEvent('pc_event_1').subscribe(event => {
      expect(event.id).toBe('pc_event_1');
      expect(event.attributes.name).toBe('Test Event');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/events/pc_event_1`);
    expect(req.request.method).toBe('GET');
    req.flush(mockEvent);
  });

  it('should get a single list', () => {
    const mockList = {
      id: 'pc_list_1',
      type: 'List',
      attributes: {
        name: 'Test List',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    };

    service.getList('pc_list_1').subscribe(list => {
      expect(list.id).toBe('pc_list_1');
      expect(list.attributes.name).toBe('Test List');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/lists/pc_list_1`);
    expect(req.request.method).toBe('GET');
    req.flush(mockList);
  });

  it('should sync all', () => {
    const mockResponse = { status: 'started' };

    service.syncAll().subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/planning-center/all`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });
});
