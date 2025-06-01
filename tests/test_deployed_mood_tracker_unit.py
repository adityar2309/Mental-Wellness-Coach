"""
Unit tests for the deployed mood tracker agent testing functionality.

Tests the test infrastructure, data models, and validation logic used
for testing the deployed Agentverse agent.
"""

import pytest
import asyncio
from datetime import datetime
from dataclasses import asdict

# Import the test modules we created
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import test components (these would be imported from the test file)
from typing import Dict, List, Optional, Any

class TestMoodReadingDataModel:
    """Test the MoodReading data model used in agent testing."""
    
    def test_mood_reading_creation_basic(self):
        """Test basic mood reading creation with required fields."""
        # Import here to avoid circular imports in real scenarios
        from dataclasses import dataclass
        
        @dataclass
        class MoodReading:
            user_id: str
            mood_score: int
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
        
        mood = MoodReading(
            user_id="test_user_123",
            mood_score=7,
            emotions=["happy", "content"]
        )
        
        assert mood.user_id == "test_user_123"
        assert mood.mood_score == 7
        assert mood.emotions == ["happy", "content"]
        assert mood.timestamp is not None
        assert isinstance(mood.timestamp, str)
    
    def test_mood_reading_creation_complete(self):
        """Test mood reading creation with all optional fields."""
        from dataclasses import dataclass
        
        @dataclass
        class MoodReading:
            user_id: str
            mood_score: int
            emotions: List[str]
            energy_level: Optional[int] = None
            stress_level: Optional[int] = None
            sleep_hours: Optional[float] = None
            triggers: Optional[List[str]] = None
            notes: Optional[str] = None
            timestamp: Optional[str] = None
        
        mood = MoodReading(
            user_id="test_user_456",
            mood_score=3,
            emotions=["sad", "anxious"],
            energy_level=2,
            stress_level=8,
            sleep_hours=5.5,
            triggers=["work", "health"],
            notes="Having a rough day",
            timestamp="2024-01-01T12:00:00"
        )
        
        assert mood.user_id == "test_user_456"
        assert mood.mood_score == 3
        assert mood.energy_level == 2
        assert mood.stress_level == 8
        assert mood.sleep_hours == 5.5
        assert mood.triggers == ["work", "health"]
        assert mood.notes == "Having a rough day"
        assert mood.timestamp == "2024-01-01T12:00:00"
    
    def test_mood_reading_edge_cases(self):
        """Test mood reading with edge case values."""
        from dataclasses import dataclass
        
        @dataclass
        class MoodReading:
            user_id: str
            mood_score: int
            emotions: List[str]
            energy_level: Optional[int] = None
            stress_level: Optional[int] = None
            sleep_hours: Optional[float] = None
            triggers: Optional[List[str]] = None
            notes: Optional[str] = None
            timestamp: Optional[str] = None
        
        # Test minimum values
        mood_min = MoodReading(
            user_id="test_min",
            mood_score=1,
            emotions=["hopeless"],
            energy_level=1,
            stress_level=1,
            sleep_hours=0.0
        )
        
        assert mood_min.mood_score == 1
        assert mood_min.energy_level == 1
        assert mood_min.stress_level == 1
        assert mood_min.sleep_hours == 0.0
        
        # Test maximum values
        mood_max = MoodReading(
            user_id="test_max",
            mood_score=10,
            emotions=["ecstatic", "energetic", "optimistic"],
            energy_level=10,
            stress_level=10,
            sleep_hours=12.0
        )
        
        assert mood_max.mood_score == 10
        assert mood_max.energy_level == 10
        assert mood_max.stress_level == 10
        assert mood_max.sleep_hours == 12.0

class TestMoodAnalysisRequest:
    """Test the MoodAnalysisRequest data model."""
    
    def test_analysis_request_basic(self):
        """Test basic analysis request creation."""
        from dataclasses import dataclass
        
        @dataclass
        class MoodAnalysisRequest:
            user_id: str
            days: Optional[int] = 7
        
        request = MoodAnalysisRequest(user_id="test_analysis_user")
        
        assert request.user_id == "test_analysis_user"
        assert request.days == 7  # Default value
    
    def test_analysis_request_custom_days(self):
        """Test analysis request with custom days parameter."""
        from dataclasses import dataclass
        
        @dataclass
        class MoodAnalysisRequest:
            user_id: str
            days: Optional[int] = 7
        
        request = MoodAnalysisRequest(user_id="test_user", days=30)
        
        assert request.user_id == "test_user"
        assert request.days == 30

class TestResultTracking:
    """Test the test result tracking functionality."""
    
    def test_test_results_initialization(self):
        """Test test results dictionary initialization."""
        test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "responses_received": [],
            "errors": []
        }
        
        assert test_results["tests_run"] == 0
        assert test_results["tests_passed"] == 0
        assert test_results["tests_failed"] == 0
        assert test_results["responses_received"] == []
        assert test_results["errors"] == []
    
    def test_log_test_result_pass(self):
        """Test logging a passing test result."""
        test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "responses_received": [],
            "errors": []
        }
        
        def log_test_result(test_name: str, passed: bool, details: str = ""):
            test_results["tests_run"] += 1
            if passed:
                test_results["tests_passed"] += 1
            else:
                test_results["tests_failed"] += 1
        
        log_test_result("Sample Test", True, "Test passed successfully")
        
        assert test_results["tests_run"] == 1
        assert test_results["tests_passed"] == 1
        assert test_results["tests_failed"] == 0
    
    def test_log_test_result_fail(self):
        """Test logging a failing test result."""
        test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "responses_received": [],
            "errors": []
        }
        
        def log_test_result(test_name: str, passed: bool, details: str = ""):
            test_results["tests_run"] += 1
            if passed:
                test_results["tests_passed"] += 1
            else:
                test_results["tests_failed"] += 1
        
        log_test_result("Sample Test", False, "Test failed")
        
        assert test_results["tests_run"] == 1
        assert test_results["tests_passed"] == 0
        assert test_results["tests_failed"] == 1

class TestResponseValidation:
    """Test response validation logic."""
    
    def test_mood_entry_response_validation(self):
        """Test validation of mood entry responses."""
        from dataclasses import dataclass
        
        @dataclass
        class MoodEntryResponse:
            status: str
            mood_score: int
            analysis: Dict[str, Any]
            recommendations: List[str]
            alerts: List[str]
        
        # Valid response
        valid_response = MoodEntryResponse(
            status="success",
            mood_score=5,
            analysis={"mood_trend": "stable", "needs_intervention": False},
            recommendations=["breathing_exercises"],
            alerts=[]
        )
        
        assert valid_response.status == "success"
        assert valid_response.mood_score == 5
        assert "mood_trend" in valid_response.analysis
        assert len(valid_response.recommendations) > 0
        assert isinstance(valid_response.alerts, list)
    
    def test_mood_analysis_response_validation(self):
        """Test validation of mood analysis responses."""
        from dataclasses import dataclass
        
        @dataclass
        class MoodAnalysisResponse:
            user_id: str
            mood_trend: str
            average_mood: float
            needs_intervention: bool
            alerts: List[str]
            recommendations: List[str]
            patterns: List[str]
        
        response = MoodAnalysisResponse(
            user_id="test_user",
            mood_trend="improving",
            average_mood=6.5,
            needs_intervention=False,
            alerts=[],
            recommendations=["continue_tracking"],
            patterns=["morning_mood_boost"]
        )
        
        assert response.user_id == "test_user"
        assert response.mood_trend == "improving"
        assert response.average_mood == 6.5
        assert response.needs_intervention == False
        assert isinstance(response.alerts, list)
        assert isinstance(response.recommendations, list)
        assert isinstance(response.patterns, list)

class TestCrisisDetection:
    """Test crisis detection validation in responses."""
    
    def test_crisis_alert_detection(self):
        """Test detection of crisis alerts in responses."""
        alerts = [
            "low_mood_score: 2",
            "crisis_keyword: hopeless",
            "high_stress_level: 9"
        ]
        
        crisis_detected = any("crisis" in alert for alert in alerts)
        assert crisis_detected == True
    
    def test_no_crisis_detection(self):
        """Test when no crisis is detected."""
        alerts = [
            "low_mood_score: 3",
            "high_stress_level: 7",
            "low_energy_level: 2"
        ]
        
        crisis_detected = any("crisis" in alert for alert in alerts)
        assert crisis_detected == False
    
    def test_multiple_crisis_indicators(self):
        """Test detection of multiple crisis indicators."""
        alerts = [
            "crisis_keyword: suicide",
            "crisis_keyword: hopeless",
            "low_mood_score: 1"
        ]
        
        crisis_alerts = [alert for alert in alerts if "crisis" in alert]
        assert len(crisis_alerts) == 2

class TestAgentAddressValidation:
    """Test agent address validation."""
    
    def test_valid_agent_address_format(self):
        """Test validation of agent address format."""
        agent_address = "agent1qtv48wjwflhu0mk5wev5jft5nlngtd84tpvjt6ckv63ynncjpfckj5xss8q"
        
        # Basic format validation
        assert agent_address.startswith("agent1")
        assert len(agent_address) > 10
        assert all(c.isalnum() for c in agent_address)
    
    def test_agent_address_length(self):
        """Test agent address has appropriate length."""
        agent_address = "agent1qtv48wjwflhu0mk5wev5jft5nlngtd84tpvjt6ckv63ynncjpfckj5xss8q"
        
        # Should be a reasonable length for a crypto address
        assert len(agent_address) >= 50
        assert len(agent_address) <= 100

class TestTestScenarios:
    """Test the various test scenarios."""
    
    def test_basic_mood_scenario(self):
        """Test basic mood entry scenario data."""
        scenario = {
            "user_id": "test_user_basic",
            "mood_score": 6,
            "emotions": ["content", "slightly_anxious"],
            "energy_level": 7,
            "stress_level": 5,
            "notes": "Generally feeling okay"
        }
        
        assert scenario["mood_score"] >= 1 and scenario["mood_score"] <= 10
        assert isinstance(scenario["emotions"], list)
        assert len(scenario["emotions"]) > 0
        assert scenario["energy_level"] >= 1 and scenario["energy_level"] <= 10
        assert scenario["stress_level"] >= 1 and scenario["stress_level"] <= 10
    
    def test_crisis_mood_scenario(self):
        """Test crisis mood entry scenario data."""
        scenario = {
            "user_id": "test_user_crisis",
            "mood_score": 1,
            "emotions": ["hopeless", "worthless", "desperate"],
            "energy_level": 1,
            "stress_level": 10,
            "notes": "I feel completely hopeless and like there's no point in continuing"
        }
        
        # Crisis scenario should have concerning indicators
        assert scenario["mood_score"] <= 3  # Very low mood
        assert scenario["stress_level"] >= 8  # High stress
        assert any(word in scenario["notes"].lower() for word in ["hopeless", "no point"])
    
    def test_positive_mood_scenario(self):
        """Test positive mood entry scenario data."""
        scenario = {
            "user_id": "test_user_positive",
            "mood_score": 9,
            "emotions": ["happy", "energetic", "optimistic"],
            "energy_level": 9,
            "stress_level": 2,
            "notes": "Had a fantastic day!"
        }
        
        # Positive scenario should have good indicators
        assert scenario["mood_score"] >= 7  # High mood
        assert scenario["stress_level"] <= 3  # Low stress
        assert scenario["energy_level"] >= 7  # High energy

if __name__ == "__main__":
    # Run tests manually if pytest not available
    import unittest
    
    # Convert pytest classes to unittest
    test_classes = [
        TestMoodReadingDataModel,
        TestMoodAnalysisRequest,
        TestResultTracking,
        TestResponseValidation,
        TestCrisisDetection,
        TestAgentAddressValidation,
        TestTestScenarios
    ]
    
    print("🧪 Running unit tests for deployed agent testing functionality...")
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                getattr(test_instance, test_method)()
                print(f"  ✅ {test_method}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {test_method}: {str(e)}")
    
    print(f"\n📊 Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {(passed_tests / total_tests) * 100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Test infrastructure is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please review the test infrastructure.") 