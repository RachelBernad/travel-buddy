from typing import Dict, Any, List
from ..base_handler import BaseHandler
from ...models.response_models import HandlerTypeEnum, ChatContext, ClassificationTags, TaskResult


class SummaryHandler(BaseHandler):
    """Handler for generating conversation summaries."""
    
    def __init__(self):
        super().__init__("summary", "Generates intelligent summaries of conversation history")

    @property
    def prompt_template(self) -> str:
            return """You are an intelligent conversation summarizer for a travel assistant.

Your task is to create a concise, informative summary of the conversation that captures:
- Key travel preferences and requirements
- Destinations mentioned or discussed
- Trip details (dates, budget, type of trip)
- Important context for future interactions

{context}

Generate a clear, structured summary that will help the assistant provide better responses in future interactions. Focus on actionable information and user preferences.

Summary:"""
    
    def build_prompt(self, user_input: str, context: ChatContext, classification_tags: Dict[str, Any] = None) -> str:
        """Build prompt for conversation summarization."""
        # Extract conversation history
        conversation_text = ""
        for msg in context.messages:
            role = msg.role
            content = msg.content
            conversation_text += f"{role.title()}: {content}\n"
        
        return self.prompt_template.format(context=conversation_text)
