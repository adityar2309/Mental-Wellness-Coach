"""
Mental Wellness Coach - Mindfulness Routes

Flask routes for mindfulness and meditation session management.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from werkzeug.exceptions import BadRequest

from database import db
from models import User, MindfulnessSession

# Create Blueprint for mindfulness routes
mindfulness_bp = Blueprint('mindfulness', __name__, url_prefix='/api/mindfulness')

def token_required(f):
    """Decorator to require JWT token for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated_function

@mindfulness_bp.route('/sessions', methods=['GET'])
@token_required
def get_mindfulness_sessions(current_user):
    """
    Get all mindfulness sessions for the current user.
    
    Query parameters:
    - session_type: Filter by session type
    - completed: Filter by completion status (true/false)
    - limit: Number of sessions to return (default: 50)
    - offset: Number of sessions to skip (default: 0)
    """
    try:
        # Get query parameters
        session_type = request.args.get('session_type')
        completed = request.args.get('completed')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = MindfulnessSession.query.filter_by(user_id=current_user.id)
        
        if session_type:
            query = query.filter_by(session_type=session_type)
        
        if completed is not None:
            completed_bool = completed.lower() == 'true'
            query = query.filter_by(completed=completed_bool)
        
        # Apply pagination and ordering
        sessions = query.order_by(MindfulnessSession.created_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions],
            'total': query.count()
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid limit or offset parameter'}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting mindfulness sessions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mindfulness_bp.route('/sessions', methods=['POST'])
@token_required
def create_mindfulness_session(current_user):
    """
    Create a new mindfulness session.
    
    Expected JSON body:
    {
        "session_type": "breathing|meditation|body_scan|progressive_relaxation",
        "title": "Session title",
        "description": "Optional description",
        "duration_minutes": 10,
        "mood_before": 5,
        "stress_before": 7
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['session_type', 'title', 'duration_minutes']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate session type
        valid_types = ['breathing', 'meditation', 'body_scan', 'progressive_relaxation']
        if data['session_type'] not in valid_types:
            return jsonify({'error': f'Invalid session_type. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Validate duration
        if not isinstance(data['duration_minutes'], int) or data['duration_minutes'] <= 0:
            return jsonify({'error': 'duration_minutes must be a positive integer'}), 400
        
        # Create new session
        session = MindfulnessSession(
            user_id=current_user.id,
            session_type=data['session_type'],
            title=data['title'],
            description=data.get('description'),
            duration_minutes=data['duration_minutes'],
            mood_before=data.get('mood_before'),
            stress_before=data.get('stress_before')
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Mindfulness session created successfully',
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating mindfulness session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mindfulness_bp.route('/sessions/<int:session_id>', methods=['GET'])
@token_required
def get_mindfulness_session(current_user, session_id):
    """Get a specific mindfulness session by ID."""
    try:
        session = MindfulnessSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({'session': session.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting mindfulness session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mindfulness_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@token_required
def update_mindfulness_session(current_user, session_id):
    """
    Update a mindfulness session (typically used to complete a session).
    
    Expected JSON body:
    {
        "completed": true,
        "completed_duration_minutes": 8,
        "mood_after": 7,
        "stress_after": 4,
        "effectiveness_rating": 8,
        "notes": "Session notes",
        "session_data": {"breathing_rate": 6}
    }
    """
    try:
        session = MindfulnessSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'completed' in data:
            session.completed = data['completed']
            if data['completed']:
                session.completed_at = datetime.utcnow()
        
        if 'completed_duration_minutes' in data:
            session.completed_duration_minutes = data['completed_duration_minutes']
        
        if 'mood_after' in data:
            session.mood_after = data['mood_after']
        
        if 'stress_after' in data:
            session.stress_after = data['stress_after']
        
        if 'effectiveness_rating' in data:
            if not (1 <= data['effectiveness_rating'] <= 10):
                return jsonify({'error': 'effectiveness_rating must be between 1 and 10'}), 400
            session.effectiveness_rating = data['effectiveness_rating']
        
        if 'notes' in data:
            session.notes = data['notes']
        
        if 'session_data' in data:
            session.set_session_data(data['session_data'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Session updated successfully',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating mindfulness session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mindfulness_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@token_required
def delete_mindfulness_session(current_user, session_id):
    """Delete a mindfulness session."""
    try:
        session = MindfulnessSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'message': 'Session deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting mindfulness session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mindfulness_bp.route('/templates', methods=['GET'])
@token_required
def get_session_templates(current_user):
    """
    Get predefined mindfulness session templates.
    
    Returns templates organized by session type with suggested durations and descriptions.
    """
    templates = {
        "breathing": [
            {
                "title": "4-7-8 Breathing",
                "description": "A calming breathing technique where you inhale for 4 counts, hold for 7, and exhale for 8.",
                "duration_minutes": 5,
                "instructions": "Inhale through your nose for 4 counts, hold your breath for 7 counts, then exhale through your mouth for 8 counts."
            },
            {
                "title": "Box Breathing",
                "description": "A simple technique used by Navy SEALs to reduce stress and improve focus.",
                "duration_minutes": 10,
                "instructions": "Breathe in for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat this cycle."
            },
            {
                "title": "Deep Belly Breathing",
                "description": "Focus on breathing deeply into your diaphragm to activate relaxation response.",
                "duration_minutes": 8,
                "instructions": "Place one hand on chest, one on belly. Breathe so only the belly hand moves."
            }
        ],
        "meditation": [
            {
                "title": "Mindfulness Meditation",
                "description": "Focus on the present moment and observe thoughts without judgment.",
                "duration_minutes": 15,
                "instructions": "Sit comfortably, focus on your breath, and gently return attention when mind wanders."
            },
            {
                "title": "Loving-Kindness Meditation",
                "description": "Cultivate feelings of love and compassion for yourself and others.",
                "duration_minutes": 20,
                "instructions": "Start with loving yourself, then extend those feelings to loved ones, neutral people, and all beings."
            },
            {
                "title": "Quick Centering",
                "description": "A brief meditation to center yourself during busy days.",
                "duration_minutes": 5,
                "instructions": "Take 3 deep breaths, scan your body, and set an intention for the day."
            }
        ],
        "body_scan": [
            {
                "title": "Progressive Body Scan",
                "description": "Systematically relax each part of your body from head to toe.",
                "duration_minutes": 20,
                "instructions": "Start at the top of your head and slowly move attention down through each body part."
            },
            {
                "title": "Quick Body Check",
                "description": "A brief scan to identify and release tension.",
                "duration_minutes": 8,
                "instructions": "Notice where you hold tension and consciously relax those areas."
            }
        ],
        "progressive_relaxation": [
            {
                "title": "Muscle Tension Release",
                "description": "Tense and release each muscle group to achieve deep relaxation.",
                "duration_minutes": 15,
                "instructions": "Tense each muscle group for 5 seconds, then release and notice the relaxation."
            },
            {
                "title": "Guided Imagery",
                "description": "Use visualization to create a peaceful mental space.",
                "duration_minutes": 12,
                "instructions": "Imagine a peaceful place in detail, engaging all your senses."
            }
        ]
    }
    
    return jsonify({'templates': templates}), 200

@mindfulness_bp.route('/analytics', methods=['GET'])
@token_required
def get_mindfulness_analytics(current_user):
    """
    Get analytics for user's mindfulness practice.
    
    Query parameters:
    - days: Number of days to analyze (default: 30)
    """
    try:
        days = int(request.args.get('days', 30))
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sessions in the specified period
        sessions = MindfulnessSession.query.filter(
            MindfulnessSession.user_id == current_user.id,
            MindfulnessSession.created_at >= cutoff_date
        ).all()
        
        # Calculate analytics
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.completed])
        total_minutes = sum(s.completed_duration_minutes or 0 for s in sessions if s.completed)
        
        # Average ratings (only for completed sessions with ratings)
        effectiveness_ratings = [s.effectiveness_rating for s in sessions if s.effectiveness_rating]
        avg_effectiveness = sum(effectiveness_ratings) / len(effectiveness_ratings) if effectiveness_ratings else None
        
        # Mood and stress improvements
        mood_improvements = []
        stress_improvements = []
        
        for session in sessions:
            if session.mood_before and session.mood_after:
                mood_improvements.append(session.mood_after - session.mood_before)
            if session.stress_before and session.stress_after:
                stress_improvements.append(session.stress_before - session.stress_after)
        
        avg_mood_improvement = sum(mood_improvements) / len(mood_improvements) if mood_improvements else None
        avg_stress_reduction = sum(stress_improvements) / len(stress_improvements) if stress_improvements else None
        
        # Session type breakdown
        session_types = {}
        for session in sessions:
            session_types[session.session_type] = session_types.get(session.session_type, 0) + 1
        
        analytics = {
            'period_days': days,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'completion_rate': completed_sessions / total_sessions if total_sessions > 0 else 0,
            'total_minutes': total_minutes,
            'average_effectiveness': avg_effectiveness,
            'average_mood_improvement': avg_mood_improvement,
            'average_stress_reduction': avg_stress_reduction,
            'session_types': session_types,
            'streak_days': calculate_mindfulness_streak(current_user.id)
        }
        
        return jsonify({'analytics': analytics}), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid days parameter'}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting mindfulness analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def calculate_mindfulness_streak(user_id):
    """Calculate the current mindfulness practice streak in days."""
    try:
        # Get all sessions ordered by date (most recent first)
        sessions = MindfulnessSession.query.filter_by(
            user_id=user_id,
            completed=True
        ).order_by(MindfulnessSession.completed_at.desc()).all()
        
        if not sessions:
            return 0
        
        # Check for consecutive days
        streak = 1
        current_date = sessions[0].completed_at.date()
        
        for i in range(1, len(sessions)):
            session_date = sessions[i].completed_at.date()
            expected_date = current_date - timedelta(days=1)
            
            if session_date == expected_date:
                streak += 1
                current_date = session_date
            elif session_date < expected_date:
                # Gap in the streak
                break
            # If session_date == current_date, it's the same day, continue
        
        # Check if the streak is current (last session was today or yesterday)
        today = datetime.utcnow().date()
        if current_date < today - timedelta(days=1):
            streak = 0  # Streak is broken
        
        return streak
        
    except Exception:
        return 0

# Error handlers
@mindfulness_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({'error': 'Bad request'}), 400

@mindfulness_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({'error': 'Resource not found'}), 404

@mindfulness_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({'error': 'Internal server error'}), 500 