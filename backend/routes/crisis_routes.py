"""
Mental Wellness Coach - Crisis Detection & Safety Routes

API endpoints for crisis detection, risk assessment, escalation protocols,
and safety resource management.
"""

import asyncio
import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
from datetime import datetime

# Import our custom auth system
from .auth_routes import token_required

from services.crisis_service import crisis_service, CrisisLevel, RiskFactor

logger = logging.getLogger(__name__)

# Create blueprint for crisis routes
crisis_bp = Blueprint('crisis', __name__)

@crisis_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_crisis_content():
    """
    Analyze content for crisis indicators (alias for assess).
    
    Expected JSON payload:
    {
        "content": "User message or content to analyze"
    }
    
    Returns:
        JSON response with risk assessment
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                "error": "Content is required for analysis"
            }), 400
        
        content = data.get('content', '')
        
        if not content.strip():
            return jsonify({
                "error": "Content cannot be empty"
            }), 400
        
        # Perform crisis risk assessment
        assessment = asyncio.run(crisis_service.assess_crisis_risk(
            user_id=str(user_id),
            content=content,
            trigger_source="manual_analysis",
            additional_context={}
        ))
        
        # Format response to match test expectations
        response_data = {
            "risk_level": assessment.crisis_level.value,
            "confidence": round(assessment.confidence, 3),
            "detected_factors": [factor.value for factor in assessment.detected_factors],
            "recommended_interventions": assessment.recommended_interventions,
            "safety_resources": assessment.safety_resources,
            "escalation_needed": assessment.escalation_needed,
            "assessment_timestamp": assessment.assessment_timestamp.isoformat()
        }
        
        # Log significant assessments
        if assessment.crisis_level != CrisisLevel.NONE:
            logger.warning(f"Crisis assessment for user {user_id}: {assessment.crisis_level.value}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in crisis analysis: {str(e)}")
        return jsonify({
            "error": f"Crisis analysis failed: {str(e)}"
        }), 500

@crisis_bp.route('/assess', methods=['POST'])
@token_required
def assess_crisis_risk():
    """
    Assess crisis risk from user content.
    
    Expected JSON payload:
    {
        "content": "User message or content to analyze",
        "source": "chat|mood|journal|other",
        "context": {
            "mood_score": 3,
            "recent_entries": [...],
            "conversation_history": [...]
        }
    }
    
    Returns:
        JSON response with comprehensive risk assessment
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                "status": "error",
                "message": "Content is required for crisis assessment"
            }), 400
        
        content = data.get('content', '')
        source = data.get('source', 'chat')
        context = data.get('context', {})
        
        if not content.strip():
            return jsonify({
                "status": "error",
                "message": "Content cannot be empty"
            }), 400
        
        # Perform crisis risk assessment
        assessment = asyncio.run(crisis_service.assess_crisis_risk(
            user_id=str(user_id),
            content=content,
            trigger_source=source,
            additional_context=context
        ))
        
        # Format response
        response_data = {
            "risk_assessment": {
                "crisis_level": assessment.crisis_level.value,
                "risk_score": round(assessment.risk_score, 3),
                "confidence": round(assessment.confidence, 3),
                "immediate_action_required": assessment.immediate_action_required,
                "escalation_needed": assessment.escalation_needed
            },
            "detected_factors": [factor.value for factor in assessment.detected_factors],
            "interventions": assessment.recommended_interventions,
            "safety_resources": assessment.safety_resources,
            "assessment_timestamp": assessment.assessment_timestamp.isoformat()
        }
        
        # Log significant assessments
        if assessment.crisis_level != CrisisLevel.NONE:
            logger.warning(f"Crisis assessment for user {user_id}: {assessment.crisis_level.value}")
        
        return jsonify({
            "status": "success",
            "data": response_data,
            "message": "Crisis assessment completed successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in crisis assessment: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Crisis assessment failed: {str(e)}"
        }), 500

@crisis_bp.route('/escalate', methods=['POST'])
@token_required
def escalate_crisis():
    """
    Escalate a crisis to appropriate professionals.
    
    Expected JSON payload:
    {
        "crisis_level": "high|critical",
        "trigger_content": "Content that triggered escalation",
        "escalation_type": "professional|emergency|family",
        "user_consent": true,
        "additional_info": {
            "location": "City, State",
            "emergency_contact": "contact_id"
        }
    }
    
    Returns:
        JSON response with escalation actions taken
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request data is required"
            }), 400
        
        crisis_level_str = data.get('crisis_level', 'medium')
        trigger_content = data.get('trigger_content', '')
        escalation_type = data.get('escalation_type', 'professional')
        user_consent = data.get('user_consent', False)
        
        # Validate crisis level
        try:
            crisis_level = CrisisLevel(crisis_level_str.lower())
        except ValueError:
            return jsonify({
                "status": "error",
                "message": f"Invalid crisis level: {crisis_level_str}"
            }), 400
        
        # Check user consent for non-critical situations
        if crisis_level != CrisisLevel.CRITICAL and not user_consent:
            return jsonify({
                "status": "error",
                "message": "User consent required for escalation"
            }), 400
        
        # Create assessment for escalation (simplified)
        from services.crisis_service import RiskAssessment
        assessment = RiskAssessment(
            user_id=str(user_id),
            trigger_content=trigger_content,
            crisis_level=crisis_level,
            risk_score=0.8 if crisis_level == CrisisLevel.HIGH else 0.9,
            detected_factors=[],
            confidence=0.9,
            immediate_action_required=True,
            recommended_interventions=[],
            safety_resources=[],
            escalation_needed=True
        )
        
        # Perform escalation
        escalation_result = asyncio.run(crisis_service.escalate_crisis(
            assessment=assessment,
            escalation_type=escalation_type
        ))
        
        return jsonify({
            "status": "success",
            "data": escalation_result,
            "message": "Crisis escalation initiated successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in crisis escalation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Crisis escalation failed: {str(e)}"
        }), 500

@crisis_bp.route('/resources', methods=['GET'])
@token_required
def get_safety_resources():
    """
    Get available safety resources.
    
    Query parameters:
    - crisis_level: Filter by crisis level (optional)
    - country: Filter by country code (optional)
    - type: Filter by resource type (hotline, website, text, etc.)
    - emergency_only: Show only emergency resources (true/false)
    
    Returns:
        JSON response with available safety resources
    """
    try:
        # Get query parameters
        crisis_level_str = request.args.get('crisis_level')
        country = request.args.get('country', 'US')
        resource_type = request.args.get('type')
        emergency_only = request.args.get('emergency_only', 'false').lower() == 'true'
        
        # Mock safety resources data instead of using crisis_service
        all_resources_data = [
            {
                "name": "National Suicide Prevention Lifeline",
                "type": "hotline",
                "contact": "988",
                "availability": "24/7",
                "description": "Free and confidential support for people in distress",
                "country_code": "US",
                "language": "English",
                "is_emergency": True
            },
            {
                "name": "Crisis Text Line",
                "type": "text",
                "contact": "Text HOME to 741741",
                "availability": "24/7",
                "description": "Free, 24/7 crisis support via text message",
                "country_code": "US",
                "language": "English",
                "is_emergency": True
            },
            {
                "name": "SAMHSA National Helpline",
                "type": "hotline",
                "contact": "1-800-662-4357",
                "availability": "24/7",
                "description": "Treatment referral and information service",
                "country_code": "US",
                "language": "English",
                "is_emergency": False
            },
            {
                "name": "Mental Health America",
                "type": "website",
                "contact": "https://www.mhanational.org",
                "availability": "Always",
                "description": "Mental health resources and advocacy",
                "country_code": "US",
                "language": "English",
                "is_emergency": False
            }
        ]
        
        # Apply filters
        filtered_resources = []
        for resource in all_resources_data:
            # Country filter
            if resource["country_code"] != country:
                continue
            
            # Emergency filter
            if emergency_only and not resource["is_emergency"]:
                continue
            
            # Type filter
            if resource_type and resource["type"] != resource_type:
                continue
            
            filtered_resources.append(resource)
        
        # Sort by emergency status and name
        filtered_resources.sort(key=lambda x: (not x["is_emergency"], x["name"]))
        
        return jsonify({
            "resources": filtered_resources,
            "total_count": len(filtered_resources),
            "filters_applied": {
                "country": country,
                "type": resource_type,
                "emergency_only": emergency_only
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting safety resources: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get safety resources: {str(e)}"
        }), 500

@crisis_bp.route('/history', methods=['GET'])
@token_required
def get_crisis_history():
    """
    Get user's crisis event history.
    
    Query parameters:
    - days: Number of days to look back (default: 30)
    - limit: Maximum number of events (default: 50)
    
    Returns:
        JSON response with crisis event history
    """
    try:
        user_id = request.current_user_id
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 50))
        
        # Validate parameters
        if days < 1 or days > 365:
            return jsonify({
                "status": "error",
                "message": "Days must be between 1 and 365"
            }), 400
        
        if limit < 1 or limit > 100:
            return jsonify({
                "status": "error",
                "message": "Limit must be between 1 and 100"
            }), 400
        
        # Get crisis history
        crisis_events = asyncio.run(crisis_service.get_user_crisis_history(
            user_id=str(user_id),
            days=days
        ))
        
        # Apply limit
        crisis_events = crisis_events[:limit]
        
        # Calculate summary statistics
        if crisis_events:
            crisis_levels = [event.get('crisis_level', 'none') for event in crisis_events]
            level_counts = {}
            for level in crisis_levels:
                level_counts[level] = level_counts.get(level, 0) + 1
        else:
            level_counts = {}
        
        return jsonify({
            "status": "success",
            "data": {
                "events": crisis_events,
                "total_events": len(crisis_events),
                "period_days": days,
                "level_summary": level_counts,
                "recent_escalations": sum(1 for event in crisis_events if event.get('professional_notified', False))
            },
            "message": "Crisis history retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting crisis history: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get crisis history: {str(e)}"
        }), 500

@crisis_bp.route('/intervention-status/<int:event_id>', methods=['PUT'])
@token_required
def update_intervention_status(event_id: int):
    """
    Update intervention status for a crisis event.
    
    Expected JSON payload:
    {
        "user_response": "User's response to intervention",
        "resolved": true,
        "follow_up_needed": false,
        "notes": "Additional notes from user or professional"
    }
    
    Returns:
        JSON response with update confirmation
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Update data is required"
            }), 400
        
        # Import here to avoid circular imports
        from models import CrisisEvent
        from database import db
        
        # Find the crisis event
        crisis_event = CrisisEvent.query.filter_by(
            id=event_id,
            user_id=int(user_id)
        ).first()
        
        if not crisis_event:
            return jsonify({
                "status": "error",
                "message": "Crisis event not found"
            }), 404
        
        # Update crisis event
        if 'user_response' in data:
            crisis_event.user_response = data['user_response']
        
        if data.get('resolved', False):
            crisis_event.resolved_at = datetime.utcnow()
        
        # Update intervention notes
        if 'notes' in data:
            import json
            current_intervention = crisis_event.intervention_taken or "[]"
            interventions = json.loads(current_intervention)
            interventions.append(f"User update: {data['notes']}")
            crisis_event.intervention_taken = json.dumps(interventions)
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "data": {
                "event_id": event_id,
                "updated_at": datetime.utcnow().isoformat(),
                "resolved": crisis_event.resolved_at is not None
            },
            "message": "Intervention status updated successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating intervention status: {str(e)}")
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Failed to update intervention status: {str(e)}"
        }), 500

@crisis_bp.route('/safety-plan', methods=['POST'])
@token_required
def create_safety_plan():
    """
    Create or update a user's safety plan.
    
    Expected JSON payload:
    {
        "warning_signs": ["List of personal warning signs"],
        "coping_strategies": ["List of coping strategies"],
        "support_people": [
            {
                "name": "Contact name",
                "phone": "Phone number",
                "relationship": "Relationship to user"
            }
        ],
        "professional_contacts": [
            {
                "name": "Professional name",
                "phone": "Phone number",
                "type": "therapist|psychiatrist|counselor"
            }
        ],
        "environment_safety": ["Steps to make environment safe"],
        "reasons_to_live": ["Personal reasons for living"]
    }
    
    Returns:
        JSON response with safety plan confirmation
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Safety plan data is required"
            }), 400
        
        # Validate required fields
        required_fields = ['warning_signs', 'coping_strategies', 'support_people']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Required field missing: {field}"
                }), 400
        
        # TODO: Store safety plan in database
        # For now, we'll just validate and return success
        
        safety_plan = {
            "user_id": user_id,
            "warning_signs": data.get('warning_signs', []),
            "coping_strategies": data.get('coping_strategies', []),
            "support_people": data.get('support_people', []),
            "professional_contacts": data.get('professional_contacts', []),
            "environment_safety": data.get('environment_safety', []),
            "reasons_to_live": data.get('reasons_to_live', []),
            "created_at": datetime.utcnow().isoformat(),
            "plan_id": f"sp_{user_id}_{int(datetime.utcnow().timestamp())}"
        }
        
        logger.info(f"Safety plan created for user {user_id}")
        
        return jsonify({
            "status": "success",
            "data": {
                "plan_id": safety_plan["plan_id"],
                "created_at": safety_plan["created_at"],
                "sections_completed": len([k for k, v in safety_plan.items() if v and k not in ['user_id', 'created_at', 'plan_id']])
            },
            "message": "Safety plan created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating safety plan: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to create safety plan: {str(e)}"
        }), 500

@crisis_bp.route('/emergency-contacts', methods=['GET'])
@token_required
def get_emergency_contacts():
    """
    Get user's emergency contacts.
    
    Returns:
        JSON response with emergency contacts
    """
    try:
        user_id = request.current_user_id
        
        # TODO: Implement emergency contacts in database
        # For now, return placeholder data
        
        emergency_contacts = [
            {
                "id": "ec_001",
                "name": "National Suicide Prevention Lifeline",
                "phone": "988",
                "relationship": "crisis_hotline",
                "priority": 1,
                "is_active": True
            },
            {
                "id": "ec_002",
                "name": "Crisis Text Line",
                "phone": "741741",
                "relationship": "crisis_text",
                "priority": 2,
                "is_active": True
            },
            {
                "id": "ec_003",
                "name": "Emergency Services",
                "phone": "911",
                "relationship": "emergency",
                "priority": 3,
                "is_active": True
            }
        ]
        
        return jsonify({
            "status": "success",
            "contacts": emergency_contacts,
            "total_contacts": len(emergency_contacts),
            "active_contacts": len([c for c in emergency_contacts if c["is_active"]]),
            "message": "Emergency contacts retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting emergency contacts: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get emergency contacts: {str(e)}"
        }), 500

@crisis_bp.route('/risk-factors', methods=['GET'])
@token_required
def get_risk_factors():
    """
    Get information about crisis risk factors.
    
    Returns:
        JSON response with risk factor information
    """
    try:
        risk_factors = []
        
        for factor in RiskFactor:
            factor_info = {
                "name": factor.value,
                "display_name": factor.value.replace('_', ' ').title(),
                "description": _get_risk_factor_description(factor),
                "severity": _get_risk_factor_severity(factor),
                "warning_signs": _get_risk_factor_warning_signs(factor)
            }
            risk_factors.append(factor_info)
        
        return jsonify({
            "status": "success",
            "data": {
                "risk_factors": risk_factors,
                "total_factors": len(risk_factors)
            },
            "message": "Risk factors retrieved successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting risk factors: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get risk factors: {str(e)}"
        }), 500

def _get_risk_factor_description(factor: RiskFactor) -> str:
    """Get description for a risk factor."""
    descriptions = {
        RiskFactor.SUICIDAL_IDEATION: "Thoughts of suicide or ending one's life",
        RiskFactor.SELF_HARM: "Intentional self-inflicted injury or harm",
        RiskFactor.SUBSTANCE_ABUSE: "Problematic use of drugs or alcohol",
        RiskFactor.ISOLATION: "Social withdrawal and lack of support connections",
        RiskFactor.HOPELESSNESS: "Feelings that things will never improve",
        RiskFactor.DEPRESSION: "Persistent sadness and loss of interest",
        RiskFactor.ANXIETY: "Excessive worry and fear",
        RiskFactor.TRAUMA: "Impact of traumatic experiences",
        RiskFactor.RELATIONSHIP_ISSUES: "Problems in personal relationships",
        RiskFactor.FINANCIAL_STRESS: "Stress related to financial problems"
    }
    return descriptions.get(factor, "Mental health risk factor")

def _get_risk_factor_severity(factor: RiskFactor) -> str:
    """Get severity level for a risk factor."""
    high_severity = [RiskFactor.SUICIDAL_IDEATION, RiskFactor.SELF_HARM]
    medium_severity = [RiskFactor.HOPELESSNESS, RiskFactor.DEPRESSION, RiskFactor.TRAUMA]
    
    if factor in high_severity:
        return "high"
    elif factor in medium_severity:
        return "medium"
    else:
        return "low"

def _get_risk_factor_warning_signs(factor: RiskFactor) -> list:
    """Get warning signs for a risk factor."""
    warning_signs = {
        RiskFactor.SUICIDAL_IDEATION: [
            "Talking about wanting to die",
            "Looking for ways to hurt oneself",
            "Talking about feeling hopeless",
            "Giving away prized possessions"
        ],
        RiskFactor.SELF_HARM: [
            "Unexplained cuts or bruises",
            "Wearing long sleeves in warm weather",
            "Secretive behavior",
            "Talking about self-punishment"
        ],
        RiskFactor.DEPRESSION: [
            "Persistent sadness",
            "Loss of interest in activities",
            "Changes in sleep or appetite",
            "Feelings of worthlessness"
        ]
    }
    return warning_signs.get(factor, ["Consult mental health professional for guidance"]) 