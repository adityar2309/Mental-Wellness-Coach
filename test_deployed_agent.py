"""
Test script for the deployed Agentverse Mental Wellness Mood Tracker Agent.

This script demonstrates how to send messages to your live agent on Agentverse.
"""

import asyncio
from datetime import datetime
from uagents import Agent, Context, Model
from typing import List, Optional, Dict, Any

# Your deployed mood tracker agent address
DEPLOYED_MOOD_TRACKER_ADDRESS = "agent1qtv48wjwflhu0mk5wev5jft5nlngtd84tpvjt6ckv63ynncjpfckj5xss8q"

# Create a test client agent
test_client = Agent(
    name="mood_test_client",
    seed="test_client_seed_phrase_unique_12345",
    port=8003,
    endpoint=["http://127.0.0.1:8003/submit"],
)

class MoodReading(Model):
    """Mood reading data model - matches your deployed agent."""
    user_id: str
    mood_score: int  # 1-10 scale
    emotions: List[str]
    energy_level: Optional[int] = None
    stress_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    triggers: Optional[List[str]] = None
    notes: Optional[str] = None
    timestamp: Optional[str] = None

class MoodEntryResponse(Model):
    """Expected response from mood tracker agent."""
    status: str
    mood_score: int
    analysis: Dict[str, Any]
    recommendations: List[str]
    alerts: List[str]

@test_client.on_event("startup")
async def send_test_mood_data(ctx: Context):
    """Send test mood data to the deployed agent."""
    ctx.logger.info("🧪 Testing deployed Mental Wellness Mood Tracker Agent...")
    
    # Test case 1: Normal mood entry
    test_mood = MoodReading(
        user_id="agentverse_test_user",
        mood_score=6,
        emotions=["content", "slightly_tired"],
        energy_level=6,
        stress_level=4,
        sleep_hours=7.5,
        triggers=["good_weather", "completed_project"],
        notes="Feeling pretty good today, got some work done",
        timestamp=datetime.utcnow().isoformat()
    )
    
    ctx.logger.info(f"📤 Sending test mood data to agent: {DEPLOYED_MOOD_TRACKER_ADDRESS}")
    ctx.logger.info(f"📊 Test Mood Score: {test_mood.mood_score}/10")
    ctx.logger.info(f"😊 Test Emotions: {', '.join(test_mood.emotions)}")
    
    try:
        await ctx.send(DEPLOYED_MOOD_TRACKER_ADDRESS, test_mood)
        ctx.logger.info("✅ Test mood data sent successfully!")
    except Exception as e:
        ctx.logger.error(f"❌ Failed to send test data: {str(e)}")

@test_client.on_message(model=MoodEntryResponse)
async def handle_mood_response(ctx: Context, sender: str, msg: MoodEntryResponse):
    """Handle response from the mood tracker agent."""
    ctx.logger.info("📥 Received response from deployed mood tracker agent!")
    ctx.logger.info(f"📊 Response Status: {msg.status}")
    ctx.logger.info(f"🔍 Analysis: {len(msg.recommendations)} recommendations, {len(msg.alerts)} alerts")
    
    if msg.recommendations:
        ctx.logger.info("💡 Recommendations received:")
        for rec in msg.recommendations[:3]:  # Show first 3
            ctx.logger.info(f"   - {rec.replace('_', ' ').title()}")
    
    if msg.alerts:
        ctx.logger.info("⚠️  Alerts generated:")
        for alert in msg.alerts:
            ctx.logger.info(f"   - {alert}")
    
    ctx.logger.info("✅ Test completed successfully! Your agent is working on Agentverse! 🎉")

if __name__ == "__main__":
    print("🧪 Testing deployed Mental Wellness Mood Tracker Agent on Agentverse...")
    print(f"📡 Target Agent: {DEPLOYED_MOOD_TRACKER_ADDRESS}")
    print("🚀 Starting test client...")
    
    test_client.run() 