"""
Test script for deployed Mental Wellness Mood Tracker Agent on Agentverse.

This script tests the deployed mood tracker agent by sending various types of 
mood readings and analysis requests to verify functionality, crisis detection,
and response quality.

Agent Address: test-agent://agent1qtv48wjwflhu0mk5wev5jft5nlngtd84tpvjt6ckv63ynncjpfckj5xss8q
"""

import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import json

from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test agent configuration
TEST_AGENT_SEED = "mood_tracker_test_agent_seed_phrase_12345"
TEST_AGENT_PORT = 8001
TEST_AGENT_ENDPOINT = ["http://127.0.0.1:8001/submit"]

# Deployed agent address to test
DEPLOYED_AGENT_ADDRESS = "agent1qtv48wjwflhu0mk5wev5jft5nlngtd84tpvjt6ckv63ynncjpfckj5xss8q"

# Create test agent
test_agent = Agent(
    name="mood_tracker_tester",
    seed=TEST_AGENT_SEED,
    port=TEST_AGENT_PORT,
    endpoint=TEST_AGENT_ENDPOINT,
)

# Fund agent if needed
fund_agent_if_low(test_agent.wallet.address())

@dataclass
class MoodReading(Model):
    """Structured mood reading data model for Agentverse."""
    user_id: str
    mood_score: int  # 1-10 scale
    emotions: List[str]
    energy_level: Optional[int] = None
    stress_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    triggers: Optional[List[str]] = None
    notes: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class MoodAnalysisRequest(Model):
    """Request for mood analysis."""
    user_id: str
    days: Optional[int] = 7

@dataclass
class MoodEntryResponse(Model):
    """Response after processing a mood entry."""
    status: str
    mood_score: int
    analysis: Dict[str, Any]
    recommendations: List[str]
    alerts: List[str]

@dataclass
class MoodAnalysisResponse(Model):
    """Response containing mood analysis results."""
    user_id: str
    mood_trend: str
    average_mood: float
    needs_intervention: bool
    alerts: List[str]
    recommendations: List[str]
    patterns: List[str]

# Test results tracking
test_results = {
    "tests_run": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "responses_received": [],
    "errors": []
}

def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name: str, description: str):
    """Print a formatted test header."""
    print(f"\n🔬 {test_name}: {description}")
    print("-" * 50)

def log_test_result(test_name: str, passed: bool, details: str = ""):
    """Log test result."""
    test_results["tests_run"] += 1
    if passed:
        test_results["tests_passed"] += 1
        logger.info(f"✅ {test_name} PASSED - {details}")
    else:
        test_results["tests_failed"] += 1
        logger.error(f"❌ {test_name} FAILED - {details}")

# Create test protocol
test_protocol = Protocol("Mood Tracker Testing Protocol")

@test_protocol.on_message(model=MoodEntryResponse)
async def handle_mood_entry_response(ctx: Context, sender: str, msg: MoodEntryResponse):
    """Handle response from mood tracker agent."""
    try:
        ctx.logger.info(f"Received mood entry response from {sender}")
        
        # Store response for analysis
        response_data = {
            "type": "MoodEntryResponse",
            "sender": sender,
            "timestamp": datetime.utcnow().isoformat(),
            "data": asdict(msg)
        }
        test_results["responses_received"].append(response_data)
        
        # Analyze response quality
        if msg.status == "success":
            log_test_result(
                "Mood Entry Response", 
                True, 
                f"Status: {msg.status}, Alerts: {len(msg.alerts)}, Recommendations: {len(msg.recommendations)}"
            )
        else:
            log_test_result(
                "Mood Entry Response", 
                False, 
                f"Status: {msg.status}, Analysis: {msg.analysis}"
            )
        
        # Print response details
        print(f"📊 Mood Entry Response:")
        print(f"   Status: {msg.status}")
        print(f"   Mood Score: {msg.mood_score}")
        print(f"   Alerts: {len(msg.alerts)} found")
        if msg.alerts:
            print(f"   Alert Details: {', '.join(msg.alerts)}")
        print(f"   Recommendations: {len(msg.recommendations)} provided")
        if msg.recommendations:
            print(f"   Recommendation Details: {', '.join(msg.recommendations[:3])}")
        
        # Check for crisis detection
        crisis_detected = any("crisis" in alert for alert in msg.alerts)
        if crisis_detected:
            print(f"🚨 CRISIS DETECTED in response!")
            log_test_result("Crisis Detection", True, "Crisis properly detected")
        
    except Exception as e:
        ctx.logger.error(f"Error handling mood entry response: {str(e)}")
        test_results["errors"].append(f"Response handling error: {str(e)}")

@test_protocol.on_message(model=MoodAnalysisResponse)
async def handle_mood_analysis_response(ctx: Context, sender: str, msg: MoodAnalysisResponse):
    """Handle mood analysis response from agent."""
    try:
        ctx.logger.info(f"Received mood analysis response from {sender}")
        
        # Store response for analysis
        response_data = {
            "type": "MoodAnalysisResponse",
            "sender": sender,
            "timestamp": datetime.utcnow().isoformat(),
            "data": asdict(msg)
        }
        test_results["responses_received"].append(response_data)
        
        # Analyze response quality
        if msg.user_id:
            log_test_result(
                "Mood Analysis Response", 
                True, 
                f"Trend: {msg.mood_trend}, Avg: {msg.average_mood}, Intervention: {msg.needs_intervention}"
            )
        else:
            log_test_result("Mood Analysis Response", False, "Missing user_id in response")
        
        # Print analysis details
        print(f"📈 Mood Analysis Response:")
        print(f"   User ID: {msg.user_id}")
        print(f"   Mood Trend: {msg.mood_trend}")
        print(f"   Average Mood: {msg.average_mood}")
        print(f"   Needs Intervention: {msg.needs_intervention}")
        print(f"   Alerts: {len(msg.alerts)} found")
        print(f"   Patterns: {len(msg.patterns)} identified")
        print(f"   Recommendations: {len(msg.recommendations)} provided")
        
    except Exception as e:
        ctx.logger.error(f"Error handling mood analysis response: {str(e)}")
        test_results["errors"].append(f"Analysis response error: {str(e)}")

# Include protocol in test agent
test_agent.include(test_protocol)

async def test_basic_mood_entry():
    """Test basic mood entry functionality."""
    print_test("Test 1", "Basic mood entry with moderate stress")
    
    mood_reading = MoodReading(
        user_id="test_user_basic",
        mood_score=6,
        emotions=["content", "slightly_anxious"],
        energy_level=7,
        stress_level=5,
        sleep_hours=7.5,
        triggers=["work_deadline"],
        notes="Generally feeling okay, just a bit worried about the upcoming deadline"
    )
    
    try:
        await test_agent.send(DEPLOYED_AGENT_ADDRESS, mood_reading)
        logger.info("✅ Basic mood entry sent successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send basic mood entry: {str(e)}")
        test_results["errors"].append(f"Basic mood entry error: {str(e)}")
        return False

async def test_low_mood_entry():
    """Test mood entry with low mood scores."""
    print_test("Test 2", "Low mood entry with multiple triggers")
    
    mood_reading = MoodReading(
        user_id="test_user_low_mood",
        mood_score=2,
        emotions=["sad", "overwhelmed", "anxious"],
        energy_level=2,
        stress_level=9,
        sleep_hours=4.0,
        triggers=["work_pressure", "relationship_issues", "financial_stress"],
        notes="Feeling really down today. Everything seems too much to handle and I barely slept"
    )
    
    try:
        await test_agent.send(DEPLOYED_AGENT_ADDRESS, mood_reading)
        logger.info("✅ Low mood entry sent successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send low mood entry: {str(e)}")
        test_results["errors"].append(f"Low mood entry error: {str(e)}")
        return False

async def test_crisis_mood_entry():
    """Test mood entry with crisis indicators."""
    print_test("Test 3", "Crisis mood entry with concerning language")
    
    mood_reading = MoodReading(
        user_id="test_user_crisis",
        mood_score=1,
        emotions=["hopeless", "worthless", "desperate"],
        energy_level=1,
        stress_level=10,
        sleep_hours=2.0,
        triggers=["everything", "life_situation"],
        notes="I feel completely hopeless and like there's no point in continuing. I can't go on like this anymore"
    )
    
    try:
        await test_agent.send(DEPLOYED_AGENT_ADDRESS, mood_reading)
        logger.info("✅ Crisis mood entry sent successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send crisis mood entry: {str(e)}")
        test_results["errors"].append(f"Crisis mood entry error: {str(e)}")
        return False

async def test_positive_mood_entry():
    """Test mood entry with positive indicators."""
    print_test("Test 4", "Positive mood entry")
    
    mood_reading = MoodReading(
        user_id="test_user_positive",
        mood_score=9,
        emotions=["happy", "energetic", "optimistic"],
        energy_level=9,
        stress_level=2,
        sleep_hours=8.0,
        triggers=["good_news", "exercise"],
        notes="Had a fantastic day! Got some great news and feeling really positive about everything"
    )
    
    try:
        await test_agent.send(DEPLOYED_AGENT_ADDRESS, mood_reading)
        logger.info("✅ Positive mood entry sent successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send positive mood entry: {str(e)}")
        test_results["errors"].append(f"Positive mood entry error: {str(e)}")
        return False

async def test_mood_analysis_request():
    """Test mood analysis request functionality."""
    print_test("Test 5", "Mood analysis request for user history")
    
    analysis_request = MoodAnalysisRequest(
        user_id="test_user_basic",
        days=7
    )
    
    try:
        await test_agent.send(DEPLOYED_AGENT_ADDRESS, analysis_request)
        logger.info("✅ Mood analysis request sent successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send mood analysis request: {str(e)}")
        test_results["errors"].append(f"Mood analysis request error: {str(e)}")
        return False

async def test_invalid_mood_entry():
    """Test handling of invalid mood entry."""
    print_test("Test 6", "Invalid mood entry with out-of-range values")
    
    # This should trigger validation or error handling
    mood_reading = MoodReading(
        user_id="test_user_invalid",
        mood_score=15,  # Invalid: should be 1-10
        emotions=["invalid_emotion_test"],
        energy_level=-1,  # Invalid: should be positive
        stress_level=20,  # Invalid: should be 1-10
        sleep_hours=-2.0,  # Invalid: should be positive
        notes="Testing invalid data handling"
    )
    
    try:
        await test_agent.send(DEPLOYED_AGENT_ADDRESS, mood_reading)
        logger.info("✅ Invalid mood entry sent successfully (testing error handling)")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send invalid mood entry: {str(e)}")
        test_results["errors"].append(f"Invalid mood entry error: {str(e)}")
        return False

@test_agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Test agent startup handler."""
    ctx.logger.info("🚀 Mood Tracker Test Agent starting up...")
    ctx.logger.info(f"Test Agent Address: {test_agent.address}")
    ctx.logger.info(f"Target Agent Address: {DEPLOYED_AGENT_ADDRESS}")
    ctx.logger.info("Ready to test deployed mood tracker agent!")

async def run_all_tests():
    """Run comprehensive test suite for deployed agent."""
    print_header("MOOD TRACKER AGENT DEPLOYMENT TESTS")
    print(f"🎯 Testing deployed agent: {DEPLOYED_AGENT_ADDRESS}")
    print(f"🤖 Test agent address: {test_agent.address}")
    
    # Allow some time for agent startup
    await asyncio.sleep(2)
    
    # Run all tests
    test_functions = [
        test_basic_mood_entry,
        test_low_mood_entry,
        test_crisis_mood_entry,
        test_positive_mood_entry,
        test_mood_analysis_request,
        test_invalid_mood_entry
    ]
    
    print(f"\n🏃 Running {len(test_functions)} test scenarios...")
    
    for test_func in test_functions:
        try:
            await test_func()
            # Wait between tests for responses
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Test {test_func.__name__} failed with exception: {str(e)}")
            test_results["errors"].append(f"{test_func.__name__}: {str(e)}")
    
    # Wait for responses to come back
    print("\n⏳ Waiting for responses from deployed agent...")
    await asyncio.sleep(10)
    
    # Print test summary
    print_test_summary()

def print_test_summary():
    """Print comprehensive test results summary."""
    print_header("TEST RESULTS SUMMARY")
    
    print(f"📊 Test Statistics:")
    print(f"   Total Tests Run: {test_results['tests_run']}")
    print(f"   Tests Passed: {test_results['tests_passed']}")
    print(f"   Tests Failed: {test_results['tests_failed']}")
    print(f"   Success Rate: {(test_results['tests_passed'] / max(test_results['tests_run'], 1)) * 100:.1f}%")
    
    print(f"\n📨 Response Statistics:")
    print(f"   Responses Received: {len(test_results['responses_received'])}")
    
    mood_responses = [r for r in test_results['responses_received'] if r['type'] == 'MoodEntryResponse']
    analysis_responses = [r for r in test_results['responses_received'] if r['type'] == 'MoodAnalysisResponse']
    
    print(f"   Mood Entry Responses: {len(mood_responses)}")
    print(f"   Analysis Responses: {len(analysis_responses)}")
    
    # Analyze response quality
    if mood_responses:
        successful_moods = [r for r in mood_responses if r['data']['status'] == 'success']
        print(f"   Successful Mood Responses: {len(successful_moods)}/{len(mood_responses)}")
        
        # Check crisis detection
        crisis_responses = [r for r in mood_responses if any('crisis' in alert for alert in r['data']['alerts'])]
        print(f"   Crisis Detections: {len(crisis_responses)}")
    
    # Print errors if any
    if test_results['errors']:
        print(f"\n❌ Errors Encountered ({len(test_results['errors'])}):")
        for i, error in enumerate(test_results['errors'], 1):
            print(f"   {i}. {error}")
    
    # Print sample responses
    if test_results['responses_received']:
        print(f"\n📋 Sample Response Analysis:")
        for response in test_results['responses_received'][:2]:  # Show first 2 responses
            print(f"   Response Type: {response['type']}")
            print(f"   Timestamp: {response['timestamp']}")
            if response['type'] == 'MoodEntryResponse':
                data = response['data']
                print(f"   Status: {data['status']}")
                print(f"   Alerts: {len(data['alerts'])}")
                print(f"   Recommendations: {len(data['recommendations'])}")
            print()

async def main():
    """Main test execution function."""
    try:
        # Run tests
        await run_all_tests()
        
        # Final summary
        print_header("DEPLOYMENT TEST COMPLETE")
        
        if test_results['tests_passed'] > 0:
            print("✅ Agent appears to be responding to messages!")
            print("✅ Basic functionality confirmed working")
        else:
            print("❌ No successful responses received")
            print("❌ Agent may not be running or accessible")
        
        if test_results['errors']:
            print(f"⚠️  {len(test_results['errors'])} errors encountered during testing")
        
        print(f"\n🎯 Deployment Status: {'OPERATIONAL' if test_results['tests_passed'] > 0 else 'NEEDS INVESTIGATION'}")
        
    except Exception as e:
        logger.error(f"Main test execution failed: {str(e)}")
        print(f"❌ Test execution failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Mental Wellness Mood Tracker Agent Tests...")
    print(f"📡 Target Agent: {DEPLOYED_AGENT_ADDRESS}")
    print("⏳ Initializing test agent and running test suite...")
    
    # Run the test agent
    test_agent.run() 