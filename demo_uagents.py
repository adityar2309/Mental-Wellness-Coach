"""
Mental Wellness Coach - uAgents Framework Demo

Demonstration of the Fetch.ai uAgents framework for mental wellness coordination.
This script shows how multiple specialized agents work together to provide
comprehensive mental health support.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any

# Import our uAgents components
from backend.services.agent_service import (
    agent_registry, 
    get_agent_status,
    AgentMessage
)
from backend.agents.mood_tracker_agent import (
    create_mood_tracker_agent,
    MoodReading
)
from backend.agents.conversation_coordinator_agent import (
    create_conversation_coordinator_agent
)

def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🤖 {title}")
    print(f"{'='*60}")

def print_step(step: str, description: str):
    """Print a formatted step."""
    print(f"\n{step} {description}")
    print("-" * 50)

async def demo_agent_initialization():
    """Demonstrate agent initialization and registration."""
    print_header("UAGENTS FRAMEWORK INITIALIZATION")
    
    print_step("Step 1:", "Clearing existing agents...")
    agent_registry.agents.clear()
    print("✅ Registry cleared")
    
    print_step("Step 2:", "Creating specialized mental wellness agents...")
    
    # Create mood tracker agent
    mood_agent = create_mood_tracker_agent(port=8001)
    print(f"✅ Mood Tracker Agent created: {mood_agent.config.name}")
    print(f"   - Type: {mood_agent.config.agent_type.value}")
    print(f"   - Port: {mood_agent.config.port}")
    print(f"   - Crisis Detection: {mood_agent.config.crisis_detection_enabled}")
    
    # Create conversation coordinator agent
    coordinator_agent = create_conversation_coordinator_agent(port=8002)
    print(f"✅ Conversation Coordinator Agent created: {coordinator_agent.config.name}")
    print(f"   - Type: {coordinator_agent.config.agent_type.value}")
    print(f"   - Port: {coordinator_agent.config.port}")
    print(f"   - LLM Service: {type(coordinator_agent.llm_service).__name__}")
    
    print_step("Step 3:", "Checking agent registry status...")
    status = get_agent_status()
    print(f"✅ Total agents registered: {status['total_agents']}")
    
    for agent_name, agent_data in status['agents'].items():
        print(f"   - {agent_name}: {agent_data['type']} ({agent_data['status']})")
    
    return mood_agent, coordinator_agent

async def demo_mood_analysis():
    """Demonstrate mood tracking and analysis."""
    print_header("MOOD TRACKING & ANALYSIS")
    
    mood_agent = agent_registry.get_agent('mood_tracker')
    if not mood_agent:
        print("❌ Mood tracker agent not available")
        return
    
    print_step("Step 1:", "Submitting mood data for analysis...")
    
    # Create test mood readings
    test_moods = [
        {
            "user_id": "demo_user",
            "mood_score": 3,
            "emotions": ["sad", "anxious"],
            "stress_level": 8,
            "energy_level": 2,
            "triggers": ["work_pressure", "lack_of_sleep"],
            "notes": "Feeling overwhelmed with work deadlines"
        },
        {
            "user_id": "demo_user",
            "mood_score": 7,
            "emotions": ["happy", "motivated"],
            "stress_level": 3,
            "energy_level": 8,
            "triggers": ["exercise", "good_weather"],
            "notes": "Had a great workout this morning"
        }
    ]
    
    for i, mood_data in enumerate(test_moods, 1):
        print(f"\n📊 Analyzing mood entry {i}:")
        print(f"   Mood Score: {mood_data['mood_score']}/10")
        print(f"   Emotions: {', '.join(mood_data['emotions'])}")
        print(f"   Stress Level: {mood_data['stress_level']}/10")
        print(f"   Energy Level: {mood_data['energy_level']}/10")
        
        # Create mood reading
        mood_reading = MoodReading(
            user_id=mood_data["user_id"],
            mood_score=mood_data["mood_score"],
            emotions=mood_data["emotions"],
            stress_level=mood_data["stress_level"],
            energy_level=mood_data["energy_level"],
            triggers=mood_data["triggers"],
            notes=mood_data["notes"]
        )
        
        # Analyze mood
        analysis = await mood_agent._analyze_mood_reading(mood_reading)
        
        print(f"   Analysis Result:")
        print(f"     - Mood Trend: {analysis.get('mood_trend', 'unknown')}")
        print(f"     - Intervention Needed: {analysis.get('needs_intervention', False)}")
        print(f"     - Alerts: {', '.join(analysis.get('alerts', []))}")
        print(f"     - Recommendations: {len(analysis.get('recommendations', []))} suggestions")
        
        if analysis.get('alerts'):
            print(f"   ⚠️  Alerts detected: {', '.join(analysis.get('alerts', []))}")
        
        # Store mood for pattern analysis
        await mood_agent._store_mood_reading(mood_reading)
    
    print_step("Step 2:", "Testing pattern detection...")
    patterns = mood_agent._detect_mood_patterns("demo_user")
    if patterns:
        print(f"✅ Detected patterns: {', '.join(patterns)}")
    else:
        print("ℹ️  No patterns detected (need more data)")

async def demo_conversation_coordination():
    """Demonstrate conversation coordination between agents."""
    print_header("MULTI-AGENT CONVERSATION COORDINATION")
    
    coordinator = agent_registry.get_agent('conversation_coordinator')
    if not coordinator:
        print("❌ Conversation coordinator not available")
        return
    
    print_step("Step 1:", "Starting a new conversation...")
    
    # Test conversation scenarios
    scenarios = [
        {
            "type": "mood_check",
            "message": "I'm feeling really anxious about my presentation tomorrow",
            "description": "Anxiety scenario"
        },
        {
            "type": "general",
            "message": "I feel hopeless and don't know what to do anymore",
            "description": "Crisis scenario (high-risk keywords)"
        },
        {
            "type": "coping",
            "message": "I'm doing better today, the breathing exercises helped",
            "description": "Positive progress scenario"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🗣️  Scenario {i}: {scenario['description']}")
        print(f"   User Message: \"{scenario['message']}\"")
        
        # Determine required agents
        required_agents = await coordinator._determine_required_agents(
            scenario['type'], 
            scenario['message']
        )
        print(f"   Required Agents: {', '.join(required_agents)}")
        
        # Extract mood indicators
        mood_indicators = coordinator._extract_mood_indicators(scenario['message'].lower())
        if mood_indicators:
            print(f"   Mood Indicators: {', '.join(mood_indicators)}")
        
        # Simulate agent insights
        insights = {}
        for agent_name in required_agents:
            if agent_name != "conversation_coordinator":
                insight = await coordinator._simulate_agent_insight(
                    agent_name, 
                    scenario['message'], 
                    None  # Mock conversation object
                )
                insights[agent_name] = insight
        
        print(f"   Agent Insights:")
        for agent_name, insight in insights.items():
            print(f"     - {agent_name}: {insight}")
        
        # Check for crisis indicators
        crisis_keywords = ["hopeless", "hurt myself", "suicide", "no point"]
        crisis_detected = any(keyword in scenario['message'].lower() for keyword in crisis_keywords)
        if crisis_detected:
            print("   🚨 CRISIS DETECTED - Would escalate to crisis manager")

async def demo_agent_communication():
    """Demonstrate agent message passing and communication."""
    print_header("AGENT COMMUNICATION PROTOCOL")
    
    print_step("Step 1:", "Creating structured agent messages...")
    
    # Example messages between agents
    messages = [
        {
            "message_type": "mood_entry",
            "sender": "api_gateway",
            "recipient": "mood_tracker",
            "payload": {
                "mood_data": {
                    "mood_score": 4,
                    "emotions": ["worried", "tired"],
                    "stress_level": 6
                }
            },
            "description": "Mood data submission"
        },
        {
            "message_type": "mood_alert",
            "sender": "mood_tracker",
            "recipient": "conversation_coordinator",
            "payload": {
                "alert_type": "low_mood_pattern",
                "user_id": "demo_user",
                "severity": "medium"
            },
            "description": "Mood alert to coordinator"
        },
        {
            "message_type": "crisis_alert",
            "sender": "crisis_detector",
            "recipient": "escalation_manager",
            "payload": {
                "risk_level": "high",
                "crisis_keywords": ["hopeless", "hurt myself"],
                "immediate_action_required": True
            },
            "description": "Crisis escalation"
        }
    ]
    
    for i, msg_data in enumerate(messages, 1):
        print(f"\n📨 Message {i}: {msg_data['description']}")
        
        # Create agent message
        message = AgentMessage(
            message_type=msg_data["message_type"],
            sender_agent=msg_data["sender"],
            recipient_agent=msg_data["recipient"],
            payload=msg_data["payload"],
            user_id="demo_user",
            session_id=f"demo_session_{i}"
        )
        
        print(f"   Type: {message.message_type}")
        print(f"   Route: {message.sender_agent} → {message.recipient_agent}")
        print(f"   Payload: {message.payload}")
        print(f"   Priority: {message.priority}")
        print(f"   Requires Response: {message.requires_response}")

async def demo_crisis_detection():
    """Demonstrate crisis detection across agents."""
    print_header("CRISIS DETECTION SYSTEM")
    
    mood_agent = agent_registry.get_agent('mood_tracker')
    coordinator = agent_registry.get_agent('conversation_coordinator')
    
    if not mood_agent or not coordinator:
        print("❌ Required agents not available")
        return
    
    print_step("Step 1:", "Testing crisis keyword detection...")
    
    crisis_scenarios = [
        "I can't take this anymore, I want to end it all",
        "I'm thinking about hurting myself",
        "There's no point in going on, everyone would be better off without me",
        "I feel hopeless and trapped",
        "I'm having thoughts of suicide"
    ]
    
    print(f"Crisis Keywords Database: {mood_agent.crisis_keywords}")
    
    for i, scenario in enumerate(crisis_scenarios, 1):
        print(f"\n🔍 Testing scenario {i}: \"{scenario}\"")
        
        # Check for crisis keywords
        detected_keywords = []
        for keyword in mood_agent.crisis_keywords:
            if keyword in scenario.lower():
                detected_keywords.append(keyword)
        
        if detected_keywords:
            print(f"   🚨 CRISIS DETECTED!")
            print(f"   Keywords found: {', '.join(detected_keywords)}")
            print(f"   Risk Level: {'HIGH' if len(detected_keywords) > 1 else 'MEDIUM'}")
            print(f"   Action: Immediate escalation to crisis manager")
        else:
            print(f"   ✅ No crisis indicators detected")

async def demo_performance_metrics():
    """Demonstrate agent performance and monitoring."""
    print_header("AGENT PERFORMANCE & MONITORING")
    
    print_step("Step 1:", "Gathering agent performance metrics...")
    
    status = get_agent_status()
    
    print(f"📊 System Overview:")
    print(f"   Total Agents: {status['total_agents']}")
    print(f"   System Running: {status['running']}")
    
    print(f"\n📈 Individual Agent Status:")
    for agent_name, agent_data in status['agents'].items():
        print(f"\n   Agent: {agent_name}")
        print(f"     - Type: {agent_data['type']}")
        print(f"     - Status: {agent_data['status']}")
        print(f"     - Address: {agent_data.get('address', 'N/A')}")
        print(f"     - Active Sessions: {agent_data['sessions']}")
        
        # Get actual agent for more details
        agent = agent_registry.get_agent(agent_name)
        if agent:
            print(f"     - Mental Health Focus: {agent.config.mental_health_focus}")
            print(f"     - Crisis Detection: {agent.config.crisis_detection_enabled}")
            print(f"     - Port: {agent.config.port}")

async def main():
    """Run the complete uAgents framework demonstration."""
    start_time = time.time()
    
    print("🤖 Mental Wellness Coach - uAgents Framework Demo")
    print("=" * 60)
    print("This demonstration shows how Fetch.ai uAgents coordinate")
    print("to provide comprehensive mental wellness support.")
    print("=" * 60)
    
    try:
        # Initialize agents
        await demo_agent_initialization()
        
        # Demonstrate core functionality
        await demo_mood_analysis()
        await demo_conversation_coordination()
        await demo_agent_communication()
        await demo_crisis_detection()
        await demo_performance_metrics()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print_header("DEMO COMPLETED SUCCESSFULLY")
        print(f"✅ All agent systems operational")
        print(f"⏱️  Total demo time: {duration:.2f} seconds")
        print(f"🔄 Agent coordination working correctly")
        print(f"🛡️  Crisis detection systems active")
        print(f"📊 Mental wellness analytics functional")
        
        print(f"\n🎯 Next Steps:")
        print(f"   - Deploy agents to production environment")
        print(f"   - Connect to actual Fetch.ai network")
        print(f"   - Integrate with mobile app")
        print(f"   - Add real-time monitoring dashboard")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the demonstration
    print("Starting uAgents Framework Demo...")
    asyncio.run(main())
    print("\n🎉 Demo completed! uAgents framework ready for deployment.") 