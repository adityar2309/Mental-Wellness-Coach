"""
Mental Wellness Coach - Mood Tracker Agent

Specialized agent for mood tracking, pattern analysis, and mood-based
coordination with other mental wellness agents.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from services.agent_service import (
    MentalWellnessAgent, 
    AgentConfiguration, 
    AgentType, 
    AgentMessage
)

try:
    from uagents import Context
except ImportError:
    Context = None

logger = logging.getLogger(__name__)

@dataclass
class MoodReading:
    """Structured mood reading data."""
    user_id: str
    mood_score: int  # 1-10 scale
    emotions: List[str]
    energy_level: Optional[int] = None
    stress_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    triggers: Optional[List[str]] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class MoodTrackerAgent(MentalWellnessAgent):
    """
    Specialized agent for mood tracking and analysis.
    
    Responsibilities:
    - Collect and analyze mood data
    - Detect mood patterns and trends
    - Coordinate with other agents based on mood insights
    - Provide mood-based recommendations
    """
    
    def __init__(self, config: AgentConfiguration):
        """Initialize the mood tracker agent."""
        super().__init__(config)
        
        # Mood tracking specific data
        self.mood_history: Dict[str, List[MoodReading]] = {}
        self.mood_patterns: Dict[str, Dict] = {}
        self.alert_thresholds = {
            "low_mood_threshold": 3,
            "consecutive_low_days": 3,
            "stress_threshold": 7,
            "energy_threshold": 2
        }
        
        # Register mood-specific message handlers
        self._register_mood_handlers()
    
    def _register_mood_handlers(self) -> None:
        """Register message handlers specific to mood tracking."""
        self.register_message_handler("mood_entry", self._handle_mood_entry)
        self.register_message_handler("mood_analysis_request", self._handle_mood_analysis_request)
        self.register_message_handler("mood_pattern_request", self._handle_mood_pattern_request)
        self.register_message_handler("mood_recommendation_request", self._handle_mood_recommendation_request)
    
    async def _on_startup(self, ctx: Context) -> None:
        """Initialize mood tracker agent."""
        logger.info("Mood Tracker Agent starting up...")
        
        # Load historical mood data if available
        await self._load_mood_history()
        
        # Start periodic mood analysis
        if ctx:
            ctx.logger.info("Mood tracking services initialized")
    
    async def _load_mood_history(self) -> None:
        """Load historical mood data from database."""
        try:
            # This would integrate with the database to load existing mood entries
            # For now, we'll initialize with empty history
            logger.info("Loading mood history from database...")
            
            # TODO: Integrate with MoodEntry model from database
            # mood_entries = MoodEntry.query.all()
            # for entry in mood_entries:
            #     self._add_mood_reading_to_history(entry)
            
        except Exception as e:
            logger.error(f"Error loading mood history: {str(e)}")
    
    async def _handle_mood_entry(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """
        Handle new mood entry from user or conversation agent.
        
        Args:
            ctx: Agent context
            sender: Sender address
            msg: Message containing mood data
        """
        try:
            mood_data = msg.payload.get("mood_data", {})
            user_id = msg.user_id
            
            if not user_id or not mood_data:
                logger.warning("Invalid mood entry data received")
                return
            
            # Create mood reading
            mood_reading = MoodReading(
                user_id=user_id,
                mood_score=mood_data.get("mood_score", 5),
                emotions=mood_data.get("emotions", []),
                energy_level=mood_data.get("energy_level"),
                stress_level=mood_data.get("stress_level"),
                sleep_hours=mood_data.get("sleep_hours"),
                triggers=mood_data.get("triggers", []),
                notes=mood_data.get("notes")
            )
            
            # Store mood reading
            await self._store_mood_reading(mood_reading)
            
            # Analyze for patterns and alerts
            analysis = await self._analyze_mood_reading(mood_reading)
            
            # Send analysis to conversation coordinator if needed
            if analysis.get("needs_intervention"):
                await self._send_mood_alert(user_id, mood_reading, analysis)
            
            # Send confirmation back
            response = AgentMessage(
                message_type="mood_entry_processed",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload={
                    "status": "success",
                    "mood_score": mood_reading.mood_score,
                    "analysis": analysis,
                    "recommendations": analysis.get("recommendations", [])
                },
                user_id=user_id,
                session_id=msg.session_id
            )
            
            await self.send_message_to_agent(sender, response)
            
        except Exception as e:
            logger.error(f"Error handling mood entry: {str(e)}")
    
    async def _store_mood_reading(self, mood_reading: MoodReading) -> None:
        """Store mood reading in memory and database."""
        try:
            user_id = mood_reading.user_id
            
            # Store in memory
            if user_id not in self.mood_history:
                self.mood_history[user_id] = []
            
            self.mood_history[user_id].append(mood_reading)
            
            # Keep only last 100 readings in memory
            if len(self.mood_history[user_id]) > 100:
                self.mood_history[user_id] = self.mood_history[user_id][-100:]
            
            # TODO: Store in database
            # mood_entry = MoodEntry(
            #     user_id=mood_reading.user_id,
            #     mood_score=mood_reading.mood_score,
            #     emotions=mood_reading.emotions,
            #     ...
            # )
            # db.session.add(mood_entry)
            # db.session.commit()
            
            logger.info(f"Stored mood reading for user {user_id}: {mood_reading.mood_score}")
            
        except Exception as e:
            logger.error(f"Error storing mood reading: {str(e)}")
    
    async def _analyze_mood_reading(self, mood_reading: MoodReading) -> Dict[str, Any]:
        """
        Analyze mood reading for patterns and alerts.
        
        Args:
            mood_reading: The mood reading to analyze
            
        Returns:
            Analysis results with recommendations and alerts
        """
        try:
            user_id = mood_reading.user_id
            analysis = {
                "mood_trend": "stable",
                "needs_intervention": False,
                "recommendations": [],
                "alerts": [],
                "pattern_insights": []
            }
            
            # Get recent mood history
            recent_moods = self._get_recent_moods(user_id, days=7)
            
            if len(recent_moods) < 2:
                return analysis
            
            # Analyze mood trend
            mood_scores = [reading.mood_score for reading in recent_moods]
            current_score = mood_reading.mood_score
            avg_score = sum(mood_scores) / len(mood_scores)
            
            # Determine trend
            if current_score < avg_score - 1:
                analysis["mood_trend"] = "declining"
            elif current_score > avg_score + 1:
                analysis["mood_trend"] = "improving"
            
            # Check for intervention needs
            low_mood_days = sum(1 for score in mood_scores[-3:] if score <= self.alert_thresholds["low_mood_threshold"])
            
            if low_mood_days >= self.alert_thresholds["consecutive_low_days"]:
                analysis["needs_intervention"] = True
                analysis["alerts"].append("consecutive_low_mood")
            
            if current_score <= 2:
                analysis["needs_intervention"] = True
                analysis["alerts"].append("severe_low_mood")
            
            # Check stress and energy levels
            if mood_reading.stress_level and mood_reading.stress_level >= self.alert_thresholds["stress_threshold"]:
                analysis["alerts"].append("high_stress")
                analysis["recommendations"].append("stress_management_techniques")
            
            if mood_reading.energy_level and mood_reading.energy_level <= self.alert_thresholds["energy_threshold"]:
                analysis["alerts"].append("low_energy")
                analysis["recommendations"].append("energy_boosting_activities")
            
            # Pattern analysis
            patterns = self._detect_mood_patterns(user_id)
            if patterns:
                analysis["pattern_insights"] = patterns
            
            # Generate recommendations based on analysis
            recommendations = self._generate_mood_recommendations(mood_reading, analysis)
            analysis["recommendations"].extend(recommendations)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing mood reading: {str(e)}")
            return {"error": str(e)}
    
    def _get_recent_moods(self, user_id: str, days: int = 7) -> List[MoodReading]:
        """Get recent mood readings for a user."""
        if user_id not in self.mood_history:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_moods = [
            reading for reading in self.mood_history[user_id]
            if reading.timestamp >= cutoff_date
        ]
        
        return sorted(recent_moods, key=lambda x: x.timestamp)
    
    def _detect_mood_patterns(self, user_id: str) -> List[str]:
        """Detect patterns in user's mood data."""
        patterns = []
        recent_moods = self._get_recent_moods(user_id, days=30)
        
        if len(recent_moods) < 5:
            return patterns
        
        # Weekly pattern detection
        weekday_moods = {}
        for reading in recent_moods:
            weekday = reading.timestamp.weekday()
            if weekday not in weekday_moods:
                weekday_moods[weekday] = []
            weekday_moods[weekday].append(reading.mood_score)
        
        # Find consistently low days
        for weekday, scores in weekday_moods.items():
            if len(scores) >= 3 and sum(scores) / len(scores) < 4:
                day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][weekday]
                patterns.append(f"low_mood_on_{day_name.lower()}")
        
        # Trigger pattern analysis
        trigger_counts = {}
        for reading in recent_moods:
            if reading.triggers:
                for trigger in reading.triggers:
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        # Find frequent triggers
        for trigger, count in trigger_counts.items():
            if count >= 3:
                patterns.append(f"frequent_trigger_{trigger}")
        
        return patterns
    
    def _generate_mood_recommendations(self, mood_reading: MoodReading, analysis: Dict) -> List[str]:
        """Generate personalized recommendations based on mood analysis."""
        recommendations = []
        
        # Low mood recommendations
        if mood_reading.mood_score <= 4:
            recommendations.extend([
                "gentle_self_care_activities",
                "connect_with_support_system",
                "practice_gratitude_exercise"
            ])
        
        # High stress recommendations
        if "high_stress" in analysis.get("alerts", []):
            recommendations.extend([
                "deep_breathing_exercise",
                "progressive_muscle_relaxation",
                "mindfulness_meditation"
            ])
        
        # Low energy recommendations
        if "low_energy" in analysis.get("alerts", []):
            recommendations.extend([
                "light_physical_activity",
                "healthy_nutrition_check",
                "sleep_hygiene_review"
            ])
        
        # Pattern-based recommendations
        for pattern in analysis.get("pattern_insights", []):
            if "low_mood_on" in pattern:
                recommendations.append("weekly_planning_support")
            elif "frequent_trigger" in pattern:
                recommendations.append("trigger_management_strategies")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _send_mood_alert(self, user_id: str, mood_reading: MoodReading, analysis: Dict) -> None:
        """Send mood alert to conversation coordinator."""
        try:
            alert_message = AgentMessage(
                message_type="mood_alert",
                sender_agent=self.config.name,
                recipient_agent="conversation_coordinator",
                payload={
                    "alert_type": "mood_intervention_needed",
                    "user_id": user_id,
                    "current_mood": mood_reading.mood_score,
                    "alerts": analysis.get("alerts", []),
                    "recommendations": analysis.get("recommendations", []),
                    "mood_trend": analysis.get("mood_trend"),
                    "timestamp": datetime.utcnow().isoformat()
                },
                priority="high",
                requires_response=True
            )
            
            await self.send_message_to_agent("conversation_coordinator", alert_message)
            logger.info(f"Sent mood alert for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending mood alert: {str(e)}")
    
    async def _handle_mood_analysis_request(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Handle request for mood analysis."""
        try:
            user_id = msg.user_id
            days = msg.payload.get("days", 7)
            
            recent_moods = self._get_recent_moods(user_id, days)
            
            if not recent_moods:
                response_payload = {"error": "No mood data available"}
            else:
                # Calculate statistics
                mood_scores = [reading.mood_score for reading in recent_moods]
                analysis = {
                    "average_mood": sum(mood_scores) / len(mood_scores),
                    "highest_mood": max(mood_scores),
                    "lowest_mood": min(mood_scores),
                    "mood_variance": self._calculate_variance(mood_scores),
                    "total_entries": len(recent_moods),
                    "patterns": self._detect_mood_patterns(user_id),
                    "recommendations": self._generate_mood_recommendations(recent_moods[-1], {
                        "pattern_insights": self._detect_mood_patterns(user_id)
                    })
                }
                response_payload = {"analysis": analysis}
            
            response = AgentMessage(
                message_type="mood_analysis_response",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload=response_payload,
                user_id=user_id,
                session_id=msg.session_id
            )
            
            await self.send_message_to_agent(sender, response)
            
        except Exception as e:
            logger.error(f"Error handling mood analysis request: {str(e)}")
    
    def _calculate_variance(self, scores: List[int]) -> float:
        """Calculate variance of mood scores."""
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        return round(variance, 2)
    
    async def _handle_mood_pattern_request(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Handle request for mood patterns."""
        try:
            user_id = msg.user_id
            patterns = self._detect_mood_patterns(user_id)
            
            response = AgentMessage(
                message_type="mood_pattern_response",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload={"patterns": patterns},
                user_id=user_id,
                session_id=msg.session_id
            )
            
            await self.send_message_to_agent(sender, response)
            
        except Exception as e:
            logger.error(f"Error handling mood pattern request: {str(e)}")
    
    async def _handle_mood_recommendation_request(self, ctx: Context, sender: str, msg: AgentMessage) -> None:
        """Handle request for mood-based recommendations."""
        try:
            user_id = msg.user_id
            recent_moods = self._get_recent_moods(user_id, days=1)
            
            if recent_moods:
                latest_mood = recent_moods[-1]
                analysis = await self._analyze_mood_reading(latest_mood)
                recommendations = analysis.get("recommendations", [])
            else:
                recommendations = ["start_daily_mood_tracking"]
            
            response = AgentMessage(
                message_type="mood_recommendation_response",
                sender_agent=self.config.name,
                recipient_agent=sender,
                payload={"recommendations": recommendations},
                user_id=user_id,
                session_id=msg.session_id
            )
            
            await self.send_message_to_agent(sender, response)
            
        except Exception as e:
            logger.error(f"Error handling mood recommendation request: {str(e)}")

# Factory function to create mood tracker agent
def create_mood_tracker_agent(port: Optional[int] = None) -> MoodTrackerAgent:
    """
    Create a mood tracker agent.
    
    Args:
        port: Optional port number
        
    Returns:
        Configured mood tracker agent
    """
    config = AgentConfiguration(
        agent_type=AgentType.MOOD_TRACKER,
        name="mood_tracker",
        port=port or 8001,
        seed="mood_tracker_seed",
        crisis_detection_enabled=True,
        mental_health_focus=True
    )
    
    return MoodTrackerAgent(config) 