"""Validation and self-correction nodes for travel buddy graphs."""

from typing import Dict, Any


def validate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Simple validation step to check response quality and completeness."""
    answer = state.get("answer", "")
    user_input = state.get("question", "")
    
    # Clean text to prevent encoding issues
    def clean_text(text: str) -> str:
        if not text:
            return text
        return text.encode('utf-8', errors='replace').decode('utf-8')
    
    answer = clean_text(answer)
    user_input = clean_text(user_input)
    
    # Simple validation criteria
    validation_issues = []
    
    # Check if response is empty or too short
    if not answer or len(answer.strip()) < 10:
        validation_issues.append("Response is too short or empty")
    
    # Check if response contains common error patterns
    error_patterns = ["I don't know", "I can't help", "I'm not sure", "I apologize but", "encountered an error"]
    if any(pattern in answer.lower() for pattern in error_patterns):
        validation_issues.append("Response contains error or uncertainty patterns")
    
    # Check if response is relevant to the question
    if user_input and len(user_input) > 5:
        # Simple relevance check - if question mentions location, response should too
        if any(word in user_input.lower() for word in ["where", "location", "place", "city", "country", "trip", "visit"]):
            if not any(word in answer.lower() for word in ["location", "place", "city", "country", "where", "visit", "trip", "day"]):
                validation_issues.append("Response may not be location-relevant")
    
    # Set validation status
    is_valid = len(validation_issues) == 0
    state["validation_passed"] = is_valid
    state["validation_issues"] = validation_issues
    state["answer"] = answer  # Update with cleaned answer
    
    if not is_valid:
        from travel_buddy.logger import logger
        logger.warning("Response validation failed", issues=validation_issues)
    
    return state


def self_correct_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Self-correction step when validation fails."""
    if state.get("validation_passed", True):
        return state
    
    user_input = state.get("question", "")
    original_answer = state.get("answer", "")
    validation_issues = state.get("validation_issues", [])
    
    # Clean text to prevent encoding issues
    def clean_text(text: str) -> str:
        if not text:
            return text
        return text.encode('utf-8', errors='replace').decode('utf-8')
    
    user_input = clean_text(user_input)
    original_answer = clean_text(original_answer)
    
    # Build correction prompt
    correction_prompt = f"""
    The previous response had validation issues: {', '.join(validation_issues)}
    
    Original question: {user_input}
    Original response: {original_answer}
    
    Please provide a corrected response that:
    1. Is more complete and helpful
    2. Directly addresses the user's question
    3. Provides specific, actionable information
    4. Avoids uncertainty or vague language
    
    Corrected response:
    """
    
    try:
        from travel_buddy.models.llm_loader import generate
        corrected_answer = generate(correction_prompt, temperature=0.3)
        
        # Clean the corrected answer
        corrected_answer = clean_text(corrected_answer)
        
        # Update the answer with the corrected version
        state["answer"] = corrected_answer
        state["validation_passed"] = True
        state["was_corrected"] = True
        
        from travel_buddy.logger import logger
        logger.info("Response self-corrected successfully")
        
    except Exception as e:
        from travel_buddy.logger import logger
        logger.error("Self-correction failed", error=str(e))
        # Keep original answer if correction fails
        state["was_corrected"] = False
    
    return state


def should_correct_response(state: Dict[str, Any]) -> str:
    """Determine if response needs correction based on validation."""
    if not state.get("validation_passed", True):
        return "self_correct"
    else:
        return "generate_summary"
