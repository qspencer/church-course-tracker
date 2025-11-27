"""
Utility for intelligent attribute matching between Planning Center and local models
Uses fuzzy string matching to match attributes even when names don't exactly match
"""

from typing import Any, Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process


class AttributeMatcher:
    """Matches attributes using fuzzy string matching"""
    
    def __init__(self, similarity_threshold: float = 0.75):
        """
        Initialize the attribute matcher
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider a match.
                                  Default 0.75 (75% similarity)
        """
        self.similarity_threshold = similarity_threshold
    
    def normalize_attribute_name(self, name: str) -> str:
        """
        Normalize attribute name for better matching
        
        Args:
            name: Attribute name to normalize
            
        Returns:
            Normalized attribute name
        """
        if not name:
            return ""
        
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove common prefixes/suffixes
        normalized = normalized.replace("_", " ").replace("-", " ")
        
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        
        return normalized
    
    def find_best_match(
        self,
        source_attr: str,
        target_attrs: List[str],
        min_score: Optional[float] = None
    ) -> Optional[Tuple[str, float]]:
        """
        Find the best matching attribute from a list of target attributes
        
        Args:
            source_attr: Source attribute name to match
            target_attrs: List of target attribute names to match against
            min_score: Minimum similarity score (overrides instance threshold)
            
        Returns:
            Tuple of (matched_attribute_name, similarity_score) or None if no match
        """
        if not source_attr or not target_attrs:
            return None
        
        min_score = min_score or self.similarity_threshold
        
        # Normalize source attribute
        normalized_source = self.normalize_attribute_name(source_attr)
        
        # Use rapidfuzz process.extractOne for best match
        # This uses token_sort_ratio which handles word order differences
        result = process.extractOne(
            normalized_source,
            [self.normalize_attribute_name(attr) for attr in target_attrs],
            scorer=fuzz.token_sort_ratio
        )
        
        if result and result[1] >= (min_score * 100):  # rapidfuzz returns 0-100
            # Find the original attribute name (before normalization)
            matched_normalized = result[0]
            for attr in target_attrs:
                if self.normalize_attribute_name(attr) == matched_normalized:
                    return (attr, result[1] / 100.0)  # Convert to 0-1 scale
        
        return None
    
    def match_attributes(
        self,
        source_attrs: Dict[str, any],
        target_attr_names: List[str],
        min_score: Optional[float] = None
    ) -> Dict[str, Tuple[str, float]]:
        """
        Match multiple source attributes to target attributes
        
        Args:
            source_attrs: Dictionary of source attributes {attr_name: value}
            target_attr_names: List of target attribute names to match against
            min_score: Minimum similarity score (overrides instance threshold)
            
        Returns:
            Dictionary mapping source attribute names to (matched_target_name, score)
        """
        matches = {}
        
        for source_attr in source_attrs.keys():
            match = self.find_best_match(source_attr, target_attr_names, min_score)
            if match:
                matches[source_attr] = match
        
        return matches
    
    def match_with_confidence(
        self,
        source_attr: str,
        target_attrs: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Get all potential matches with confidence scores, sorted by score
        
        Args:
            source_attr: Source attribute name to match
            target_attrs: List of target attribute names to match against
            
        Returns:
            List of (matched_attribute_name, similarity_score) tuples, sorted by score
        """
        if not source_attr or not target_attrs:
            return []
        
        normalized_source = self.normalize_attribute_name(source_attr)
        
        # Get all matches with scores
        results = process.extract(
            normalized_source,
            [self.normalize_attribute_name(attr) for attr in target_attrs],
            scorer=fuzz.token_sort_ratio,
            limit=len(target_attrs)
        )
        
        # Map back to original attribute names and convert scores to 0-1
        matches = []
        for normalized_match, score, _ in results:
            for attr in target_attrs:
                if self.normalize_attribute_name(attr) == normalized_match:
                    matches.append((attr, score / 100.0))
                    break
        
        return matches


# Predefined attribute mappings for common Planning Center fields
PLANNING_CENTER_TO_LOCAL_MAPPINGS = {
    # People/Person attributes
    "first_name": ["first_name", "firstname", "fname", "given_name"],
    "last_name": ["last_name", "lastname", "lname", "surname", "family_name"],
    "email": ["email", "email_address", "e_mail"],
    "email_address": ["email", "email_address", "e_mail"],  # Also map from email_address
    "phone": ["phone", "phone_number", "mobile", "cell", "telephone"],
    "phone_number": ["phone", "phone_number", "mobile", "cell", "telephone"],  # Also map from phone_number
    "mobile": ["phone", "phone_number", "mobile", "cell", "telephone"],  # Also map from mobile
    "date_of_birth": ["date_of_birth", "dob", "birth_date", "birthdate"],
    "gender": ["gender", "sex"],
    "address1": ["address1", "address", "street_address", "address_line_1"],
    "address2": ["address2", "address_line_2", "apt", "apartment"],
    "city": ["city"],
    "state": ["state", "province"],
    "zip": ["zip", "zip_code", "postal_code", "postcode"],
    "zip_code": ["zip", "zip_code", "postal_code", "postcode"],  # Also map from zip_code
    "household_id": ["household_id", "household", "family_id"],
    "household_name": ["household_name", "household", "family_name"],
    "status": ["status", "member_status", "active_status"],
    "join_date": ["join_date", "joined_date", "membership_date"],
    
    # Course/Event attributes
    "title": ["title", "name", "event_name", "course_name"],
    "description": ["description", "desc", "details", "summary"],
    "start_date": ["start_date", "start", "event_start", "begin_date"],
    "end_date": ["end_date", "end", "event_end", "finish_date"],
    "max_capacity": ["max_capacity", "capacity", "max_registrations", "max_attendees"],
    
    # Registration/Enrollment attributes
    "registration_status": ["registration_status", "status", "reg_status", "enrollment_status"],
    "registration_date": ["registration_date", "registered_date", "enrollment_date"],
    "checked_in": ["checked_in", "checkedin", "attended", "present"],
    
    # Program-specific attributes (from your recent work)
    "role_name": ["role_name", "role", "participant_role", "position"],
    "start_date": ["start_date", "start", "begin_date", "enrollment_date"],
    "end_date": ["end_date", "end", "finish_date", "completion_date"],
    "status": ["status", "participant_status", "enrollment_status"],
    "notes": ["notes", "note", "comments", "remarks"],
    "discipler_name": ["discipler_name", "discipler", "mentor", "coach", "leader"],
}


def get_predefined_mapping(pc_attr: str) -> Optional[List[str]]:
    """
    Get predefined local attribute names for a Planning Center attribute
    
    Args:
        pc_attr: Planning Center attribute name
        
    Returns:
        List of potential local attribute names, or None if not found
    """
    return PLANNING_CENTER_TO_LOCAL_MAPPINGS.get(pc_attr.lower())


def match_pc_list_attributes_to_program_fields(
    pc_list_attributes: Dict[str, Any],
    program: Any,  # Program model
    similarity_threshold: float = 0.75
) -> Dict[str, Tuple[str, float, bool]]:
    """
    Match Planning Center list attributes to program participant fields
    
    This handles both standard program participant fields and program-specific
    custom attributes that may be stored in the program's custom_attributes_config.
    
    Args:
        pc_list_attributes: Dictionary of PC list attributes {attr_name: value}
        program: Program model instance (to access custom_attributes_config)
        similarity_threshold: Minimum similarity score (0-1) to consider a match
        
    Returns:
        Dictionary mapping PC attribute names to (local_field_name, score, is_predefined)
    """
    from app.models.program import ProgramParticipant
    
    # Get standard ProgramParticipant model fields
    standard_fields = [
        col.name for col in ProgramParticipant.__table__.columns
        if col.name not in ['id', 'created_at', 'updated_at', 'program_id', 'people_id']
    ]
    
    # Get custom attribute field names from program config (if exists)
    custom_fields = []
    if hasattr(program, 'custom_attributes_config') and program.custom_attributes_config:
        custom_fields = [
            attr.get('name') for attr in program.custom_attributes_config
            if attr.get('name')
        ]
    
    # Combine standard and custom fields
    all_local_fields = standard_fields + custom_fields
    
    # Match attributes
    return match_pc_to_local_attributes(
        pc_list_attributes,
        all_local_fields,
        similarity_threshold=similarity_threshold,
        use_predefined=True
    )


def match_pc_to_local_attributes(
    pc_attributes: Dict[str, Any],
    local_attr_names: List[str],
    similarity_threshold: float = 0.75,
    use_predefined: bool = True
) -> Dict[str, Tuple[str, float, bool]]:
    """
    Match Planning Center attributes to local attributes with intelligent matching
    
    Args:
        pc_attributes: Dictionary of Planning Center attributes {attr_name: value}
        local_attr_names: List of local attribute names to match against
        similarity_threshold: Minimum similarity score (0-1) to consider a match
        use_predefined: Whether to use predefined mappings first (faster, more accurate)
        
    Returns:
        Dictionary mapping PC attribute names to (local_attr_name, score, is_predefined)
        where is_predefined indicates if it used a predefined mapping
    """
    matcher = AttributeMatcher(similarity_threshold)
    matches = {}
    
    for pc_attr, value in pc_attributes.items():
        # Try predefined mapping first if enabled
        if use_predefined:
            predefined = get_predefined_mapping(pc_attr)
            if predefined:
                # Check if any predefined name exists in local attributes
                for local_attr in predefined:
                    if local_attr in local_attr_names:
                        matches[pc_attr] = (local_attr, 1.0, True)
                        break
        
        # If no predefined match, use fuzzy matching
        if pc_attr not in matches:
            match = matcher.find_best_match(pc_attr, local_attr_names, similarity_threshold)
            if match:
                matches[pc_attr] = (match[0], match[1], False)
    
    return matches

