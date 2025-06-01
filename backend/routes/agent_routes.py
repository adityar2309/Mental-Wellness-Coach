"""
Mental Wellness Coach - Agent Management Routes

API endpoints for managing uAgents framework including agent status,
conversation coordination, and multi-agent system monitoring.
"""

import asyncio
import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
from datetime import datetime

# Import our custom auth system
from .auth_routes import token_required

from services.agent_service import (
    agent_registry, 
    create_mental_wellness_agent, 
    get_agent_status,
    AgentType, 
    AgentMessage
)
from agents.mood_tracker_agent import create_mood_tracker_agent
from agents.conversation_coordinator_agent import create_conversation_coordinator_agent

logger = logging.getLogger(__name__)

# Create blueprint for agent routes
agent_bp = Blueprint('agents', __name__)

@agent_bp.route('/status', methods=['GET'])
@token_required
def get_agents_status():
    """
    Get status of all mental wellness agents.
    
    Returns:
        JSON response with agent status information
    """
    try:
        status = get_agent_status()
        
        # Format the response to match test expectations
        agents_list = []
        for agent_name, agent_data in status.get('agents', {}).items():
            agents_list.append({
                'name': agent_name,
                'status': agent_data.get('status', 'unknown'),
                'type': agent_data.get('type', 'unknown'),
                'last_seen': agent_data.get('last_seen'),
                'health': agent_data.get('health', 'unknown')
            })
        
        return jsonify({
            "agents": agents_list,
            "total_agents": len(agents_list),
            "active_agents": len([a for a in agents_list if a['status'] == 'active']),
            "timestamp": status.get('timestamp')
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return jsonify({
            "error": f"Failed to get agent status: {str(e)}"
        }), 500

@agent_bp.route('/initialize', methods=['POST'])
@token_required
def initialize_agents():
    """
    Initialize the mental wellness agent system.
    
    Expected JSON payload:
    {
        "agents": ["mood_tracker", "conversation_coordinator", "crisis_detector"],
        "auto_start": true
    }
    
    Returns:
        JSON response with initialization status
    """
    try:
        data = request.get_json()
        requested_agents = data.get('agents', ['mood_tracker', 'conversation_coordinator'])
        auto_start = data.get('auto_start', False)
        
        initialized_agents = []
        
        # Initialize requested agents
        for agent_name in requested_agents:
            if agent_name == 'mood_tracker':
                agent = create_mood_tracker_agent(port=8001)
                initialized_agents.append(agent_name)
                
            elif agent_name == 'conversation_coordinator':
                agent = create_conversation_coordinator_agent(port=8002)
                initialized_agents.append(agent_name)
                
            elif agent_name == 'crisis_detector':
                agent = create_mental_wellness_agent(
                    AgentType.CRISIS_DETECTOR, 
                    'crisis_detector', 
                    port=8003
                )
                initialized_agents.append(agent_name)
                
            elif agent_name == 'coping_advisor':
                agent = create_mental_wellness_agent(
                    AgentType.COPING_ADVISOR, 
                    'coping_advisor', 
                    port=8004
                )
                initialized_agents.append(agent_name)
                
            elif agent_name == 'journaling_assistant':
                agent = create_mental_wellness_agent(
                    AgentType.JOURNALING_ASSISTANT, 
                    'journaling_assistant', 
                    port=8005
                )
                initialized_agents.append(agent_name)
                
            elif agent_name == 'escalation_manager':
                agent = create_mental_wellness_agent(
                    AgentType.ESCALATION_MANAGER, 
                    'escalation_manager', 
                    port=8006
                )
                initialized_agents.append(agent_name)
        
        # Start agents if requested
        if auto_start and initialized_agents:
            try:
                agent_registry.run_all_agents()
            except Exception as e:
                logger.warning(f"Could not auto-start agents: {str(e)}")
        
        return jsonify({
            "status": "success",
            "data": {
                "initialized_agents": initialized_agents,
                "total_agents": len(initialized_agents),
                "auto_started": auto_start
            },
            "message": f"Successfully initialized {len(initialized_agents)} agents"
        }), 200
        
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to initialize agents: {str(e)}"
        }), 500

@agent_bp.route('/start', methods=['POST'])
@token_required
def start_agents():
    """
    Start all registered mental wellness agents.
    
    Returns:
        JSON response with start status
    """
    try:
        if not agent_registry.agents:
            return jsonify({
                "status": "error",
                "message": "No agents registered. Initialize agents first."
            }), 400
        
        # Create bureau and start agents
        agent_registry.create_bureau()
        
        # Note: In production, agents would run in background processes
        # For development, we'll track the start request
        agent_count = len(agent_registry.agents)
        
        return jsonify({
            "status": "success",
            "data": {
                "started_agents": list(agent_registry.agents.keys()),
                "total_agents": agent_count,
                "bureau_created": True
            },
            "message": f"Agent system started with {agent_count} agents"
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting agents: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to start agents: {str(e)}"
        }), 500

@agent_bp.route('/stop', methods=['POST'])
@token_required
def stop_agents():
    """
    Stop all running mental wellness agents.
    
    Returns:
        JSON response with stop status
    """
    try:
        agent_registry.stop_all_agents()
        
        return jsonify({
            "status": "success",
            "message": "All agents stopped successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping agents: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to stop agents: {str(e)}"
        }), 500

@agent_bp.route('/conversation/start', methods=['POST'])
@token_required
def start_agent_conversation():
    """
    Start a new conversation using the agent system.
    
    Expected JSON payload:
    {
        "conversation_type": "mood_check",
        "initial_message": "I'm feeling anxious today",
        "user_preferences": {},
        "mood_context": {}
    }
    
    Returns:
        JSON response with conversation session details
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        conversation_type = data.get('conversation_type', 'general')
        initial_message = data.get('initial_message', '')
        user_preferences = data.get('user_preferences', {})
        mood_context = data.get('mood_context', {})
        
        # Get conversation coordinator agent
        coordinator = agent_registry.get_agent('conversation_coordinator')
        if not coordinator:
            return jsonify({
                "status": "error",
                "message": "Conversation coordinator not available. Initialize agents first."
            }), 400
        
        # Create conversation start message
        session_id = f"session_{user_id}_{data.get('timestamp', '')}"
        
        start_message = AgentMessage(
            message_type="start_conversation",
            sender_agent="api_gateway",
            recipient_agent="conversation_coordinator",
            payload={
                "conversation_type": conversation_type,
                "initial_message": initial_message,
                "user_preferences": user_preferences,
                "mood_context": mood_context
            },
            user_id=user_id,
            session_id=session_id
        )
        
        # For development, we'll simulate the agent response
        # In production, this would send the message to the actual agent
        response_data = _simulate_conversation_start(coordinator, start_message)
        
        return jsonify({
            "status": "success",
            "data": response_data,
            "message": "Conversation started successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting agent conversation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to start conversation: {str(e)}"
        }), 500

@agent_bp.route('/conversation/continue', methods=['POST'])
@token_required
def continue_agent_conversation():
    """
    Continue an existing conversation through the agent system.
    
    Expected JSON payload:
    {
        "session_id": "session_123",
        "message": "I think the breathing exercises are helping"
    }
    
    Returns:
        JSON response with agent-coordinated response
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        session_id = data.get('session_id')
        message = data.get('message', '')
        
        if not session_id:
            return jsonify({
                "status": "error",
                "message": "Session ID is required"
            }), 400
        
        # Get conversation coordinator
        coordinator = agent_registry.get_agent('conversation_coordinator')
        if not coordinator:
            return jsonify({
                "status": "error",
                "message": "Conversation coordinator not available"
            }), 400
        
        # Create continue message
        continue_message = AgentMessage(
            message_type="continue_conversation",
            sender_agent="api_gateway",
            recipient_agent="conversation_coordinator",
            payload={"message": message},
            user_id=user_id,
            session_id=session_id
        )
        
        # Simulate agent coordination response
        response_data = _simulate_conversation_continue(coordinator, continue_message)
        
        return jsonify({
            "status": "success",
            "data": response_data,
            "message": "Conversation continued successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error continuing agent conversation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to continue conversation: {str(e)}"
        }), 500

@agent_bp.route('/mood/submit', methods=['POST'])
@token_required
def submit_mood_to_agents():
    """
    Submit mood data to the agent system for analysis.
    
    Expected JSON payload:
    {
        "mood_score": 7,
        "emotions": ["happy", "energetic"],
        "energy_level": 8,
        "stress_level": 3,
        "sleep_hours": 7.5,
        "triggers": ["exercise", "good_weather"],
        "notes": "Had a great workout this morning"
    }
    
    Returns:
        JSON response with mood analysis from agents
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        # Get mood tracker agent
        mood_tracker = agent_registry.get_agent('mood_tracker')
        if not mood_tracker:
            return jsonify({
                "status": "error",
                "message": "Mood tracker agent not available"
            }), 400
        
        # Create mood entry message
        mood_message = AgentMessage(
            message_type="mood_entry",
            sender_agent="api_gateway",
            recipient_agent="mood_tracker",
            payload={"mood_data": data},
            user_id=user_id
        )
        
        # Simulate mood analysis
        analysis_result = _simulate_mood_analysis(mood_tracker, mood_message)
        
        return jsonify({
            "status": "success",
            "data": analysis_result,
            "message": "Mood data processed successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting mood to agents: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process mood data: {str(e)}"
        }), 500

@agent_bp.route('/mood/analysis', methods=['GET'])
@token_required
def get_mood_analysis():
    """
    Get mood analysis from the mood tracker agent.
    
    Query parameters:
    - days: Number of days to analyze (default: 7)
    
    Returns:
        JSON response with mood analysis and insights
    """
    try:
        user_id = request.current_user_id
        days = request.args.get('days', 7, type=int)
        
        # Get mood tracker agent
        mood_tracker = agent_registry.get_agent('mood_tracker')
        if not mood_tracker:
            return jsonify({
                "status": "error",
                "message": "Mood tracker agent not available"
            }), 400
        
        # Create analysis request
        analysis_request = AgentMessage(
            message_type="mood_analysis_request",
            sender_agent="api_gateway",
            recipient_agent="mood_tracker",
            payload={"days": days},
            user_id=user_id
        )
        
        # Simulate analysis response
        analysis_data = _simulate_mood_analysis_request(mood_tracker, analysis_request)
        
        return jsonify({
            "status": "success",
            "data": analysis_data,
            "message": "Mood analysis retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting mood analysis: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get mood analysis: {str(e)}"
        }), 500

@agent_bp.route('/agents/<agent_name>/health', methods=['GET'])
@token_required
def get_agent_health(agent_name: str):
    """
    Get health status of a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        JSON response with agent health information
    """
    try:
        agent = agent_registry.get_agent(agent_name)
        if not agent:
            return jsonify({
                "status": "error",
                "message": f"Agent '{agent_name}' not found"
            }), 404
        
        health_data = {
            "agent_name": agent_name,
            "agent_type": agent.config.agent_type.value,
            "status": agent.status.value,
            "address": agent.agent.address if agent.agent else None,
            "port": agent.config.port,
            "mental_health_focus": agent.config.mental_health_focus,
            "crisis_detection_enabled": agent.config.crisis_detection_enabled,
            "active_sessions": len(agent.user_sessions),
            "last_activity": "active"  # Would track actual last activity
        }
        
        return jsonify({
            "status": "success",
            "data": health_data,
            "message": f"Health status for {agent_name} retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting agent health: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get agent health: {str(e)}"
        }), 500

@agent_bp.route('/coordinate', methods=['POST'])
@token_required
def coordinate_agent_task():
    """
    Coordinate a task across multiple agents.
    
    Expected JSON payload:
    {
        "task_type": "mood_analysis|conversation|crisis_detection",
        "data": {...},
        "target_agents": ["mood_tracker", "conversation_coordinator"]
    }
    
    Returns:
        JSON response with task coordination results
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'task_type' not in data:
            return jsonify({'error': 'Task type is required'}), 400
        
        task_type = data.get('task_type')
        task_data = data.get('data', {})
        target_agents = data.get('target_agents', ['mood_tracker'])
        
        # Simulate task coordination
        task_id = f"task_{task_type}_{user_id}_{len(agent_registry.agents)}"
        
        # Mock coordination results
        coordination_results = {
            'task_id': task_id,
            'task_type': task_type,
            'status': 'coordinated',
            'assigned_agents': target_agents,
            'started_at': logging.getLogger().handlers[0].formatter.converter(None)[0] if logging.getLogger().handlers else None,
            'estimated_completion': '30 seconds'
        }
        
        logger.info(f"Task {task_id} coordinated for user {user_id}")
        
        return jsonify(coordination_results), 200
        
    except Exception as e:
        logger.error(f"Error coordinating agent task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@agent_bp.route('/communicate', methods=['POST'])
@token_required
def communicate_with_agent():
    """
    Send a message to a specific agent.
    
    Expected JSON payload:
    {
        "target_agent": "mood_tracker",
        "message": "Please analyze recent mood patterns",
        "priority": "normal|high|urgent"
    }
    
    Returns:
        JSON response with communication results
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'target_agent' not in data or 'message' not in data:
            return jsonify({'error': 'Target agent and message are required'}), 400
        
        target_agent = data.get('target_agent')
        message = data.get('message')
        priority = data.get('priority', 'normal')
        
        # Simulate agent communication
        message_id = f"msg_{target_agent}_{user_id}_{hash(message) % 10000}"
        
        # Mock communication results
        communication_results = {
            'message_id': message_id,
            'target_agent': target_agent,
            'status': 'delivered',
            'priority': priority,
            'sent_at': str(datetime.now()),
            'response_expected': True
        }
        
        logger.info(f"Message {message_id} sent to agent {target_agent} for user {user_id}")
        
        return jsonify(communication_results), 200
        
    except Exception as e:
        logger.error(f"Error communicating with agent: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@agent_bp.route('/metrics', methods=['GET'])
@token_required
def get_agent_metrics():
    """
    Get performance metrics for all agents.
    
    Returns:
        JSON response with agent performance metrics
    """
    try:
        user_id = request.current_user_id
        
        # Simulate agent metrics
        mock_metrics = {
            'mood_tracker': {
                'total_requests': 42,
                'average_response_time': 150,  # milliseconds
                'success_rate': 98.5,
                'last_active': str(datetime.now()),
                'memory_usage': '45MB',
                'cpu_usage': '12%'
            },
            'conversation_coordinator': {
                'total_requests': 28,
                'average_response_time': 220,
                'success_rate': 97.8,
                'last_active': str(datetime.now()),
                'memory_usage': '38MB',
                'cpu_usage': '8%'
            },
            'crisis_detector': {
                'total_requests': 15,
                'average_response_time': 180,
                'success_rate': 100.0,
                'last_active': str(datetime.now()),
                'memory_usage': '32MB',
                'cpu_usage': '5%'
            }
        }
        
        # Calculate overall metrics
        total_requests = sum(agent['total_requests'] for agent in mock_metrics.values())
        avg_response_time = sum(agent['average_response_time'] for agent in mock_metrics.values()) / len(mock_metrics)
        overall_success_rate = sum(agent['success_rate'] for agent in mock_metrics.values()) / len(mock_metrics)
        
        metrics_response = {
            'metrics': mock_metrics,
            'overview': {
                'total_agents': len(mock_metrics),
                'total_requests': total_requests,
                'average_response_time': round(avg_response_time, 1),
                'overall_success_rate': round(overall_success_rate, 2),
                'system_health': 'healthy'
            },
            'timestamp': str(datetime.now())
        }
        
        logger.info(f"Agent metrics retrieved for user {user_id}")
        
        return jsonify(metrics_response), 200
        
    except Exception as e:
        logger.error(f"Error getting agent metrics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Simulation functions for development
def _simulate_conversation_start(coordinator, message: AgentMessage) -> Dict[str, Any]:
    """Simulate conversation start response."""
    return {
        "session_id": message.session_id,
        "response": "Hello! I'm here to support your mental wellness journey. How are you feeling today?",
        "conversation_type": message.payload.get("conversation_type"),
        "participating_agents": ["conversation_coordinator", "mood_tracker", "crisis_detector"],
        "suggested_actions": ["Share your current mood", "Describe what's on your mind"],
        "conversation_tags": ["greeting", "mental_health"],
        "crisis_level": "none"
    }

def _simulate_conversation_continue(coordinator, message: AgentMessage) -> Dict[str, Any]:
    """Simulate conversation continuation response."""
    user_message = message.payload.get("message", "")
    
    # Simple response based on message content
    if "anxious" in user_message.lower():
        response = "I understand you're feeling anxious. Let's try a quick breathing exercise together."
        suggested_actions = ["Deep breathing exercise", "Grounding technique", "Share more about triggers"]
        tags = ["anxiety", "coping"]
    elif "good" in user_message.lower() or "better" in user_message.lower():
        response = "That's wonderful to hear! What's contributing to feeling better today?"
        suggested_actions = ["Identify positive factors", "Plan to maintain progress"]
        tags = ["positive", "progress"]
    else:
        response = "I hear you. Can you tell me more about what's going through your mind?"
        suggested_actions = ["Continue sharing", "Explore feelings deeper"]
        tags = ["exploration", "support"]
    
    return {
        "response": response,
        "suggested_actions": suggested_actions,
        "conversation_tags": tags,
        "crisis_level": "none",
        "agent_insights": {
            "mood_tracker": {"mood_indicators": ["anxious"] if "anxious" in user_message.lower() else []},
            "crisis_detector": {"risk_level": "low"}
        }
    }

def _simulate_mood_analysis(mood_tracker, message: AgentMessage) -> Dict[str, Any]:
    """Simulate mood analysis response."""
    mood_data = message.payload.get("mood_data", {})
    mood_score = mood_data.get("mood_score", 5)
    
    return {
        "status": "success",
        "mood_score": mood_score,
        "analysis": {
            "mood_trend": "stable" if mood_score >= 5 else "concerning",
            "needs_intervention": mood_score <= 3,
            "recommendations": [
                "continue_daily_tracking",
                "stress_management" if mood_data.get("stress_level", 0) > 6 else "maintain_routine"
            ],
            "alerts": ["low_mood"] if mood_score <= 3 else [],
            "pattern_insights": []
        },
        "recommendations": [
            "Track mood daily",
            "Practice self-care" if mood_score < 5 else "Keep up the good work"
        ]
    }

def _simulate_mood_analysis_request(mood_tracker, message: AgentMessage) -> Dict[str, Any]:
    """Simulate mood analysis request response."""
    days = message.payload.get("days", 7)
    
    return {
        "analysis": {
            "average_mood": 6.2,
            "highest_mood": 8,
            "lowest_mood": 4,
            "mood_variance": 1.8,
            "total_entries": days,
            "patterns": ["consistent_morning_energy", "midweek_stress"],
            "recommendations": [
                "maintain_morning_routine",
                "midweek_stress_management",
                "weekend_relaxation"
            ]
        },
        "insights": {
            "trend": "stable_with_weekly_pattern",
            "risk_factors": ["work_stress"],
            "protective_factors": ["exercise", "social_connection"]
        }
    } 