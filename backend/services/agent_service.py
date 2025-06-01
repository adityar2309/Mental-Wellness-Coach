"""
Mental Wellness Coach - uAgents Service

This module provides the Fetch.ai uAgents framework implementation for
multi-agent coordination and communication in mental wellness contexts.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from uagents import Agent, Context, Protocol, Bureau
    from uagents.setup import fund_agent_if_low
    from uagents.communication import send_message
except ImportError:
    # Fallback for when uAgents is not available
    Agent = None
    Context = None
    Protocol = None
    Bureau = None
    fund_agent_if_low = None
    send_message = None

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of mental wellness agents."""
    MOOD_TRACKER = "mood_tracker"
    CONVERSATION_COORDINATOR = "conversation_coordinator"
    CRISIS_DETECTOR = "crisis_detector"
    COPING_ADVISOR = "coping_advisor"
    JOURNALING_ASSISTANT = "journaling_assistant"
    ESCALATION_MANAGER = "escalation_manager"

class AgentStatus(Enum):
    """Agent operational status."""
    STARTING = "starting"
    RUNNING = "running"
    IDLE = "idle"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class AgentConfiguration:
    """Configuration for mental wellness agents."""
    agent_type: AgentType
    name: str
    port: Optional[int] = None
    seed: Optional[str] = None
    endpoint: Optional[str] = None
    log_level: str = "INFO"
    mental_health_focus: bool = True
    crisis_detection_enabled: bool = True
    privacy_mode: bool = True

class AgentMessage(BaseModel):
    """Structured message format for agent communication."""
    message_type: str = Field(..., description="Type of message")
    sender_agent: str = Field(..., description="Sending agent identifier")
    recipient_agent: str = Field(..., description="Target recipient agent")
    payload: Dict[str, Any] = Field(..., description="Message payload data")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    priority: str = Field(default="normal", description="Message priority level")
    requires_response: bool = Field(default=False, description="Whether response is required")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MentalWellnessAgent:
    """
    Base class for mental wellness uAgents.
    
    Provides common functionality for agents in the mental wellness ecosystem.
    """
    
    def __init__(self, config: AgentConfiguration):
        """
        Initialize the mental wellness agent.
        
        Args:
            config: Agent configuration settings
        """
        self.config = config
        self.status = AgentStatus.STARTING
        self.agent = None
        self.protocols = {}
        self.message_handlers = {}
        self.user_sessions = {}
        
        # Mental health specific settings
        self.crisis_keywords = [
            "suicide", "kill myself", "end it all", "don't want to live",
            "hurt myself", "self-harm", "cutting", "overdose",
            "hopeless", "no point", "everyone would be better off", "can't go on"
        ]
        
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize the uAgent instance."""
        try:
            if Agent is None:
                logger.warning("uAgents library not available. Using mock agent.")
                return
            
            # Create agent with optional configuration
            agent_kwargs = {
                "name": self.config.name,
                "log_level": self.config.log_level
            }
            
            if self.config.seed:
                agent_kwargs["seed"] = self.config.seed
            if self.config.port:
                agent_kwargs["port"] = self.config.port
            if self.config.endpoint:
                agent_kwargs["endpoint"] = self.config.endpoint
            
            self.agent = Agent(**agent_kwargs)
            
            # Fund agent if needed (for Fetch.ai network participation)
            if fund_agent_if_low:
                fund_agent_if_low(self.agent.wallet.address())
            
            # Setup default handlers
            self._setup_default_handlers()
            
            logger.info(f"Mental wellness agent '{self.config.name}' initialized successfully")
            logger.info(f"Agent address: {self.agent.address}")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            self.status = AgentStatus.ERROR
    
    def _setup_default_handlers(self) -> None:
        """Setup default message handlers for mental wellness functionality."""
        if not self.agent:
            return
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            """Handle agent startup."""
            self.status = AgentStatus.RUNNING
            logger.info(f"Mental wellness agent {self.config.name} started")
            await self._on_startup(ctx)
        
        @self.agent.on_event("shutdown")
        async def shutdown_handler(ctx: Context):
            """Handle agent shutdown."""
            self.status = AgentStatus.STOPPED
            logger.info(f"Mental wellness agent {self.config.name} stopped")
            await self._on_shutdown(ctx)
        
        @self.agent.on_interval(period=60.0)
        async def health_check(ctx: Context):
            """Periodic health check."""
            await self._health_check(ctx)
        
        # Default message handler for AgentMessage types
        @self.agent.on_message(model=AgentMessage)
        async def handle_agent_message(ctx: Context, sender: str, msg: AgentMessage):
            """Handle structured agent messages."""
            await self._handle_message(ctx, sender, msg)
    
    async def _on_startup(self, ctx: Context) -> None:
        """Override in subclasses for startup logic."""
        pass
    
    async def _on_shutdown(self, ctx: Context) -> None:
        """Override in subclasses for shutdown logic."""
        pass
    
    async def _health_check(self, ctx: Context) -> None:
        """Perform health check and update status."""
        if self.status == AgentStatus.ERROR:
            logger.warning(f"Agent {self.config.name} is in error state")
        elif self.status == AgentStatus.RUNNING:
            # Update to idle if no recent activity
            if not self.user_sessions:
                self.status = AgentStatus.IDLE
    
    async def _handle_message(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """
        Handle incoming agent messages.
        
        Args:
            ctx: Agent context
            sender: Sender address
            msg: Structured message
        """
        try:
            logger.info(f"Received message from {sender}: {msg.message_type}")
            
            # Crisis detection if enabled
            if self.config.crisis_detection_enabled:
                await self._check_crisis_indicators(ctx, msg)
            
            # Route to specific handler
            handler = self.message_handlers.get(msg.message_type)
            if handler:
                await handler(ctx, sender, msg)
            else:
                await self._default_message_handler(ctx, sender, msg)
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    async def _check_crisis_indicators(self, ctx: Context, msg: AgentMessage) -> None:
        """Check for crisis indicators in message content."""
        try:
            # Extract text content from payload
            text_content = ""
            if "content" in msg.payload:
                text_content = str(msg.payload["content"]).lower()
            
            # Check for crisis keywords
            detected_keywords = []
            for keyword in self.crisis_keywords:
                if keyword in text_content:
                    detected_keywords.append(keyword)
            
            if detected_keywords:
                logger.warning(f"Crisis indicators detected: {detected_keywords}")
                await self._handle_crisis_detection(ctx, msg, detected_keywords)
                
        except Exception as e:
            logger.error(f"Error in crisis detection: {str(e)}")
    
    async def _handle_crisis_detection(self, ctx: Context, msg: AgentMessage, keywords: List[str]) -> None:
        """Handle crisis detection event."""
        # Create crisis alert message
        crisis_alert = AgentMessage(
            message_type="crisis_alert",
            sender_agent=self.config.name,
            recipient_agent="escalation_manager",
            payload={
                "user_id": msg.user_id,
                "session_id": msg.session_id,
                "crisis_keywords": keywords,
                "original_message": msg.payload,
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": "high" if len(keywords) > 1 else "medium"
            },
            priority="urgent",
            requires_response=True
        )
        
        # Try to send to escalation manager
        await self.send_message_to_agent("escalation_manager", crisis_alert)
    
    async def _default_message_handler(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Default handler for unknown message types."""
        logger.warning(f"No handler for message type: {msg.message_type}")
    
    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """
        Register a handler for specific message types.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    async def send_message_to_agent(self, recipient_address: str, message: AgentMessage) -> bool:
        """
        Send a message to another agent.
        
        Args:
            recipient_address: Target agent address
            message: Message to send
            
        Returns:
            Success status
        """
        try:
            if not self.agent or send_message is None:
                logger.warning("Cannot send message - agent not initialized")
                return False
            
            # Send the message
            await send_message(recipient_address, message, self.agent)
            logger.info(f"Sent message to {recipient_address}: {message.message_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
    
    def run(self) -> None:
        """Start the agent."""
        if not self.agent:
            logger.error("Cannot run - agent not initialized")
            return
        
        logger.info(f"Starting mental wellness agent: {self.config.name}")
        self.agent.run()

class AgentRegistry:
    """
    Registry for managing multiple mental wellness agents.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, MentalWellnessAgent] = {}
        self.bureau = None
        self.is_running = False
    
    def register_agent(self, agent: MentalWellnessAgent) -> None:
        """
        Register an agent in the registry.
        
        Args:
            agent: Mental wellness agent to register
        """
        agent_name = agent.config.name
        self.agents[agent_name] = agent
        logger.info(f"Registered agent: {agent_name}")
    
    def get_agent(self, agent_name: str) -> Optional[MentalWellnessAgent]:
        """
        Get an agent by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent instance or None
        """
        return self.agents.get(agent_name)
    
    def create_bureau(self) -> None:
        """Create a bureau to run multiple agents together."""
        try:
            if Bureau is None:
                logger.warning("uAgents Bureau not available")
                return
            
            self.bureau = Bureau()
            
            # Add all registered agents to the bureau
            for agent in self.agents.values():
                if agent.agent:
                    self.bureau.add(agent.agent)
                    logger.info(f"Added agent {agent.config.name} to bureau")
            
            logger.info(f"Created bureau with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to create bureau: {str(e)}")
    
    def run_all_agents(self) -> None:
        """Run all registered agents in the bureau."""
        if not self.bureau:
            self.create_bureau()
        
        if not self.bureau:
            logger.error("Cannot run agents - bureau not created")
            return
        
        try:
            logger.info("Starting all mental wellness agents...")
            self.is_running = True
            self.bureau.run()
            
        except Exception as e:
            logger.error(f"Error running agents: {str(e)}")
            self.is_running = False
    
    def stop_all_agents(self) -> None:
        """Stop all running agents."""
        self.is_running = False
        logger.info("Stopping all mental wellness agents...")

# Global agent registry instance
agent_registry = AgentRegistry()

# Utility functions for easy agent management
def create_mental_wellness_agent(
    agent_type: AgentType,
    name: str,
    port: Optional[int] = None,
    **kwargs
) -> MentalWellnessAgent:
    """
    Create and register a mental wellness agent.
    
    Args:
        agent_type: Type of agent to create
        name: Agent name
        port: Optional port number
        **kwargs: Additional configuration options
        
    Returns:
        Created agent instance
    """
    config = AgentConfiguration(
        agent_type=agent_type,
        name=name,
        port=port,
        **kwargs
    )
    
    agent = MentalWellnessAgent(config)
    agent_registry.register_agent(agent)
    
    return agent

def get_agent_status() -> Dict[str, Any]:
    """
    Get status of all registered agents.
    
    Returns:
        Status information for all agents
    """
    status = {
        "total_agents": len(agent_registry.agents),
        "running": agent_registry.is_running,
        "agents": {}
    }
    
    for name, agent in agent_registry.agents.items():
        status["agents"][name] = {
            "type": agent.config.agent_type.value,
            "status": agent.status.value,
            "address": agent.agent.address if agent.agent else None,
            "sessions": len(agent.user_sessions)
        }
    
    return status 