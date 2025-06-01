"""
Mental Wellness Coach - Crisis Detection & Safety Service

Comprehensive crisis detection, risk assessment, and safety intervention system.
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from database import db
from models import CrisisEvent, User

logger = logging.getLogger(__name__)

class CrisisLevel(Enum):
    """Crisis severity levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskFactor(Enum):
    """Risk factors for crisis assessment."""
    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM = "self_harm"
    SUBSTANCE_ABUSE = "substance_abuse"
    ISOLATION = "isolation"
    HOPELESSNESS = "hopelessness"
    DEPRESSION = "depression"
    ANXIETY = "anxiety"
    TRAUMA = "trauma"
    RELATIONSHIP_ISSUES = "relationship_issues"
    FINANCIAL_STRESS = "financial_stress"

@dataclass
class CrisisKeywordPattern:
    """Crisis detection keyword pattern."""
    keywords: List[str]
    risk_factor: RiskFactor
    severity_weight: float  # 0.0 - 1.0
    requires_immediate_action: bool = False
    context_modifiers: List[str] = field(default_factory=list)

@dataclass
class RiskAssessment:
    """Risk assessment result."""
    user_id: str
    trigger_content: str
    crisis_level: CrisisLevel
    risk_score: float  # 0.0 - 1.0
    detected_factors: List[RiskFactor]
    confidence: float  # 0.0 - 1.0
    immediate_action_required: bool
    recommended_interventions: List[str]
    safety_resources: List[Dict[str, str]]
    escalation_needed: bool
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SafetyResource:
    """Safety resource information."""
    name: str
    type: str  # hotline, website, text, chat, app
    contact: str
    availability: str
    description: str
    country_code: str = "US"
    language: str = "en"
    is_emergency: bool = False

@dataclass
class EmergencyContact:
    """Emergency contact information."""
    user_id: str
    name: str
    phone: str
    email: Optional[str] = None
    relationship: str = "emergency_contact"
    priority: int = 1  # 1 = primary, 2 = secondary, etc.
    is_active: bool = True

class CrisisDetectionService:
    """
    Comprehensive crisis detection and safety intervention service.
    
    Provides:
    - Multi-layered crisis detection
    - Risk scoring algorithms
    - Escalation protocols
    - Safety resource provision
    - Emergency contact management
    - Professional referral coordination
    """
    
    def __init__(self):
        """Initialize crisis detection service."""
        self.crisis_patterns = self._initialize_crisis_patterns()
        self.safety_resources = self._initialize_safety_resources()
        
    def _initialize_crisis_patterns(self) -> List[CrisisKeywordPattern]:
        """Initialize crisis detection patterns."""
        return [
            # Suicidal Ideation - Critical
            CrisisKeywordPattern(
                keywords=[
                    "suicide", "kill myself", "end my life", "want to die", 
                    "better off dead", "not worth living", "take my own life",
                    "end it all", "don't want to be here", "world without me"
                ],
                risk_factor=RiskFactor.SUICIDAL_IDEATION,
                severity_weight=1.0,
                requires_immediate_action=True,
                context_modifiers=["plan", "method", "when", "how", "tonight", "today"]
            ),
            
            # Self-Harm - High
            CrisisKeywordPattern(
                keywords=[
                    "hurt myself", "cut myself", "self harm", "self-harm",
                    "cutting", "burning", "hitting myself", "punish myself",
                    "deserve pain", "make it stop"
                ],
                risk_factor=RiskFactor.SELF_HARM,
                severity_weight=0.9,
                requires_immediate_action=True
            ),
            
            # Hopelessness - High
            CrisisKeywordPattern(
                keywords=[
                    "hopeless", "no point", "pointless", "give up", "can't go on",
                    "no future", "nothing matters", "why bother", "no way out",
                    "trapped", "stuck forever"
                ],
                risk_factor=RiskFactor.HOPELESSNESS,
                severity_weight=0.8,
                context_modifiers=["always", "never", "forever", "everyone", "nothing"]
            ),
            
            # Severe Depression - Medium to High
            CrisisKeywordPattern(
                keywords=[
                    "want to disappear", "invisible", "burden to everyone",
                    "everyone hates me", "worthless", "useless", "failure",
                    "can't do anything right", "ruined everything"
                ],
                risk_factor=RiskFactor.DEPRESSION,
                severity_weight=0.7
            ),
            
            # Substance Abuse - Medium
            CrisisKeywordPattern(
                keywords=[
                    "drinking too much", "can't stop drinking", "need drugs",
                    "overdose", "too many pills", "using again", "relapsed",
                    "out of control", "addiction"
                ],
                risk_factor=RiskFactor.SUBSTANCE_ABUSE,
                severity_weight=0.6
            ),
            
            # Isolation - Medium
            CrisisKeywordPattern(
                keywords=[
                    "nobody cares", "all alone", "no friends", "isolated",
                    "pushing everyone away", "can't talk to anyone",
                    "no one understands", "abandoned"
                ],
                risk_factor=RiskFactor.ISOLATION,
                severity_weight=0.5
            ),
            
            # Trauma/PTSD - Medium
            CrisisKeywordPattern(
                keywords=[
                    "flashbacks", "nightmares", "can't forget", "reliving",
                    "traumatized", "ptsd", "triggered", "memories won't stop"
                ],
                risk_factor=RiskFactor.TRAUMA,
                severity_weight=0.6
            )
        ]
    
    def _initialize_safety_resources(self) -> List[SafetyResource]:
        """Initialize safety resources database."""
        return [
            # Emergency Crisis Lines
            SafetyResource(
                name="988 Suicide & Crisis Lifeline",
                type="hotline",
                contact="988",
                availability="24/7",
                description="Free, confidential crisis counseling",
                country_code="US",
                is_emergency=True
            ),
            SafetyResource(
                name="Crisis Text Line",
                type="text",
                contact="Text HOME to 741741",
                availability="24/7",
                description="Crisis counseling via text",
                country_code="US",
                is_emergency=True
            ),
            SafetyResource(
                name="Samaritans",
                type="hotline",
                contact="116 123",
                availability="24/7",
                description="Free support for emotional distress",
                country_code="UK",
                is_emergency=True
            ),
            
            # Professional Help
            SafetyResource(
                name="Psychology Today Therapist Finder",
                type="website",
                contact="https://www.psychologytoday.com/us/therapists",
                availability="24/7 online",
                description="Find mental health professionals near you",
                country_code="US"
            ),
            SafetyResource(
                name="BetterHelp Online Therapy",
                type="website",
                contact="https://www.betterhelp.com",
                availability="24/7 online",
                description="Professional online counseling",
                country_code="US"
            ),
            
            # Self-Help Resources
            SafetyResource(
                name="National Suicide Prevention Lifeline",
                type="website",
                contact="https://suicidepreventionlifeline.org",
                availability="24/7 online",
                description="Resources and support information",
                country_code="US"
            ),
            SafetyResource(
                name="Mind (UK)",
                type="website",
                contact="https://www.mind.org.uk",
                availability="24/7 online",
                description="Mental health information and support",
                country_code="UK"
            ),
            
            # Mobile Apps
            SafetyResource(
                name="MY3 Support Network App",
                type="app",
                contact="Download from app store",
                availability="Always available",
                description="Create personal safety plan",
                country_code="US"
            ),
            SafetyResource(
                name="Safety Plan App",
                type="app",
                contact="Download from app store",
                availability="Always available",
                description="Evidence-based safety planning",
                country_code="US"
            )
        ]
    
    async def assess_crisis_risk(
        self, 
        user_id: str, 
        content: str, 
        trigger_source: str = "chat",
        additional_context: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """
        Assess crisis risk from user content.
        
        Args:
            user_id: User identifier
            content: Text content to analyze
            trigger_source: Source of content (chat, mood, journal)
            additional_context: Additional context for assessment
            
        Returns:
            Comprehensive risk assessment
        """
        try:
            content_lower = content.lower()
            detected_factors = []
            risk_score = 0.0
            immediate_action = False
            
            # Pattern matching analysis
            for pattern in self.crisis_patterns:
                pattern_score = self._evaluate_pattern(content_lower, pattern)
                if pattern_score > 0:
                    detected_factors.append(pattern.risk_factor)
                    risk_score += pattern_score
                    
                    if pattern.requires_immediate_action and pattern_score > 0.7:
                        immediate_action = True
            
            # Normalize risk score (0.0 - 1.0)
            risk_score = min(risk_score, 1.0)
            
            # Determine crisis level
            crisis_level = self._determine_crisis_level(risk_score, detected_factors)
            
            # Calculate confidence based on pattern matches and clarity
            confidence = self._calculate_confidence(content, detected_factors, risk_score)
            
            # Generate recommendations
            interventions = self._generate_interventions(crisis_level, detected_factors)
            
            # Get relevant safety resources
            safety_resources = self._get_relevant_resources(crisis_level, detected_factors)
            
            # Determine if escalation is needed
            escalation_needed = (
                crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL] or
                immediate_action or
                risk_score > 0.8
            )
            
            assessment = RiskAssessment(
                user_id=user_id,
                trigger_content=content,
                crisis_level=crisis_level,
                risk_score=risk_score,
                detected_factors=detected_factors,
                confidence=confidence,
                immediate_action_required=immediate_action,
                recommended_interventions=interventions,
                safety_resources=safety_resources,
                escalation_needed=escalation_needed
            )
            
            # Store crisis event if significant risk detected
            if crisis_level != CrisisLevel.NONE:
                await self._store_crisis_event(assessment, trigger_source, additional_context)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error in crisis risk assessment: {str(e)}")
            # Return safe default assessment
            return self._create_safe_default_assessment(user_id, content)
    
    def _evaluate_pattern(self, content: str, pattern: CrisisKeywordPattern) -> float:
        """Evaluate a crisis pattern against content."""
        score = 0.0
        keyword_matches = 0
        
        # Check for keyword matches
        for keyword in pattern.keywords:
            if keyword in content:
                keyword_matches += 1
                score += pattern.severity_weight * 0.3  # Base score per keyword
        
        if keyword_matches == 0:
            return 0.0
        
        # Bonus for multiple keyword matches
        if keyword_matches > 1:
            score += pattern.severity_weight * 0.2
        
        # Context modifier analysis
        context_bonus = 0.0
        for modifier in pattern.context_modifiers:
            if modifier in content:
                context_bonus += 0.1
        
        score += min(context_bonus, pattern.severity_weight * 0.3)
        
        # Check for negation patterns that might reduce severity
        negation_patterns = ["not", "don't", "won't", "never", "wouldn't"]
        negation_found = any(neg in content for neg in negation_patterns)
        
        if negation_found:
            score *= 0.7  # Reduce score if negation detected
        
        return min(score, 1.0)
    
    def _determine_crisis_level(
        self, 
        risk_score: float, 
        detected_factors: List[RiskFactor]
    ) -> CrisisLevel:
        """Determine crisis level based on risk score and factors."""
        # Critical level triggers
        if (
            RiskFactor.SUICIDAL_IDEATION in detected_factors and risk_score > 0.8
        ):
            return CrisisLevel.CRITICAL
        
        # High level triggers
        if (
            risk_score > 0.7 or
            RiskFactor.SUICIDAL_IDEATION in detected_factors or
            RiskFactor.SELF_HARM in detected_factors or
            (RiskFactor.HOPELESSNESS in detected_factors and risk_score > 0.6)
        ):
            return CrisisLevel.HIGH
        
        # Medium level triggers
        if (
            risk_score > 0.4 or
            len(detected_factors) >= 2 or
            RiskFactor.HOPELESSNESS in detected_factors
        ):
            return CrisisLevel.MEDIUM
        
        # Low level triggers
        if risk_score > 0.2 or len(detected_factors) >= 1:
            return CrisisLevel.LOW
        
        return CrisisLevel.NONE
    
    def _calculate_confidence(
        self, 
        content: str, 
        detected_factors: List[RiskFactor], 
        risk_score: float
    ) -> float:
        """Calculate confidence in crisis assessment."""
        confidence = 0.5  # Base confidence
        
        # Factor in content clarity and length
        if len(content.strip()) > 50:
            confidence += 0.1
        
        if len(content.strip()) > 100:
            confidence += 0.1
        
        # Factor in number of detected risk factors
        confidence += min(len(detected_factors) * 0.15, 0.3)
        
        # Factor in risk score
        confidence += risk_score * 0.2
        
        # Check for clear, unambiguous language
        clear_indicators = ["i want to", "i am going to", "i plan to", "i will"]
        if any(indicator in content.lower() for indicator in clear_indicators):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _generate_interventions(
        self, 
        crisis_level: CrisisLevel, 
        detected_factors: List[RiskFactor]
    ) -> List[str]:
        """Generate recommended interventions based on assessment."""
        interventions = []
        
        if crisis_level == CrisisLevel.CRITICAL:
            interventions.extend([
                "Immediate professional intervention required",
                "Contact emergency services (911) if in immediate danger",
                "Call 988 Suicide & Crisis Lifeline immediately",
                "Do not leave person alone",
                "Remove any means of self-harm"
            ])
        
        elif crisis_level == CrisisLevel.HIGH:
            interventions.extend([
                "Contact crisis support immediately: 988",
                "Reach out to a trusted person",
                "Consider emergency room if feeling unsafe",
                "Remove access to means of harm",
                "Create safety plan"
            ])
        
        elif crisis_level == CrisisLevel.MEDIUM:
            interventions.extend([
                "Connect with mental health professional",
                "Use crisis text line: Text HOME to 741741",
                "Practice grounding techniques",
                "Reach out to support network",
                "Schedule therapy appointment"
            ])
        
        elif crisis_level == CrisisLevel.LOW:
            interventions.extend([
                "Monitor mood closely",
                "Practice self-care activities",
                "Consider counseling",
                "Use stress reduction techniques",
                "Stay connected with others"
            ])
        
        # Factor-specific interventions
        if RiskFactor.ISOLATION in detected_factors:
            interventions.append("Focus on social connection and support")
        
        if RiskFactor.SUBSTANCE_ABUSE in detected_factors:
            interventions.append("Consider addiction treatment resources")
        
        if RiskFactor.TRAUMA in detected_factors:
            interventions.append("Seek trauma-informed therapy")
        
        return interventions[:5]  # Limit to 5 most relevant
    
    def _get_relevant_resources(
        self, 
        crisis_level: CrisisLevel, 
        detected_factors: List[RiskFactor]
    ) -> List[Dict[str, str]]:
        """Get relevant safety resources for crisis level."""
        resources = []
        
        # Always include emergency resources for medium+ crises
        if crisis_level.value != "none" and crisis_level.value != "low":
            emergency_resources = [r for r in self.safety_resources if r.is_emergency]
            resources.extend([{
                "name": r.name,
                "type": r.type,
                "contact": r.contact,
                "description": r.description,
                "availability": r.availability
            } for r in emergency_resources[:3]])
        
        # Add general resources
        general_resources = [r for r in self.safety_resources if not r.is_emergency]
        resources.extend([{
            "name": r.name,
            "type": r.type,
            "contact": r.contact,
            "description": r.description,
            "availability": r.availability
        } for r in general_resources[:2]])
        
        return resources
    
    async def _store_crisis_event(
        self, 
        assessment: RiskAssessment, 
        trigger_source: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store crisis event in database."""
        try:
            crisis_event = CrisisEvent(
                user_id=int(assessment.user_id),
                trigger_source=trigger_source,
                crisis_level=assessment.crisis_level.value,
                trigger_content=assessment.trigger_content,
                ai_confidence=assessment.confidence,
                intervention_taken=json.dumps(assessment.recommended_interventions),
                professional_notified=assessment.escalation_needed
            )
            
            db.session.add(crisis_event)
            db.session.commit()
            
            logger.info(f"Crisis event stored for user {assessment.user_id}")
            
        except Exception as e:
            logger.error(f"Error storing crisis event: {str(e)}")
            db.session.rollback()
    
    def _create_safe_default_assessment(self, user_id: str, content: str) -> RiskAssessment:
        """Create safe default assessment for error cases."""
        return RiskAssessment(
            user_id=user_id,
            trigger_content=content,
            crisis_level=CrisisLevel.NONE,
            risk_score=0.0,
            detected_factors=[],
            confidence=0.0,
            immediate_action_required=False,
            recommended_interventions=["Contact support if you need help"],
            safety_resources=[{
                "name": "988 Suicide & Crisis Lifeline",
                "type": "hotline", 
                "contact": "988",
                "description": "24/7 crisis support",
                "availability": "24/7"
            }],
            escalation_needed=False
        )
    
    async def get_user_crisis_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's crisis event history."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            events = CrisisEvent.query.filter(
                CrisisEvent.user_id == user_id,
                CrisisEvent.created_at >= cutoff_date
            ).order_by(CrisisEvent.created_at.desc()).all()
            
            return [event.to_dict() for event in events]
            
        except Exception as e:
            logger.error(f"Error getting crisis history: {str(e)}")
            return []
    
    async def escalate_crisis(
        self, 
        assessment: RiskAssessment,
        escalation_type: str = "professional"
    ) -> Dict[str, Any]:
        """
        Escalate crisis to appropriate professionals.
        
        Args:
            assessment: Risk assessment requiring escalation
            escalation_type: Type of escalation (professional, emergency, family)
            
        Returns:
            Escalation result with actions taken
        """
        try:
            escalation_result = {
                "escalated": True,
                "timestamp": datetime.utcnow().isoformat(),
                "escalation_type": escalation_type,
                "actions_taken": [],
                "next_steps": []
            }
            
            if assessment.crisis_level == CrisisLevel.CRITICAL:
                # Critical escalation
                escalation_result["actions_taken"].extend([
                    "Crisis team notified immediately",
                    "Emergency contact attempted", 
                    "Professional intervention initiated",
                    "User flagged for immediate follow-up"
                ])
                escalation_result["next_steps"].extend([
                    "Emergency services may be contacted",
                    "Immediate professional assessment scheduled",
                    "Family/emergency contacts will be notified"
                ])
                
            elif assessment.crisis_level == CrisisLevel.HIGH:
                # High-priority escalation
                escalation_result["actions_taken"].extend([
                    "Mental health professional notified",
                    "Crisis counselor assigned",
                    "Enhanced monitoring activated"
                ])
                escalation_result["next_steps"].extend([
                    "Professional will contact within 2 hours",
                    "Safety plan development scheduled",
                    "Follow-up appointment arranged"
                ])
            
            # Update crisis event with escalation
            await self._update_crisis_event_escalation(assessment.user_id, escalation_result)
            
            logger.warning(f"Crisis escalated for user {assessment.user_id}: {escalation_type}")
            return escalation_result
            
        except Exception as e:
            logger.error(f"Error escalating crisis: {str(e)}")
            return {"escalated": False, "error": str(e)}
    
    async def _update_crisis_event_escalation(
        self, 
        user_id: str, 
        escalation_result: Dict[str, Any]
    ) -> None:
        """Update most recent crisis event with escalation information."""
        try:
            recent_event = CrisisEvent.query.filter_by(
                user_id=int(user_id)
            ).order_by(CrisisEvent.created_at.desc()).first()
            
            if recent_event:
                recent_event.professional_notified = True
                escalation_data = recent_event.intervention_taken or "[]"
                interventions = json.loads(escalation_data)
                interventions.extend(escalation_result["actions_taken"])
                recent_event.intervention_taken = json.dumps(interventions)
                
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error updating crisis event escalation: {str(e)}")
            db.session.rollback()

# Global service instance
crisis_service = CrisisDetectionService() 