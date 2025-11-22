import { TestBed } from '@angular/core/testing';

import { PlanningCenterService } from './planning-center.service';

describe('PlanningCenterService', () => {
  let service: PlanningCenterService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PlanningCenterService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
