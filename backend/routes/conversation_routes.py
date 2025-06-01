"""
Mental Wellness Coach - Conversation Routes

Flask blueprint for AI conversation management and chat functionality.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import logging
import asyncio
from typing import Dict, List, Optional

# Import our custom auth system
from .auth_routes import token_required

# Import LLM service
try:
    from services.llm_service import ASILLMService, create_conversation_context, LLMResponse
    llm_service = ASILLMService()
    HAS_LLM_SERVICE = True
except ImportError:
    HAS_LLM_SERVICE = False
    llm_service = None

# Import crisis detection service
try:
    from services.crisis_service import crisis_service, CrisisLevel
    HAS_CRISIS_SERVICE = True
except ImportError:
    HAS_CRISIS_SERVICE = False
    crisis_service = None

# Create blueprint with correct name expected by app.py
conversation_bp = Blueprint('conversation', __name__)
bp = conversation_bp  # Keep both for compatibility
logger = logging.getLogger(__name__)

# Mock conversation storage (since database is not connected)
mock_conversations = {}
mock_messages = {}

@conversation_bp.route('/chat', methods=['POST'])
@token_required
def chat():
    """
    Simple chat endpoint for AI conversation.
    
    Expected JSON:
    {
        "message": "I'm feeling anxious today",
        "conversation_id": "optional-conversation-id"
    }
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message_content = data.get('message')
        conversation_id = data.get('conversation_id', f"conv_{datetime.utcnow().timestamp()}")
        
        # Store user message
        if conversation_id not in mock_messages:
            mock_messages[conversation_id] = []
        
        user_message = {
            'id': f"msg_{len(mock_messages[conversation_id])}",
            'role': 'user',
            'content': message_content,
            'timestamp': datetime.utcnow().isoformat()
        }
        mock_messages[conversation_id].append(user_message)
        
        # Perform crisis assessment if service is available
        crisis_assessment = None
        if HAS_CRISIS_SERVICE:
            try:
                crisis_assessment = asyncio.run(crisis_service.assess_crisis_risk(
                    user_id=str(user_id),
                    content=message_content,
                    trigger_source="chat",
                    additional_context={
                        "conversation_id": conversation_id,
                        "message_history": mock_messages.get(conversation_id, [])[-5:]  # Last 5 messages for context
                    }
                ))
                logger.info(f"Crisis assessment completed for user {user_id}: {crisis_assessment.crisis_level.value}")
            except Exception as e:
                logger.error(f"Crisis assessment failed: {str(e)}")
                crisis_assessment = None
        
        # Generate AI response based on crisis assessment or fallback to mock
        if crisis_assessment and crisis_assessment.crisis_level != CrisisLevel.NONE:
            # Use crisis assessment for response
            ai_response = {
                'text': _generate_crisis_response(crisis_assessment),
                'crisis_level': crisis_assessment.crisis_level.value,
                'confidence': round(crisis_assessment.confidence, 3),
                'suggested_actions': crisis_assessment.recommended_interventions,
                'conversation_tags': ['crisis_detected', 'safety_support'],
                'safety_resources': crisis_assessment.safety_resources,
                'risk_factors': [factor.value for factor in crisis_assessment.detected_factors],
                'escalation_needed': crisis_assessment.escalation_needed
            }
            
            # Log high-risk situations
            if crisis_assessment.crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]:
                logger.warning(f"HIGH RISK DETECTED: User {user_id} - {crisis_assessment.crisis_level.value}")
        else:
            # Use fallback mock response
            ai_response = _generate_mock_response(message_content)
        
        # Store AI response
        ai_message = {
            'id': f"msg_{len(mock_messages[conversation_id])}",
            'role': 'assistant',
            'content': ai_response['text'],
            'timestamp': datetime.utcnow().isoformat()
        }
        mock_messages[conversation_id].append(ai_message)
        
        # Update conversation metadata
        mock_conversations[conversation_id] = {
            'id': conversation_id,
            'user_id': user_id,
            'created_at': mock_conversations.get(conversation_id, {}).get('created_at', datetime.utcnow().isoformat()),
            'last_message_at': datetime.utcnow().isoformat(),
            'message_count': len(mock_messages[conversation_id])
        }
        
        logger.info(f"Chat message processed for user {user_id} in conversation {conversation_id}")
        
        return jsonify({
            'conversation_id': conversation_id,
            'response': ai_response,
            'message_id': ai_message['id']
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@conversation_bp.route('/history/<conversation_id>', methods=['GET'])
@token_required
def get_conversation_history(conversation_id):
    """Get conversation history."""
    try:
        user_id = request.current_user_id
        
        # Check if conversation exists and belongs to user
        if conversation_id not in mock_conversations:
            return jsonify({'error': 'Conversation not found'}), 404
        
        conversation = mock_conversations[conversation_id]
        if conversation['user_id'] != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        messages = mock_messages.get(conversation_id, [])
        
        return jsonify({
            'conversation_id': conversation_id,
            'messages': messages,
            'total_messages': len(messages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@conversation_bp.route('/conversations', methods=['GET'])
@token_required
def get_user_conversations():
    """Get all conversations for the current user."""
    try:
        user_id = request.current_user_id
        
        # Filter conversations by user
        user_conversations = {}
        for conv_id, conv_data in mock_conversations.items():
            if conv_data['user_id'] == user_id:
                user_conversations[conv_id] = conv_data
        
        # Add latest message to each conversation
        conversations_with_preview = []
        for conv_id, conv_data in user_conversations.items():
            messages = mock_messages.get(conv_id, [])
            latest_message = messages[-1] if messages else None
            
            conversations_with_preview.append({
                'id': conv_id,
                'created_at': conv_data['created_at'],
                'last_message_at': conv_data['last_message_at'],
                'message_count': conv_data['message_count'],
                'latest_message': latest_message
            })
        
        # Sort by last message time
        conversations_with_preview.sort(key=lambda x: x['last_message_at'], reverse=True)
        
        return jsonify({
            'conversations': conversations_with_preview,
            'total': len(conversations_with_preview)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user conversations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@conversation_bp.route('/', methods=['GET'])
@token_required
def list_user_conversations():
    """Get all conversations for the current user (alternative endpoint)."""
    return get_user_conversations()

@conversation_bp.route('/start', methods=['POST'])
@token_required
def start_conversation():
    """
    Start a new conversation.
    
    Expected JSON:
    {
        "initial_message": "Hello, I'm feeling anxious today",
        "conversation_type": "support"
    }
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'initial_message' not in data:
            return jsonify({'error': 'Initial message is required'}), 400
        
        initial_message = data.get('initial_message')
        conversation_type = data.get('conversation_type', 'general')
        
        # Create new conversation
        conversation_id = f"conv_{datetime.utcnow().timestamp()}_{user_id}"
        
        # Initialize conversation
        mock_conversations[conversation_id] = {
            'id': conversation_id,
            'user_id': user_id,
            'type': conversation_type,
            'created_at': datetime.utcnow().isoformat(),
            'last_message_at': datetime.utcnow().isoformat(),
            'message_count': 0
        }
        
        # Initialize messages list
        mock_messages[conversation_id] = []
        
        # Process the initial message
        user_message = {
            'id': f"msg_{len(mock_messages[conversation_id])}",
            'role': 'user',
            'content': initial_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        mock_messages[conversation_id].append(user_message)
        
        # Generate AI response
        if HAS_LLM_SERVICE:
            try:
                # Use LLM service for response
                ai_response = _generate_mock_response(initial_message)  # Fallback for now
            except Exception as e:
                logger.error(f"LLM service error: {str(e)}")
                ai_response = _generate_mock_response(initial_message)
        else:
            ai_response = _generate_mock_response(initial_message)
        
        # Store AI response
        ai_message = {
            'id': f"msg_{len(mock_messages[conversation_id])}",
            'role': 'assistant',
            'content': ai_response['text'],
            'timestamp': datetime.utcnow().isoformat()
        }
        mock_messages[conversation_id].append(ai_message)
        
        # Update conversation metadata
        mock_conversations[conversation_id]['message_count'] = len(mock_messages[conversation_id])
        mock_conversations[conversation_id]['last_message_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Started new conversation {conversation_id} for user {user_id}")
        
        return jsonify({
            'conversation_id': conversation_id,
            'ai_response': ai_message,
            'status': 'success'
        }), 201
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@conversation_bp.route('/<conversation_id>/messages', methods=['GET', 'POST'])
@token_required
def conversation_messages(conversation_id):
    """
    Handle messages in a conversation - GET to retrieve messages, POST to send new message.
    """
    user_id = request.current_user_id
    
    # Check if conversation exists and belongs to user
    if conversation_id not in mock_conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    
    conversation = mock_conversations[conversation_id]
    if conversation['user_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if request.method == 'GET':
        try:
            messages = mock_messages.get(conversation_id, [])
            
            return jsonify({
                'conversation_id': conversation_id,
                'messages': messages,
                'total_messages': len(messages)
            }), 200
            
        except Exception as e:
            logger.error(f"Error retrieving messages: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data or 'message' not in data:
                return jsonify({'error': 'Message is required'}), 400
            
            message_content = data.get('message')
            message_type = data.get('message_type', 'user')
            
            # Store user message
            user_message = {
                'id': f"msg_{len(mock_messages[conversation_id])}",
                'role': 'user',
                'content': message_content,
                'type': message_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            mock_messages[conversation_id].append(user_message)
            
            # Generate AI response
            if HAS_LLM_SERVICE:
                try:
                    ai_response = _generate_mock_response(message_content)  # Fallback for now
                except Exception as e:
                    logger.error(f"LLM service error: {str(e)}")
                    ai_response = _generate_mock_response(message_content)
            else:
                ai_response = _generate_mock_response(message_content)
            
            # Store AI response
            ai_message = {
                'id': f"msg_{len(mock_messages[conversation_id])}",
                'role': 'assistant',
                'content': ai_response['text'],
                'timestamp': datetime.utcnow().isoformat()
            }
            mock_messages[conversation_id].append(ai_message)
            
            # Update conversation metadata
            mock_conversations[conversation_id]['message_count'] = len(mock_messages[conversation_id])
            mock_conversations[conversation_id]['last_message_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Message sent in conversation {conversation_id} for user {user_id}")
            
            return jsonify({
                'message_id': user_message['id'],
                'ai_response': ai_message,
                'status': 'success'
            }), 201
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

def _generate_mock_response(message_content):
    """Generate a mock AI response for testing."""
    message_lower = message_content.lower()
    
    # Crisis detection
    crisis_keywords = ['suicide', 'kill myself', 'end my life', 'want to die', 'hurt myself', 'self harm']
    is_crisis = any(keyword in message_lower for keyword in crisis_keywords)
    
    if is_crisis:
        return {
            'text': "I'm really concerned about what you're sharing. Please consider reaching out to a crisis hotline: 988 (US). Your safety is important.",
            'crisis_level': 'high',
            'confidence': 0.9,
            'suggested_actions': ['Contact crisis hotline: 988', 'Reach out to someone you trust'],
            'conversation_tags': ['crisis', 'safety_concern']
        }
    
    # Check for anxiety
    if any(word in message_lower for word in ['anxious', 'anxiety', 'worried']):
        return {
            'text': "I understand you're feeling anxious. Can you tell me more about what's causing these feelings?",
            'crisis_level': 'none',
            'confidence': 0.8,
            'suggested_actions': ['Practice deep breathing', 'Try grounding techniques'],
            'conversation_tags': ['anxiety', 'support']
        }
    
    # Check for sadness
    if any(word in message_lower for word in ['sad', 'depressed', 'down']):
        return {
            'text': "I hear that you're feeling sad. Your feelings are valid. Would you like to share what's on your mind?",
            'crisis_level': 'none',
            'confidence': 0.8,
            'suggested_actions': ['Self-care activity', 'Reach out to a friend'],
            'conversation_tags': ['sadness', 'emotional_support']
        }
    
    # Default response
    return {
        'text': "Thank you for sharing. I'm here to listen and support you. How are you feeling today?",
        'crisis_level': 'none',
        'confidence': 0.6,
        'suggested_actions': ['Continue sharing', 'Take your time'],
        'conversation_tags': ['general_support']
    }

def _generate_crisis_response(assessment):
    """Generate appropriate crisis response based on assessment."""
    crisis_level = assessment.crisis_level
    
    if crisis_level == CrisisLevel.CRITICAL:
        return (
            "I'm very concerned about what you're sharing. Your safety is the top priority right now. "
            "Please contact emergency services (911) immediately if you're in immediate danger, or call "
            "the 988 Suicide & Crisis Lifeline. You don't have to go through this alone - help is available."
        )
    elif crisis_level == CrisisLevel.HIGH:
        return (
            "I'm really concerned about you. What you're experiencing sounds very difficult. "
            "Please consider reaching out to the 988 Suicide & Crisis Lifeline (call or text 988) "
            "or contact a trusted person right away. Your safety and wellbeing matter."
        )
    elif crisis_level == CrisisLevel.MEDIUM:
        return (
            "I hear that you're going through a difficult time. It takes courage to share these feelings. "
            "Consider reaching out to a mental health professional or using the Crisis Text Line "
            "(text HOME to 741741). You deserve support during this challenging time."
        )
    elif crisis_level == CrisisLevel.LOW:
        return (
            "Thank you for sharing what you're experiencing. It's important to acknowledge these feelings. "
            "If things feel overwhelming, remember that support is available. Consider talking to someone "
            "you trust or a mental health professional."
        )
    else:
        return (
            "Thank you for sharing. I'm here to listen and support you. How are you feeling today?"
        )

# Export both blueprint names for compatibility
__all__ = ['conversation_bp', 'bp'] 