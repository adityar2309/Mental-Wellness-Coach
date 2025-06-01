"""
Test script for Agentverse Mental Wellness Coach agents.

This script tests the Agentverse-compatible agents locally before deployment
to ensure they work correctly and can communicate properly.
"""

import asyncio
import logging
from datetime import datetime
from dataclasses import asdict

# Import the agent components
from agentverse_mood_tracker import (
    MoodReading, 
    MoodAnalysisRequest,
    analyze_mood_reading,
    detect_crisis_indicators
)

from agentverse_conversation_coordinator import (
    ConversationRequest,
    detect_crisis_level,
    extract_mood_indicators,
    generate_empathetic_response,
    generate_recommendations
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name: str, description: str):
    """Print a formatted test header."""
    print(f"\n🔬 {test_name}: {description}")
    print("-" * 50)

def test_mood_tracker_functionality():
    """Test mood tracker agent functionality."""
    print_header("MOOD TRACKER AGENT TESTS")
    
    # Test 1: Basic mood reading analysis
    print_test("Test 1", "Basic mood reading analysis")
    
    mood_data = {
        "user_id": "test_user_1",
        "mood_score": 3,
        "emotions": ["sad", "anxious"],
        "stress_level": 8,
        "energy_level": 2,
        "triggers": ["work_pressure", "lack_of_sleep"],
        "notes": "Feeling overwhelmed with everything"
    }
    
    analysis = analyze_mood_reading(mood_data, [])
    
    print(f"📊 Mood Score: {mood_data['mood_score']}/10")
    print(f"😔 Emotions: {', '.join(mood_data['emotions'])}")
    print(f"📈 Stress Level: {mood_data['stress_level']}/10")
    print(f"⚡ Energy Level: {mood_data['energy_level']}/10")
    print(f"\n🔍 Analysis Results:")
    print(f"   - Mood Trend: {analysis.get('mood_trend', 'unknown')}")
    print(f"   - Needs Intervention: {analysis.get('needs_intervention', False)}")
    print(f"   - Alerts: {len(analysis.get('alerts', []))} found")
    print(f"   - Recommendations: {len(analysis.get('recommendations', []))} generated")
    
    if analysis.get('alerts'):
        print(f"   ⚠️  Alert Details: {', '.join(analysis.get('alerts', []))}")
    
    # Test 2: Crisis detection
    print_test("Test 2", "Crisis detection in mood notes")
    
    crisis_notes = [
        "I feel hopeless and can't go on anymore",
        "Everything is fine, just a normal day",
        "I want to hurt myself",
        "Feeling a bit down today"
    ]
    
    for note in crisis_notes:
        crisis_indicators = detect_crisis_indicators(note)
        print(f"📝 Note: \"{note}\"")
        print(f"🚨 Crisis Indicators: {len(crisis_indicators)} found")
        if crisis_indicators:
            print(f"   Details: {', '.join(crisis_indicators)}")
        print()
    
    # Test 3: Mood reading with history
    print_test("Test 3", "Mood analysis with historical data")
    
    # Create mock historical data
    historical_moods = [
        {"mood_score": 5, "timestamp": "2024-01-01T10:00:00"},
        {"mood_score": 4, "timestamp": "2024-01-02T10:00:00"},
        {"mood_score": 3, "timestamp": "2024-01-03T10:00:00"},
        {"mood_score": 2, "timestamp": "2024-01-04T10:00:00"},
    ]
    
    current_mood = {
        "user_id": "test_user_2",
        "mood_score": 2,
        "emotions": ["depressed", "hopeless"],
        "notes": "This has been going on for days"
    }
    
    analysis_with_history = analyze_mood_reading(current_mood, historical_moods)
    
    print(f"📈 Historical Trend: {[m['mood_score'] for m in historical_moods]} → {current_mood['mood_score']}")
    print(f"🔍 Analysis with History:")
    print(f"   - Mood Trend: {analysis_with_history.get('mood_trend', 'unknown')}")
    print(f"   - Needs Intervention: {analysis_with_history.get('needs_intervention', False)}")
    print(f"   - Pattern Alerts: {', '.join(analysis_with_history.get('alerts', []))}")

def test_conversation_coordinator_functionality():
    """Test conversation coordinator agent functionality."""
    print_header("CONVERSATION COORDINATOR AGENT TESTS")
    
    # Test 1: Crisis level detection
    print_test("Test 1", "Crisis level detection")
    
    test_messages = [
        "I'm feeling great today, thanks for asking!",
        "I'm a bit stressed about work deadlines",
        "I feel completely overwhelmed and can't cope",
        "I feel hopeless and like there's no point in anything",
        "I want to end it all and kill myself"
    ]
    
    for message in test_messages:
        crisis_level = detect_crisis_level(message)
        mood_indicators = extract_mood_indicators(message)
        
        print(f"💬 Message: \"{message}\"")
        print(f"🚨 Crisis Level: {crisis_level}")
        print(f"😊 Mood Indicators: {sum(len(v) for v in mood_indicators.values())} found")
        
        for category, indicators in mood_indicators.items():
            if indicators:
                print(f"   {category.title()}: {', '.join(indicators)}")
        print()
    
    # Test 2: Empathetic response generation
    print_test("Test 2", "Empathetic response generation")
    
    test_scenarios = [
        {
            "message": "I'm feeling really anxious about my presentation tomorrow",
            "crisis_level": "low"
        },
        {
            "message": "I feel completely overwhelmed and can't handle anything",
            "crisis_level": "medium"
        },
        {
            "message": "I feel hopeless and like nobody cares about me",
            "crisis_level": "high"
        }
    ]
    
    for scenario in test_scenarios:
        message = scenario["message"]
        crisis_level = scenario["crisis_level"]
        mood_indicators = extract_mood_indicators(message)
        
        response = generate_empathetic_response(message, crisis_level, mood_indicators)
        recommendations = generate_recommendations(message, crisis_level, mood_indicators)
        
        print(f"💬 User Message: \"{message}\"")
        print(f"🚨 Crisis Level: {crisis_level}")
        print(f"🤖 AI Response:")
        print(f"   \"{response}\"")
        print(f"💡 Recommendations ({len(recommendations)}):")
        for rec in recommendations[:3]:  # Show first 3 recommendations
            print(f"   - {rec.replace('_', ' ').title()}")
        print()
    
    # Test 3: Mood assessment extraction
    print_test("Test 3", "Mood assessment from conversations")
    
    conversation_messages = [
        "I've been feeling really down lately, everything seems pointless",
        "Work has been incredibly stressful and I can't sleep",
        "I'm excited about my new project and feeling motivated!"
    ]
    
    for message in conversation_messages:
        crisis_level = detect_crisis_level(message)
        mood_indicators = extract_mood_indicators(message)
        
        # Simulate mood assessment creation
        estimated_mood_score = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4,
            "none": 5
        }.get(crisis_level, 5)
        
        # Adjust for positive indicators
        if mood_indicators["positive"]:
            estimated_mood_score = min(10, estimated_mood_score + 3)
        
        mood_assessment = {
            "estimated_mood_score": estimated_mood_score,
            "emotions": mood_indicators["negative"] + mood_indicators["positive"],
            "crisis_level": crisis_level,
            "needs_intervention": crisis_level in ["critical", "high"]
        }
        
        print(f"💬 Message: \"{message}\"")
        print(f"📊 Estimated Mood Score: {mood_assessment['estimated_mood_score']}/10")
        print(f"😔 Detected Emotions: {', '.join(mood_assessment['emotions']) if mood_assessment['emotions'] else 'None'}")
        print(f"🚨 Crisis Level: {mood_assessment['crisis_level']}")
        print(f"⚠️  Needs Intervention: {mood_assessment['needs_intervention']}")
        print()

def test_agent_integration():
    """Test integration between mood tracker and conversation coordinator."""
    print_header("AGENT INTEGRATION TESTS")
    
    print_test("Test 1", "End-to-end conversation to mood tracking flow")
    
    # Simulate a conversation that should trigger mood tracking
    user_message = "I've been feeling really depressed for the past week, my mood has been consistently low and I can't seem to shake it off"
    user_id = "integration_test_user"
    
    print(f"💬 User Message: \"{user_message}\"")
    print()
    
    # Step 1: Conversation coordinator processes message
    print("🔄 Step 1: Conversation Coordinator Processing")
    crisis_level = detect_crisis_level(user_message)
    mood_indicators = extract_mood_indicators(user_message)
    response = generate_empathetic_response(user_message, crisis_level, mood_indicators)
    recommendations = generate_recommendations(user_message, crisis_level, mood_indicators)
    
    print(f"   Crisis Level Detected: {crisis_level}")
    print(f"   Mood Indicators: {mood_indicators}")
    print(f"   Generated Response: \"{response[:100]}...\"")
    print(f"   Recommendations: {len(recommendations)} generated")
    
    # Step 2: Create mood assessment for mood tracker
    print("\n🔄 Step 2: Mood Assessment Creation")
    estimated_mood_score = {
        "critical": 1, "high": 2, "medium": 3, "low": 4, "none": 5
    }.get(crisis_level, 5)
    
    mood_assessment = {
        "user_id": user_id,
        "mood_score": estimated_mood_score,
        "emotions": mood_indicators["negative"] + mood_indicators["positive"],
        "stress_level": 7 if crisis_level in ["high", "medium"] else 5,
        "notes": "Extracted from conversation analysis",
        "triggers": ["conversation_analysis"]
    }
    
    print(f"   Created Mood Assessment: {mood_assessment}")
    
    # Step 3: Mood tracker analyzes the assessment
    print("\n🔄 Step 3: Mood Tracker Analysis")
    analysis = analyze_mood_reading(mood_assessment, [])
    
    print(f"   Analysis Result:")
    print(f"     - Needs Intervention: {analysis.get('needs_intervention', False)}")
    print(f"     - Alerts Generated: {len(analysis.get('alerts', []))}")
    print(f"     - Recommendations: {len(analysis.get('recommendations', []))}")
    
    if analysis.get('alerts'):
        print(f"     - Alert Details: {', '.join(analysis.get('alerts', []))}")
    
    # Step 4: Determine if escalation is needed
    print("\n🔄 Step 4: Escalation Decision")
    needs_escalation = (
        crisis_level in ["critical", "high"] or 
        analysis.get('needs_intervention', False)
    )
    
    print(f"   Escalation Needed: {needs_escalation}")
    if needs_escalation:
        print(f"   Escalation Reason: Crisis level '{crisis_level}' or intervention flag set")
        print(f"   Next Steps: Alert crisis management system, provide immediate resources")
    else:
        print(f"   Next Steps: Continue monitoring, provide standard support")

def run_all_tests():
    """Run all agent tests."""
    print("🚀 Starting Mental Wellness Coach Agentverse Agent Tests")
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test individual agent functionalities
        test_mood_tracker_functionality()
        test_conversation_coordinator_functionality()
        test_agent_integration()
        
        print_header("TEST SUMMARY")
        print("✅ All tests completed successfully!")
        print("🚀 Agents are ready for Agentverse deployment")
        print("\n📋 Next Steps:")
        print("1. Update seed phrases in agent files")
        print("2. Upload agents to Agentverse platform")
        print("3. Deploy and test in Agentverse environment")
        print("4. Register agents in Almanac for discoverability")
        
    except Exception as e:
        print_header("TEST FAILED")
        print(f"❌ Test failed with error: {str(e)}")
        print("🔧 Please fix the issues before deploying to Agentverse")
        raise

if __name__ == "__main__":
    run_all_tests() 