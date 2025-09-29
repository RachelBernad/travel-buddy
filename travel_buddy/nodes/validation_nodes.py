"""Validation and self-correction nodes for travel buddy graphs."""

from typing import Dict, Any

VALIDATION_PROMPT_TEMPLATE = """
You are a response quality validator for a travel assistant. Evaluate if the response is helpful and complete.

User Question: {user_input}
Assistant Response: {answer}

Rate the response on these criteria:
1. Completeness: Does it fully address the user's question?
2. Helpfulness: Is it useful and actionable?
3. Accuracy: Does it avoid errors or uncertainty?
4. Relevance: Is it directly related to the travel question?

Respond with ONLY a JSON object:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["list of specific issues if any"],
    "reasoning": "brief explanation"
}}

Examples:
- Good response: {{"is_valid": true, "confidence": 0.9, "issues": [], "reasoning": "Complete and helpful travel advice"}}
- Poor response: {{"is_valid": false, "confidence": 0.3, "issues": ["Too vague", "No specific recommendations"], "reasoning": "Lacks actionable details"}}
"""

CORRECTION_PROMPT_TEMPLATE = """
You are a travel assistant response corrector. The previous response failed validation.

Original Question: {user_input}
Original Response: {original_answer}

Validation Issues: {validation_issues}
Validation Reasoning: {validation_reasoning}

Please provide a corrected response that addresses these issues:
1. Is more complete and helpful
2. Directly addresses the user's question
3. Provides specific, actionable information
4. Avoids uncertainty or vague language
5. Is relevant to travel planning

Provide only the corrected response, no explanations:
"""


def validate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based validation step to check response quality and completeness."""
    answer = state.get("answer", "")
    user_input = state.get("question", "")

    # Clean text to prevent encoding issues
    def clean_text(text: str) -> str:
        if not text:
            return text
        return text.encode('utf-8', errors='replace').decode('utf-8')

    answer = clean_text(answer)
    user_input = clean_text(user_input)

    # Basic checks first
    if not answer or len(answer.strip()) < 10:
        state["validation_passed"] = False
        state["validation_issues"] = ["Response is too short or empty"]
        state["answer"] = answer
        return state

    # LLM-based validation
    validation_prompt = VALIDATION_PROMPT_TEMPLATE.format(
        user_input=user_input,
        answer=answer
    )

    try:
        from travel_buddy.models.llm_loader import generate
        import json

        validation_result = generate(validation_prompt, temperature=0.1)
        validation_result = clean_text(validation_result)

        # Parse JSON response
        try:
            validation_data = json.loads(validation_result)
            is_valid = validation_data.get("is_valid", False)
            confidence = validation_data.get("confidence", 0.5)
            issues = validation_data.get("issues", [])
            reasoning = validation_data.get("reasoning", "")

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            is_valid = "true" in validation_result.lower() or "valid" in validation_result.lower()
            confidence = 0.5
            issues = ["Could not parse validation response"]
            reasoning = "JSON parsing failed"

        state["validation_passed"] = is_valid
        state["validation_issues"] = issues
        state["validation_confidence"] = confidence
        state["validation_reasoning"] = reasoning
        state["answer"] = answer

        if not is_valid:
            from travel_buddy.logger import logger
            logger.warning("Response validation failed", issues=issues, confidence=confidence)

    except Exception as e:
        from travel_buddy.logger import logger
        logger.error("Validation failed", error=str(e))
        # Fallback to basic validation
        state["validation_passed"] = True  # Default to pass if validation fails
        state["validation_issues"] = []
        state["validation_confidence"] = 0.5
        state["answer"] = answer

    return state


def self_correct_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Self-correction step when validation fails."""
    if state.get("validation_passed", True):
        return state

    user_input = state.get("question", "")
    original_answer = state.get("answer", "")
    validation_issues = state.get("validation_issues", [])
    validation_reasoning = state.get("validation_reasoning", "")

    # Clean text to prevent encoding issues
    def clean_text(text: str) -> str:
        if not text:
            return text
        return text.encode('utf-8', errors='replace').decode('utf-8')

    user_input = clean_text(user_input)
    original_answer = clean_text(original_answer)

    # Build correction prompt with validation details
    correction_prompt = CORRECTION_PROMPT_TEMPLATE.format(user_input=user_input, original_answer=original_answer,
                                                          validation_issues=', '.join(validation_issues),
                                                          validation_prompt=validation_prompt,
                                                          validation_reasoning=validation_reasoning)

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
        logger.info("Response self-corrected successfully",
                    original_issues=validation_issues,
                    correction_reasoning=validation_reasoning)

    except Exception as e:
        from travel_buddy.logger import logger
        logger.error("Self-correction failed", error=str(e))
        # Keep original answer if correction fails
        state["was_corrected"] = False

    return state


def should_correct_response(state: Dict[str, Any]) -> str:
    """
    Determine if response
    needs
    correction
    based
    on
    validation.
    """
    if not state.get("validation_passed", True):
        return "self_correct"
    else:
        return "generate_summary"
