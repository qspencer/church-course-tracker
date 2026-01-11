# Role Definitions Explanation

## Understanding Min/Max Participants in Role Definitions

Based on the code structure, here's how Role Definitions work:

### Current Implementation

The **Min Participants** and **Max Participants** fields in Role Definitions are **intended to define the number of participants of that role per pairing/group**, NOT the total number in the entire program.

### Example: Default Mentor/Mentee Setup

**Mentor Role:**
- Min Participants: 1
- Max Participants: 1
- Is Primary: Yes
- **Meaning**: Each pairing/group must have exactly **1 mentor**

**Mentee Role:**
- Min Participants: 1
- Max Participants: 3
- Is Primary: No
- **Meaning**: Each pairing/group can have **1 to 3 mentees**

### How Pairings/Groups Work

1. **With 1 Mentor + 1 Mentee** = A **pair** (1:1 relationship)
2. **With 1 Mentor + 2-3 Mentees** = A **group** (1:many relationship)

So yes, if you have max_mentees = 3, and a mentor is paired with 3 mentees, that would be a **group**, not a pair.

### Important Notes

**Current Gap in Implementation:**
- The `min_participants` and `max_participants` in role definitions are **not currently enforced** in the pairing validation logic
- The actual pairing constraints are controlled by the **Relationship Configuration** section:
  - `allow_multiple_secondary`: Controls if a primary can have multiple secondaries
  - `max_secondary_per_primary`: Maximum number of secondary participants per primary (this is what actually limits mentees per mentor)

**What This Means:**
- The role definition min/max are more like **documentation/guidelines** right now
- The actual enforcement happens through `relationship_config.max_secondary_per_primary`
- For the default setup (Mentee max: 3), you'd want to set `max_secondary_per_primary: 3` in relationship config

### Answers to Your Questions

1. **"Does Mentor Min:1, Max:1 mean only 1 mentor in the Program?"**
   - **No** - It means **1 mentor per pairing/group**. You can have many mentors in the program, but each pairing/group should have exactly 1 mentor.

2. **"Does Mentee Min:1, Max:3 mean only 3 mentees total in the program?"**
   - **No** - It means **1-3 mentees per pairing/group**. You can have many mentees in the program, but each mentor can be paired with 1-3 mentees.

3. **"If there are more than 2 roles, would we then have groups instead of pairs?"**
   - **Yes** - If you have more than 2 participants in a pairing (e.g., 1 Mentor + 2 Mentees), that's a **group**, not a pair. The system uses the term "pairing" generically, but it can represent both pairs (1:1) and groups (1:many).

4. **"If a mentor has 3 mentees, would that be a group and not a pair?"**
   - **Yes, exactly!** 1 Mentor + 3 Mentees = a **group** (1:3 relationship), not a pair.

### Recommended Enhancement

The role definition min/max should ideally be enforced during pairing creation to ensure:
- Each pairing has at least `min_participants` of each role
- Each pairing has at most `max_participants` of each role
- This would make the role definitions more meaningful and enforce the intended structure

Currently, you need to manually ensure the relationship_config matches your role definition intentions.

