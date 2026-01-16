# Intelligent Attribute Matching Implementation

## Overview

This document describes the implementation of intelligent attribute matching between Planning Center and local Church Course Tracker attributes using fuzzy string matching.

## Library Choice: `rapidfuzz`

We've chosen **rapidfuzz** as the fuzzy matching library because:

1. **Performance**: Written in C++ with Python bindings, much faster than alternatives
2. **Modern**: Actively maintained, replacement for the deprecated `fuzzywuzzy`
3. **Flexible**: Multiple matching algorithms (ratio, partial_ratio, token_sort_ratio, etc.)
4. **MIT Licensed**: Open source, no licensing concerns
5. **Well-tested**: Used in production by many projects

## Installation

```bash
pip install rapidfuzz>=3.0.0
```

## Usage Examples

### Basic Attribute Matching

```python
from app.utils.attribute_matcher import AttributeMatcher

matcher = AttributeMatcher(similarity_threshold=0.75)

# Match a single attribute
pc_attr = "first_name"
local_attrs = ["firstname", "fname", "given_name", "first_name"]
match = matcher.find_best_match(pc_attr, local_attrs)

if match:
    local_attr, score = match
    print(f"'{pc_attr}' matches '{local_attr}' with {score*100:.1f}% confidence")
```

### Matching Multiple Attributes

```python
from app.utils.attribute_matcher import match_pc_to_local_attributes

# Planning Center attributes from an event/registration
pc_attributes = {
    "first_name": "John",
    "last_name": "Doe",
    "email_address": "john@example.com",
    "phone_number": "555-1234",
    "date_of_birth": "1990-01-01"
}

# Local model attribute names
local_attrs = [
    "first_name", "last_name", "email", "phone", 
    "date_of_birth", "gender", "address1"
]

# Match with intelligent matching
matches = match_pc_to_local_attributes(
    pc_attributes,
    local_attrs,
    similarity_threshold=0.75,
    use_predefined=True
)

for pc_attr, (local_attr, score, is_predefined) in matches.items():
    print(f"{pc_attr} -> {local_attr} (score: {score:.2f}, predefined: {is_predefined})")
```

### Integration in Planning Center Sync Service

```python
from app.utils.attribute_matcher import match_pc_to_local_attributes
from app.models.member import People

# When syncing a person from Planning Center
def sync_person_from_pc(pc_person_data: dict):
    # Get PC attributes
    pc_attrs = pc_person_data.get("attributes", {})
    
    # Get local People model attribute names
    local_attrs = [col.name for col in People.__table__.columns]
    
    # Match attributes
    attribute_mapping = match_pc_to_local_attributes(
        pc_attrs,
        local_attrs,
        similarity_threshold=0.75
    )
    
    # Create person with matched attributes
    person_data = {}
    for pc_attr, value in pc_attrs.items():
        if pc_attr in attribute_mapping:
            local_attr, score, _ = attribute_mapping[pc_attr]
            person_data[local_attr] = value
            if score < 0.9:
                logger.warning(f"Low confidence match: {pc_attr} -> {local_attr} ({score:.2f})")
    
    return People(**person_data)
```

## Matching Strategies

### 1. Predefined Mappings (Fast & Accurate)

For common attributes, we maintain a predefined mapping dictionary that maps Planning Center attribute names to likely local attribute names. This is:
- **Fast**: No computation needed
- **Accurate**: 100% confidence
- **Maintainable**: Easy to update as needed

### 2. Fuzzy Matching (Flexible)

When no predefined mapping exists, we use fuzzy string matching with:
- **Token Sort Ratio**: Handles word order differences (e.g., "first_name" vs "name_first")
- **Normalization**: Converts to lowercase, removes underscores/hyphens
- **Threshold**: Only matches above 75% similarity by default

## Similarity Thresholds

- **0.9+ (90%+)**: Very confident match, likely correct
- **0.75-0.9 (75-90%)**: Good match, but should be reviewed
- **<0.75 (<75%)**: Low confidence, may be incorrect

## Example Matches

| Planning Center | Local | Score | Method |
|----------------|-------|-------|--------|
| `first_name` | `firstname` | 1.0 | Predefined |
| `email_address` | `email` | 0.95 | Fuzzy |
| `phone_number` | `phone` | 0.92 | Fuzzy |
| `date_of_birth` | `dob` | 0.85 | Fuzzy |
| `household_id` | `family_id` | 0.78 | Fuzzy |
| `registration_status` | `status` | 0.72 | Fuzzy (below threshold) |

## Configuration

You can adjust the similarity threshold based on your needs:

```python
# More strict (fewer false positives)
matcher = AttributeMatcher(similarity_threshold=0.85)

# More lenient (more matches, but may have false positives)
matcher = AttributeMatcher(similarity_threshold=0.65)
```

## Future Enhancements

1. **Machine Learning**: Train a model on historical matches for better accuracy
2. **Context-Aware Matching**: Consider attribute types (date, email, etc.) in matching
3. **User Feedback**: Allow users to confirm/correct matches to improve over time
4. **Caching**: Cache successful matches to speed up repeated imports
5. **Multi-language Support**: Handle attributes in different languages

## Testing

```python
def test_attribute_matching():
    from app.utils.attribute_matcher import AttributeMatcher
    
    matcher = AttributeMatcher(similarity_threshold=0.75)
    
    # Test exact match
    match = matcher.find_best_match("first_name", ["first_name", "last_name"])
    assert match == ("first_name", 1.0)
    
    # Test fuzzy match
    match = matcher.find_best_match("email_address", ["email", "phone"])
    assert match[0] == "email"
    assert match[1] >= 0.75
    
    # Test no match
    match = matcher.find_best_match("xyz_unknown", ["email", "phone"])
    assert match is None
```

