"""
Mental Wellness Coach - Flask Backend Application

This is the main entry point for the Flask API server.
It sets up Flask, middleware, routes, and starts the server.
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import extensions from database module to avoid circular imports
from database import db, migrate

jwt = JWTManager()

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Configuration - Using SQLite instead of PostgreSQL
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wellness_coach.db'  # Force SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'dev-jwt-secret')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Security middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO if os.getenv('NODE_ENV') != 'development' else logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.getenv('NODE_ENV', 'development'),
            'version': '1.0.0',
            'service': 'mental-wellness-coach-flask-api',
            'database': 'sqlite'
        }), 200
    
    # Basic route
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information."""
        return jsonify({
            'message': 'Mental Wellness Coach Flask API',
            'version': '1.0.0',
            'documentation': '/api/docs',
            'health': '/health',
            'framework': 'Flask',
            'language': 'Python',
            'database': 'SQLite'
        }), 200
    
    # 404 handler
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Route not found',
            'message': f'The route {request.url} does not exist'
        }), 404
    
    # 500 handler
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f'Internal server error: {error}')
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong' if os.getenv('NODE_ENV') == 'production' else str(error)
        }), 500
    
    # Register routes when they're ready
    with app.app_context():
        try:
            # Import models to ensure they're registered with SQLAlchemy
            # This import happens inside app context to avoid circular imports
            import models
            
            # Create SQLite database tables
            models.init_database()
            logger.info("✅ SQLite database tables created successfully")
        except Exception as e:
            logger.warning(f"Database initialization error: {e}")
            
        # Register blueprints when available
        try:
            from routes.auth_routes import auth_bp
            from routes.mood_routes import mood_bp
            from routes.conversation_routes import conversation_bp
            from routes.agent_routes import agent_bp
            from routes.crisis_routes import crisis_bp
            from routes.journal_routes import journal_bp
            from routes.mindfulness_routes import mindfulness_bp
            app.register_blueprint(auth_bp, url_prefix='/api/auth')
            app.register_blueprint(mood_bp, url_prefix='/api/mood')
            app.register_blueprint(conversation_bp, url_prefix='/api/conversations')
            app.register_blueprint(agent_bp, url_prefix='/api/agents')
            app.register_blueprint(crisis_bp, url_prefix='/api/crisis')
            app.register_blueprint(journal_bp, url_prefix='/api/journal')
            app.register_blueprint(mindfulness_bp, url_prefix='/api/mindfulness')
            logger.info("✅ All routes registered successfully")
        except ImportError as e:
            logger.warning(f"Some routes not available: {e}")
    
    return app

# Create app instance for direct running
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    print(f"🚀 Mental Wellness Coach Flask API starting on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"🌍 Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"🐍 Framework: Flask (Python)")
    print(f"🗃️ Database: SQLite")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 