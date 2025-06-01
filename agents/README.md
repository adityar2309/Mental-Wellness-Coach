# 🧠 Mental Wellness Mood Tracker Agent

A specialized AI agent designed for comprehensive mood tracking, analysis, and mental wellness insights, optimized for deployment on **Fetch.ai's Agentverse**.

## 🎯 Overview

The Mental Wellness Mood Tracker Agent is part of the Mental Wellness Coach ecosystem, providing:
- **Real-time mood tracking** with intelligent analysis
- **Crisis detection** and intervention recommendations
- **Pattern recognition** for emotional trends
- **Personalized wellness insights** and recommendations
- **24/7 availability** through Agentverse deployment

## ✨ Key Features

### 🔍 Mood Analysis Engine
- **Multi-dimensional mood scoring** (1-10 scale with emotions, energy, stress levels)
- **Crisis indicator detection** using natural language processing
- **Historical trend analysis** and pattern recognition
- **Intervention recommendation** based on analysis results

### 🚨 Crisis Detection System
- **Real-time crisis keyword detection** for immediate intervention
- **Consecutive low mood monitoring** with configurable thresholds
- **Stress and energy level alerts** for comprehensive wellness tracking
- **Automated escalation protocols** for critical situations

### 📊 Advanced Analytics
- **Mood trend analysis** (improving, stable, declining)
- **Pattern recognition** across multiple timeframes
- **Personalized recommendations** based on user history
- **Statistical insights** with average mood calculations

### 🔐 Privacy & Security
- **In-memory data processing** for development (configurable for production databases)
- **Structured data models** with Pydantic validation
- **Secure agent communication** through Fetch.ai protocols
- **Configurable data retention** policies

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- Fetch.ai uAgents framework
- Agentverse account for deployment

### Installation

1. **Clone the Mental Wellness Coach repository**:
```bash
git clone <repository-url>
cd mental-wellness-coach/agents
```

2. **Install dependencies**:
```bash
pip install uagents
```

3. **Configure the agent**:
```python
# Update mood-tracker-agent.py configuration
MOOD_TRACKER_SEED = "your_unique_seed_phrase_here"
MOOD_TRACKER_PORT = 8000
MOOD_TRACKER_ENDPOINT = ["http://your-endpoint.com:8000/submit"]
```

### Local Testing

```bash
python mood-tracker-agent.py
```

### Agentverse Deployment

1. **Prepare for deployment**:
   - Update the seed phrase to a unique value
   - Configure production endpoints
   - Set appropriate alert thresholds

2. **Deploy to Agentverse**:
   - Upload `mood-tracker-agent.py` to Agentverse
   - Configure environment variables
   - Start the agent service

## 📋 Data Models

### MoodReading
```python
{
    "user_id": str,              # Unique user identifier
    "mood_score": int,           # 1-10 mood scale
    "emotions": List[str],       # List of emotions
    "energy_level": int,         # Optional 1-10 energy scale
    "stress_level": int,         # Optional 1-10 stress scale
    "sleep_hours": float,        # Optional sleep duration
    "triggers": List[str],       # Optional mood triggers
    "notes": str,                # Optional text notes
    "timestamp": str             # ISO format timestamp
}
```

### MoodAnalysisResponse
```python
{
    "user_id": str,
    "mood_trend": str,           # "improving", "stable", "declining"
    "average_mood": float,       # Statistical average
    "needs_intervention": bool,  # Intervention recommendation
    "alerts": List[str],         # Active alerts
    "recommendations": List[str], # Personalized recommendations
    "patterns": List[str]        # Detected patterns
}
```

## 🔧 Configuration Options

### Alert Thresholds
```python
ALERT_THRESHOLDS = {
    "low_mood_threshold": 3,        # Mood scores ≤ 3 trigger alerts
    "consecutive_low_days": 3,      # Days of low mood before intervention
    "stress_threshold": 7,          # Stress levels ≥ 7 trigger alerts
    "energy_threshold": 2,          # Energy levels ≤ 2 trigger alerts
    "crisis_keywords": [            # Keywords for crisis detection
        "suicide", "hopeless", "worthless", "can't go on"
    ]
}
```

### Agent Settings
```python
MOOD_TRACKER_SEED = "your_unique_seed"    # Unique agent identifier
MOOD_TRACKER_PORT = 8000                  # Local testing port
MOOD_TRACKER_ENDPOINT = ["http://..."]    # Agent endpoints
```

## 💡 Usage Examples

### Sending a Mood Reading
```python
from uagents import Agent, Context

# Create mood reading
mood_data = MoodReading(
    user_id="user123",
    mood_score=6,
    emotions=["calm", "focused"],
    energy_level=7,
    stress_level=4,
    notes="Good day at work, feeling productive"
)

# Send to mood tracker agent
await ctx.send(mood_tracker_address, mood_data)
```

### Requesting Mood Analysis
```python
# Request 7-day analysis
analysis_request = MoodAnalysisRequest(
    user_id="user123",
    days=7
)

await ctx.send(mood_tracker_address, analysis_request)
```

## 🔄 Integration with Mental Wellness Ecosystem

### Agent Communication
The Mood Tracker Agent integrates seamlessly with other Mental Wellness Coach agents:

- **Conversation Coordinator**: Receives mood insights during chat sessions
- **Crisis Intervention Agent**: Triggered for emergency situations
- **Wellness Recommendation Agent**: Provides personalized activity suggestions
- **Analytics Agent**: Aggregates data for population-level insights

### API Integration
```python
# Example integration with Flask backend
@app.route('/api/mood-entry', methods=['POST'])
async def submit_mood():
    mood_data = request.json
    
    # Send to mood tracker agent
    response = await send_to_agent(mood_tracker_address, mood_data)
    
    return jsonify(response)
```

## 📊 Analytics & Monitoring

### Key Metrics Tracked
- **Mood score distributions** and trends
- **Crisis detection frequency** and response times
- **Intervention effectiveness** measurements
- **User engagement patterns** and retention

### Health Check Endpoints
```python
# Agent health monitoring
@mood_tracker.on_query("health")
async def health_check(ctx: Context):
    return {
        "status": "healthy",
        "uptime": get_uptime(),
        "memory_usage": get_memory_usage(),
        "active_users": len(mood_history)
    }
```

## ⚠️ Safety & Crisis Management

### Crisis Detection Pipeline
1. **Keyword Analysis**: Scan text for crisis indicators
2. **Pattern Recognition**: Identify concerning mood patterns
3. **Risk Assessment**: Calculate intervention priority
4. **Escalation Protocol**: Alert appropriate support systems

### Safety Features
- **Immediate crisis detection** with keyword scanning
- **Graduated intervention levels** based on risk assessment
- **Professional escalation pathways** for serious concerns
- **Emergency contact integration** (configurable)

### Crisis Response Example
```python
# Crisis detected in mood entry
if crisis_indicators:
    logger.critical(f"CRISIS DETECTED for user {user_id}")
    
    # Immediate recommendations
    recommendations.extend([
        "immediate_professional_support",
        "crisis_hotline_contact",
        "emergency_services_if_needed"
    ])
    
    # Alert coordination agent
    await ctx.send(coordinator_address, crisis_alert)
```

## 🛠️ Development & Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run agent tests
pytest tests/test_mood_tracker.py -v
```

### Development Mode
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Use test data
ENABLE_TEST_DATA = True
```

### Mock Data Generation
```python
# Generate test mood entries
test_moods = generate_test_mood_data(
    user_id="test_user",
    days=30,
    mood_range=(2, 8)
)
```

## 📈 Performance Optimization

### Memory Management
- **Sliding window storage**: Keep last 100 entries per user
- **Automatic cleanup**: Remove expired data
- **Efficient data structures**: Optimized for fast lookups

### Response Times
- **Target latency**: < 100ms for mood analysis
- **Batch processing**: Handle multiple requests efficiently
- **Caching**: Store frequent calculations

## 🔒 Security Considerations

### Data Protection
- **No persistent storage** of sensitive data in development
- **Encryption ready** for production deployment
- **Minimal data retention** policies
- **Secure agent communication** protocols

### Privacy Features
- **User data isolation** between different users
- **Configurable data retention** periods
- **Secure disposal** of sensitive information
- **Audit logging** for compliance

## 📚 Additional Resources

### Documentation
- [Mental Wellness Coach Project Overview](../docs/PLANNING.md)
- [Fetch.ai uAgents Documentation](https://docs.fetch.ai/)
- [Agentverse Deployment Guide](https://agentverse.ai/docs)

### Support & Community
- **GitHub Issues**: Report bugs and feature requests
- **Fetch.ai Discord**: Community support and discussions
- **Project Wiki**: Extended documentation and examples

## 🤝 Contributing

We welcome contributions to improve the Mental Wellness Mood Tracker Agent! Please see our [contributing guidelines](../CONTRIBUTING.md) for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Community guidelines

## 📄 License

This project is part of the Mental Wellness Coach ecosystem. See the main project [LICENSE](../LICENSE) for details.

---

**⚡ Ready to deploy?** Upload this agent to Agentverse and start providing 24/7 mental wellness support with intelligent mood tracking and crisis detection capabilities! 