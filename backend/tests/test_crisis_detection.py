"""
Mental Wellness Coach - Crisis Detection Tests

Comprehensive test suite for crisis detection, risk assessment, and safety systems.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the crisis detection service
from services.crisis_service import (
    CrisisDetectionService, 
    CrisisLevel, 
    RiskFactor,
    RiskAssessment,
    CrisisKeywordPattern,
    SafetyResource
)

class TestCrisisDetectionService:
    """Test crisis detection service functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.crisis_service = CrisisDetectionService()
        self.test_user_id = "test_user_123"
    
    def test_service_initialization(self):
        """Test crisis service initializes properly."""
        assert self.crisis_service is not None
        assert len(self.crisis_service.crisis_patterns) > 0
        assert len(self.crisis_service.safety_resources) > 0
        
        # Check that critical patterns are included
        pattern_factors = [p.risk_factor for p in self.crisis_service.crisis_patterns]
        assert RiskFactor.SUICIDAL_IDEATION in pattern_factors
        assert RiskFactor.SELF_HARM in pattern_factors
        assert RiskFactor.HOPELESSNESS in pattern_factors
    
    @pytest.mark.asyncio
    async def test_critical_crisis_detection(self):
        """Test detection of critical crisis indicators."""
        critical_messages = [
            "I want to kill myself tonight",
            "I have a plan to end my life",
            "I'm going to take all these pills",
            "I want to die and I know how"
        ]
        
        for message in critical_messages:
            assessment = await self.crisis_service.assess_crisis_risk(
                user_id=self.test_user_id,
                content=message,
                trigger_source="test"
            )
            
            assert assessment.crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
            assert assessment.immediate_action_required == True
            assert assessment.escalation_needed == True
            assert RiskFactor.SUICIDAL_IDEATION in assessment.detected_factors
            assert assessment.confidence > 0.7
    
    @pytest.mark.asyncio
    async def test_high_risk_detection(self):
        """Test detection of high-risk indicators."""
        high_risk_messages = [
            "I want to hurt myself",
            "I cut myself last night",
            "I feel completely hopeless",
            "Nothing will ever get better"
        ]
        
        for message in high_risk_messages:
            assessment = await self.crisis_service.assess_crisis_risk(
                user_id=self.test_user_id,
                content=message,
                trigger_source="test"
            )
            
            assert assessment.crisis_level in [CrisisLevel.MEDIUM, CrisisLevel.HIGH]
            assert len(assessment.detected_factors) > 0
            assert len(assessment.recommended_interventions) > 0
    
    @pytest.mark.asyncio
    async def test_medium_risk_detection(self):
        """Test detection of medium-risk indicators."""
        medium_risk_messages = [
            "I feel worthless and useless",
            "Everyone would be better off without me",
            "I can't stop drinking",
            "I feel so alone and isolated"
        ]
        
        for message in medium_risk_messages:
            assessment = await self.crisis_service.assess_crisis_risk(
                user_id=self.test_user_id,
                content=message,
                trigger_source="test"
            )
            
            assert assessment.crisis_level in [CrisisLevel.LOW, CrisisLevel.MEDIUM]
            assert len(assessment.detected_factors) > 0
    
    @pytest.mark.asyncio
    async def test_low_risk_detection(self):
        """Test detection of low-risk indicators."""
        low_risk_messages = [
            "I'm feeling sad today",
            "Work has been stressful",
            "I'm worried about my family",
            "I feel anxious sometimes"
        ]
        
        for message in low_risk_messages:
            assessment = await self.crisis_service.assess_crisis_risk(
                user_id=self.test_user_id,
                content=message,
                trigger_source="test"
            )
            
            assert assessment.crisis_level in [CrisisLevel.NONE, CrisisLevel.LOW]
            assert assessment.immediate_action_required == False
    
    @pytest.mark.asyncio
    async def test_no_risk_detection(self):
        """Test that normal messages don't trigger crisis detection."""
        normal_messages = [
            "I had a great day today",
            "Thanks for the help",
            "How does this app work?",
            "The weather is nice"
        ]
        
        for message in normal_messages:
            assessment = await self.crisis_service.assess_crisis_risk(
                user_id=self.test_user_id,
                content=message,
                trigger_source="test"
            )
            
            assert assessment.crisis_level == CrisisLevel.NONE
            assert assessment.immediate_action_required == False
            assert assessment.escalation_needed == False
            assert len(assessment.detected_factors) == 0
    
    def test_pattern_evaluation(self):
        """Test crisis pattern evaluation logic."""
        # Create test pattern
        test_pattern = CrisisKeywordPattern(
            keywords=["test_keyword", "another_test"],
            risk_factor=RiskFactor.DEPRESSION,
            severity_weight=0.8,
            context_modifiers=["always", "never"]
        )
        
        # Test keyword match
        score1 = self.crisis_service._evaluate_pattern("I have test_keyword feelings", test_pattern)
        assert score1 > 0
        
        # Test multiple keywords
        score2 = self.crisis_service._evaluate_pattern("test_keyword and another_test", test_pattern)
        assert score2 > score1  # Multiple keywords should score higher
        
        # Test context modifier bonus
        score3 = self.crisis_service._evaluate_pattern("I always have test_keyword", test_pattern)
        assert score3 > score1  # Context modifier should increase score
        
        # Test negation reduction
        score4 = self.crisis_service._evaluate_pattern("I don't have test_keyword", test_pattern)
        assert score4 < score1  # Negation should reduce score
        
        # Test no match
        score5 = self.crisis_service._evaluate_pattern("no matching words here", test_pattern)
        assert score5 == 0
    
    def test_crisis_level_determination(self):
        """Test crisis level determination logic."""
        # Test critical level
        critical_level = self.crisis_service._determine_crisis_level(0.9, [RiskFactor.SUICIDAL_IDEATION])
        assert critical_level == CrisisLevel.CRITICAL
        
        # Test high level
        high_level = self.crisis_service._determine_crisis_level(0.8, [RiskFactor.SELF_HARM])
        assert high_level == CrisisLevel.HIGH
        
        # Test medium level
        medium_level = self.crisis_service._determine_crisis_level(0.5, [RiskFactor.DEPRESSION, RiskFactor.ISOLATION])
        assert medium_level == CrisisLevel.MEDIUM
        
        # Test low level
        low_level = self.crisis_service._determine_crisis_level(0.3, [RiskFactor.ANXIETY])
        assert low_level == CrisisLevel.LOW
        
        # Test none level
        none_level = self.crisis_service._determine_crisis_level(0.0, [])
        assert none_level == CrisisLevel.NONE
    
    def test_confidence_calculation(self):
        """Test confidence calculation."""
        # Test with various inputs
        confidence1 = self.crisis_service._calculate_confidence(
            "Short message", 
            [RiskFactor.DEPRESSION], 
            0.7
        )
        assert 0.0 <= confidence1 <= 1.0
        
        confidence2 = self.crisis_service._calculate_confidence(
            "This is a much longer message that provides more context and detail about the user's situation", 
            [RiskFactor.DEPRESSION, RiskFactor.ANXIETY], 
            0.8
        )
        assert confidence2 > confidence1  # Longer message with more factors should have higher confidence
        
        confidence3 = self.crisis_service._calculate_confidence(
            "I am going to hurt myself tonight", 
            [RiskFactor.SUICIDAL_IDEATION], 
            0.9
        )
        assert confidence3 > confidence2  # Clear intent should have highest confidence
    
    def test_intervention_generation(self):
        """Test intervention recommendation generation."""
        # Test critical interventions
        critical_interventions = self.crisis_service._generate_interventions(
            CrisisLevel.CRITICAL, 
            [RiskFactor.SUICIDAL_IDEATION]
        )
        assert any("911" in intervention for intervention in critical_interventions)
        assert any("988" in intervention for intervention in critical_interventions)
        
        # Test high interventions
        high_interventions = self.crisis_service._generate_interventions(
            CrisisLevel.HIGH, 
            [RiskFactor.SELF_HARM]
        )
        assert any("988" in intervention for intervention in high_interventions)
        assert len(high_interventions) > 0
        
        # Test medium interventions
        medium_interventions = self.crisis_service._generate_interventions(
            CrisisLevel.MEDIUM, 
            [RiskFactor.DEPRESSION]
        )
        assert any("professional" in intervention.lower() for intervention in medium_interventions)
        
        # Test low interventions
        low_interventions = self.crisis_service._generate_interventions(
            CrisisLevel.LOW, 
            [RiskFactor.ANXIETY]
        )
        assert any("self-care" in intervention.lower() for intervention in low_interventions)
    
    def test_safety_resources(self):
        """Test safety resource filtering."""
        # Test emergency resources
        emergency_resources = self.crisis_service._get_relevant_resources(
            CrisisLevel.HIGH, 
            [RiskFactor.SUICIDAL_IDEATION]
        )
        assert len(emergency_resources) > 0
        assert any(resource.get("name", "").startswith("988") for resource in emergency_resources)
        
        # Test general resources
        general_resources = self.crisis_service._get_relevant_resources(
            CrisisLevel.LOW, 
            [RiskFactor.ANXIETY]
        )
        assert len(general_resources) > 0
    
    @pytest.mark.asyncio
    async def test_escalation_process(self):
        """Test crisis escalation process."""
        # Create high-risk assessment
        assessment = RiskAssessment(
            user_id=self.test_user_id,
            trigger_content="I want to kill myself",
            crisis_level=CrisisLevel.HIGH,
            risk_score=0.9,
            detected_factors=[RiskFactor.SUICIDAL_IDEATION],
            confidence=0.95,
            immediate_action_required=True,
            recommended_interventions=["Contact crisis support"],
            safety_resources=[],
            escalation_needed=True
        )
        
        # Test escalation
        escalation_result = await self.crisis_service.escalate_crisis(
            assessment=assessment,
            escalation_type="professional"
        )
        
        assert escalation_result["escalated"] == True
        assert len(escalation_result["actions_taken"]) > 0
        assert len(escalation_result["next_steps"]) > 0
    
    @pytest.mark.asyncio
    async def test_crisis_event_storage(self):
        """Test crisis event storage in database."""
        # Mock database operations
        with patch('services.crisis_service.db') as mock_db:
            mock_db.session.add = MagicMock()
            mock_db.session.commit = MagicMock()
            
            assessment = RiskAssessment(
                user_id=self.test_user_id,
                trigger_content="Test crisis content",
                crisis_level=CrisisLevel.MEDIUM,
                risk_score=0.6,
                detected_factors=[RiskFactor.DEPRESSION],
                confidence=0.8,
                immediate_action_required=False,
                recommended_interventions=["Seek support"],
                safety_resources=[],
                escalation_needed=False
            )
            
            await self.crisis_service._store_crisis_event(assessment, "test", {})
            
            # Verify database operations were called
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in crisis assessment."""
        # Test with empty content
        assessment = await self.crisis_service.assess_crisis_risk(
            user_id=self.test_user_id,
            content="",
            trigger_source="test"
        )
        assert assessment.crisis_level == CrisisLevel.NONE
        
        # Test with very long content
        long_content = "test " * 1000
        assessment = await self.crisis_service.assess_crisis_risk(
            user_id=self.test_user_id,
            content=long_content,
            trigger_source="test"
        )
        assert assessment is not None
    
    def test_safe_default_assessment(self):
        """Test safe default assessment creation."""
        default_assessment = self.crisis_service._create_safe_default_assessment(
            self.test_user_id, 
            "test content"
        )
        
        assert default_assessment.crisis_level == CrisisLevel.NONE
        assert default_assessment.risk_score == 0.0
        assert default_assessment.escalation_needed == False
        assert len(default_assessment.safety_resources) > 0


class TestCrisisAPIEndpoints:
    """Test crisis detection API endpoints."""
    
    def setup_method(self):
        """Setup test fixtures."""
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Mock authentication
        self.test_user_id = "test_user_123"
        self.auth_headers = {"Authorization": "Bearer mock_token"}
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        self.app_context.pop()
    
    @patch('services.crisis_service.crisis_service.assess_crisis_risk')
    @patch('routes.crisis_routes.get_jwt_identity')
    def test_crisis_assessment_endpoint(self, mock_jwt, mock_assess):
        """Test crisis assessment API endpoint."""
        # Setup mocks
        mock_jwt.return_value = self.test_user_id
        mock_assessment = MagicMock()
        mock_assessment.crisis_level = CrisisLevel.MEDIUM
        mock_assessment.risk_score = 0.6
        mock_assessment.confidence = 0.8
        mock_assessment.immediate_action_required = False
        mock_assessment.escalation_needed = False
        mock_assessment.detected_factors = [RiskFactor.DEPRESSION]
        mock_assessment.recommended_interventions = ["Seek support"]
        mock_assessment.safety_resources = []
        mock_assessment.assessment_timestamp = datetime.utcnow()
        
        # Mock the async function
        async def mock_assess_async(*args, **kwargs):
            return mock_assessment
        
        mock_assess.return_value = mock_assess_async()
        
        # Test request
        response = self.client.post('/api/crisis/assess', 
            json={
                "content": "I feel really sad today",
                "source": "chat"
            },
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "risk_assessment" in data["data"]
    
    @patch('routes.crisis_routes.get_jwt_identity')
    def test_safety_resources_endpoint(self, mock_jwt):
        """Test safety resources API endpoint."""
        mock_jwt.return_value = self.test_user_id
        
        response = self.client.get('/api/crisis/resources?country=US', 
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "resources" in data["data"]
        assert len(data["data"]["resources"]) > 0
    
    @patch('routes.crisis_routes.get_jwt_identity')
    def test_risk_factors_endpoint(self, mock_jwt):
        """Test risk factors API endpoint."""
        mock_jwt.return_value = self.test_user_id
        
        response = self.client.get('/api/crisis/risk-factors', 
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "risk_factors" in data["data"]
        assert len(data["data"]["risk_factors"]) > 0
        
        # Check that each risk factor has required fields
        for factor in data["data"]["risk_factors"]:
            assert "name" in factor
            assert "description" in factor
            assert "severity" in factor
            assert "warning_signs" in factor
    
    def test_crisis_assessment_validation(self):
        """Test crisis assessment input validation."""
        # Test missing content
        response = self.client.post('/api/crisis/assess', 
            json={},
            headers=self.auth_headers
        )
        assert response.status_code == 400
        
        # Test empty content
        response = self.client.post('/api/crisis/assess', 
            json={"content": ""},
            headers=self.auth_headers
        )
        assert response.status_code == 400
    
    @patch('routes.crisis_routes.get_jwt_identity')
    def test_safety_plan_endpoint(self, mock_jwt):
        """Test safety plan creation endpoint."""
        mock_jwt.return_value = self.test_user_id
        
        safety_plan_data = {
            "warning_signs": ["Feeling hopeless", "Isolation"],
            "coping_strategies": ["Deep breathing", "Call friend"],
            "support_people": [
                {
                    "name": "John Doe",
                    "phone": "555-1234",
                    "relationship": "friend"
                }
            ],
            "professional_contacts": [],
            "environment_safety": ["Remove harmful items"],
            "reasons_to_live": ["Family", "Future goals"]
        }
        
        response = self.client.post('/api/crisis/safety-plan', 
            json=safety_plan_data,
            headers=self.auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "success"
        assert "plan_id" in data["data"]


class TestCrisisIntegration:
    """Test crisis detection integration with other systems."""
    
    def setup_method(self):
        """Setup test fixtures."""
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.test_user_id = "test_user_123"
        self.auth_headers = {"Authorization": "Bearer mock_token"}
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        self.app_context.pop()
    
    @patch('routes.conversation_routes.get_jwt_identity')
    @patch('routes.conversation_routes.HAS_CRISIS_SERVICE', True)
    def test_conversation_crisis_integration(self, mock_jwt):
        """Test crisis detection integration with conversation endpoint."""
        mock_jwt.return_value = self.test_user_id
        
        # Test crisis message in conversation
        response = self.client.post('/api/conversation/chat', 
            json={
                "message": "I want to hurt myself tonight",
                "conversation_id": "test_conv_123"
            },
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "response" in data
        
        # Check if crisis was detected (should have crisis level)
        ai_response = data["response"]
        if "crisis_level" in ai_response:
            assert ai_response["crisis_level"] in ["low", "medium", "high", "critical"]
            if ai_response["crisis_level"] in ["high", "critical"]:
                assert "safety_resources" in ai_response
                assert "988" in ai_response["text"]


if __name__ == "__main__":
    # Run specific test
    pytest.main([__file__, "-v"]) 