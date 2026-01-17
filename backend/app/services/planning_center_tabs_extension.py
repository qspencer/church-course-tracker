"""
Planning Center Custom Tabs Extension
Methods for discovering and fetching custom tab data
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


def get_person_tabs(self, person_id: str) -> List[Dict[str, Any]]:
    """
    Get all custom tabs available for a person

    Args:
        person_id: Planning Center person ID

    Returns:
        List of tab dictionaries with id, name, slug

    Example:
        [
          {
            "id": "12345",
            "type": "Tab",
            "attributes": {
              "name": "Life On Life Discipleship",
              "slug": "life_on_life_discipleship",
              "tab_id": 67890
            }
          }
        ]
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.base_url}/people/v2/people/{person_id}/tabs",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

            return data.get("data", [])

    except httpx.HTTPStatusError as e:
        logger.error(f"Planning Center API error fetching tabs: {e.response.status_code} - {e.response.text}")
        raise ValueError(f"Failed to fetch tabs: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Planning Center API: {str(e)}")
        raise ValueError(f"Connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching tabs: {str(e)}", exc_info=True)
        raise


def get_tab_field_definitions(self, tab_id: str) -> List[Dict[str, Any]]:
    """
    Get field definitions for a custom tab

    Args:
        tab_id: Planning Center tab ID

    Returns:
        List of field definition dictionaries

    Example:
        [
          {
            "id": "11111",
            "type": "FieldDefinition",
            "attributes": {
              "name": "Role",
              "slug": "role",
              "data_type": "select",
              "options": ["Mentor", "Mentee"],
              "required": true
            }
          }
        ]
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.base_url}/people/v2/tabs/{tab_id}/field_definitions",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

            return data.get("data", [])

    except httpx.HTTPStatusError as e:
        logger.error(f"Planning Center API error fetching field definitions: {e.response.status_code} - {e.response.text}")
        raise ValueError(f"Failed to fetch field definitions: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Planning Center API: {str(e)}")
        raise ValueError(f"Connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching field definitions: {str(e)}", exc_info=True)
        raise


def get_person_tab_data(self, person_id: str, tab_slug: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get custom tab field data for a specific person

    Args:
        person_id: Planning Center person ID
        tab_slug: Optional tab slug to filter (e.g., 'life_on_life_discipleship')
                 If None, returns data from all tabs

    Returns:
        List of field data dictionaries with values

    Example:
        [
          {
            "id": "22222",
            "type": "FieldDatum",
            "attributes": {
              "value": "Mentor",
              "file": null,
              "file_size": null,
              "file_name": null,
              "file_content_type": null
            },
            "relationships": {
              "field_definition": {
                "data": {
                  "type": "FieldDefinition",
                  "id": "11111"
                }
              }
            },
            "_tab_name": "Life On Life Discipleship",
            "_tab_slug": "life_on_life_discipleship",
            "_field_name": "Role",
            "_field_slug": "role"
          }
        ]
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            # First, get the person's tabs
            tabs_response = client.get(
                f"{self.base_url}/people/v2/people/{person_id}/tabs",
                headers=self.headers
            )
            tabs_response.raise_for_status()
            tabs_data = tabs_response.json()

            tabs = tabs_data.get("data", [])

            # Filter by tab slug if provided
            if tab_slug:
                tabs = [tab for tab in tabs if tab.get("attributes", {}).get("slug") == tab_slug]

            if not tabs:
                logger.warning(f"No tabs found for person {person_id}" + (f" with slug {tab_slug}" if tab_slug else ""))
                return []

            # Get field data for each tab
            all_field_data = []
            for tab in tabs:
                tab_id = tab.get("id")
                tab_name = tab.get("attributes", {}).get("name")
                tab_slug_actual = tab.get("attributes", {}).get("slug")

                # Get field definitions for this tab to enrich data
                field_defs_response = client.get(
                    f"{self.base_url}/people/v2/tabs/{tab_id}/field_definitions",
                    headers=self.headers
                )
                field_defs_response.raise_for_status()
                field_defs_data = field_defs_response.json()
                field_definitions = {fd["id"]: fd for fd in field_defs_data.get("data", [])}

                # Get field data for this tab
                field_data_response = client.get(
                    f"{self.base_url}/people/v2/people/{person_id}/tabs/{tab_id}/field_data",
                    headers=self.headers
                )
                field_data_response.raise_for_status()
                field_data = field_data_response.json()

                # Enrich field data with tab info and field definition details
                for field in field_data.get("data", []):
                    # Add tab context
                    field["_tab_name"] = tab_name
                    field["_tab_slug"] = tab_slug_actual

                    # Add field definition details
                    field_def_id = field.get("relationships", {}).get("field_definition", {}).get("data", {}).get("id")
                    if field_def_id and field_def_id in field_definitions:
                        field_def = field_definitions[field_def_id]
                        field["_field_name"] = field_def.get("attributes", {}).get("name")
                        field["_field_slug"] = field_def.get("attributes", {}).get("slug")
                        field["_field_type"] = field_def.get("attributes", {}).get("data_type")

                    all_field_data.append(field)

            return all_field_data

    except httpx.HTTPStatusError as e:
        logger.error(f"Planning Center API error fetching tab data: {e.response.status_code} - {e.response.text}")
        raise ValueError(f"Failed to fetch tab data: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Planning Center API: {str(e)}")
        raise ValueError(f"Connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching tab data: {str(e)}", exc_info=True)
        raise


def get_list_people_with_tab_data(
    self,
    list_id: str,
    tab_slug: str
) -> List[Dict[str, Any]]:
    """
    Get all people from a Planning Center list WITH their custom tab data

    Args:
        list_id: Planning Center list ID
        tab_slug: Tab slug to fetch (e.g., 'life_on_life_discipleship')

    Returns:
        List of person dictionaries with 'custom_tab_data' array added

    Example:
        [
          {
            "id": "12345",
            "type": "Person",
            "attributes": {
              "first_name": "John",
              "last_name": "Doe",
              ...
            },
            "custom_tab_data": [
              {
                "id": "22222",
                "attributes": {"value": "Mentor"},
                "_field_name": "Role",
                "_field_slug": "role"
              }
            ]
          }
        ]
    """
    # Get the list of people
    people = self.get_list_people(list_id)

    logger.info(f"Fetching tab data for {len(people)} people from list {list_id}")

    # Fetch tab data for each person
    for i, person in enumerate(people):
        person_id = person.get("id")
        try:
            tab_data = self.get_person_tab_data(person_id, tab_slug)
            person["custom_tab_data"] = tab_data

            if (i + 1) % 10 == 0:
                logger.info(f"Fetched tab data for {i + 1}/{len(people)} people")

        except Exception as e:
            logger.warning(f"Failed to fetch tab data for person {person_id}: {e}")
            person["custom_tab_data"] = []

    logger.info(f"Completed fetching tab data for all {len(people)} people")
    return people


def apply_tab_field_mappings(
    self,
    person_data: Dict[str, Any],
    tab_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply field mappings from tab config to person data

    Args:
        person_data: Person dict with 'custom_tab_data' array
        tab_config: Program's planning_center_tab_config

    Returns:
        Dictionary with mapped participant fields:
        {
          "role_name": "Mentor",
          "status": "active",
          "start_date": "2026-01-15",
          "notes": "Experienced mentor",
          "progress_percentage": 0
        }
    """
    result = {}
    tab_data = person_data.get("custom_tab_data", [])

    # Create field lookup by slug
    fields_by_slug = {}
    for field in tab_data:
        field_slug = field.get("_field_slug")
        if field_slug:
            fields_by_slug[field_slug] = field.get("attributes", {}).get("value")

    # Apply each field mapping
    for mapping in tab_config.get("field_mappings", []):
        pc_slug = mapping.get("pc_field_slug")
        target_type = mapping.get("target_type")
        mapping_rules = mapping.get("mapping_rules")

        if not pc_slug or not target_type:
            continue

        if target_type == "ignore":
            continue  # Skip ignored fields

        if pc_slug not in fields_by_slug:
            logger.debug(f"Field {pc_slug} not found in tab data for person {person_data.get('id')}")
            continue  # Field not present

        pc_value = fields_by_slug[pc_slug]

        # Apply mapping based on target type
        if target_type == "participant_role":
            mapped_value = self._apply_mapping_rules(pc_value, mapping_rules, "assign_role")
            if mapped_value:
                result["role_name"] = mapped_value

        elif target_type == "participant_status":
            mapped_value = self._apply_mapping_rules(pc_value, mapping_rules, "assign_status")
            result["status"] = mapped_value or tab_config.get("default_status", "active")

        elif target_type == "participant_start_date":
            result["start_date"] = pc_value  # Direct mapping

        elif target_type == "participant_end_date":
            result["end_date"] = pc_value

        elif target_type == "participant_notes":
            result["notes"] = str(pc_value) if pc_value else None

        elif target_type == "participant_progress":
            try:
                result["progress_percentage"] = int(pc_value) if pc_value else 0
            except (ValueError, TypeError):
                logger.warning(f"Invalid progress value: {pc_value}, defaulting to 0")
                result["progress_percentage"] = 0

    # Set default status if not mapped
    if "status" not in result:
        result["status"] = tab_config.get("default_status", "active")

    return result


def _apply_mapping_rules(
    self,
    value: Any,
    rules: Optional[List[Dict[str, Any]]],
    assign_key: str
) -> Any:
    """
    Apply conditional mapping rules

    Args:
        value: The value from Planning Center
        rules: List of mapping rules or None for direct mapping
        assign_key: Key to extract from matching rule (e.g., 'assign_role', 'assign_status')

    Returns:
        Mapped value or None if no rule matches

    If rules is None, returns value directly (direct mapping)
    Otherwise, finds matching rule and returns assigned value
    """
    if rules is None:
        return value

    for rule in rules:
        rule_condition = rule.get("when")

        # Handle different types of conditions
        if isinstance(rule_condition, bool) and isinstance(value, bool):
            if rule_condition == value:
                return rule.get(assign_key)
        elif rule_condition == value:
            return rule.get(assign_key)
        # Case-insensitive string matching
        elif isinstance(rule_condition, str) and isinstance(value, str):
            if rule_condition.lower() == value.lower():
                return rule.get(assign_key)

    # No matching rule found
    logger.debug(f"No mapping rule matched for value '{value}' with key '{assign_key}'")
    return None
