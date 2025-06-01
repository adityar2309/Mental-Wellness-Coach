"""
Tests for mindfulness routes.
"""

import pytest
import json
from datetime import datetime, timedelta
from backend.app import create_app
from backend.database import db
from backend.models import User, MindfulnessSession

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def auth_user(app):
    """Create and return authenticated user with token."""
    with app.app_context():
        user = User(email='test@example.com', name='Test User')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=user.id)
        return user, token

class TestMindfulnessRoutes:
    """Test mindfulness routes."""
    
    def test_get_sessions_empty(self, client, auth_user):
        """Test getting sessions when none exist."""
        user, token = auth_user
        
        response = client.get(
            '/api/mindfulness/sessions',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sessions'] == []
        assert data['total'] == 0
    
    def test_create_session_success(self, client, auth_user):
        """Test creating a mindfulness session successfully."""
        user, token = auth_user
        
        session_data = {
            'session_type': 'breathing',
            'title': 'Test Breathing Session',
            'description': 'A test breathing session',
            'duration_minutes': 10,
            'mood_before': 5,
            'stress_before': 7
        }
        
        response = client.post(
            '/api/mindfulness/sessions',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Mindfulness session created successfully'
        assert data['session']['title'] == 'Test Breathing Session'
        assert data['session']['session_type'] == 'breathing'
        assert data['session']['duration_minutes'] == 10
        assert data['session']['mood_before'] == 5
        assert data['session']['stress_before'] == 7
        assert data['session']['completed'] == False
    
    def test_create_session_missing_fields(self, client, auth_user):
        """Test creating a session with missing required fields."""
        user, token = auth_user
        
        session_data = {
            'title': 'Test Session'
            # Missing session_type and duration_minutes
        }
        
        response = client.post(
            '/api/mindfulness/sessions',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required field' in data['error']
    
    def test_create_session_invalid_type(self, client, auth_user):
        """Test creating a session with invalid session type."""
        user, token = auth_user
        
        session_data = {
            'session_type': 'invalid_type',
            'title': 'Test Session',
            'duration_minutes': 10
        }
        
        response = client.post(
            '/api/mindfulness/sessions',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid session_type' in data['error']
    
    def test_get_session_by_id(self, client, auth_user, app):
        """Test getting a specific session by ID."""
        user, token = auth_user
        
        # Create a session first
        with app.app_context():
            session = MindfulnessSession(
                user_id=user.id,
                session_type='meditation',
                title='Test Meditation',
                duration_minutes=15,
                mood_before=6
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
        
        response = client.get(
            f'/api/mindfulness/sessions/{session_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['session']['title'] == 'Test Meditation'
        assert data['session']['session_type'] == 'meditation'
    
    def test_get_session_not_found(self, client, auth_user):
        """Test getting a session that doesn't exist."""
        user, token = auth_user
        
        response = client.get(
            '/api/mindfulness/sessions/999',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Session not found'
    
    def test_update_session_complete(self, client, auth_user, app):
        """Test updating a session to mark it as complete."""
        user, token = auth_user
        
        # Create a session first
        with app.app_context():
            session = MindfulnessSession(
                user_id=user.id,
                session_type='breathing',
                title='Test Breathing',
                duration_minutes=10
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
        
        update_data = {
            'completed': True,
            'completed_duration_minutes': 8,
            'mood_after': 7,
            'stress_after': 4,
            'effectiveness_rating': 8,
            'notes': 'Great session!',
            'session_data': {'breathing_rate': 6}
        }
        
        response = client.put(
            f'/api/mindfulness/sessions/{session_id}',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Session updated successfully'
        assert data['session']['completed'] == True
        assert data['session']['completed_duration_minutes'] == 8
        assert data['session']['mood_after'] == 7
        assert data['session']['stress_after'] == 4
        assert data['session']['effectiveness_rating'] == 8
        assert data['session']['notes'] == 'Great session!'
        assert data['session']['session_data']['breathing_rate'] == 6
        assert data['session']['completed_at'] is not None
    
    def test_update_session_invalid_rating(self, client, auth_user, app):
        """Test updating a session with invalid effectiveness rating."""
        user, token = auth_user
        
        # Create a session first
        with app.app_context():
            session = MindfulnessSession(
                user_id=user.id,
                session_type='meditation',
                title='Test Meditation',
                duration_minutes=15
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
        
        update_data = {
            'effectiveness_rating': 15  # Invalid rating (should be 1-10)
        }
        
        response = client.put(
            f'/api/mindfulness/sessions/{session_id}',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'effectiveness_rating must be between 1 and 10' in data['error']
    
    def test_delete_session(self, client, auth_user, app):
        """Test deleting a mindfulness session."""
        user, token = auth_user
        
        # Create a session first
        with app.app_context():
            session = MindfulnessSession(
                user_id=user.id,
                session_type='body_scan',
                title='Test Body Scan',
                duration_minutes=20
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
        
        response = client.delete(
            f'/api/mindfulness/sessions/{session_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Session deleted successfully'
        
        # Verify session is deleted
        get_response = client.get(
            f'/api/mindfulness/sessions/{session_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert get_response.status_code == 404
    
    def test_get_templates(self, client, auth_user):
        """Test getting session templates."""
        user, token = auth_user
        
        response = client.get(
            '/api/mindfulness/templates',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'templates' in data
        
        templates = data['templates']
        assert 'breathing' in templates
        assert 'meditation' in templates
        assert 'body_scan' in templates
        assert 'progressive_relaxation' in templates
        
        # Check breathing templates
        breathing_templates = templates['breathing']
        assert len(breathing_templates) > 0
        assert 'title' in breathing_templates[0]
        assert 'description' in breathing_templates[0]
        assert 'duration_minutes' in breathing_templates[0]
        assert 'instructions' in breathing_templates[0]
    
    def test_get_analytics_no_sessions(self, client, auth_user):
        """Test getting analytics when user has no sessions."""
        user, token = auth_user
        
        response = client.get(
            '/api/mindfulness/analytics',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        analytics = data['analytics']
        assert analytics['total_sessions'] == 0
        assert analytics['completed_sessions'] == 0
        assert analytics['completion_rate'] == 0
        assert analytics['total_minutes'] == 0
        assert analytics['streak_days'] == 0
        assert analytics['session_types'] == {}
    
    def test_get_analytics_with_sessions(self, client, auth_user, app):
        """Test getting analytics with existing sessions."""
        user, token = auth_user
        
        # Create several sessions with different data
        with app.app_context():
            # Completed session 1
            session1 = MindfulnessSession(
                user_id=user.id,
                session_type='breathing',
                title='Breathing Session 1',
                duration_minutes=10,
                completed_duration_minutes=9,
                completed=True,
                effectiveness_rating=8,
                mood_before=5,
                mood_after=7,
                stress_before=8,
                stress_after=5,
                completed_at=datetime.utcnow()
            )
            
            # Completed session 2
            session2 = MindfulnessSession(
                user_id=user.id,
                session_type='meditation',
                title='Meditation Session 1',
                duration_minutes=15,
                completed_duration_minutes=15,
                completed=True,
                effectiveness_rating=9,
                mood_before=4,
                mood_after=8,
                stress_before=7,
                stress_after=3,
                completed_at=datetime.utcnow()
            )
            
            # Incomplete session
            session3 = MindfulnessSession(
                user_id=user.id,
                session_type='breathing',
                title='Breathing Session 2',
                duration_minutes=10,
                completed=False
            )
            
            db.session.add_all([session1, session2, session3])
            db.session.commit()
        
        response = client.get(
            '/api/mindfulness/analytics',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        analytics = data['analytics']
        assert analytics['total_sessions'] == 3
        assert analytics['completed_sessions'] == 2
        assert analytics['completion_rate'] == 2/3
        assert analytics['total_minutes'] == 24  # 9 + 15
        assert analytics['average_effectiveness'] == 8.5  # (8 + 9) / 2
        assert analytics['average_mood_improvement'] == 3.5  # ((7-5) + (8-4)) / 2
        assert analytics['average_stress_reduction'] == 3.5  # ((8-5) + (7-3)) / 2
        assert analytics['session_types']['breathing'] == 2
        assert analytics['session_types']['meditation'] == 1
    
    def test_get_analytics_custom_period(self, client, auth_user, app):
        """Test getting analytics for a custom time period."""
        user, token = auth_user
        
        # Create a session from 40 days ago
        with app.app_context():
            old_session = MindfulnessSession(
                user_id=user.id,
                session_type='meditation',
                title='Old Session',
                duration_minutes=10,
                completed=True,
                created_at=datetime.utcnow() - timedelta(days=40)
            )
            
            # Create a recent session
            recent_session = MindfulnessSession(
                user_id=user.id,
                session_type='breathing',
                title='Recent Session',
                duration_minutes=5,
                completed=True,
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            
            db.session.add_all([old_session, recent_session])
            db.session.commit()
        
        # Get analytics for last 30 days (should only include recent session)
        response = client.get(
            '/api/mindfulness/analytics?days=30',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        analytics = data['analytics']
        assert analytics['period_days'] == 30
        assert analytics['total_sessions'] == 1  # Only recent session
        assert analytics['session_types']['breathing'] == 1
        assert 'meditation' not in analytics['session_types']  # Old session excluded
    
    def test_unauthorized_access(self, client):
        """Test accessing mindfulness routes without authentication."""
        # Test without token
        response = client.get('/api/mindfulness/sessions')
        assert response.status_code == 401
        
        response = client.post('/api/mindfulness/sessions')
        assert response.status_code == 401
        
        response = client.get('/api/mindfulness/templates')
        assert response.status_code == 401
        
        response = client.get('/api/mindfulness/analytics')
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """Test accessing mindfulness routes with invalid token."""
        response = client.get(
            '/api/mindfulness/sessions',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        assert response.status_code == 401
    
    def test_session_filtering(self, client, auth_user, app):
        """Test filtering sessions by type and completion status."""
        user, token = auth_user
        
        # Create sessions of different types and completion status
        with app.app_context():
            sessions = [
                MindfulnessSession(
                    user_id=user.id,
                    session_type='breathing',
                    title='Breathing 1',
                    duration_minutes=5,
                    completed=True
                ),
                MindfulnessSession(
                    user_id=user.id,
                    session_type='breathing',
                    title='Breathing 2',
                    duration_minutes=5,
                    completed=False
                ),
                MindfulnessSession(
                    user_id=user.id,
                    session_type='meditation',
                    title='Meditation 1',
                    duration_minutes=10,
                    completed=True
                ),
            ]
            db.session.add_all(sessions)
            db.session.commit()
        
        # Filter by session type
        response = client.get(
            '/api/mindfulness/sessions?session_type=breathing',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['sessions']) == 2
        assert all(s['session_type'] == 'breathing' for s in data['sessions'])
        
        # Filter by completion status
        response = client.get(
            '/api/mindfulness/sessions?completed=true',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['sessions']) == 2
        assert all(s['completed'] for s in data['sessions'])
        
        # Combine filters
        response = client.get(
            '/api/mindfulness/sessions?session_type=breathing&completed=false',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['sessions']) == 1
        assert data['sessions'][0]['session_type'] == 'breathing'
        assert not data['sessions'][0]['completed']
    
    def test_session_pagination(self, client, auth_user, app):
        """Test session pagination."""
        user, token = auth_user
        
        # Create 15 sessions
        with app.app_context():
            sessions = []
            for i in range(15):
                session = MindfulnessSession(
                    user_id=user.id,
                    session_type='meditation',
                    title=f'Session {i+1}',
                    duration_minutes=10
                )
                sessions.append(session)
            db.session.add_all(sessions)
            db.session.commit()
        
        # Get first page (limit 10)
        response = client.get(
            '/api/mindfulness/sessions?limit=10&offset=0',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['sessions']) == 10
        assert data['total'] == 15
        
        # Get second page
        response = client.get(
            '/api/mindfulness/sessions?limit=10&offset=10',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['sessions']) == 5
        assert data['total'] == 15 