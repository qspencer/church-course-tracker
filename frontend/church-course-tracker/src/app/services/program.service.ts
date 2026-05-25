import { Injectable, isDevMode, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { LoggerService } from './logger.service';
import {
  Program,
  ProgramCreate,
  ProgramUpdate,
  ProgramQueryParams,
  ProgramAdmin,
  ProgramAdminCreate,
  ProgramAdminUpdate,
  ProgramParticipant,
  ProgramParticipantCreate,
  ProgramParticipantUpdate,
  ProgramPairing,
  ProgramPairingCreate,
  ProgramPairingUpdate,
  ProgramSession,
  ProgramSessionCreate,
  ProgramSessionUpdate,
  ProgramProgress,
  ProgramProgressCreate,
  ProgramProgressUpdate
} from '../models/program.model';

@Injectable({
  providedIn: 'root'
})
export class ProgramService {
  private http = inject(HttpClient);
  private logger = inject(LoggerService);

  private readonly API_URL = `${environment.apiUrl}/programs`;

  constructor() {
    if (isDevMode()) {
      this.logger.debug('ProgramService API_URL', { apiUrl: this.API_URL });
    }
  }

  // Program CRUD
  getPrograms(params?: ProgramQueryParams): Observable<Program[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return this.http.get<Program[]>(this.API_URL, { params: httpParams });
  }

  getProgram(id: number): Observable<Program> {
    return this.http.get<Program>(`${this.API_URL}/${id}`);
  }

  createProgram(program: ProgramCreate): Observable<Program> {
    return this.http.post<Program>(this.API_URL, program);
  }

  updateProgram(id: number, program: ProgramUpdate): Observable<Program> {
    return this.http.put<Program>(`${this.API_URL}/${id}`, program);
  }

  deleteProgram(id: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${id}`);
  }

  // Program Admin methods
  getProgramAdmins(programId: number): Observable<ProgramAdmin[]> {
    return this.http.get<ProgramAdmin[]>(`${this.API_URL}/${programId}/admins`);
  }

  addProgramAdmin(programId: number, admin: ProgramAdminCreate): Observable<ProgramAdmin> {
    return this.http.post<ProgramAdmin>(`${this.API_URL}/${programId}/admins`, admin);
  }

  updateProgramAdmin(adminId: number, admin: ProgramAdminUpdate): Observable<ProgramAdmin> {
    return this.http.put<ProgramAdmin>(`${this.API_URL}/admins/${adminId}`, admin);
  }

  removeProgramAdmin(adminId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/admins/${adminId}`);
  }

  // Program Participant methods
  getAllProgramParticipants(status?: string): Observable<ProgramParticipant[]> {
    let httpParams = new HttpParams();
    if (status) {
      httpParams = httpParams.set('status', status);
    }
    return this.http.get<ProgramParticipant[]>(`${this.API_URL}/participants`, { params: httpParams });
  }

  getProgramParticipants(programId: number, status?: string, skip?: number, limit?: number, search?: string): Observable<ProgramParticipant[]> {
    let httpParams = new HttpParams();
    if (status) {
      httpParams = httpParams.set('status', status);
    }
    if (skip !== undefined && skip !== null) {
      httpParams = httpParams.set('skip', skip.toString());
    }
    if (limit !== undefined && limit !== null) {
      httpParams = httpParams.set('limit', limit.toString());
    }
    if (search) {
      httpParams = httpParams.set('search', search);
    }
    return this.http.get<ProgramParticipant[]>(`${this.API_URL}/${programId}/participants`, { params: httpParams });
  }

  getProgramParticipantsCount(programId: number, status?: string, search?: string): Observable<{ count: number }> {
    let httpParams = new HttpParams();
    if (status) {
      httpParams = httpParams.set('status', status);
    }
    if (search) {
      httpParams = httpParams.set('search', search);
    }
    return this.http.get<{ count: number }>(`${this.API_URL}/${programId}/participants/count`, { params: httpParams });
  }

  addProgramParticipant(programId: number, participant: ProgramParticipantCreate): Observable<ProgramParticipant> {
    return this.http.post<ProgramParticipant>(`${this.API_URL}/${programId}/participants`, participant);
  }

  updateProgramParticipant(participantId: number, participant: ProgramParticipantUpdate): Observable<ProgramParticipant> {
    return this.http.put<ProgramParticipant>(`${this.API_URL}/participants/${participantId}`, participant);
  }

  removeProgramParticipant(participantId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/participants/${participantId}`);
  }

  // Program Pairing methods
  getProgramPairings(programId: number, status?: string): Observable<ProgramPairing[]> {
    let httpParams = new HttpParams();
    if (status) {
      httpParams = httpParams.set('status', status);
    }
    return this.http.get<ProgramPairing[]>(`${this.API_URL}/${programId}/pairings`, { params: httpParams });
  }

  createProgramPairing(programId: number, pairing: ProgramPairingCreate): Observable<ProgramPairing> {
    return this.http.post<ProgramPairing>(`${this.API_URL}/${programId}/pairings`, pairing);
  }

  updateProgramPairing(pairingId: number, pairing: ProgramPairingUpdate): Observable<ProgramPairing> {
    return this.http.put<ProgramPairing>(`${this.API_URL}/pairings/${pairingId}`, pairing);
  }

  removeProgramPairing(pairingId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/pairings/${pairingId}`);
  }

  // Program Session methods
  getProgramSessions(programId: number, pairingId?: number): Observable<ProgramSession[]> {
    let httpParams = new HttpParams();
    if (pairingId) {
      httpParams = httpParams.set('pairing_id', pairingId.toString());
    }
    return this.http.get<ProgramSession[]>(`${this.API_URL}/${programId}/sessions`, { params: httpParams });
  }

  createProgramSession(programId: number, session: ProgramSessionCreate): Observable<ProgramSession> {
    return this.http.post<ProgramSession>(`${this.API_URL}/${programId}/sessions`, session);
  }

  updateProgramSession(sessionId: number, session: ProgramSessionUpdate): Observable<ProgramSession> {
    return this.http.put<ProgramSession>(`${this.API_URL}/sessions/${sessionId}`, session);
  }

  deleteProgramSession(sessionId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/sessions/${sessionId}`);
  }

  // Program Progress methods
  getProgramProgress(programId: number, participantId?: number): Observable<ProgramProgress[]> {
    let httpParams = new HttpParams();
    if (participantId) {
      httpParams = httpParams.set('participant_id', participantId.toString());
    }
    return this.http.get<ProgramProgress[]>(`${this.API_URL}/${programId}/progress`, { params: httpParams });
  }

  createProgramProgress(programId: number, progress: ProgramProgressCreate): Observable<ProgramProgress> {
    return this.http.post<ProgramProgress>(`${this.API_URL}/${programId}/progress`, progress);
  }

  updateProgramProgress(progressId: number, progress: ProgramProgressUpdate): Observable<ProgramProgress> {
    return this.http.put<ProgramProgress>(`${this.API_URL}/progress/${progressId}`, progress);
  }

  deleteProgramProgress(progressId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/progress/${progressId}`);
  }

  // Bulk import participants from Planning Center
  bulkImportParticipantsFromPCEvent(data: { 
    program_id: number, 
    pc_event_id: string, 
    role_name: string,
    status_filter?: string[], 
    update_existing?: boolean 
  }): Observable<ProgramParticipant[]> {
    return this.http.post<ProgramParticipant[]>(`${this.API_URL}/participants/bulk-from-pc-event`, data);
  }

  bulkImportParticipantsFromPCList(data: {
    program_id: number,
    pc_list_id: string,
    role_name: string,
    update_existing?: boolean
  }): Observable<ProgramParticipant[]> {
    return this.http.post<ProgramParticipant[]>(`${this.API_URL}/participants/bulk-from-pc-list`, data);
  }

  // Planning Center Custom Tab methods
  getPlanningCenterTabs(personId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_URL}/planning-center/tabs/${personId}`);
  }

  getTabFieldDefinitions(tabId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_URL}/planning-center/tabs/${tabId}/fields`);
  }

  bulkImportParticipantsFromPCListWithTabs(
    programId: number,
    data: { list_id: string; role_name?: string }
  ): Observable<any> {
    return this.http.post<any>(
      `${this.API_URL}/${programId}/participants/bulk-from-pc-list-with-tabs`,
      data
    );
  }
}

