import { Injectable } from '@angular/core';
import { Person } from '../models';

/**
 * Shared service for consistent search/filter functionality across components
 */
@Injectable({
  providedIn: 'root'
})
export class SearchFilterService {

  /**
   * Checks if a person's name matches the search text
   * Searches if first name or last name STARTS with the search text (case-insensitive)
   * Optionally also searches email with includes() for partial matching
   * 
   * @param member - The Person object to search
   * @param searchText - The search text to match against
   * @param includeEmail - Whether to also search email (default: true)
   * @returns true if the person matches the search criteria
   */
  matchesNameSearch(member: Person, searchText: string, includeEmail: boolean = true): boolean {
    if (!searchText || !member) {
      return false;
    }

    const searchLower = searchText.trim().toLowerCase();
    if (!searchLower) {
      return true; // Empty search matches all
    }

    const firstName = (member.first_name || '').toLowerCase();
    const lastName = (member.last_name || '').toLowerCase();
    const email = includeEmail ? ((member.email || '').toLowerCase()) : '';

    // Check if first name or last name starts with search text
    const nameMatches = firstName.startsWith(searchLower) || lastName.startsWith(searchLower);
    
    // Optionally check email with includes for partial matching
    const emailMatches = includeEmail && email.includes(searchLower);

    return nameMatches || emailMatches;
  }

  /**
   * Filters an array of items that have a people_id, using member lookup
   * 
   * @param items - Array of items with a people_id property
   * @param members - Array of Person objects for lookup
   * @param searchText - The search text to filter by
   * @param includeEmail - Whether to also search email (default: true)
   * @returns Filtered array of items
   */
  filterByPersonName<T extends { people_id: number }>(
    items: T[],
    members: Person[],
    searchText: string,
    includeEmail: boolean = true
  ): T[] {
    if (!searchText || !searchText.trim()) {
      return items;
    }

    return items.filter(item => {
      const member = members.find(m => m.id === item.people_id);
      if (!member) {
        return false;
      }
      return this.matchesNameSearch(member, searchText, includeEmail);
    });
  }

  /**
   * Filters an array of items that have a primary_participant_id and secondary_participant_id
   * 
   * @param items - Array of items with primary_participant_id and secondary_participant_id
   * @param members - Array of Person objects for lookup
   * @param participants - Array of participant objects with id and people_id
   * @param searchText - The search text to filter by
   * @param includeEmail - Whether to also search email (default: true)
   * @returns Filtered array of items
   */
  filterByParticipantNames<T extends { primary_participant_id: number; secondary_participant_id: number }>(
    items: T[],
    members: Person[],
    participants: Array<{ id: number; people_id: number }>,
    searchText: string,
    includeEmail: boolean = true
  ): T[] {
    if (!searchText || !searchText.trim()) {
      return items;
    }

    return items.filter(item => {
      // Find primary participant by participant ID
      const primaryParticipant = participants.find(p => p.id === item.primary_participant_id);
      const primaryMember = primaryParticipant 
        ? members.find(m => m.id === primaryParticipant.people_id)
        : null;

      // Find secondary participant by participant ID
      const secondaryParticipant = participants.find(p => p.id === item.secondary_participant_id);
      const secondaryMember = secondaryParticipant
        ? members.find(m => m.id === secondaryParticipant.people_id)
        : null;

      // Check if either participant matches
      const primaryMatches = primaryMember ? this.matchesNameSearch(primaryMember, searchText, includeEmail) : false;
      const secondaryMatches = secondaryMember ? this.matchesNameSearch(secondaryMember, searchText, includeEmail) : false;

      return primaryMatches || secondaryMatches;
    });
  }
}
