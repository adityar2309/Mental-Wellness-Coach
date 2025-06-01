"""
Mental Wellness Coach - Conversation Coordinator Agent

Central agent that coordinates conversation flow and orchestrates
communication between specialized mental wellness agents.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from services.agent_service import (
    MentalWellnessAgent, 
    AgentConfiguration, 
    AgentType, 
    AgentMessage
)
from services.llm_service import ASILLMService, create_conversation_context, LLMResponse

try:
    from uagents import Context
except ImportError:
    Context = None

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """States of conversation coordination."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    MOOD_FOCUSED = "mood_focused"
    CRISIS_HANDLING = "crisis_handling"
    ENDING = "ending"
    COMPLETED = "completed"

@dataclass
class ActiveConversation:
    """Active conversation management data."""
    user_id: str
    session_id: str
    state: ConversationState
    participating_agents: Set[str]
    conversation_type: str
    last_activity: datetime
    context_data: Dict[str, Any]
    intervention_level: str = "none"  # none, low, medium, high, crisis
    
    def __post_init__(self):
        if isinstance(self.participating_agents, list):
            self.participating_agents = set(self.participating_agents)

class ConversationCoordinatorAgent(MentalWellnessAgent):
    """
    Central coordination agent for mental wellness conversations.
    
    Responsibilities:
    - Coordinate conversation flow between agents
    - Manage conversation state and context
    - Route messages to appropriate specialized agents
    - Integrate responses from multiple agents
    - Handle escalation and crisis coordination
    """
    
    def __init__(self, config: AgentConfiguration):
        """Initialize the conversation coordinator agent."""
        super().__init__(config)
        
        # Conversation management
        self.active_conversations: Dict[str, ActiveConversation] = {}
        self.agent_capabilities = {
            "mood_tracker": ["mood_analysis", "mood_patterns", "mood_recommendations"],
            "coping_advisor": ["coping_strategies", "stress_management", "relaxation_techniques"],
            "journaling_assistant": ["journaling_prompts", "reflection_guidance", "emotional_processing"],
            "crisis_detector": ["risk_assessment", "safety_planning", "crisis_intervention"],
            "escalation_manager": ["professional_referral", "emergency_response", "follow_up_care"]
        }
        
        # LLM service for conversation generation
        self.llm_service = ASILLMService()
        
        # Register coordinator-specific message handlers
        self._register_coordinator_handlers()
    
    def _register_coordinator_handlers(self) -> None:
        """Register message handlers for conversation coordination."""
        # Conversation lifecycle
        self.register_message_handler("start_conversation", self._handle_start_conversation)
        self.register_message_handler("continue_conversation", self._handle_continue_conversation)
        self.register_message_handler("end_conversation", self._handle_end_conversation)
        
        # Agent coordination
        self.register_message_handler("agent_response", self._handle_agent_response)
        self.register_message_handler("request_agent_consultation", self._handle_agent_consultation)
        
        # Crisis and alerts
        self.register_message_handler("mood_alert", self._handle_mood_alert)
        self.register_message_handler("crisis_alert", self._handle_crisis_alert)
        
        # User interaction
        self.register_message_handler("user_message", self._handle_user_message)
    
    async def _on_startup(self, ctx: Context) -> None:
        """Initialize conversation coordinator."""
        logger.info("Conversation Coordinator Agent starting up...")
        
        # Initialize agent registry awareness
        await self._discover_available_agents()
        
        if ctx:
            ctx.logger.info("Conversation coordination services initialized")
    
    async def _discover_available_agents(self) -> None:
        """Discover and register available mental wellness agents."""
        # This would integrate with the agent registry to discover available agents
        logger.info("Discovering available mental wellness agents...")
        
        # For now, we'll use the predefined capabilities
        available_agents = list(self.agent_capabilities.keys())
        logger.info(f"Available agents: {available_agents}")
    
    async def _handle_start_conversation(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """
        Handle conversation start request.
        
        Args:
            ctx: Agent context
            sender: Sender address
            msg: Message with conversation start data
        """
        try:
            user_id = msg.user_id
            session_id = msg.session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            conversation_type = msg.payload.get("conversation_type", "general")
            initial_message = msg.payload.get("initial_message", "")
            
            # Create active conversation
            conversation = ActiveConversation(
                user_id=user_id,
                session_id=session_id,
                state=ConversationState.INITIALIZING,
                participating_agents={"conversation_coordinator"},
                conversation_type=conversation_type,
                last_activity=datetime.utcnow(),
                context_data={
                    "conversation_history": [],
                    "user_preferences": msg.payload.get("user_preferences", {}),
                    "mood_context": msg.payload.get("mood_context", {}),
                    "initial_message": initial_message
                }
            )
            
            self.active_conversations[session_id] = conversation
            
            # Determine which agents to involve
            agents_to_involve = await self._determine_required_agents(conversation_type, initial_message)
            conversation.participating_agents.update(agents_to_involve)
            
            # Generate initial response
            response = await self._generate_coordinated_response(conversation, initial_message)
            
            # Update conversation state
            conversation.state = ConversationState.ACTIVE
            conversation.last_activity = datetime.utcnow()
            
            # Send response back
            response_msg = AgentMessage(
                message_type="conversation_started",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload={
                    "session_id": session_id,
                    "response": response.text,
                    "conversation_type": conversation_type,
                    "participating_agents": list(conversation.participating_agents),
                    "suggested_actions": response.suggested_actions,
                    "conversation_tags": response.conversation_tags
                },
                user_id=user_id,
                session_id=session_id
            )
            
            await self.send_message_to_agent(sender, response_msg)
            logger.info(f"Started conversation {session_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
    
    async def _determine_required_agents(self, conversation_type: str, initial_message: str) -> Set[str]:
        """
        Determine which agents should participate in the conversation.
        
        Args:
            conversation_type: Type of conversation
            initial_message: Initial user message
            
        Returns:
            Set of agent names to involve
        """
        agents = set()
        
        # Always include mood tracker for mental health conversations
        if conversation_type in ["mood_check", "mental_health", "general"]:
            agents.add("mood_tracker")
        
        # Crisis detection for all conversations
        agents.add("crisis_detector")
        
        # Type-specific agents
        if conversation_type == "coping":
            agents.add("coping_advisor")
        elif conversation_type == "journaling":
            agents.add("journaling_assistant")
        
        # Message content analysis for additional agents
        if initial_message:
            message_lower = initial_message.lower()
            
            if any(word in message_lower for word in ["stressed", "anxiety", "anxious", "overwhelmed"]):
                agents.add("coping_advisor")
            
            if any(word in message_lower for word in ["write", "journal", "reflect", "think"]):
                agents.add("journaling_assistant")
            
            # Crisis keywords
            crisis_keywords = ["suicide", "hurt myself", "hopeless", "end it all"]
            if any(keyword in message_lower for keyword in crisis_keywords):
                agents.add("escalation_manager")
        
        return agents
    
    async def _generate_coordinated_response(self, conversation: ActiveConversation, user_message: str) -> LLMResponse:
        """
        Generate a coordinated response using ASI LLM and agent insights.
        
        Args:
            conversation: Active conversation data
            user_message: User's message
            
        Returns:
            Generated LLM response
        """
        try:
            # Gather insights from participating agents
            agent_insights = await self._gather_agent_insights(conversation, user_message)
            
            # Create conversation context for LLM
            context = create_conversation_context(
                user_id=conversation.user_id,
                session_id=conversation.session_id,
                conversation_history=conversation.context_data.get("conversation_history", []),
                mood_context=conversation.context_data.get("mood_context", {}),
                user_profile=conversation.context_data.get("user_preferences", {})
            )
            
            # Add agent insights to context
            if agent_insights:
                context.metadata = {"agent_insights": agent_insights}
            
            # Generate response using LLM service
            response = await self.llm_service.generate_response(user_message, context)
            
            # Enhance response with agent recommendations
            if agent_insights:
                response = await self._enhance_response_with_insights(response, agent_insights)
            
            # Update conversation history
            conversation.context_data["conversation_history"].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response.text}
            ])
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating coordinated response: {str(e)}")
            # Return fallback response
            return LLMResponse(
                text="I'm here to support you. Could you tell me more about how you're feeling?",
                confidence=0.5,
                crisis_level="none",
                suggested_actions=["Continue sharing", "Take a moment to breathe"],
                conversation_tags=["fallback"],
                metadata={"error": str(e)}
            )
    
    async def _gather_agent_insights(self, conversation: ActiveConversation, user_message: str) -> Dict[str, Any]:
        """
        Gather insights from participating agents.
        
        Args:
            conversation: Active conversation
            user_message: User's message
            
        Returns:
            Compiled insights from agents
        """
        insights = {}
        
        try:
            # Request insights from each participating agent
            for agent_name in conversation.participating_agents:
                if agent_name == "conversation_coordinator":
                    continue
                
                # Send consultation request
                consultation_msg = AgentMessage(
                    message_type="consultation_request",
                    sender_agent=self.config.name,
                    recipient_agent=agent_name,
                    payload={
                        "user_message": user_message,
                        "conversation_type": conversation.conversation_type,
                        "conversation_history": conversation.context_data.get("conversation_history", [])[-5:],  # Last 5 exchanges
                        "context": conversation.context_data
                    },
                    user_id=conversation.user_id,
                    session_id=conversation.session_id,
                    requires_response=True
                )
                
                # Note: In a real implementation, we'd await responses from agents
                # For now, we'll simulate insights based on agent capabilities
                insights[agent_name] = await self._simulate_agent_insight(agent_name, user_message, conversation)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error gathering agent insights: {str(e)}")
            return {}
    
    async def _simulate_agent_insight(self, agent_name: str, user_message: str, conversation: ActiveConversation) -> Dict[str, Any]:
        """Simulate agent insights for development purposes."""
        message_lower = user_message.lower()
        
        if agent_name == "mood_tracker":
            return {
                "mood_indicators": self._extract_mood_indicators(message_lower),
                "recommendations": ["track_daily_mood", "identify_patterns"] if "mood" in message_lower else []
            }
        elif agent_name == "coping_advisor":
            stress_level = "high" if any(word in message_lower for word in ["stressed", "overwhelmed", "anxious"]) else "moderate"
            return {
                "stress_level": stress_level,
                "coping_strategies": ["deep_breathing", "grounding_exercise"] if stress_level == "high" else ["mindfulness"]
            }
        elif agent_name == "crisis_detector":
            crisis_keywords = ["suicide", "hurt myself", "hopeless", "end it all", "no point"]
            risk_level = "high" if any(keyword in message_lower for keyword in crisis_keywords) else "low"
            return {
                "risk_level": risk_level,
                "safety_recommendations": ["immediate_support", "crisis_resources"] if risk_level == "high" else []
            }
        
        return {"status": "consulted"}
    
    def _extract_mood_indicators(self, message: str) -> List[str]:
        """Extract mood indicators from message."""
        mood_keywords = {
            "sad": ["sad", "down", "depressed", "blue"],
            "anxious": ["anxious", "worried", "nervous", "stressed"],
            "angry": ["angry", "frustrated", "mad", "irritated"],
            "happy": ["happy", "good", "great", "wonderful"],
            "tired": ["tired", "exhausted", "drained", "weary"]
        }
        
        indicators = []
        for mood, keywords in mood_keywords.items():
            if any(keyword in message for keyword in keywords):
                indicators.append(mood)
        
        return indicators
    
    async def _enhance_response_with_insights(self, response: LLMResponse, insights: Dict[str, Any]) -> LLMResponse:
        """
        Enhance LLM response with agent insights.
        
        Args:
            response: Original LLM response
            insights: Insights from agents
            
        Returns:
            Enhanced response
        """
        # Combine suggested actions from agents
        additional_actions = []
        for agent_name, agent_insight in insights.items():
            if isinstance(agent_insight, dict):
                if "recommendations" in agent_insight:
                    additional_actions.extend(agent_insight["recommendations"])
                if "coping_strategies" in agent_insight:
                    additional_actions.extend(agent_insight["coping_strategies"])
                if "safety_recommendations" in agent_insight:
                    additional_actions.extend(agent_insight["safety_recommendations"])
        
        # Update response with additional insights
        response.suggested_actions.extend(additional_actions)
        response.metadata["agent_insights"] = insights
        
        # Update crisis level if any agent detected high risk
        for agent_insight in insights.values():
            if isinstance(agent_insight, dict) and agent_insight.get("risk_level") == "high":
                response.crisis_level = "high"
                break
        
        return response
    
    async def _handle_continue_conversation(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Handle conversation continuation."""
        try:
            session_id = msg.session_id
            user_message = msg.payload.get("message", "")
            
            if session_id not in self.active_conversations:
                logger.warning(f"No active conversation found for session {session_id}")
                return
            
            conversation = self.active_conversations[session_id]
            conversation.last_activity = datetime.utcnow()
            
            # Generate coordinated response
            response = await self._generate_coordinated_response(conversation, user_message)
            
            # Send response
            response_msg = AgentMessage(
                message_type="conversation_response",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload={
                    "response": response.text,
                    "suggested_actions": response.suggested_actions,
                    "conversation_tags": response.conversation_tags,
                    "crisis_level": response.crisis_level
                },
                user_id=conversation.user_id,
                session_id=session_id
            )
            
            await self.send_message_to_agent(sender, response_msg)
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {str(e)}")
    
    async def _handle_mood_alert(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Handle mood alerts from mood tracker agent."""
        try:
            user_id = msg.user_id
            alert_data = msg.payload
            
            logger.warning(f"Mood alert received for user {user_id}: {alert_data}")
            
            # Find active conversation for this user
            user_sessions = [conv for conv in self.active_conversations.values() if conv.user_id == user_id]
            
            if user_sessions:
                conversation = user_sessions[0]  # Use most recent session
                conversation.intervention_level = "medium"
                conversation.state = ConversationState.MOOD_FOCUSED
                
                # Add coping advisor to conversation if not already present
                conversation.participating_agents.add("coping_advisor")
                
                # Update context with mood alert
                conversation.context_data["mood_alert"] = alert_data
            
            # Acknowledge alert
            response = AgentMessage(
                message_type="alert_acknowledged",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload={"status": "acknowledged", "action": "conversation_adjusted"},
                user_id=user_id
            )
            
            await self.send_message_to_agent(sender, response)
            
        except Exception as e:
            logger.error(f"Error handling mood alert: {str(e)}")
    
    async def _handle_crisis_alert(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Handle crisis alerts with immediate escalation."""
        try:
            user_id = msg.user_id
            crisis_data = msg.payload
            
            logger.critical(f"CRISIS ALERT for user {user_id}: {crisis_data}")
            
            # Find active conversation
            user_sessions = [conv for conv in self.active_conversations.values() if conv.user_id == user_id]
            
            if user_sessions:
                conversation = user_sessions[0]
                conversation.intervention_level = "crisis"
                conversation.state = ConversationState.CRISIS_HANDLING
                
                # Add escalation manager
                conversation.participating_agents.add("escalation_manager")
                
                # Update context
                conversation.context_data["crisis_alert"] = crisis_data
            
            # Forward to escalation manager
            escalation_msg = AgentMessage(
                message_type="crisis_escalation",
                sender_agent=self.config.name,
                recipient_agent="escalation_manager",
                payload=crisis_data,
                user_id=user_id,
                priority="urgent",
                requires_response=True
            )
            
            await self.send_message_to_agent("escalation_manager", escalation_msg)
            
        except Exception as e:
            logger.error(f"Error handling crisis alert: {str(e)}")
    
    async def _handle_end_conversation(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Handle conversation end request."""
        try:
            session_id = msg.session_id
            
            if session_id in self.active_conversations:
                conversation = self.active_conversations[session_id]
                conversation.state = ConversationState.COMPLETED
                
                # Archive conversation data
                await self._archive_conversation(conversation)
                
                # Remove from active conversations
                del self.active_conversations[session_id]
                
                logger.info(f"Ended conversation {session_id}")
            
            # Send confirmation
            response = AgentMessage(
                message_type="conversation_ended",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload={"status": "completed", "session_id": session_id},
                session_id=session_id
            )
            
            await self.send_message_to_agent(sender, response)
            
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
    
    async def _archive_conversation(self, conversation: ActiveConversation) -> None:
        """Archive completed conversation data."""
        try:
            # TODO: Save conversation data to database
            logger.info(f"Archiving conversation {conversation.session_id}")
            
            # Calculate conversation metrics
            history = conversation.context_data.get("conversation_history", [])
            metrics = {
                "duration": (datetime.utcnow() - conversation.last_activity).total_seconds(),
                "message_count": len(history),
                "participating_agents": list(conversation.participating_agents),
                "intervention_level": conversation.intervention_level,
                "conversation_type": conversation.conversation_type
            }
            
            logger.info(f"Conversation metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"Error archiving conversation: {str(e)}")

# Factory function to create conversation coordinator agent
def create_conversation_coordinator_agent(port: Optional[int] = None) -> ConversationCoordinatorAgent:
    """
    Create a conversation coordinator agent.
    
    Args:
        port: Optional port number
        
    Returns:
        Configured conversation coordinator agent
    """
    config = AgentConfiguration(
        agent_type=AgentType.CONVERSATION_COORDINATOR,
        name="conversation_coordinator",
        port=port or 8002,
        seed="conversation_coordinator_seed",
        crisis_detection_enabled=True,
        mental_health_focus=True
    )
    
    return ConversationCoordinatorAgent(config) 