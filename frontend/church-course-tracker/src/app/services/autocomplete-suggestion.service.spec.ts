import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AutocompleteSuggestionService } from './autocomplete-suggestion.service';
import { environment } from '../../environments/environment';

describe('AutocompleteSuggestionService', () => {
  let service: AutocompleteSuggestionService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AutocompleteSuggestionService]
    });

    service = TestBed.inject(AutocompleteSuggestionService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getSuggestions', () => {
    it('should fetch suggestions for a field type', () => {
      const mockSuggestions = ['Location 1', 'Location 2', 'Location 3'];

      service.getSuggestions('location').subscribe(suggestions => {
        expect(suggestions).toEqual(mockSuggestions);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/autocomplete-suggestions/location` &&
        request.params.get('limit') === '50'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockSuggestions);
    });

    it('should fetch suggestions with custom limit', () => {
      const mockSuggestions = ['Location 1'];

      service.getSuggestions('location', 10).subscribe(suggestions => {
        expect(suggestions).toEqual(mockSuggestions);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/autocomplete-suggestions/location` &&
        request.params.get('limit') === '10'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockSuggestions);
    });
  });

  describe('addSuggestion', () => {
    it('should add a suggestion', () => {
      const mockResponse = { success: true };

      service.addSuggestion('location', 'New Location').subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/autocomplete-suggestions/location` &&
        request.params.get('value') === 'New Location'
      );
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toBeNull();
      req.flush(mockResponse);
    });
  });

  describe('addSuggestionsBatch', () => {
    it('should add multiple suggestions at once', () => {
      const values = ['Location 1', 'Location 2', 'Location 3'];
      const mockResponse = [{ success: true }, { success: true }, { success: true }];

      service.addSuggestionsBatch('location', values).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/autocomplete-suggestions/location/batch`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(values);
      req.flush(mockResponse);
    });
  });
});
