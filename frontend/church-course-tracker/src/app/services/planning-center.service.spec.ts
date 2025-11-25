import { TestBed } from '@angular/core/testing';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

import { PlanningCenterService } from './planning-center.service';

describe('PlanningCenterService', () => {
  let service: PlanningCenterService;

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
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
