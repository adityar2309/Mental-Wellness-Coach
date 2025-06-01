"""
Mental Wellness Coach - Mood Tracking Routes

Flask blueprint for mood tracking and analytics functionality.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

# Import our custom auth system and database models
from .auth_routes import token_required
from database import db
from models import MoodEntry, get_user_stats

# Create blueprint
mood_bp = Blueprint('mood', __name__)
logger = logging.getLogger(__name__)

@mood_bp.route('/checkin', methods=['POST'])
@token_required
def mood_checkin():
    """
    Record a comprehensive mood check-in.
    
    Expected JSON:
    {
        "mood_score": 7,
        "emotions": ["happy", "content"],
        "energy": 6,
        "stress": 3,
        "sleep": 8,
        "description": "Feeling good today!",
        "triggers": ["exercise", "good_weather"]
    }
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'mood_score' not in data:
            return jsonify({'error': 'Mood score is required'}), 400
        
        # Validate mood score
        mood_score = data.get('mood_score')
        if not isinstance(mood_score, int) or mood_score < 1 or mood_score > 10:
            return jsonify({'error': 'Mood score must be between 1 and 10'}), 400
        
        # Create new mood entry
        mood_entry = MoodEntry(
            user_id=user_id,
            mood_score=mood_score,
            energy=data.get('energy'),
            stress=data.get('stress'),
            sleep=data.get('sleep'),
            description=data.get('description')
        )
        
        # Set emotions and triggers
        if data.get('emotions'):
            mood_entry.set_emotions(data['emotions'])
        if data.get('triggers'):
            mood_entry.set_triggers(data['triggers'])
        
        # Save to database
        db.session.add(mood_entry)
        db.session.commit()
        
        logger.info(f"Mood check-in recorded for user {user_id}, mood score: {mood_score}")
        
        return jsonify({
            'status': 'success',
            'message': 'Mood check-in recorded',
            'mood_entry': mood_entry.to_dict(),
            'entry_id': mood_entry.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in mood check-in: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mood_bp.route('/quick-checkin', methods=['POST'])
@token_required
def quick_mood_checkin():
    """
    Record a quick mood check-in with just a mood score.
    
    Expected JSON:
    {
        "mood_score": 5
    }
    """
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        if not data or 'mood_score' not in data:
            return jsonify({'error': 'Mood score is required'}), 400
        
        # Validate mood score
        mood_score = data.get('mood_score')
        if not isinstance(mood_score, int) or mood_score < 1 or mood_score > 10:
            return jsonify({'error': 'Mood score must be between 1 and 10'}), 400
        
        # Create quick mood entry
        mood_entry = MoodEntry(
            user_id=user_id,
            mood_score=mood_score,
            description="Quick check-in"
        )
        
        # Save to database
        db.session.add(mood_entry)
        db.session.commit()
        
        logger.info(f"Quick mood check-in recorded for user {user_id}, mood score: {mood_score}")
        
        return jsonify({
            'status': 'success',
            'message': 'Quick mood check-in recorded',
            'mood_entry': mood_entry.to_dict(),
            'entry_id': mood_entry.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in quick mood check-in: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mood_bp.route('/history', methods=['GET'])
@token_required
def get_mood_history():
    """Get mood history for the current user."""
    try:
        user_id = request.current_user_id
        
        # Get query parameters
        limit = request.args.get('limit', 30, type=int)
        limit = min(limit, 100)  # Cap at 100 entries
        
        days = request.args.get('days', 30, type=int)
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Query mood entries
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= since_date
        ).order_by(MoodEntry.created_at.desc()).limit(limit).all()
        
        # Convert to dictionaries
        mood_data = [entry.to_dict() for entry in mood_entries]
        
        logger.info(f"Retrieved {len(mood_entries)} mood entries for user {user_id}")
        
        return jsonify({
            'mood_entries': mood_data,
            'total': len(mood_data),
            'days_requested': days,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving mood history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mood_bp.route('/analytics', methods=['GET'])
@token_required
def get_mood_analytics():
    """Get mood analytics and insights for the current user."""
    try:
        user_id = request.current_user_id
        
        # Get analytics period
        days = request.args.get('days', 30, type=int)
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Query mood entries
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= since_date
        ).all()
        
        if not mood_entries:
            return jsonify({
                'analytics': {
                    'total_entries': 0,
                    'period_days': days,
                    'message': 'No mood data available for this period'
                }
            }), 200
        
        # Calculate analytics
        mood_scores = [entry.mood_score for entry in mood_entries]
        energy_scores = [entry.energy for entry in mood_entries if entry.energy is not None]
        stress_scores = [entry.stress for entry in mood_entries if entry.stress is not None]
        
        # Collect all emotions
        all_emotions = []
        for entry in mood_entries:
            all_emotions.extend(entry.get_emotions())
        
        # Count emotion frequency
        emotion_counts = {}
        for emotion in all_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Calculate trends (simple trend detection)
        if len(mood_scores) >= 7:
            recent_avg = sum(mood_scores[:7]) / 7
            older_avg = sum(mood_scores[7:14]) / min(7, len(mood_scores[7:14])) if len(mood_scores) > 7 else recent_avg
            trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            trend = "insufficient_data"
        
        analytics = {
            'total_entries': len(mood_entries),
            'period_days': days,
            'average_mood': round(sum(mood_scores) / len(mood_scores), 1),
            'highest_mood': max(mood_scores),
            'lowest_mood': min(mood_scores),
            'mood_trend': trend,
            'average_energy': round(sum(energy_scores) / len(energy_scores), 1) if energy_scores else None,
            'average_stress': round(sum(stress_scores) / len(stress_scores), 1) if stress_scores else None,
            'most_common_emotions': sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'insights': _generate_mood_insights(mood_scores, emotion_counts, trend)
        }
        
        logger.info(f"Generated mood analytics for user {user_id}: {days} days, {len(mood_entries)} entries")
        
        return jsonify({
            'analytics': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating mood analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mood_bp.route('/trends', methods=['GET'])
@token_required  
def get_mood_trends():
    """Get detailed mood trends and patterns."""
    try:
        user_id = request.current_user_id
        
        # Get last 30 days of mood data
        since_date = datetime.utcnow() - timedelta(days=30)
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= since_date
        ).order_by(MoodEntry.created_at.asc()).all()
        
        if not mood_entries:
            return jsonify({
                'trends': {
                    'weekly_averages': [],
                    'daily_pattern': {},
                    'message': 'Insufficient data for trend analysis'
                }
            }), 200
        
        # Group by week and calculate averages
        weekly_data = {}
        daily_data = {str(i): [] for i in range(7)}  # Monday=0, Sunday=6
        
        for entry in mood_entries:
            # Weekly grouping
            week_start = entry.created_at - timedelta(days=entry.created_at.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = []
            weekly_data[week_key].append(entry.mood_score)
            
            # Daily pattern (day of week)
            day_of_week = str(entry.created_at.weekday())
            daily_data[day_of_week].append(entry.mood_score)
        
        # Calculate weekly averages
        weekly_averages = []
        for week, scores in sorted(weekly_data.items()):
            weekly_averages.append({
                'week_start': week,
                'average_mood': round(sum(scores) / len(scores), 1),
                'entry_count': len(scores)
            })
        
        # Calculate daily patterns
        daily_pattern = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day_num, scores in daily_data.items():
            if scores:
                daily_pattern[day_names[int(day_num)]] = {
                    'average_mood': round(sum(scores) / len(scores), 1),
                    'entry_count': len(scores)
                }
        
        return jsonify({
            'trends': {
                'weekly_averages': weekly_averages,
                'daily_pattern': daily_pattern,
                'total_entries': len(mood_entries),
                'analysis_period': '30 days'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating mood trends: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mood_bp.route('/entries', methods=['GET', 'POST'])
@token_required
def mood_entries():
    """
    Handle mood entries - GET to retrieve entries, POST to create new entry.
    This endpoint matches the expected API pattern for CRUD operations.
    """
    if request.method == 'GET':
        try:
            user_id = request.current_user_id
            
            # Get query parameters
            limit = request.args.get('limit', 30, type=int)
            limit = min(limit, 100)  # Cap at 100 entries
            
            days = request.args.get('days', 30, type=int)
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Query mood entries
            mood_entries = MoodEntry.query.filter(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= since_date
            ).order_by(MoodEntry.created_at.desc()).limit(limit).all()
            
            # Convert to dictionaries
            mood_data = [entry.to_dict() for entry in mood_entries]
            
            logger.info(f"Retrieved {len(mood_entries)} mood entries for user {user_id}")
            
            return jsonify({
                'entries': mood_data,
                'total': len(mood_data),
                'days_requested': days,
                'limit': limit
            }), 200
            
        except Exception as e:
            logger.error(f"Error retrieving mood entries: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    elif request.method == 'POST':
        try:
            user_id = request.current_user_id
            data = request.get_json()
            
            if not data or 'mood_score' not in data:
                return jsonify({'error': 'Mood score is required'}), 400
            
            # Validate mood score
            mood_score = data.get('mood_score')
            if not isinstance(mood_score, int) or mood_score < 1 or mood_score > 10:
                return jsonify({'error': 'Mood score must be between 1 and 10'}), 400
            
            # Create new mood entry
            mood_entry = MoodEntry(
                user_id=user_id,
                mood_score=mood_score,
                energy=data.get('energy_level') or data.get('energy'),
                stress=data.get('stress_level') or data.get('stress'),
                sleep=data.get('sleep_quality') or data.get('sleep'),
                description=data.get('notes') or data.get('description')
            )
            
            # Set emotions and triggers if provided
            if data.get('emotions'):
                mood_entry.set_emotions(data['emotions'])
            if data.get('triggers'):
                mood_entry.set_triggers(data['triggers'])
            
            # Save to database
            db.session.add(mood_entry)
            db.session.commit()
            
            logger.info(f"Mood entry created for user {user_id}, mood score: {mood_score}")
            
            return jsonify({
                'status': 'success',
                'message': 'Mood entry created',
                'entry': mood_entry.to_dict(),
                'id': mood_entry.id
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating mood entry: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

def _generate_mood_insights(mood_scores, emotion_counts, trend):
    """Generate personalized mood insights based on data."""
    insights = []
    
    avg_mood = sum(mood_scores) / len(mood_scores)
    
    # Mood level insights
    if avg_mood >= 7:
        insights.append("Your mood has been generally positive this period.")
    elif avg_mood >= 5:
        insights.append("Your mood has been moderate with room for improvement.")
    else:
        insights.append("Your mood has been challenging lately. Consider reaching out for support.")
    
    # Trend insights
    if trend == "improving":
        insights.append("Great news! Your mood trend is improving over time.")
    elif trend == "declining":
        insights.append("Your mood has been declining recently. This might be a good time to focus on self-care.")
    
    # Emotion insights
    if emotion_counts:
        top_emotion = max(emotion_counts.items(), key=lambda x: x[1])
        insights.append(f"Your most common emotion this period was '{top_emotion[0]}'.")
    
    # Variability insights
    mood_range = max(mood_scores) - min(mood_scores)
    if mood_range >= 6:
        insights.append("You've experienced a wide range of moods. Consider identifying triggers for the fluctuations.")
    elif mood_range <= 2:
        insights.append("Your mood has been quite stable, which is a positive sign.")
    
    return insights

# Export blueprint
__all__ = ['mood_bp'] 