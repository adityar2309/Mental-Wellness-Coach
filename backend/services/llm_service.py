"""
Mental Wellness Coach - ASI:One LLM Service

This module provides the core AI conversation capabilities using ASI:One LLM
for natural language processing and mental health support conversations.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass

try:
    from llama_index.llms.openai_like import OpenAILike
    from llama_index.core.base.llms.types import ChatMessage
    HAS_OPENAI_LIKE = True
except ImportError:
    # Fallback for when OpenAI-like LLM is not available
    OpenAILike = None
    ChatMessage = None
    HAS_OPENAI_LIKE = False

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Container for conversation context and memory."""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, str]]
    user_profile: Optional[Dict[str, Any]] = None
    mood_context: Optional[Dict[str, Any]] = None
    crisis_indicators: List[str] = None
    
    def __post_init__(self):
        if self.crisis_indicators is None:
            self.crisis_indicators = []


class LLMResponse(BaseModel):
    """Structured response from the LLM service."""
    text: str = Field(..., description="The main response text")
    confidence: float = Field(default=0.8, description="Confidence score (0-1)")
    sentiment: Optional[str] = Field(default=None, description="Detected sentiment")
    crisis_level: str = Field(default="none", description="Crisis risk level")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested follow-up actions")
    conversation_tags: List[str] = Field(default_factory=list, description="Conversation topic tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ASILLMService:
    """
    ASI:One LLM Service for Mental Wellness Coach.
    
    Handles AI conversations, context management, and mental health-focused responses.
    Uses ASI:One API which is OpenAI-compatible.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "asi1-mini"):
        """
        Initialize the ASI LLM Service.
        
        Args:
            api_key: ASI API key (will use environment variable if not provided)
            model: ASI model to use (default: asi1-mini)
        """
        self.api_key = api_key or os.getenv("ASI_API_KEY")
        self.model = model
        self.llm = None
        self.api_base = "https://api.asi1.ai/v1"
        
        # Mental health conversation templates
        self.conversation_templates = {
            "greeting": "Hello! I'm here to support your mental wellness journey. How are you feeling today?",
            "mood_check": "I notice you'd like to talk about your mood. Can you tell me more about how you're feeling right now?",
            "crisis_support": "I'm here to listen and support you. Your feelings are valid and important. Would you like to talk about what's happening?",
            "coping_strategies": "It sounds like you're looking for ways to cope. Let me suggest some techniques that might help.",
            "encouragement": "Thank you for sharing that with me. You're taking important steps by reaching out and being open about your feelings."
        }
        
        # Crisis detection keywords
        self.crisis_keywords = [
            "suicide", "kill myself", "end it all", "don't want to live", 
            "hurt myself", "self-harm", "cutting", "overdose",
            "hopeless", "no point", "everyone would be better off", "can't go on"
        ]
        
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize the ASI LLM client using OpenAI-compatible interface."""
        try:
            if not HAS_OPENAI_LIKE:
                logger.warning("OpenAI-like LLM library not available. Using mock responses.")
                return
                
            if not self.api_key:
                logger.warning("ASI API key not found. Set ASI_API_KEY environment variable.")
                return
                
            # Initialize ASI:One using OpenAI-compatible interface
            self.llm = OpenAILike(
                model=self.model,
                api_base=self.api_base,
                api_key=self.api_key,
                context_window=32000,  # ASI:One context window
                is_chat_model=True,
                is_function_calling_model=True,
                timeout=30.0,
                max_retries=3
            )
            logger.info(f"ASI:One LLM initialized with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ASI:One LLM: {str(e)}")
            self.llm = None
    
    def _create_system_prompt(self, context: ConversationContext) -> str:
        """
        Create a system prompt tailored for mental wellness conversations.
        
        Args:
            context: Conversation context including user information
            
        Returns:
            Formatted system prompt string
        """
        base_prompt = """You are a compassionate AI mental wellness coach. Your role is to:

1. Provide emotional support and validation
2. Listen actively and respond empathetically
3. Suggest evidence-based coping strategies
4. Recognize signs of crisis and provide appropriate resources
5. Maintain a warm, non-judgmental, and professional tone
6. Never provide medical diagnosis or replace professional therapy

Guidelines:
- Always validate the user's feelings
- Ask open-ended questions to encourage sharing
- Offer practical, actionable suggestions
- If crisis indicators are detected, prioritize safety and professional resources
- Keep responses concise but meaningful (2-3 sentences typically)
- Use "I" statements to show active listening ("I hear that...", "I understand...")
"""
        
        # Add user context if available
        if context.user_profile:
            base_prompt += f"\nUser context: {context.user_profile.get('preferences', '')}"
        
        if context.mood_context:
            recent_mood = context.mood_context.get('recent_mood_score', 'unknown')
            base_prompt += f"\nRecent mood score: {recent_mood}/10"
        
        return base_prompt
    
    def _detect_crisis_indicators(self, message: str) -> tuple[bool, List[str]]:
        """
        Detect potential crisis indicators in user message.
        
        Args:
            message: User's message text
            
        Returns:
            Tuple of (is_crisis, detected_keywords)
        """
        message_lower = message.lower()
        detected = []
        
        for keyword in self.crisis_keywords:
            if keyword in message_lower:
                detected.append(keyword)
        
        is_crisis = len(detected) > 0
        return is_crisis, detected
    
    def _format_conversation_history(self, context: ConversationContext) -> List[ChatMessage]:
        """
        Format conversation history for ASI LLM.
        
        Args:
            context: Conversation context with history
            
        Returns:
            List of ChatMessage objects
        """
        if ChatMessage is None:
            return []
        
        messages = []
        
        # Add system message
        system_prompt = self._create_system_prompt(context)
        messages.append(ChatMessage(role="system", content=system_prompt))
        
        # Add conversation history (keep last 10 exchanges to manage context length)
        history = context.conversation_history[-20:] if context.conversation_history else []
        
        for entry in history:
            role = entry.get("role", "user")
            content = entry.get("content", "")
            if content:
                messages.append(ChatMessage(role=role, content=content))
        
        return messages
    
    async def generate_response(
        self, 
        user_message: str, 
        context: ConversationContext
    ) -> LLMResponse:
        """
        Generate an AI response for mental wellness conversation.
        
        Args:
            user_message: The user's input message
            context: Conversation context and user information
            
        Returns:
            LLMResponse with the AI's response and metadata
        """
        try:
            # Check for crisis indicators
            is_crisis, crisis_keywords = self._detect_crisis_indicators(user_message)
            
            # Update context with crisis indicators
            if is_crisis:
                context.crisis_indicators.extend(crisis_keywords)
            
            # If ASI LLM is not available, use fallback response
            if self.llm is None:
                return self._generate_fallback_response(user_message, is_crisis)
            
            # Format messages for ASI LLM
            messages = self._format_conversation_history(context)
            messages.append(ChatMessage(role="user", content=user_message))
            
            # Generate response using ASI LLM
            response = await self._call_asi_llm(messages)
            
            # Analyze response and create structured output
            llm_response = LLMResponse(
                text=response,
                crisis_level="high" if is_crisis else "none",
                suggested_actions=self._generate_suggested_actions(user_message, is_crisis),
                conversation_tags=self._extract_conversation_tags(user_message),
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": self.model,
                    "crisis_keywords": crisis_keywords,
                    "user_id": context.user_id,
                    "session_id": context.session_id
                }
            )
            
            logger.info(f"Generated response for user {context.user_id}")
            return llm_response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return self._generate_error_response(str(e))
    
    async def _call_asi_llm(self, messages: List[ChatMessage]) -> str:
        """
        Call ASI LLM with retry logic.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Response text from ASI LLM
        """
        try:
            # Use async chat if available, otherwise use sync
            if hasattr(self.llm, 'achat'):
                response = await self.llm.achat(messages)
            else:
                # Run sync method in thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self.llm.chat, messages)
            
            return response.message.content
            
        except Exception as e:
            logger.error(f"ASI LLM API call failed: {str(e)}")
            return self._get_fallback_text("I'm having trouble processing your message right now. Could you please try again?")
    
    def _generate_fallback_response(self, user_message: str, is_crisis: bool) -> LLMResponse:
        """
        Generate a fallback response when ASI LLM is unavailable.
        
        Args:
            user_message: User's input message
            is_crisis: Whether crisis indicators were detected
            
        Returns:
            LLMResponse with fallback content
        """
        if is_crisis:
            text = ("I hear that you're going through a really difficult time right now. "
                   "Your feelings are important and valid. Please consider reaching out to "
                   "a mental health professional or crisis hotline for immediate support.")
            suggested_actions = [
                "Contact a crisis hotline",
                "Reach out to a trusted friend or family member",
                "Consider seeking professional help"
            ]
        else:
            text = ("Thank you for sharing with me. I'm here to listen and support you. "
                   "Could you tell me more about what's on your mind today?")
            suggested_actions = [
                "Continue the conversation",
                "Try a breathing exercise",
                "Check in with your mood"
            ]
        
        return LLMResponse(
            text=text,
            confidence=0.6,  # Lower confidence for fallback
            crisis_level="high" if is_crisis else "none",
            suggested_actions=suggested_actions,
            conversation_tags=["fallback", "support"],
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "model": "fallback",
                "is_fallback": True
            }
        )
    
    def _generate_error_response(self, error_message: str) -> LLMResponse:
        """Generate response for error cases."""
        return LLMResponse(
            text="I apologize, but I'm having technical difficulties right now. Please try again in a moment.",
            confidence=0.5,
            crisis_level="none",
            suggested_actions=["Try again later", "Contact support if issues persist"],
            conversation_tags=["error", "technical"],
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "error": error_message,
                "is_error": True
            }
        )
    
    def _generate_suggested_actions(self, user_message: str, is_crisis: bool) -> List[str]:
        """Generate contextual suggested actions."""
        if is_crisis:
            return [
                "Contact crisis support: 988 (Suicide & Crisis Lifeline)",
                "Reach out to a trusted person",
                "Consider professional help"
            ]
        
        # Basic suggestions based on common patterns
        message_lower = user_message.lower()
        suggestions = []
        
        if any(word in message_lower for word in ["anxious", "anxiety", "worried"]):
            suggestions.extend(["Try deep breathing", "Practice grounding techniques"])
        
        if any(word in message_lower for word in ["sad", "depressed", "down"]):
            suggestions.extend(["Journal your thoughts", "Connect with a friend"])
        
        if any(word in message_lower for word in ["stress", "overwhelmed"]):
            suggestions.extend(["Take a short break", "Try progressive muscle relaxation"])
        
        if not suggestions:
            suggestions = ["Continue sharing", "Track your mood", "Practice self-care"]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _extract_conversation_tags(self, user_message: str) -> List[str]:
        """Extract topic tags from user message."""
        message_lower = user_message.lower()
        tags = []
        
        tag_keywords = {
            "anxiety": ["anxious", "anxiety", "worried", "nervous"],
            "depression": ["sad", "depressed", "hopeless", "empty"],
            "stress": ["stress", "overwhelmed", "pressure"],
            "sleep": ["sleep", "insomnia", "tired", "exhausted"],
            "relationships": ["family", "friends", "partner", "relationship"],
            "work": ["work", "job", "career", "boss"],
            "mood": ["mood", "feeling", "emotions"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                tags.append(tag)
        
        return tags[:5]  # Limit to 5 tags
    
    def _get_fallback_text(self, default: str) -> str:
        """Get fallback text for error cases."""
        return default


# Utility functions for conversation management
def create_conversation_context(
    user_id: str,
    session_id: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    mood_context: Optional[Dict[str, Any]] = None
) -> ConversationContext:
    """
    Create a conversation context object.
    
    Args:
        user_id: Unique user identifier
        session_id: Session identifier (auto-generated if not provided)
        conversation_history: Previous conversation messages
        user_profile: User profile information
        mood_context: Recent mood/mental health data
        
    Returns:
        ConversationContext object
    """
    if session_id is None:
        session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}"
    
    return ConversationContext(
        user_id=user_id,
        session_id=session_id,
        conversation_history=conversation_history or [],
        user_profile=user_profile,
        mood_context=mood_context
    ) 