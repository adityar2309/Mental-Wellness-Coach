"""
Mental Wellness Coach - Agentverse Conversation Coordinator Agent

Standalone agent for conversation coordination and AI-powered mental wellness support.
This agent specializes in:
- Managing AI conversations with users
- Coordinating with other specialized agents (mood tracker, crisis detector)
- Providing empathetic responses and mental health guidance
- Escalating to appropriate resources when needed

Deploy this agent to Agentverse for 24/7 conversation support.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import re

from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
COORDINATOR_SEED = "conversation_coordinator_wellness_coach_seed_phrase_here"
COORDINATOR_PORT = 8001
COORDINATOR_ENDPOINT = ["http://127.0.0.1:8001/submit"]

# Create the conversation coordinator agent
conversation_coordinator = Agent(
    name="conversation_coordinator",
    seed=COORDINATOR_SEED,
    port=COORDINATOR_PORT,
    endpoint=COORDINATOR_ENDPOINT,
)

# Fund agent if needed (for testnet)
fund_agent_if_low(conversation_coordinator.wallet.address())

@dataclass
class ConversationMessage(Model):
    """Message in a conversation."""
    user_id: str
    session_id: str
    message: str
    message_type: str = "user"  # user, assistant, system
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class ConversationRequest(Model):
    """Request to start or continue a conversation."""
    user_id: str
    session_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None

@dataclass
class ConversationResponse(Model):
    """Response from conversation coordinator."""
    user_id: str
    session_id: str
    response: str
    recommendations: List[str]
    requires_followup: bool
    crisis_detected: bool
    mood_assessment: Optional[Dict[str, Any]] = None

@dataclass
class CrisisAlert(Model):
    """Alert for crisis situation."""
    user_id: str
    session_id: str
    message: str
    crisis_level: str  # low, medium, high, critical
    recommendations: List[str]
    requires_immediate_action: bool

# In-memory storage for conversations
conversations: Dict[str, List[Dict]] = {}
user_contexts: Dict[str, Dict] = {}

# Crisis keywords and patterns
CRISIS_KEYWORDS = {
    "critical": [
        "suicide", "kill myself", "end it all", "want to die", "killing myself",
        "suicide plan", "taking my life", "ending my life"
    ],
    "high": [
        "hopeless", "worthless", "can't go on", "no point", "give up",
        "hurt myself", "self harm", "cutting", "nobody cares"
    ],
    "medium": [
        "depressed", "overwhelmed", "can't cope", "breaking down",
        "losing it", "falling apart", "desperate"
    ],
    "low": [
        "sad", "down", "upset", "worried", "anxious", "stressed"
    ]
}

MOOD_INDICATORS = {
    "positive": [
        "happy", "good", "great", "excellent", "wonderful", "amazing",
        "excited", "motivated", "optimistic", "hopeful", "grateful"
    ],
    "neutral": [
        "okay", "fine", "alright", "normal", "regular", "average"
    ],
    "negative": [
        "sad", "down", "low", "bad", "terrible", "awful", "depressed",
        "anxious", "worried", "stressed", "overwhelmed", "frustrated"
    ]
}

def detect_crisis_level(message: str) -> str:
    """
    Detect crisis level from message content.
    
    Args:
        message: User message to analyze
        
    Returns:
        Crisis level: critical, high, medium, low, or none
    """
    message_lower = message.lower()
    
    # Check for critical keywords first
    for keyword in CRISIS_KEYWORDS["critical"]:
        if keyword in message_lower:
            return "critical"
    
    # Check for high-risk keywords
    for keyword in CRISIS_KEYWORDS["high"]:
        if keyword in message_lower:
            return "high"
    
    # Check for medium-risk keywords
    for keyword in CRISIS_KEYWORDS["medium"]:
        if keyword in message_lower:
            return "medium"
    
    # Check for low-risk keywords
    for keyword in CRISIS_KEYWORDS["low"]:
        if keyword in message_lower:
            return "low"
    
    return "none"

def extract_mood_indicators(message: str) -> Dict[str, List[str]]:
    """
    Extract mood indicators from message.
    
    Args:
        message: User message to analyze
        
    Returns:
        Dictionary with mood categories and found indicators
    """
    message_lower = message.lower()
    found_indicators = {"positive": [], "neutral": [], "negative": []}
    
    for category, indicators in MOOD_INDICATORS.items():
        for indicator in indicators:
            if indicator in message_lower:
                found_indicators[category].append(indicator)
    
    return found_indicators

def generate_empathetic_response(message: str, crisis_level: str, mood_indicators: Dict) -> str:
    """
    Generate an empathetic response based on message analysis.
    
    Args:
        message: User's message
        crisis_level: Detected crisis level
        mood_indicators: Detected mood indicators
        
    Returns:
        Empathetic response text
    """
    responses = {
        "critical": [
            "I'm very concerned about what you're sharing with me. Your life has value and meaning. Please reach out to a crisis helpline immediately at 988 (Suicide & Crisis Lifeline) or go to your nearest emergency room.",
            "What you're feeling right now is incredibly difficult, but you don't have to face this alone. Please contact emergency services or a trusted person right away. You matter, and there is help available."
        ],
        "high": [
            "I hear how much pain you're in right now, and I want you to know that these feelings, while overwhelming, can change. Have you considered talking to a mental health professional or calling a crisis support line?",
            "It sounds like you're going through an incredibly difficult time. You're not alone in this - many people have felt this way and found their way through with support. Can we explore some immediate coping strategies?"
        ],
        "medium": [
            "I can sense that you're struggling right now, and that takes courage to share. These feelings are valid, and it's okay to not be okay sometimes. What has helped you cope with difficult emotions in the past?",
            "Thank you for trusting me with how you're feeling. Depression and overwhelm can feel all-consuming, but they don't define you. Would you like to talk about what's been most challenging lately?"
        ],
        "low": [
            "I hear that you're having a tough time. It's completely normal to feel this way sometimes. Sometimes just acknowledging these feelings can be the first step. What's been on your mind today?",
            "Everyone goes through difficult periods, and it sounds like you're in one right now. I'm here to listen and support you through this. Would you like to share more about what's been affecting your mood?"
        ],
        "none": [
            "Thank you for sharing with me. I'm here to listen and provide support. How are you feeling today, and what would be most helpful for our conversation?",
            "I appreciate you taking the time to connect. Mental wellness is a journey, and I'm here to support you along the way. What's on your mind?"
        ]
    }
    
    # Add mood-specific responses
    if mood_indicators["positive"]:
        if crisis_level == "none":
            return f"It's wonderful to hear the positive energy in your message! I noticed you mentioned feeling {', '.join(mood_indicators['positive'][:2])}. This is great - would you like to talk about what's contributing to these good feelings?"
    
    # Select appropriate response based on crisis level
    response_options = responses.get(crisis_level, responses["none"])
    return response_options[0]  # Return first option for consistency

def generate_recommendations(message: str, crisis_level: str, mood_indicators: Dict) -> List[str]:
    """
    Generate appropriate recommendations based on message analysis.
    
    Args:
        message: User's message
        crisis_level: Detected crisis level
        mood_indicators: Detected mood indicators
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if crisis_level == "critical":
        recommendations.extend([
            "immediate_crisis_intervention",
            "emergency_services_contact",
            "crisis_hotline_988",
            "trusted_person_contact"
        ])
    elif crisis_level == "high":
        recommendations.extend([
            "professional_mental_health_support",
            "crisis_support_line",
            "safety_planning",
            "trusted_friend_family_contact"
        ])
    elif crisis_level == "medium":
        recommendations.extend([
            "mental_health_professional_consultation",
            "coping_strategies_practice",
            "support_group_consideration",
            "self_care_routine"
        ])
    elif crisis_level == "low":
        recommendations.extend([
            "mood_tracking",
            "stress_management_techniques",
            "physical_activity",
            "social_connection"
        ])
    else:
        # Positive or neutral mood
        if mood_indicators["positive"]:
            recommendations.extend([
                "maintain_positive_habits",
                "gratitude_practice",
                "share_positivity_with_others"
            ])
        else:
            recommendations.extend([
                "daily_mood_check_in",
                "mindfulness_practice",
                "healthy_lifestyle_maintenance"
            ])
    
    return recommendations

def store_conversation_message(user_id: str, session_id: str, message_data: Dict) -> None:
    """Store conversation message in memory."""
    conversation_key = f"{user_id}_{session_id}"
    
    if conversation_key not in conversations:
        conversations[conversation_key] = []
    
    conversations[conversation_key].append(message_data)
    
    # Keep only last 50 messages per conversation
    if len(conversations[conversation_key]) > 50:
        conversations[conversation_key] = conversations[conversation_key][-50:]
    
    logger.info(f"Stored message for conversation {conversation_key}")

def get_conversation_history(user_id: str, session_id: str, limit: int = 10) -> List[Dict]:
    """Get conversation history."""
    conversation_key = f"{user_id}_{session_id}"
    
    if conversation_key not in conversations:
        return []
    
    return conversations[conversation_key][-limit:]

def update_user_context(user_id: str, context_update: Dict) -> None:
    """Update user context information."""
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    
    user_contexts[user_id].update(context_update)
    user_contexts[user_id]["last_updated"] = datetime.utcnow().isoformat()

# Create conversation protocol
conversation_protocol = Protocol("Conversation Coordination Protocol")

@conversation_protocol.on_message(model=ConversationRequest)
async def handle_conversation_request(ctx: Context, sender: str, msg: ConversationRequest):
    """
    Handle conversation request from user or other agents.
    
    Args:
        ctx: Agent context
        sender: Sender address
        msg: Conversation request
    """
    try:
        ctx.logger.info(f"Received conversation request from {sender} for user {msg.user_id}")
        
        # Generate session ID if not provided
        session_id = msg.session_id or f"session_{int(datetime.utcnow().timestamp())}"
        
        # Analyze the message for crisis and mood indicators
        crisis_level = detect_crisis_level(msg.message)
        mood_indicators = extract_mood_indicators(msg.message)
        
        # Generate empathetic response
        response_text = generate_empathetic_response(msg.message, crisis_level, mood_indicators)
        
        # Generate recommendations
        recommendations = generate_recommendations(msg.message, crisis_level, mood_indicators)
        
        # Store the conversation messages
        user_message_data = {
            "message": msg.message,
            "message_type": "user",
            "timestamp": datetime.utcnow().isoformat(),
            "crisis_level": crisis_level,
            "mood_indicators": mood_indicators
        }
        
        assistant_message_data = {
            "message": response_text,
            "message_type": "assistant", 
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": recommendations
        }
        
        store_conversation_message(msg.user_id, session_id, user_message_data)
        store_conversation_message(msg.user_id, session_id, assistant_message_data)
        
        # Update user context
        context_update = {
            "last_crisis_level": crisis_level,
            "last_mood_indicators": mood_indicators,
            "conversation_count": user_contexts.get(msg.user_id, {}).get("conversation_count", 0) + 1
        }
        update_user_context(msg.user_id, context_update)
        
        # Determine if follow-up is needed
        requires_followup = crisis_level in ["critical", "high", "medium"]
        crisis_detected = crisis_level in ["critical", "high"]
        
        # Create mood assessment for mood tracker
        mood_assessment = None
        if mood_indicators["negative"] or crisis_level != "none":
            estimated_mood_score = {
                "critical": 1,
                "high": 2,
                "medium": 3,
                "low": 4,
                "none": 5
            }.get(crisis_level, 5)
            
            mood_assessment = {
                "estimated_mood_score": estimated_mood_score,
                "emotions": mood_indicators["negative"] + mood_indicators["positive"],
                "crisis_level": crisis_level,
                "needs_intervention": crisis_detected
            }
        
        # Prepare response
        response = ConversationResponse(
            user_id=msg.user_id,
            session_id=session_id,
            response=response_text,
            recommendations=recommendations,
            requires_followup=requires_followup,
            crisis_detected=crisis_detected,
            mood_assessment=mood_assessment
        )
        
        # Send response back to sender
        await ctx.send(sender, response)
        
        # Send crisis alert if needed
        if crisis_detected:
            crisis_alert = CrisisAlert(
                user_id=msg.user_id,
                session_id=session_id,
                message=msg.message,
                crisis_level=crisis_level,
                recommendations=recommendations,
                requires_immediate_action=(crisis_level == "critical")
            )
            
            # In a real deployment, this would be sent to crisis management systems
            ctx.logger.critical(f"CRISIS ALERT: {crisis_level} level crisis detected for user {msg.user_id}")
            
            # TODO: Send to crisis management agent or external emergency systems
        
        ctx.logger.info(f"Processed conversation for user {msg.user_id}, crisis level: {crisis_level}")
        
    except Exception as e:
        ctx.logger.error(f"Error processing conversation request: {str(e)}")
        
        # Send error response
        error_response = ConversationResponse(
            user_id=msg.user_id,
            session_id=msg.session_id or "error_session",
            response="I apologize, but I'm experiencing technical difficulties. Please try again, or if this is urgent, please contact emergency services or a crisis helpline.",
            recommendations=["retry_conversation", "emergency_contact_if_urgent"],
            requires_followup=True,
            crisis_detected=False
        )
        await ctx.send(sender, error_response)

@conversation_protocol.on_message(model=ConversationMessage)
async def handle_conversation_message(ctx: Context, sender: str, msg: ConversationMessage):
    """
    Handle individual conversation messages for logging/storage.
    
    Args:
        ctx: Agent context
        sender: Sender address
        msg: Conversation message
    """
    try:
        ctx.logger.info(f"Received conversation message from {sender}")
        
        # Store the message
        message_data = asdict(msg)
        store_conversation_message(msg.user_id, msg.session_id, message_data)
        
        ctx.logger.info(f"Stored message for user {msg.user_id} in session {msg.session_id}")
        
    except Exception as e:
        ctx.logger.error(f"Error handling conversation message: {str(e)}")

# Include the conversation protocol in the agent
conversation_coordinator.include(conversation_protocol)

@conversation_coordinator.on_event("startup")
async def startup_handler(ctx: Context):
    """Agent startup handler."""
    ctx.logger.info("💬 Mental Wellness Conversation Coordinator Agent starting up...")
    ctx.logger.info(f"Agent address: {conversation_coordinator.address}")
    ctx.logger.info("Ready to provide empathetic conversation support!")

@conversation_coordinator.on_event("shutdown")
async def shutdown_handler(ctx: Context):
    """Agent shutdown handler."""
    ctx.logger.info("💬 Mental Wellness Conversation Coordinator Agent shutting down...")

if __name__ == "__main__":
    print("🚀 Starting Mental Wellness Conversation Coordinator Agent for Agentverse...")
    print(f"💬 Agent Address: {conversation_coordinator.address}")
    print(f"🌐 Port: {COORDINATOR_PORT}")
    print("💡 This agent provides empathetic conversation support and coordination")
    print("🔄 Coordinates with mood tracker and crisis management systems")
    print("📈 Deploy to Agentverse for 24/7 availability!")
    
    conversation_coordinator.run() 