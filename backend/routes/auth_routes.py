"""
Authentication routes for Mental Wellness Coach Flask API.
Provides JWT-based authentication and user management endpoints.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Mock user storage (in production, this would be in the database)
mock_users = {
    "demo@example.com": {
        "id": "demo-user-123",
        "email": "demo@example.com", 
        "password_hash": generate_password_hash("demo123"),
        "name": "Demo User",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
}

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'dev_jwt_secret_key_12345')
JWT_EXPIRES_IN = os.getenv('JWT_EXPIRES_IN', '7d')

def token_required(f):
    """Decorator to require valid JWT token for protected endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Add user_id to request context
            request.current_user_id = current_user_id
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        
        # Check if user already exists
        if email in mock_users:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        user_id = f"user-{len(mock_users) + 1}"
        mock_users[email] = {
            "id": user_id,
            "email": email,
            "password_hash": generate_password_hash(password),
            "name": name,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            },
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Check if user exists
        if email not in mock_users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = mock_users[email]
        
        # Verify password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': email,
                'name': user['name']
            },
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user information."""
    try:
        user_id = request.current_user_id
        
        # Find user by ID
        user = None
        for email, user_data in mock_users.items():
            if user_data['id'] == user_id:
                user = user_data
                break
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_user_profile():
    """Get user profile information (alias for /me endpoint)."""
    try:
        user_id = request.current_user_id
        
        # Find user by ID
        user = None
        for email, user_data in mock_users.items():
            if user_data['id'] == user_id:
                user = user_data
                break
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user profile: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (client should discard token)."""
    return jsonify({
        'message': 'Logout successful',
        'note': 'Please discard the JWT token on client side'
    }), 200

@auth_bp.route('/demo-token', methods=['GET'])
def get_demo_token():
    """Get a demo token for testing purposes."""
    try:
        # Generate demo token
        demo_user_id = "demo-user-123"
        token = jwt.encode({
            'user_id': demo_user_id,
            'email': 'demo@example.com',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': 'Demo token generated',
            'token': token,
            'user': {
                'id': demo_user_id,
                'email': 'demo@example.com',
                'name': 'Demo User'
            },
            'expires_in': '24 hours',
            'note': 'This is for testing purposes only'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate demo token: {str(e)}'}), 500

# Export the token_required decorator for use in other routes
__all__ = ['auth_bp', 'token_required'] 