import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ProgramService } from './program.service';
import { environment } from '../../environments/environment';
import {
  Program,
  ProgramCreate,
  ProgramUpdate,
  ProgramAdmin,
  ProgramAdminCreate,
  ProgramParticipant,
  ProgramParticipantCreate,
  ProgramParticipantUpdate,
  ProgramPairing,
  ProgramPairingCreate,
  ProgramSession,
  ProgramSessionCreate,
  ProgramProgress,
  ProgramProgressCreate
} from '../models/program.model';

describe('ProgramService', () => {
  let service: ProgramService;
  let httpMock: HttpTestingController;

  const mockProgram: Program = {
    id: 1,
    title: 'Test Program',
    description: 'Test Description',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockAdmin: ProgramAdmin = {
    id: 1,
    program_id: 1,
    user_id: 1,
    can_manage_participants: true,
    can_manage_pairings: true,
    can_manage_content: true,
    created_at: '2023-01-01T00:00:00Z'
  };

  const mockParticipant: ProgramParticipant = {
    id: 1,
    program_id: 1,
    people_id: 1,
    role_name: 'participant',
    start_date: '2023-01-01',
    status: 'active',
    progress_percentage: 0,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockPairing: ProgramPairing = {
    id: 1,
    program_id: 1,
    primary_participant_id: 1,
    secondary_participant_id: 2,
    start_date: '2023-01-01',
    status: 'active',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockSession: ProgramSession = {
    id: 1,
    program_id: 1,
    pairing_id: 1,
    session_date: '2023-01-15',
    duration_minutes: 60,
    location: 'Room 101',
    created_at: '2023-01-01T00:00:00Z'
  };

  const mockProgress: ProgramProgress = {
    id: 1,
    program_id: 1,
    participant_id: 1,
    progress_type: 'content_completion',
    content_id: 1,
    completion_percentage: 100,
    completion_date: '2023-01-15T10:00:00Z',
    created_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ProgramService]
    });

    service = TestBed.inject(ProgramService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('Program CRUD', () => {
    it('should fetch programs', () => {
      service.getPrograms().subscribe(programs => {
        expect(programs).toEqual([mockProgram]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs`);
      expect(req.request.method).toBe('GET');
      req.flush([mockProgram]);
    });

    it('should fetch programs with parameters', () => {
      const params = { is_active: true };
      service.getPrograms(params).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/programs` &&
        request.params.get('is_active') === 'true'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockProgram]);
    });

    it('should fetch a single program', () => {
      service.getProgram(1).subscribe(program => {
        expect(program).toEqual(mockProgram);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockProgram);
    });

    it('should create a program', () => {
      const programCreate: ProgramCreate = {
        title: 'New Program',
        description: 'New Description',
        is_active: true
      };

      service.createProgram(programCreate).subscribe(program => {
        expect(program).toEqual(mockProgram);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(programCreate);
      req.flush(mockProgram);
    });

    it('should update a program', () => {
      const programUpdate: ProgramUpdate = {
        title: 'Updated Program'
      };

      service.updateProgram(1, programUpdate).subscribe(program => {
        expect(program).toEqual(mockProgram);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(programUpdate);
      req.flush(mockProgram);
    });

    it('should delete a program', () => {
      service.deleteProgram(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Program Admin methods', () => {
    it('should fetch program admins', () => {
      service.getProgramAdmins(1).subscribe(admins => {
        expect(admins).toEqual([mockAdmin]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/admins`);
      expect(req.request.method).toBe('GET');
      req.flush([mockAdmin]);
    });

    it('should add a program admin', () => {
      const adminCreate: ProgramAdminCreate = {
        program_id: 1,
        user_id: 1,
        can_manage_participants: true
      };

      service.addProgramAdmin(1, adminCreate).subscribe(admin => {
        expect(admin).toEqual(mockAdmin);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/admins`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(adminCreate);
      req.flush(mockAdmin);
    });

    it('should update a program admin', () => {
      const adminUpdate = { can_manage_participants: false };

      service.updateProgramAdmin(1, adminUpdate).subscribe(admin => {
        expect(admin).toEqual(mockAdmin);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/admins/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(adminUpdate);
      req.flush(mockAdmin);
    });

    it('should remove a program admin', () => {
      service.removeProgramAdmin(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/admins/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Program Participant methods', () => {
    it('should fetch all program participants', () => {
      service.getAllProgramParticipants().subscribe(participants => {
        expect(participants).toEqual([mockParticipant]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/participants`);
      expect(req.request.method).toBe('GET');
      req.flush([mockParticipant]);
    });

    it('should fetch all program participants with status filter', () => {
      service.getAllProgramParticipants('active').subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/programs/participants` &&
        request.params.get('status') === 'active'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockParticipant]);
    });

    it('should fetch program participants', () => {
      service.getProgramParticipants(1).subscribe(participants => {
        expect(participants).toEqual([mockParticipant]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/participants`);
      expect(req.request.method).toBe('GET');
      req.flush([mockParticipant]);
    });

    it('should fetch program participants with status filter', () => {
      service.getProgramParticipants(1, 'active').subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/programs/1/participants` &&
        request.params.get('status') === 'active'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockParticipant]);
    });

    it('should add a program participant', () => {
      const participantCreate: ProgramParticipantCreate = {
        program_id: 1,
        people_id: 1,
        role_name: 'participant',
        status: 'active'
      };

      service.addProgramParticipant(1, participantCreate).subscribe(participant => {
        expect(participant).toEqual(mockParticipant);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/participants`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(participantCreate);
      req.flush(mockParticipant);
    });

    it('should update a program participant', () => {
      const participantUpdate: ProgramParticipantUpdate = { status: 'completed' };

      service.updateProgramParticipant(1, participantUpdate).subscribe(participant => {
        expect(participant).toEqual(mockParticipant);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/participants/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(participantUpdate);
      req.flush(mockParticipant);
    });

    it('should remove a program participant', () => {
      service.removeProgramParticipant(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/participants/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Program Pairing methods', () => {
    it('should fetch program pairings', () => {
      service.getProgramPairings(1).subscribe(pairings => {
        expect(pairings).toEqual([mockPairing]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/pairings`);
      expect(req.request.method).toBe('GET');
      req.flush([mockPairing]);
    });

    it('should fetch program pairings with status filter', () => {
      service.getProgramPairings(1, 'active').subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/programs/1/pairings` &&
        request.params.get('status') === 'active'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockPairing]);
    });

    it('should create a program pairing', () => {
      const pairingCreate: ProgramPairingCreate = {
        program_id: 1,
        primary_participant_id: 1,
        secondary_participant_id: 2,
        start_date: '2023-01-01',
        status: 'active'
      };

      service.createProgramPairing(1, pairingCreate).subscribe(pairing => {
        expect(pairing).toEqual(mockPairing);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/pairings`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(pairingCreate);
      req.flush(mockPairing);
    });

    it('should update a program pairing', () => {
      const pairingUpdate = { status: 'completed' as any };

      service.updateProgramPairing(1, pairingUpdate).subscribe(pairing => {
        expect(pairing).toEqual(mockPairing);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/pairings/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(pairingUpdate);
      req.flush(mockPairing);
    });

    it('should remove a program pairing', () => {
      service.removeProgramPairing(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/pairings/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Program Session methods', () => {
    it('should fetch program sessions', () => {
      service.getProgramSessions(1).subscribe(sessions => {
        expect(sessions).toEqual([mockSession]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/sessions`);
      expect(req.request.method).toBe('GET');
      req.flush([mockSession]);
    });

    it('should fetch program sessions with pairing filter', () => {
      service.getProgramSessions(1, 1).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/programs/1/sessions` &&
        request.params.get('pairing_id') === '1'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockSession]);
    });

    it('should create a program session', () => {
      const sessionCreate: ProgramSessionCreate = {
        program_id: 1,
        pairing_id: 1,
        session_date: '2023-01-15',
        duration_minutes: 60,
        location: 'Room 101'
      };

      service.createProgramSession(1, sessionCreate).subscribe(session => {
        expect(session).toEqual(mockSession);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/sessions`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(sessionCreate);
      req.flush(mockSession);
    });

    it('should update a program session', () => {
      const sessionUpdate = { location: 'Room 202' };

      service.updateProgramSession(1, sessionUpdate).subscribe(session => {
        expect(session).toEqual(mockSession);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/sessions/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(sessionUpdate);
      req.flush(mockSession);
    });

    it('should delete a program session', () => {
      service.deleteProgramSession(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/sessions/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Program Progress methods', () => {
    it('should fetch program progress', () => {
      service.getProgramProgress(1).subscribe(progress => {
        expect(progress).toEqual([mockProgress]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/progress`);
      expect(req.request.method).toBe('GET');
      req.flush([mockProgress]);
    });

    it('should fetch program progress with participant filter', () => {
      service.getProgramProgress(1, 1).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/programs/1/progress` &&
        request.params.get('participant_id') === '1'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockProgress]);
    });

    it('should create program progress', () => {
      const progressCreate: ProgramProgressCreate = {
        program_id: 1,
        participant_id: 1,
        progress_type: 'content_completion',
        content_id: 1,
        completion_percentage: 100
      };

      service.createProgramProgress(1, progressCreate).subscribe(progress => {
        expect(progress).toEqual(mockProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/1/progress`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(progressCreate);
      req.flush(mockProgress);
    });

    it('should update program progress', () => {
      const progressUpdate = { 
        progress_type: 'content_completion' as any,
        completion_percentage: 75
      };

      service.updateProgramProgress(1, progressUpdate).subscribe(progress => {
        expect(progress).toEqual(mockProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/progress/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(progressUpdate);
      req.flush(mockProgress);
    });

    it('should delete program progress', () => {
      service.deleteProgramProgress(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/progress/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Bulk import methods', () => {
    it('should bulk import participants from PC event', () => {
      const importData = {
        program_id: 1,
        pc_event_id: 'pc123',
        role_name: 'participant',
        status_filter: ['confirmed'],
        update_existing: true
      };

      service.bulkImportParticipantsFromPCEvent(importData).subscribe(participants => {
        expect(participants).toEqual([mockParticipant]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/participants/bulk-from-pc-event`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(importData);
      req.flush([mockParticipant]);
    });

    it('should bulk import participants from PC list', () => {
      const importData = {
        program_id: 1,
        pc_list_id: 'pc456',
        role_name: 'participant',
        update_existing: false
      };

      service.bulkImportParticipantsFromPCList(importData).subscribe(participants => {
        expect(participants).toEqual([mockParticipant]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/programs/participants/bulk-from-pc-list`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(importData);
      req.flush([mockParticipant]);
    });
  });
});
