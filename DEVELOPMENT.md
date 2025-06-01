# Mental Wellness Coach - Development Guide

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+** (check with `python --version`)
- **PostgreSQL 12+** (database server)
- **Redis** (caching and session management)
- **Git** (version control)
- **Docker** (optional, for containerized development)

### 🔧 Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/mental-wellness-coach.git
   cd mental-wellness-coach
   ```

2. **Setup Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your configuration
   # Key variables to set:
   # - DATABASE_URL
   # - ASI_ONE_API_KEY
   # - FETCH_AI_AGENT_KEY
   # - JWT_SECRET
   # - ENCRYPTION_KEY
   ```

4. **Database Setup**
   ```bash
   # Start PostgreSQL (if using Docker)
   docker run --name wellness-postgres -e POSTGRES_PASSWORD=wellness_pass -e POSTGRES_USER=wellness_user -e POSTGRES_DB=wellness_coach -p 5432:5432 -d postgres:14
   
   # Initialize database tables
   cd backend
   python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

5. **Mobile App Setup**
   ```bash
   # Navigate to mobile directory
   cd mobile
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

### 🏃‍♂️ Running the Application

#### Backend (Flask API)
```bash
# From project root
python run-flask.py

# Or from backend directory
cd backend && python app.py
```

#### Mobile App
```bash
# Navigate to mobile directory
cd mobile

# Start Expo development server
npm run dev

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android
```

## 📁 Project Structure

```
mental-wellness-coach/
├── backend/                 # Python Flask API server
│   ├── app.py              # Flask application entry point
│   ├── models.py           # SQLAlchemy database models
│   ├── config.py           # Configuration management
│   ├── routes/             # API route blueprints
│   │   ├── mood_routes.py  # Mood tracking endpoints
│   │   ├── auth_routes.py  # Authentication endpoints
│   │   └── chat_routes.py  # AI conversation endpoints
│   └── services/           # Business logic services
│       ├── ai_service.py   # ASI:One LLM integration
│       └── crisis_service.py # Crisis detection
├── mobile/                  # React Native mobile app
│   ├── src/                # Source code
│   ├── components/         # Reusable components
│   └── screens/            # App screens
├── tests/                   # Test suites
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Multi-service Docker setup
└── README.md               # Project overview
```

## 🧪 Testing

### Backend Testing
```bash
# Run all Python tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_mood_routes.py
```

### Mobile Testing
```bash
# Navigate to mobile directory
cd mobile

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### Integration Testing
```bash
# Run end-to-end tests
pytest tests/e2e/
```

## 🔧 Development Tools

### Code Quality
```bash
# Python formatting and linting
black backend/
flake8 backend/
isort backend/

# Mobile linting
cd mobile && npm run lint
```

### Database Management
```bash
# Create database migration
cd backend
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade migration
flask db downgrade
```

### Docker Development
```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🐛 Debugging

### Backend Debugging
- Flask debug mode is enabled in development
- Use `print()` statements or Python debugger (`pdb`)
- Check logs in `backend/logs/` directory
- Use Flask-SQLAlchemy echo for SQL debugging

### Mobile Debugging
- Use React Native debugger
- Expo DevTools for development insights
- Chrome DevTools for React Native debugging
- Native platform debugging tools (Xcode/Android Studio)

## 📊 Monitoring & Health Checks

### Backend Health
```bash
# Check API health
curl http://localhost:3000/health

# Check database connection
curl http://localhost:3000/api/status
```

### Development Services
- **Backend API**: http://localhost:3000
- **Mobile App**: Expo DevTools will show URLs
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379

## 🔒 Security in Development

### Environment Variables
- Never commit `.env` files
- Use `.env.example` as template
- Rotate secrets regularly
- Use strong encryption keys (32+ characters)

### Database Security
- Use separate development database
- Enable SSL connections in production
- Implement row-level security where needed
- Regular security updates

## 📚 Additional Resources

### Documentation
- [API Documentation](docs/api.md)
- [Database Schema](docs/database.md)
- [Security Guidelines](docs/security.md)
- [Deployment Guide](docs/deployment.md)

### Mental Health Guidelines
- [Crisis Intervention Protocols](docs/crisis-protocols.md)
- [AI Response Guidelines](docs/ai-guidelines.md)
- [Privacy Requirements](docs/privacy.md)

### External APIs
- [ASI:One LLM Documentation](https://docs.asi.one/)
- [Fetch.ai uAgents Guide](https://docs.fetch.ai/uAgents/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Make changes with comprehensive tests
3. Run linting and formatting tools
4. Submit pull request with description
5. Address code review feedback
6. Merge after approval

### Code Standards
- Follow PEP8 for Python code
- Use type hints in Python functions
- Write docstrings for all functions
- Maintain >90% test coverage
- Document mental health features thoroughly

---

**Need Help?** 
- 📧 Email: dev-support@mentalwellnesscoach.ai
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/mental-wellness-coach/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/mental-wellness-coach/discussions) 