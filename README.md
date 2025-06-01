# Mental Wellness Coach 🧠💚

A privacy-first AI agent designed to provide daily emotional support and mental health maintenance using **ASI:One LLM** and **Fetch.ai's uAgents framework**.

## 🎯 Vision

Mental Wellness Coach creates a safe, empathetic, and confidential space for individuals to:
- Track their daily mental health
- Process emotions through guided journaling  
- Learn and practice healthy coping strategies
- Receive intelligent, personalized support
- Access crisis intervention when needed

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Flask Backend  │    │  ASI:One LLM    │
│  (React Native) │◄──►│    (Python)      │◄──►│   AI Engine     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   PostgreSQL     │
                       │    Database      │
                       └──────────────────┘
```

## 🛠️ Tech Stack

### Backend & AI
- **Python Flask** - RESTful API server
- **ASI:One LLM** - Advanced conversational AI
- **Fetch.ai uAgents** - Intelligent agent framework
- **PostgreSQL** - Primary database with encryption
- **Redis** - Session management and caching

### Mobile Application  
- **React Native** with Expo - Cross-platform mobile app
- **Secure storage** for offline data protection

### Infrastructure
- **Docker** - Containerized deployment
- **GitHub Actions** - CI/CD pipeline

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis
- Docker (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/mental-wellness-coach.git
cd mental-wellness-coach

# Install Python dependencies
pip install -r requirements.txt

# Install mobile dependencies  
cd mobile && npm install && cd ..

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run Flask backend
python run-flask.py

# Run mobile app (separate terminal)
cd mobile && npm run dev
```

### Environment Configuration

Key environment variables needed:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/wellness_coach

# AI Configuration  
ASI_ONE_API_KEY=your_asi_one_api_key
FETCH_AI_AGENT_KEY=your_fetch_ai_key

# Security
JWT_SECRET=your-super-secure-jwt-secret
ENCRYPTION_KEY=your-32-char-encryption-key
```

## 📱 Features

### Core Functionality
- **Daily Mood Check-ins** - Track emotional state with intelligent analysis
- **AI-Guided Journaling** - Personalized prompts and insights
- **Coping Toolkit** - Breathing exercises, mindfulness, cognitive techniques
- **Crisis Detection** - Automated risk assessment with professional escalation
- **Progress Analytics** - Long-term mental health insights

### Privacy & Security
- **End-to-end encryption** for all personal data
- **HIPAA compliance** ready architecture
- **GDPR compliance** with right-to-be-forgotten
- **Local data processing** where possible
- **Zero-knowledge** design principles

## 🏗️ Project Structure

```
mental-wellness-coach/
├── backend/                 # Python Flask API server
│   ├── models.py           # SQLAlchemy database models
│   ├── routes/             # API route handlers
│   ├── app.py              # Flask application
│   └── config.py           # Configuration management
├── mobile/                  # React Native mobile app
│   ├── src/                # Mobile app source code
│   ├── components/         # Reusable UI components
│   └── screens/            # App screens
├── tests/                   # Test suites
├── docs/                    # Documentation
├── docker-compose.yml       # Multi-service setup
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧪 Development

### Running Tests
```bash
# Backend tests
pytest

# Mobile tests  
cd mobile && npm test

# End-to-end tests
pytest tests/e2e/
```

### Code Quality
```bash
# Python linting and formatting
black backend/ && flake8 backend/

# Mobile linting
cd mobile && npm run lint
```

### Database Management
```bash
# Create migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade
```

## 🔒 Security & Compliance

### Data Protection
- All personally identifiable information (PII) is encrypted at rest
- Mental health data uses additional encryption layers
- Database queries use parameterized statements
- API endpoints implement rate limiting
- Session tokens have automatic expiration

### Mental Health Safety
- Crisis detection algorithms with multiple safety nets
- Automatic escalation to mental health professionals
- Integration with national crisis hotlines
- Clear disclaimers about AI limitations
- Emergency contact systems

## 📊 Monitoring & Analytics

- Health check endpoints for uptime monitoring
- Performance metrics and response time tracking
- Privacy-preserving usage analytics
- Error logging and alerting
- Database performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP8 for Python code
- Write comprehensive tests for new features
- Use type hints in Python code
- Ensure HIPAA compliance for health data
- Add documentation for public APIs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Resources

### Crisis Resources
- **US**: National Suicide Prevention Lifeline: 988
- **UK**: Samaritans: 116 123
- **International**: [International Association for Suicide Prevention](https://www.iasp.info/resources/Crisis_Centres/)

### Project Support
- 📧 Email: support@mentalwellnesscoach.ai
- 🐛 Bug Reports: [GitHub Issues](https://github.com/your-org/mental-wellness-coach/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/mental-wellness-coach/discussions)

---

*Built with ❤️ for mental health awareness and support* 