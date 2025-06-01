"""
Mental Wellness Coach - Database Models

SQLAlchemy models for SQLite database.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Import the shared db instance from database instead of app to avoid circular imports
from database import db

class User(db.Model):
    """User model for authentication and profile management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class MoodEntry(db.Model):
    """Mood tracking entries."""
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # 1-10 scale
    emotions = db.Column(db.Text)  # JSON array of emotions
    energy = db.Column(db.Integer)  # 1-10 scale
    stress = db.Column(db.Integer)  # 1-10 scale
    sleep = db.Column(db.Integer)  # 1-10 scale
    description = db.Column(db.Text)
    triggers = db.Column(db.Text)  # JSON array of triggers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_emotions(self, emotions_list):
        """Set emotions as JSON string."""
        self.emotions = json.dumps(emotions_list) if emotions_list else None
    
    def get_emotions(self):
        """Get emotions as list."""
        return json.loads(self.emotions) if self.emotions else []
    
    def set_triggers(self, triggers_list):
        """Set triggers as JSON string."""
        self.triggers = json.dumps(triggers_list) if triggers_list else None
    
    def get_triggers(self):
        """Get triggers as list."""
        return json.loads(self.triggers) if self.triggers else []
    
    def to_dict(self):
        """Convert mood entry to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mood_score': self.mood_score,
            'emotions': self.get_emotions(),
            'energy': self.energy,
            'stress': self.stress,
            'sleep': self.sleep,
            'description': self.description,
            'triggers': self.get_triggers(),
            'created_at': self.created_at.isoformat()
        }

class Conversation(db.Model):
    """AI conversation sessions."""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=False, index=True)  # For API references
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert conversation to dictionary."""
        return {
            'id': self.external_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': len(self.messages)
        }

class Message(db.Model):
    """Individual messages in conversations."""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    message_metadata = db.Column(db.Text)  # JSON for crisis_level, confidence, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_metadata(self, metadata_dict):
        """Set metadata as JSON string."""
        self.message_metadata = json.dumps(metadata_dict) if metadata_dict else None
    
    def get_metadata(self):
        """Get metadata as dictionary."""
        return json.loads(self.message_metadata) if self.message_metadata else {}
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'id': f"msg_{self.id}",
            'role': self.role,
            'content': self.content,
            'metadata': self.get_metadata(),
            'timestamp': self.created_at.isoformat()
        }

class JournalEntry(db.Model):
    """Journaling entries."""
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    mood_score = db.Column(db.Integer)  # Optional mood at time of writing
    emotions = db.Column(db.Text)  # JSON array of emotions
    tags = db.Column(db.Text)  # JSON array of tags
    is_private = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_emotions(self, emotions_list):
        """Set emotions as JSON string."""
        self.emotions = json.dumps(emotions_list) if emotions_list else None
    
    def get_emotions(self):
        """Get emotions as list."""
        return json.loads(self.emotions) if self.emotions else []
    
    def set_tags(self, tags_list):
        """Set tags as JSON string."""
        self.tags = json.dumps(tags_list) if tags_list else None
    
    def get_tags(self):
        """Get tags as list."""
        return json.loads(self.tags) if self.tags else []
    
    def to_dict(self):
        """Convert journal entry to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'mood_score': self.mood_score,
            'emotions': self.get_emotions(),
            'tags': self.get_tags(),
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CopingActivity(db.Model):
    """Coping activities and user engagement."""
    __tablename__ = 'coping_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # e.g., 'breathing', 'mindfulness', 'physical'
    duration_minutes = db.Column(db.Integer)
    instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert coping activity to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'duration_minutes': self.duration_minutes,
            'instructions': self.instructions
        }

class ActivityLog(db.Model):
    """User engagement with coping activities."""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('coping_activities.id'), nullable=False)
    duration_minutes = db.Column(db.Integer)
    effectiveness_rating = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='activity_logs')
    activity = db.relationship('CopingActivity', backref='usage_logs')
    
    def to_dict(self):
        """Convert activity log to dictionary."""
        return {
            'id': self.id,
            'activity': self.activity.to_dict() if self.activity else None,
            'duration_minutes': self.duration_minutes,
            'effectiveness_rating': self.effectiveness_rating,
            'notes': self.notes,
            'completed_at': self.completed_at.isoformat()
        }

class CrisisEvent(db.Model):
    """Crisis detection and intervention tracking."""
    __tablename__ = 'crisis_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trigger_source = db.Column(db.String(50))  # 'chat', 'mood', 'journal'
    crisis_level = db.Column(db.String(20))  # 'low', 'medium', 'high', 'critical'
    trigger_content = db.Column(db.Text)  # The content that triggered detection
    ai_confidence = db.Column(db.Float)  # AI confidence in crisis detection
    intervention_taken = db.Column(db.Text)  # What actions were taken
    professional_notified = db.Column(db.Boolean, default=False)
    user_response = db.Column(db.Text)  # User's response to intervention
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='crisis_events')
    
    def to_dict(self):
        """Convert crisis event to dictionary."""
        return {
            'id': self.id,
            'trigger_source': self.trigger_source,
            'crisis_level': self.crisis_level,
            'trigger_content': self.trigger_content,
            'ai_confidence': self.ai_confidence,
            'intervention_taken': self.intervention_taken,
            'professional_notified': self.professional_notified,
            'user_response': self.user_response,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat()
        }

class MindfulnessSession(db.Model):
    """Mindfulness and meditation session tracking."""
    __tablename__ = 'mindfulness_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # 'breathing', 'meditation', 'body_scan', 'progressive_relaxation'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)
    completed_duration_minutes = db.Column(db.Integer)  # Actual time completed
    completed = db.Column(db.Boolean, default=False)
    effectiveness_rating = db.Column(db.Integer)  # 1-10 scale post-session
    mood_before = db.Column(db.Integer)  # 1-10 scale
    mood_after = db.Column(db.Integer)  # 1-10 scale
    stress_before = db.Column(db.Integer)  # 1-10 scale
    stress_after = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text)
    session_data = db.Column(db.Text)  # JSON for session-specific data (breathing patterns, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='mindfulness_sessions')
    
    def set_session_data(self, data_dict):
        """Set session data as JSON string."""
        self.session_data = json.dumps(data_dict) if data_dict else None
    
    def get_session_data(self):
        """Get session data as dictionary."""
        return json.loads(self.session_data) if self.session_data else {}
    
    def to_dict(self):
        """Convert mindfulness session to dictionary."""
        return {
            'id': self.id,
            'session_type': self.session_type,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'completed_duration_minutes': self.completed_duration_minutes,
            'completed': self.completed,
            'effectiveness_rating': self.effectiveness_rating,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'stress_before': self.stress_before,
            'stress_after': self.stress_after,
            'notes': self.notes,
            'session_data': self.get_session_data(),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

# Utility functions for database operations
def init_database():
    """Initialize database tables."""
    db.create_all()
    
    # Add default coping activities
    if CopingActivity.query.count() == 0:
        default_activities = [
            {
                'name': 'Deep Breathing Exercise',
                'description': 'Calm your mind with focused breathing',
                'category': 'breathing',
                'duration_minutes': 5,
                'instructions': '1. Sit comfortably\n2. Breathe in for 4 counts\n3. Hold for 4 counts\n4. Breathe out for 6 counts\n5. Repeat 10 times'
            },
            {
                'name': '5-4-3-2-1 Grounding',
                'description': 'Ground yourself using your senses',
                'category': 'mindfulness',
                'duration_minutes': 3,
                'instructions': 'Name:\n5 things you can see\n4 things you can touch\n3 things you can hear\n2 things you can smell\n1 thing you can taste'
            },
            {
                'name': 'Progressive Muscle Relaxation',
                'description': 'Release tension through muscle relaxation',
                'category': 'physical',
                'duration_minutes': 15,
                'instructions': '1. Start with your toes\n2. Tense each muscle group for 5 seconds\n3. Release and notice the relaxation\n4. Work your way up to your head'
            }
        ]
        
        for activity_data in default_activities:
            activity = CopingActivity(**activity_data)
            db.session.add(activity)
        
        db.session.commit()

def get_user_stats(user_id):
    """Get comprehensive user statistics."""
    mood_entries = MoodEntry.query.filter_by(user_id=user_id).count()
    conversations = Conversation.query.filter_by(user_id=user_id).count()
    journal_entries = JournalEntry.query.filter_by(user_id=user_id).count()
    crisis_events = CrisisEvent.query.filter_by(user_id=user_id).count()
    
    # Calculate average mood score
    avg_mood = db.session.query(db.func.avg(MoodEntry.mood_score)).filter_by(user_id=user_id).scalar()
    
    return {
        'mood_entries': mood_entries,
        'conversations': conversations,
        'journal_entries': journal_entries,
        'crisis_events': crisis_events,
        'average_mood': round(avg_mood, 1) if avg_mood else None
    } 