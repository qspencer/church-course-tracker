"""
Test Script for Planning Center Custom Tab Import

This script demonstrates how to:
1. Discover custom tabs available for people
2. View field definitions in a custom tab
3. Configure field mappings for a program
4. Import participants from a PC list with custom tab data

Usage:
    python scripts/test_custom_tab_import.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.planning_center_sync_service import PlanningCenterSyncService
from app.services.program_service import ProgramService
from app.models.program import Program


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    print_section("Planning Center Custom Tab Import Test")

    # Setup database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/church_course_tracker.db")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Initialize services
        pc_service = PlanningCenterSyncService(db)
        program_service = ProgramService(db)

        # Step 1: Get a sample person from your list to discover tabs
        print_section("Step 1: Discover Available Custom Tabs")

        print("First, we need to get people from your 'Life on Life Discipleship Roll' list.")
        print("Enter the Planning Center List ID for 'Life on Life Discipleship Roll':")
        list_id = input("List ID: ").strip()

        if not list_id:
            print("❌ List ID is required. Exiting.")
            return

        print(f"\nFetching people from list {list_id}...")
        people = pc_service.get_list_people(list_id)

        if not people:
            print("❌ No people found in this list. Please check the list ID.")
            return

        print(f"✅ Found {len(people)} people in the list")

        # Get first person for tab discovery
        first_person = people[0]
        person_id = first_person.get("id")
        person_name = f"{first_person.get('attributes', {}).get('first_name', '')} {first_person.get('attributes', {}).get('last_name', '')}"

        print(f"\nUsing person: {person_name} (ID: {person_id}) to discover tabs...")

        # Discover tabs
        tabs = pc_service.get_person_tabs(person_id)

        if not tabs:
            print("❌ No custom tabs found for this person.")
            return

        print(f"\n✅ Found {len(tabs)} custom tabs:")
        for i, tab in enumerate(tabs, 1):
            tab_attrs = tab.get("attributes", {})
            print(f"  {i}. {tab_attrs.get('name')} (slug: {tab_attrs.get('slug')})")

        # Step 2: Select tab and view field definitions
        print_section("Step 2: View Field Definitions")

        # Find Life on Life Discipleship tab
        lol_tab = None
        for tab in tabs:
            tab_name = tab.get("attributes", {}).get("name", "")
            if "life on life" in tab_name.lower() or "discipleship" in tab_name.lower():
                lol_tab = tab
                break

        if not lol_tab:
            print("Looking for 'Life on Life Discipleship' tab...")
            print("Available tabs:")
            for i, tab in enumerate(tabs, 1):
                print(f"  {i}. {tab.get('attributes', {}).get('name')}")
            print("\nEnter the number of the tab to use:")
            tab_choice = int(input("Tab number: ").strip())
            lol_tab = tabs[tab_choice - 1]

        tab_id = lol_tab.get("id")
        tab_name = lol_tab.get("attributes", {}).get("name")
        tab_slug = lol_tab.get("attributes", {}).get("slug")

        print(f"\n✅ Using tab: {tab_name} (slug: {tab_slug})")

        # Get field definitions
        print(f"\nFetching field definitions for tab {tab_id}...")
        field_defs = pc_service.get_tab_field_definitions(tab_id)

        print(f"\n✅ Found {len(field_defs)} fields:")
        for field_def in field_defs:
            attrs = field_def.get("attributes", {})
            field_name = attrs.get("name")
            field_slug = attrs.get("slug")
            field_type = attrs.get("data_type")
            options = attrs.get("options", [])

            print(f"\n  • {field_name}")
            print(f"    Slug: {field_slug}")
            print(f"    Type: {field_type}")
            if options:
                print(f"    Options: {', '.join(options)}")

        # Step 3: Get sample tab data
        print_section("Step 3: Sample Tab Data")

        print(f"Fetching tab data for {person_name}...")
        tab_data = pc_service.get_person_tab_data(person_id, tab_slug)

        print(f"\n✅ Found {len(tab_data)} field values:")
        for field in tab_data:
            field_name = field.get("_field_name", "Unknown")
            field_slug = field.get("_field_slug", "Unknown")
            value = field.get("attributes", {}).get("value")
            print(f"  • {field_name} ({field_slug}): {value}")

        # Step 4: Generate configuration
        print_section("Step 4: Generate Configuration")

        print("Based on the field definitions, here's a suggested configuration:")

        # Generate field mappings based on field definitions
        suggested_mappings = []

        for field_def in field_defs:
            attrs = field_def.get("attributes", {})
            field_name = attrs.get("name")
            field_slug = attrs.get("slug")
            field_type = attrs.get("data_type")
            options = attrs.get("options", [])

            mapping = {
                "pc_field_name": field_name,
                "pc_field_slug": field_slug,
                "pc_field_type": field_type
            }

            # Suggest target type based on field name
            field_name_lower = field_name.lower()

            if "role" in field_name_lower:
                mapping["target_type"] = "participant_role"
                if options:
                    # Create mapping rules for each option
                    mapping["mapping_rules"] = [
                        {"when": option, "assign_role": option}
                        for option in options
                    ]
                else:
                    mapping["mapping_rules"] = None  # Direct mapping

            elif "status" in field_name_lower:
                mapping["target_type"] = "participant_status"
                if options:
                    mapping["mapping_rules"] = [
                        {"when": option, "assign_status": option.lower()}
                        for option in options
                    ]
                else:
                    mapping["mapping_rules"] = None

            elif "start" in field_name_lower and "date" in field_name_lower:
                mapping["target_type"] = "participant_start_date"
                mapping["mapping_rules"] = None

            elif "end" in field_name_lower and "date" in field_name_lower:
                mapping["target_type"] = "participant_end_date"
                mapping["mapping_rules"] = None

            elif "note" in field_name_lower or "comment" in field_name_lower:
                mapping["target_type"] = "participant_notes"
                mapping["mapping_rules"] = None

            elif "progress" in field_name_lower or "percent" in field_name_lower:
                mapping["target_type"] = "participant_progress"
                mapping["mapping_rules"] = None

            else:
                mapping["target_type"] = "ignore"
                mapping["mapping_rules"] = None

            suggested_mappings.append(mapping)

        suggested_config = {
            "enabled": True,
            "tab_slug": tab_slug,
            "tab_name": tab_name,
            "field_mappings": suggested_mappings,
            "default_status": "active",
            "update_existing": False,
            "sync_on_import": True
        }

        print("\n" + json.dumps(suggested_config, indent=2))

        # Step 5: Apply to a program
        print_section("Step 5: Apply Configuration to Program")

        print("Would you like to apply this configuration to a program? (y/n)")
        apply_config = input("Apply? ").strip().lower()

        if apply_config == 'y':
            # List existing programs
            programs = db.query(Program).filter(Program.is_active == True).all()

            if not programs:
                print("❌ No active programs found. Please create a program first.")
                return

            print("\nAvailable programs:")
            for i, prog in enumerate(programs, 1):
                print(f"  {i}. {prog.name} (ID: {prog.id})")

            print("\nEnter the number of the program to configure:")
            prog_choice = int(input("Program number: ").strip())
            selected_program = programs[prog_choice - 1]

            # Update program with configuration
            selected_program.planning_center_tab_config = suggested_config
            db.commit()

            print(f"\n✅ Configuration applied to program '{selected_program.name}'")

            # Step 6: Test import
            print_section("Step 6: Test Import")

            print(f"Would you like to test importing participants from list {list_id}? (y/n)")
            test_import = input("Test import? ").strip().lower()

            if test_import == 'y':
                print(f"\nImporting participants from list {list_id}...")
                print(f"This will use the configured field mappings.")
                print(f"Number of people to import: {len(people)}")

                print("\nConfirm import? (y/n)")
                confirm = input("Confirm? ").strip().lower()

                if confirm == 'y':
                    # Fetch people with tab data
                    print("\nFetching tab data for all people (this may take a moment)...")
                    people_with_tabs = pc_service.get_list_people_with_tab_data(list_id, tab_slug)

                    # Import participants
                    results = {
                        "imported": [],
                        "errors": []
                    }

                    for person in people_with_tabs:
                        person_id = person.get("id")
                        person_attrs = person.get("attributes", {})
                        person_name = f"{person_attrs.get('first_name', '')} {person_attrs.get('last_name', '')}"

                        try:
                            # Apply field mappings
                            mapped_data = pc_service.apply_tab_field_mappings(person, suggested_config)

                            # Sync person to local database
                            from app.services.people_service import PeopleService
                            people_service = PeopleService(db)
                            local_person = people_service.sync_person_from_pc(person)

                            # Create participant
                            participant_data = {
                                "program_id": selected_program.id,
                                "people_id": local_person.id,
                                **mapped_data
                            }

                            participant, error = program_service.add_participant(
                                participant_data,
                                created_by=1  # System user
                            )

                            if error:
                                results["errors"].append({
                                    "person": person_name,
                                    "error": error
                                })
                            else:
                                results["imported"].append({
                                    "person": person_name,
                                    "role": mapped_data.get("role_name"),
                                    "status": mapped_data.get("status")
                                })

                        except Exception as e:
                            results["errors"].append({
                                "person": person_name,
                                "error": str(e)
                            })

                    # Print results
                    print(f"\n✅ Import completed!")
                    print(f"   Successfully imported: {len(results['imported'])}")
                    print(f"   Errors: {len(results['errors'])}")

                    if results["imported"]:
                        print("\n  Imported participants:")
                        for item in results["imported"][:10]:  # Show first 10
                            print(f"    • {item['person']} - Role: {item['role']}, Status: {item['status']}")
                        if len(results["imported"]) > 10:
                            print(f"    ... and {len(results['imported']) - 10} more")

                    if results["errors"]:
                        print("\n  Errors:")
                        for item in results["errors"][:5]:  # Show first 5
                            print(f"    • {item['person']}: {item['error']}")
                        if len(results["errors"]) > 5:
                            print(f"    ... and {len(results['errors']) - 5} more")
                else:
                    print("\n❌ Import cancelled")
            else:
                print("\n✅ Configuration saved. You can test the import later via the API or frontend.")
        else:
            print("\n✅ Configuration generated. Copy the JSON above to configure your program.")

        print_section("Test Complete")
        print("The custom tab import system is ready to use!")
        print("\nNext steps:")
        print("  1. Use the frontend UI to configure tab mappings (coming soon)")
        print("  2. Use the API endpoint: POST /api/v1/programs/{id}/participants/bulk-from-pc-list-with-tabs")
        print("  3. Monitor import results in the application")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
