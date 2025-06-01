# Mental Wellness Coach - Agentverse Deployment Guide

This guide provides step-by-step instructions for deploying the Mental Wellness Coach agents to the [Agentverse platform](https://innovationlab.fetch.ai/resources/docs/agentverse).

## 🌟 Overview

The Mental Wellness Coach uses two specialized uAgents that work together to provide comprehensive mental health support:

1. **Mood Tracker Agent** (`agentverse_mood_tracker.py`) - Handles mood tracking, pattern analysis, and crisis detection
2. **Conversation Coordinator Agent** (`agentverse_conversation_coordinator.py`) - Manages AI conversations and coordinates with other agents

## 📋 Prerequisites

### 1. Agentverse Account Setup
- Create an account at [Agentverse](https://agentverse.ai)
- Verify your email address
- Complete profile setup

### 2. Wallet & Funding
- Set up a Fetch.ai wallet
- Ensure sufficient FET tokens for agent deployment (minimum 1 FET per agent)
- Note your wallet address and private key securely

### 3. Development Environment
- Python 3.8+ installed
- uAgents framework (`pip install uagents>=0.8.0`)
- Access to the agent source files

## 🚀 Deployment Steps

### Step 1: Prepare Agent Files

1. **Update Seed Phrases** (CRITICAL SECURITY STEP):
   ```python
   # In agentverse_mood_tracker.py
   MOOD_TRACKER_SEED = "your_unique_mood_tracker_seed_phrase_here"
   
   # In agentverse_conversation_coordinator.py  
   COORDINATOR_SEED = "your_unique_coordinator_seed_phrase_here"
   ```
   
   **⚠️ Security Note**: Use unique, secure seed phrases. Never share these publicly.

2. **Configure Agent Addresses**:
   - Run each agent locally once to get their addresses
   - Note the addresses for inter-agent communication setup

### Step 2: Deploy Mood Tracker Agent

1. **Access Agentverse IDE**:
   - Go to [Agentverse](https://agentverse.ai)
   - Click "Create New Agent"

2. **Agent Configuration**:
   - **Name**: `mental-wellness-mood-tracker`
   - **Description**: "Specialized agent for mood tracking, pattern analysis, and crisis detection"
   - **Category**: Mental Health

3. **Upload Code**:
   - Copy the entire content of `agentverse_mood_tracker.py`
   - Paste into the Agentverse code editor
   - Ensure all imports are correctly resolved

4. **Agent Settings**:
   ```json
   {
     "interval": 30,
     "funding_required": true,
     "public": true,
     "tags": ["mental-health", "mood-tracking", "wellness"]
   }
   ```

5. **Deploy & Test**:
   - Click "Deploy Agent"
   - Monitor logs for successful startup
   - Test with sample mood data

### Step 3: Deploy Conversation Coordinator Agent

1. **Create Second Agent**:
   - Click "Create New Agent" again
   - **Name**: `mental-wellness-conversation-coordinator`
   - **Description**: "AI conversation coordinator providing empathetic support and crisis intervention"

2. **Upload Code**:
   - Copy content of `agentverse_conversation_coordinator.py`
   - Paste into editor
   - Verify all dependencies

3. **Agent Settings**:
   ```json
   {
     "interval": 10,
     "funding_required": true,
     "public": true,
     "tags": ["mental-health", "conversation", "ai-therapy"]
   }
   ```

4. **Deploy & Test**:
   - Deploy the agent
   - Test conversation functionality
   - Verify crisis detection works

### Step 4: Configure Inter-Agent Communication

1. **Update Agent Addresses**:
   - Get deployed agent addresses from Agentverse
   - Update any hardcoded addresses in the code

2. **Test Communication**:
   - Send test messages between agents
   - Verify mood data flows from coordinator to tracker
   - Test alert escalation from tracker to coordinator

### Step 5: Register in Almanac

1. **Agent Registration**:
   - Both agents should auto-register in the Fetch.ai Almanac
   - Verify registration status in Agentverse dashboard

2. **Discoverability**:
   - Set appropriate tags and descriptions
   - Enable public discovery if desired
   - Configure service pricing (can be free)

## 🔧 Configuration Options

### Environment Variables (Set in Agentverse)

```env
# Mood Tracker Configuration
MOOD_TRACKER_CRISIS_THRESHOLD=3
MOOD_TRACKER_DATA_RETENTION_DAYS=30
MOOD_TRACKER_ALERT_FREQUENCY=60

# Conversation Coordinator Configuration
COORDINATOR_RESPONSE_TIMEOUT=5000
COORDINATOR_CRISIS_ESCALATION=true
COORDINATOR_EMPATHY_LEVEL=high
```

### Agent Metadata

```json
{
  "mood_tracker": {
    "capabilities": ["mood_analysis", "pattern_detection", "crisis_alerts"],
    "data_retention": "30_days",
    "privacy_level": "high"
  },
  "conversation_coordinator": {
    "capabilities": ["conversation_ai", "empathy", "crisis_intervention"],
    "response_time": "< 1000ms",
    "crisis_detection": "multi_level"
  }
}
```

## 🔐 Security Considerations

### 1. Data Privacy
- All mood data is processed in-memory (not persisted)
- No personal information is stored permanently
- Crisis detection uses pattern matching, not data retention

### 2. Access Control
- Agents use secure authentication
- Communication is encrypted
- Seed phrases must be kept secure

### 3. Compliance
- Designed with HIPAA awareness (not HIPAA certified)
- Privacy-first architecture
- Audit logging enabled

## 📊 Monitoring & Maintenance

### Health Checks
- Monitor agent uptime in Agentverse dashboard
- Check error logs regularly
- Verify inter-agent communication

### Performance Metrics
- Response time monitoring
- Message processing rates
- Crisis detection accuracy

### Updates & Patches
- Deploy code updates through Agentverse IDE
- Test thoroughly in staging environment
- Maintain backward compatibility

## 🆘 Crisis Management Integration

### Emergency Protocols
The agents are configured to detect and respond to mental health crises:

1. **Detection Levels**:
   - **Critical**: Immediate intervention required
   - **High**: Professional support recommended
   - **Medium**: Enhanced monitoring
   - **Low**: Standard support

2. **Response Actions**:
   - Automatic crisis resource provision
   - Professional referral recommendations
   - Emergency contact suggestions (988 Suicide & Crisis Lifeline)

3. **Escalation Pathways**:
   - Internal alert systems
   - Webhook notifications to external systems
   - Integration with crisis intervention services

## 🧪 Testing Your Deployment

### 1. Basic Functionality Test
```python
# Test mood entry
mood_data = {
    "user_id": "test_user",
    "mood_score": 3,
    "emotions": ["sad", "anxious"],
    "notes": "Feeling overwhelmed with work"
}
```

### 2. Crisis Detection Test
```python
# Test crisis detection
crisis_message = {
    "user_id": "test_user", 
    "message": "I feel hopeless and can't go on",
    "session_id": "test_session"
}
```

### 3. Inter-Agent Communication Test
- Send mood data to tracker
- Verify coordinator receives alerts
- Check recommendation generation

## 📞 Support & Resources

### Documentation
- [Agentverse Documentation](https://innovationlab.fetch.ai/resources/docs/agentverse)
- [uAgents Framework Guide](https://fetch.ai/docs/uAgents)

### Crisis Resources
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

### Technical Support
- Agentverse Support: support@fetch.ai
- Community Forum: [Fetch.ai Discord](https://discord.gg/fetchai)

## ⚡ Quick Start Commands

```bash
# 1. Test agents locally first
python agentverse_mood_tracker.py
python agentverse_conversation_coordinator.py

# 2. Check agent addresses
# Note the addresses printed on startup

# 3. Upload to Agentverse
# Use the web interface at agentverse.ai

# 4. Monitor deployment
# Check logs and health status in dashboard
```

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ Both agents are online and responsive in Agentverse
- ✅ Mood tracking accepts and processes entries
- ✅ Conversation coordinator provides empathetic responses
- ✅ Crisis detection triggers appropriate alerts
- ✅ Inter-agent communication works seamlessly
- ✅ Agents are discoverable in the Almanac

---

**⚠️ Important**: This system provides mental health support but is not a replacement for professional medical care. Ensure appropriate disclaimers and emergency procedures are in place.

**🔒 Security Reminder**: Never commit seed phrases to version control. Keep them secure and private.

For questions or issues with deployment, please refer to the [Agentverse documentation](https://innovationlab.fetch.ai/resources/docs/agentverse) or contact support. 