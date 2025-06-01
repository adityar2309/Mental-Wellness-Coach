"""
Mental Wellness Coach - Agentverse Mood Tracker Agent

Standalone agent for mood tracking and analysis, optimized for Agentverse deployment.
This agent specializes in:
- Collecting and analyzing mood data
- Detecting patterns and trends in mental wellness
- Providing mood-based recommendations
- Crisis detection and alert coordination

Deploy this agent to Agentverse for 24/7 mood tracking services.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
MOOD_TRACKER_SEED = "mood_tracker_wellness_coach_seed_phrase_here"
MOOD_TRACKER_PORT = 8000
MOOD_TRACKER_ENDPOINT = ["http://127.0.0.1:8000/submit"]

# Create the mood tracker agent
mood_tracker = Agent(
    name="mood_tracker",
    seed=MOOD_TRACKER_SEED,
    port=MOOD_TRACKER_PORT,
    endpoint=MOOD_TRACKER_ENDPOINT,
)

# Fund agent if needed (for testnet)
fund_agent_if_low(mood_tracker.wallet.address())

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
class MoodAnalysisResponse(Model):
    """Response containing mood analysis results."""
    user_id: str
    mood_trend: str
    average_mood: float
    needs_intervention: bool
    alerts: List[str]
    recommendations: List[str]
    patterns: List[str]

@dataclass
class MoodEntryResponse(Model):
    """Response after processing a mood entry."""
    status: str
    mood_score: int
    analysis: Dict[str, Any]
    recommendations: List[str]
    alerts: List[str]

# In-memory storage for mood data (in production, use persistent storage)
mood_history: Dict[str, List[Dict]] = {}
mood_patterns: Dict[str, Dict] = {}

# Alert thresholds
ALERT_THRESHOLDS = {
    "low_mood_threshold": 3,
    "consecutive_low_days": 3,
    "stress_threshold": 7,
    "energy_threshold": 2,
    "crisis_keywords": [
        "suicide", "kill myself", "end it all", "hopeless", "worthless",
        "can't go on", "no point", "give up", "hurt myself"
    ]
}

def detect_crisis_indicators(text: str) -> List[str]:
    """
    Detect crisis indicators in mood notes or emotions.
    
    Args:
        text: Text to analyze for crisis indicators
        
    Returns:
        List of detected crisis indicators
    """
    if not text:
        return []
    
    text_lower = text.lower()
    detected = []
    
    for keyword in ALERT_THRESHOLDS["crisis_keywords"]:
        if keyword in text_lower:
            detected.append(f"crisis_keyword: {keyword}")
    
    return detected

def analyze_mood_reading(mood_reading: Dict, user_history: List[Dict]) -> Dict[str, Any]:
    """
    Analyze a mood reading for patterns, trends, and alerts.
    
    Args:
        mood_reading: Current mood reading
        user_history: Historical mood readings for the user
        
    Returns:
        Analysis results including trends, alerts, and recommendations
    """
    analysis = {
        "mood_trend": "stable",
        "needs_intervention": False,
        "alerts": [],
        "recommendations": [],
        "patterns": []
    }
    
    mood_score = mood_reading.get("mood_score", 5)
    stress_level = mood_reading.get("stress_level", 5)
    energy_level = mood_reading.get("energy_level", 5)
    emotions = mood_reading.get("emotions", [])
    notes = mood_reading.get("notes", "")
    
    # Check for immediate crisis indicators
    crisis_indicators = detect_crisis_indicators(notes)
    for emotion in emotions:
        crisis_indicators.extend(detect_crisis_indicators(emotion))
    
    if crisis_indicators:
        analysis["alerts"].extend(crisis_indicators)
        analysis["needs_intervention"] = True
        analysis["recommendations"].append("immediate_professional_support")
    
    # Low mood detection
    if mood_score <= ALERT_THRESHOLDS["low_mood_threshold"]:
        analysis["alerts"].append(f"low_mood_score: {mood_score}")
        analysis["recommendations"].extend([
            "breathing_exercises",
            "mood_boosting_activities",
            "social_connection"
        ])
    
    # High stress detection
    if stress_level and stress_level >= ALERT_THRESHOLDS["stress_threshold"]:
        analysis["alerts"].append(f"high_stress_level: {stress_level}")
        analysis["recommendations"].extend([
            "stress_reduction_techniques",
            "mindfulness_practice",
            "relaxation_exercises"
        ])
    
    # Low energy detection
    if energy_level and energy_level <= ALERT_THRESHOLDS["energy_threshold"]:
        analysis["alerts"].append(f"low_energy_level: {energy_level}")
        analysis["recommendations"].extend([
            "energy_boosting_activities",
            "sleep_hygiene_check",
            "nutrition_review"
        ])
    
    # Analyze historical trends if available
    if len(user_history) >= 3:
        recent_scores = [entry.get("mood_score", 5) for entry in user_history[-7:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        if avg_recent < 4:
            analysis["mood_trend"] = "declining"
            analysis["needs_intervention"] = True
            analysis["alerts"].append("declining_mood_trend")
        elif avg_recent > 7:
            analysis["mood_trend"] = "improving"
        
        # Check for consecutive low days
        low_days = sum(1 for score in recent_scores[-3:] if score <= ALERT_THRESHOLDS["low_mood_threshold"])
        if low_days >= ALERT_THRESHOLDS["consecutive_low_days"]:
            analysis["alerts"].append("consecutive_low_mood_days")
            analysis["needs_intervention"] = True
    
    # Remove duplicate recommendations
    analysis["recommendations"] = list(set(analysis["recommendations"]))
    
    return analysis

def store_mood_reading(user_id: str, mood_data: Dict) -> None:
    """Store mood reading in memory."""
    if user_id not in mood_history:
        mood_history[user_id] = []
    
    # Add timestamp if not present
    if "timestamp" not in mood_data:
        mood_data["timestamp"] = datetime.utcnow().isoformat()
    
    mood_history[user_id].append(mood_data)
    
    # Keep only last 100 readings in memory
    if len(mood_history[user_id]) > 100:
        mood_history[user_id] = mood_history[user_id][-100:]
    
    logger.info(f"Stored mood reading for user {user_id}: score {mood_data.get('mood_score')}")

def get_user_mood_history(user_id: str, days: int = 7) -> List[Dict]:
    """Get user's mood history for specified number of days."""
    if user_id not in mood_history:
        return []
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    filtered_history = []
    for entry in mood_history[user_id]:
        entry_date = datetime.fromisoformat(entry.get("timestamp", datetime.utcnow().isoformat()))
        if entry_date >= cutoff_date:
            filtered_history.append(entry)
    
    return filtered_history

# Create mood tracking protocol
mood_protocol = Protocol("Mood Tracking Protocol")

@mood_protocol.on_message(model=MoodReading)
async def handle_mood_entry(ctx: Context, sender: str, msg: MoodReading):
    """
    Handle new mood entry from user or other agents.
    
    Args:
        ctx: Agent context
        sender: Sender address
        msg: Mood reading data
    """
    try:
        ctx.logger.info(f"Received mood entry from {sender} for user {msg.user_id}")
        
        # Convert mood reading to dict for processing
        mood_data = asdict(msg)
        
        # Get user's mood history
        user_history = get_user_mood_history(msg.user_id)
        
        # Analyze the mood reading
        analysis = analyze_mood_reading(mood_data, user_history)
        
        # Store the mood reading
        store_mood_reading(msg.user_id, mood_data)
        
        # Prepare response
        response = MoodEntryResponse(
            status="success",
            mood_score=msg.mood_score,
            analysis=analysis,
            recommendations=analysis.get("recommendations", []),
            alerts=analysis.get("alerts", [])
        )
        
        # Send response back to sender
        await ctx.send(sender, response)
        
        # Log intervention needs
        if analysis.get("needs_intervention"):
            ctx.logger.warning(f"User {msg.user_id} may need intervention. Alerts: {analysis.get('alerts')}")
        
        # If crisis detected, could send alert to coordinator agent
        if any("crisis" in alert for alert in analysis.get("alerts", [])):
            ctx.logger.critical(f"CRISIS DETECTED for user {msg.user_id}. Immediate intervention needed.")
            # TODO: Send crisis alert to conversation coordinator or emergency services
        
    except Exception as e:
        ctx.logger.error(f"Error processing mood entry: {str(e)}")
        
        error_response = MoodEntryResponse(
            status="error",
            mood_score=msg.mood_score,
            analysis={"error": str(e)},
            recommendations=[],
            alerts=["processing_error"]
        )
        await ctx.send(sender, error_response)

@mood_protocol.on_message(model=MoodAnalysisRequest)
async def handle_mood_analysis_request(ctx: Context, sender: str, msg: MoodAnalysisRequest):
    """
    Handle request for mood analysis and patterns.
    
    Args:
        ctx: Agent context
        sender: Sender address  
        msg: Analysis request
    """
    try:
        ctx.logger.info(f"Received mood analysis request from {sender} for user {msg.user_id}")
        
        # Get user's mood history
        user_history = get_user_mood_history(msg.user_id, msg.days)
        
        if not user_history:
            response = MoodAnalysisResponse(
                user_id=msg.user_id,
                mood_trend="insufficient_data",
                average_mood=5.0,
                needs_intervention=False,
                alerts=[],
                recommendations=["start_mood_tracking"],
                patterns=[]
            )
        else:
            # Calculate statistics
            mood_scores = [entry.get("mood_score", 5) for entry in user_history]
            average_mood = sum(mood_scores) / len(mood_scores)
            
            # Determine trend
            if len(mood_scores) >= 3:
                recent_avg = sum(mood_scores[-3:]) / 3
                earlier_avg = sum(mood_scores[:3]) / 3
                
                if recent_avg > earlier_avg + 1:
                    trend = "improving"
                elif recent_avg < earlier_avg - 1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Check for patterns
            patterns = []
            if len(mood_scores) >= 7:
                # Check for weekly patterns
                low_count = sum(1 for score in mood_scores if score <= 3)
                if low_count >= len(mood_scores) * 0.4:
                    patterns.append("frequent_low_moods")
                
                high_count = sum(1 for score in mood_scores if score >= 8)
                if high_count >= len(mood_scores) * 0.6:
                    patterns.append("generally_positive")
            
            # Determine intervention needs
            needs_intervention = (
                average_mood < 4 or 
                trend == "declining" or 
                "frequent_low_moods" in patterns
            )
            
            alerts = []
            recommendations = []
            
            if needs_intervention:
                alerts.append("intervention_recommended")
                recommendations.extend([
                    "professional_consultation",
                    "mood_tracking_continuation",
                    "coping_strategies_review"
                ])
            
            if average_mood < 3:
                alerts.append("persistent_low_mood")
                recommendations.append("immediate_support_consideration")
            
            response = MoodAnalysisResponse(
                user_id=msg.user_id,
                mood_trend=trend,
                average_mood=round(average_mood, 2),
                needs_intervention=needs_intervention,
                alerts=alerts,
                recommendations=recommendations,
                patterns=patterns
            )
        
        await ctx.send(sender, response)
        
    except Exception as e:
        ctx.logger.error(f"Error processing mood analysis request: {str(e)}")

# Include the mood protocol in the agent
mood_tracker.include(mood_protocol)

@mood_tracker.on_event("startup")
async def startup_handler(ctx: Context):
    """Agent startup handler."""
    ctx.logger.info("🧠 Mental Wellness Mood Tracker Agent starting up...")
    ctx.logger.info(f"Agent address: {mood_tracker.address}")
    ctx.logger.info("Ready to track moods and provide mental wellness insights!")

@mood_tracker.on_event("shutdown")
async def shutdown_handler(ctx: Context):
    """Agent shutdown handler."""
    ctx.logger.info("🧠 Mental Wellness Mood Tracker Agent shutting down...")

if __name__ == "__main__":
    print("🚀 Starting Mental Wellness Mood Tracker Agent for Agentverse...")
    print(f"📊 Agent Address: {mood_tracker.address}")
    print(f"🌐 Port: {MOOD_TRACKER_PORT}")
    print("💡 This agent provides mood tracking and mental wellness insights")
    print("📈 Deploy to Agentverse for 24/7 availability!")
    
    mood_tracker.run() 