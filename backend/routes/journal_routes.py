"""
Mental Wellness Coach - Journal Routes

Flask blueprint for journal entry management and AI-powered journaling features.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import logging
import asyncio
from typing import Dict, List, Optional

# Import our custom auth system
from .auth_routes import token_required

# Import models
from models import JournalEntry, User, db

# Import LLM service for AI prompts
try:
    from services.llm_service import ASILLMService, create_conversation_context
    llm_service = ASILLMService()
    HAS_LLM_SERVICE = True
except ImportError:
    HAS_LLM_SERVICE = False
    llm_service = None

# Create blueprint
journal_bp = Blueprint('journal', __name__)
logger = logging.getLogger(__name__)

@journal_bp.route('/entries', methods=['GET'])
@token_required
def get_journal_entries():
    """
    Get journal entries for the current user.
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Entries per page (default: 20)
    - start_date: Filter entries from this date (YYYY-MM-DD)
    - end_date: Filter entries to this date (YYYY-MM-DD)
    - search: Search in title and content
    """
    try:
        user_id = request.current_user_id
        
        # Parse query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)  # Max 100 entries per page
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search', '').strip()
        
        # Build query
        query = JournalEntry.query.filter_by(user_id=user_id)
        
        # Date filtering
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(JournalEntry.created_at >= start_date_obj)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(JournalEntry.created_at < end_date_obj)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        # Search filtering
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    JournalEntry.title.ilike(search_term),
                    JournalEntry.content.ilike(search_term)
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(JournalEntry.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        entries = [entry.to_dict() for entry in pagination.items]
        
        return jsonify({
            'status': 'success',
            'data': {
                'entries': entries,
                'pagination': {
                    'page': page,
                    'pages': pagination.pages,
                    'per_page': limit,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            'message': f'Retrieved {len(entries)} journal entries'
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving journal entries: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@journal_bp.route('/entries', methods=['POST'])
@token_required
def create_journal_entry():
    """
    Create a new journal entry.
    
    Expected JSON:
    {
        "title": "Optional title",
        "content": "Journal entry content",
        "mood_score": 7,  // Optional 1-10
        "emotions": ["happy", "grateful"],  // Optional
        "tags": ["work", "personal"],  // Optional
        "is_private": true  // Optional, default true
    }
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Validate optional fields
        title = data.get('title', '').strip()
        mood_score = data.get('mood_score')
        emotions = data.get('emotions', [])
        tags = data.get('tags', [])
        is_private = data.get('is_private', True)
        
        # Validate mood_score if provided
        if mood_score is not None:
            if not isinstance(mood_score, int) or mood_score < 1 or mood_score > 10:
                return jsonify({'error': 'mood_score must be an integer between 1 and 10'}), 400
        
        # Validate emotions and tags are lists
        if not isinstance(emotions, list):
            return jsonify({'error': 'emotions must be a list'}), 400
        if not isinstance(tags, list):
            return jsonify({'error': 'tags must be a list'}), 400
        
        # Create journal entry
        entry = JournalEntry(
            user_id=user_id,
            title=title if title else None,
            content=content,
            mood_score=mood_score,
            is_private=is_private
        )
        
        # Set emotions and tags
        entry.set_emotions(emotions)
        entry.set_tags(tags)
        
        db.session.add(entry)
        db.session.commit()
        
        logger.info(f"Journal entry created for user {user_id}: {entry.id}")
        
        return jsonify({
            'status': 'success',
            'data': entry.to_dict(),
            'message': 'Journal entry created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating journal entry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@journal_bp.route('/entries/<int:entry_id>', methods=['GET'])
@token_required
def get_journal_entry(entry_id):
    """Get a specific journal entry by ID."""
    try:
        user_id = request.current_user_id
        
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return jsonify({'error': 'Journal entry not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': entry.to_dict(),
            'message': 'Journal entry retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving journal entry {entry_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@journal_bp.route('/entries/<int:entry_id>', methods=['PUT'])
@token_required
def update_journal_entry(entry_id):
    """
    Update a journal entry.
    
    Expected JSON: Same as create_journal_entry
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return jsonify({'error': 'Journal entry not found'}), 404
        
        # Update fields
        if 'title' in data:
            entry.title = data['title'].strip() if data['title'] else None
        
        if 'content' in data:
            content = data['content'].strip()
            if not content:
                return jsonify({'error': 'Content is required'}), 400
            entry.content = content
        
        if 'mood_score' in data:
            mood_score = data['mood_score']
            if mood_score is not None:
                if not isinstance(mood_score, int) or mood_score < 1 or mood_score > 10:
                    return jsonify({'error': 'mood_score must be an integer between 1 and 10'}), 400
            entry.mood_score = mood_score
        
        if 'emotions' in data:
            emotions = data['emotions']
            if not isinstance(emotions, list):
                return jsonify({'error': 'emotions must be a list'}), 400
            entry.set_emotions(emotions)
        
        if 'tags' in data:
            tags = data['tags']
            if not isinstance(tags, list):
                return jsonify({'error': 'tags must be a list'}), 400
            entry.set_tags(tags)
        
        if 'is_private' in data:
            entry.is_private = data['is_private']
        
        # Update timestamp
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Journal entry {entry_id} updated for user {user_id}")
        
        return jsonify({
            'status': 'success',
            'data': entry.to_dict(),
            'message': 'Journal entry updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating journal entry {entry_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@journal_bp.route('/entries/<int:entry_id>', methods=['DELETE'])
@token_required
def delete_journal_entry(entry_id):
    """Delete a journal entry."""
    try:
        user_id = request.current_user_id
        
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return jsonify({'error': 'Journal entry not found'}), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        logger.info(f"Journal entry {entry_id} deleted for user {user_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Journal entry deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting journal entry {entry_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@journal_bp.route('/prompts', methods=['GET'])
@token_required
def get_journal_prompts():
    """
    Get AI-generated journal prompts based on user's recent mood and activity.
    
    Query Parameters:
    - count: Number of prompts to generate (default: 3, max: 10)
    - mood: Current mood to tailor prompts (1-10)
    - topic: Specific topic for prompts (e.g., "gratitude", "stress", "growth")
    """
    try:
        user_id = request.current_user_id
        
        count = min(request.args.get('count', 3, type=int), 10)
        mood = request.args.get('mood', type=int)
        topic = request.args.get('topic', '').strip()
        
        # Validate mood if provided
        if mood is not None and (mood < 1 or mood > 10):
            return jsonify({'error': 'mood must be between 1 and 10'}), 400
        
        # For now, use fallback prompts since LLM integration is complex
        # TODO: Implement proper async LLM integration in future version
        prompts = _get_fallback_prompts(count, mood, topic)
        
        return jsonify({
            'status': 'success',
            'data': {
                'prompts': prompts,
                'count': len(prompts)
            },
            'message': f'Generated {len(prompts)} journal prompts'
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating journal prompts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@journal_bp.route('/analytics', methods=['GET'])
@token_required
def get_journal_analytics():
    """
    Get journal analytics and insights for the user.
    
    Query Parameters:
    - start_date: Start date for analytics (YYYY-MM-DD)
    - end_date: End date for analytics (YYYY-MM-DD)
    """
    try:
        user_id = request.current_user_id
        
        # Parse date parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Build query for the date range
        query = JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= start_date,
            JournalEntry.created_at <= end_date + timedelta(days=1)
        )
        
        entries = query.all()
        
        # Calculate analytics
        total_entries = len(entries)
        avg_mood = None
        mood_trend = "stable"
        common_emotions = []
        common_tags = []
        writing_streak = 0
        
        if entries:
            # Calculate average mood
            mood_scores = [entry.mood_score for entry in entries if entry.mood_score]
            if mood_scores:
                avg_mood = round(sum(mood_scores) / len(mood_scores), 1)
                
                # Simple mood trend calculation
                if len(mood_scores) >= 2:
                    recent_avg = sum(mood_scores[-3:]) / len(mood_scores[-3:])
                    earlier_avg = sum(mood_scores[:-3]) / len(mood_scores[:-3]) if len(mood_scores) > 3 else recent_avg
                    
                    if recent_avg > earlier_avg + 0.5:
                        mood_trend = "improving"
                    elif recent_avg < earlier_avg - 0.5:
                        mood_trend = "declining"
            
            # Analyze emotions and tags
            all_emotions = []
            all_tags = []
            
            for entry in entries:
                all_emotions.extend(entry.get_emotions())
                all_tags.extend(entry.get_tags())
            
            # Get most common emotions and tags
            if all_emotions:
                emotion_counts = {}
                for emotion in all_emotions:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                common_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                common_emotions = [{'emotion': emotion, 'count': count} for emotion, count in common_emotions]
            
            if all_tags:
                tag_counts = {}
                for tag in all_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                common_tags = [{'tag': tag, 'count': count} for tag, count in common_tags]
        
        # Calculate writing streak (consecutive days with entries)
        # This is a simplified calculation - a more sophisticated version would
        # check actual consecutive days
        recent_entries = JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= datetime.utcnow() - timedelta(days=30)
        ).order_by(JournalEntry.created_at.desc()).all()
        
        if recent_entries:
            # Group by date and count consecutive days
            entry_dates = set()
            for entry in recent_entries:
                entry_dates.add(entry.created_at.date())
            
            current_date = datetime.utcnow().date()
            while current_date in entry_dates:
                writing_streak += 1
                current_date -= timedelta(days=1)
        
        analytics = {
            'total_entries': total_entries,
            'average_mood': avg_mood,
            'mood_trend': mood_trend,
            'common_emotions': common_emotions,
            'common_tags': common_tags,
            'writing_streak': writing_streak,
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': analytics,
            'message': 'Journal analytics retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating journal analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Helper functions

def _get_mood_context(mood_score):
    """Get descriptive context for mood score."""
    if mood_score >= 8:
        return "very positive"
    elif mood_score >= 6:
        return "generally positive"
    elif mood_score >= 4:
        return "neutral"
    elif mood_score >= 2:
        return "somewhat low"
    else:
        return "very low"

def _parse_prompts_from_response(response_text, count):
    """Parse AI response into individual prompts."""
    try:
        # Split by common prompt separators
        lines = response_text.split('\n')
        prompts = []
        
        for line in lines:
            line = line.strip()
            # Remove numbering and bullet points
            line = line.lstrip('0123456789.-• ')
            if len(line) > 10 and '?' in line:  # Basic filter for prompt-like text
                prompts.append(line)
                if len(prompts) >= count:
                    break
        
        # If we didn't get enough prompts, pad with fallback
        while len(prompts) < count:
            prompts.extend(_get_fallback_prompts(count - len(prompts)))
            break
        
        return prompts[:count]
        
    except Exception:
        return _get_fallback_prompts(count)

def _get_fallback_prompts(count, mood=None, topic=None):
    """Get fallback prompts when AI generation fails."""
    all_prompts = [
        "What are three things you're grateful for today, and why do they matter to you?",
        "Describe a moment today when you felt truly present. What made it special?",
        "What emotion are you feeling most strongly right now? What might be causing it?",
        "If you could tell your past self from a week ago one thing, what would it be?",
        "What's one small thing that brought you joy recently? How can you create more moments like that?",
        "What challenge are you currently facing, and what strengths do you have to help you through it?",
        "Describe someone who made a positive impact on your day. What did they do?",
        "What does self-care look like for you right now? What do you need more of?",
        "If your feelings had a color today, what would it be and why?",
        "What's one thing you learned about yourself this week?",
        "Write about a time when you overcame something difficult. What helped you through it?",
        "What would you say to a friend who was feeling exactly how you feel right now?",
        "What patterns do you notice in your thoughts and feelings lately?",
        "Describe your ideal peaceful moment. What elements make it perfect for you?",
        "What boundaries do you need to set or maintain for your wellbeing?"
    ]
    
    # Filter by topic if specified
    if topic:
        topic_prompts = {
            'gratitude': [
                "What are three things you're grateful for today, and why do they matter to you?",
                "Describe someone who made a positive impact on your day. What did they do?",
                "What's one small thing that brought you joy recently? How can you create more moments like that?"
            ],
            'stress': [
                "What challenge are you currently facing, and what strengths do you have to help you through it?",
                "What does self-care look like for you right now? What do you need more of?",
                "What boundaries do you need to set or maintain for your wellbeing?"
            ],
            'growth': [
                "What's one thing you learned about yourself this week?",
                "If you could tell your past self from a week ago one thing, what would it be?",
                "Write about a time when you overcame something difficult. What helped you through it?"
            ]
        }
        
        if topic.lower() in topic_prompts:
            all_prompts = topic_prompts[topic.lower()] + all_prompts
    
    # Adjust prompts based on mood
    if mood and mood <= 4:
        # For low moods, focus on supportive prompts
        supportive_prompts = [
            "What would you say to a friend who was feeling exactly how you feel right now?",
            "What's one small thing that brought you comfort recently?",
            "What strengths have helped you through difficult times before?",
            "Describe one person who cares about you. How do they show they care?"
        ]
        all_prompts = supportive_prompts + all_prompts
    
    return all_prompts[:count] 