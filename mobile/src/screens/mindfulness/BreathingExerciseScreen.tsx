import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Animated,
  Dimensions,
} from 'react-native';
import { MindfulnessService } from '../../services/MindfulnessService';

interface BreathingExerciseScreenProps {
  navigation: any;
  route?: {
    params?: {
      template?: any;
      sessionType?: string;
    };
  };
}

const { width, height } = Dimensions.get('window');

const BreathingExerciseScreen: React.FC<BreathingExerciseScreenProps> = ({ navigation, route }) => {
  const [isActive, setIsActive] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<'inhale' | 'hold' | 'exhale' | 'rest'>('inhale');
  const [seconds, setSeconds] = useState(0);
  const [totalSeconds, setTotalSeconds] = useState(0);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [breathCount, setBreathCount] = useState(0);
  const [pattern, setPattern] = useState({ inhale: 4, hold: 7, exhale: 8, rest: 0 }); // 4-7-8 breathing
  const [selectedPattern, setSelectedPattern] = useState('4-7-8');
  
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(0.3)).current;
  
  const patterns = {
    '4-7-8': { inhale: 4, hold: 7, exhale: 8, rest: 0, name: '4-7-8 Breathing' },
    'box': { inhale: 4, hold: 4, exhale: 4, rest: 4, name: 'Box Breathing' },
    'triangle': { inhale: 4, hold: 4, exhale: 4, rest: 0, name: 'Triangle Breathing' },
    'deep': { inhale: 6, hold: 2, exhale: 6, rest: 2, name: 'Deep Breathing' },
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isActive) {
      interval = setInterval(() => {
        setSeconds(prevSeconds => {
          const newSeconds = prevSeconds + 1;
          setTotalSeconds(prev => prev + 1);
          
          // Determine current phase based on pattern
          const totalCycle = pattern.inhale + pattern.hold + pattern.exhale + pattern.rest;
          const cyclePosition = newSeconds % totalCycle;
          
          let newPhase: typeof currentPhase;
          if (cyclePosition < pattern.inhale) {
            newPhase = 'inhale';
          } else if (cyclePosition < pattern.inhale + pattern.hold) {
            newPhase = 'hold';
          } else if (cyclePosition < pattern.inhale + pattern.hold + pattern.exhale) {
            newPhase = 'exhale';
          } else {
            newPhase = 'rest';
          }
          
          if (newPhase !== currentPhase) {
            setCurrentPhase(newPhase);
            if (newPhase === 'inhale' && cyclePosition === 0) {
              setBreathCount(prev => prev + 1);
            }
          }
          
          return newSeconds;
        });
      }, 1000);
    }
    
    return () => clearInterval(interval);
  }, [isActive, pattern, currentPhase]);

  useEffect(() => {
    // Animate circle based on breathing phase
    const animateCircle = () => {
      const inhaleScale = 1.5;
      const exhaleScale = 0.8;
      const duration = 1000;
      
      switch (currentPhase) {
        case 'inhale':
          Animated.parallel([
            Animated.timing(scaleAnim, {
              toValue: inhaleScale,
              duration: pattern.inhale * duration,
              useNativeDriver: true,
            }),
            Animated.timing(opacityAnim, {
              toValue: 0.8,
              duration: pattern.inhale * duration,
              useNativeDriver: true,
            }),
          ]).start();
          break;
        case 'hold':
          // Stay at current size
          break;
        case 'exhale':
          Animated.parallel([
            Animated.timing(scaleAnim, {
              toValue: exhaleScale,
              duration: pattern.exhale * duration,
              useNativeDriver: true,
            }),
            Animated.timing(opacityAnim, {
              toValue: 0.3,
              duration: pattern.exhale * duration,
              useNativeDriver: true,
            }),
          ]).start();
          break;
        case 'rest':
          // Stay at small size
          break;
      }
    };
    
    if (isActive) {
      animateCircle();
    }
  }, [currentPhase, isActive, pattern, scaleAnim, opacityAnim]);

  const startSession = async () => {
    try {
      // Create a new mindfulness session
      const response = await MindfulnessService.createSession({
        session_type: 'breathing',
        title: patterns[selectedPattern as keyof typeof patterns].name,
        description: `${selectedPattern} breathing pattern for relaxation and stress relief`,
        duration_minutes: 5, // Default 5 minutes
      });
      
      setSessionId(response.session.id);
      setIsActive(true);
      setSeconds(0);
      setTotalSeconds(0);
      setBreathCount(0);
      setCurrentPhase('inhale');
    } catch (error) {
      console.error('Error starting breathing session:', error);
      Alert.alert('Error', 'Failed to start breathing session');
    }
  };

  const pauseSession = () => {
    setIsActive(false);
  };

  const resumeSession = () => {
    setIsActive(true);
  };

  const endSession = async () => {
    try {
      setIsActive(false);
      
      if (sessionId) {
        await MindfulnessService.completeSession(sessionId, {
          completed_duration_minutes: Math.floor(totalSeconds / 60),
          session_data: {
            breathing_pattern: selectedPattern,
            total_breaths: breathCount,
            total_seconds: totalSeconds,
          },
        });
      }
      
      navigation.navigate('SessionComplete', {
        sessionData: {
          duration: Math.floor(totalSeconds / 60),
          breathCount,
          pattern: selectedPattern,
        },
      });
    } catch (error) {
      console.error('Error completing breathing session:', error);
      Alert.alert('Error', 'Failed to save session data');
      navigation.goBack();
    }
  };

  const selectPattern = (patternKey: string) => {
    if (!isActive) {
      setSelectedPattern(patternKey);
      setPattern(patterns[patternKey as keyof typeof patterns]);
    }
  };

  const getPhaseText = () => {
    switch (currentPhase) {
      case 'inhale': return 'Breathe In';
      case 'hold': return 'Hold';
      case 'exhale': return 'Breathe Out';
      case 'rest': return 'Rest';
      default: return 'Breathe';
    }
  };

  const getPhaseColor = () => {
    switch (currentPhase) {
      case 'inhale': return '#4ECDC4';
      case 'hold': return '#45B7D1';
      case 'exhale': return '#96CEB4';
      case 'rest': return '#FECA57';
      default: return '#4ECDC4';
    }
  };

  const formatTime = (totalSeconds: number) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Breathing Exercise</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Pattern Selection */}
      {!isActive && (
        <View style={styles.patternSection}>
          <Text style={styles.sectionTitle}>Choose a Pattern</Text>
          <View style={styles.patternGrid}>
            {Object.entries(patterns).map(([key, patternData]) => (
              <TouchableOpacity
                key={key}
                style={[
                  styles.patternCard,
                  selectedPattern === key && styles.selectedPattern
                ]}
                onPress={() => selectPattern(key)}
              >
                <Text style={[
                  styles.patternName,
                  selectedPattern === key && styles.selectedPatternText
                ]}>
                  {patternData.name}
                </Text>
                <Text style={[
                  styles.patternDetails,
                  selectedPattern === key && styles.selectedPatternText
                ]}>
                  {patternData.inhale}-{patternData.hold}-{patternData.exhale}
                  {patternData.rest > 0 && `-${patternData.rest}`}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {/* Breathing Circle */}
      <View style={styles.circleContainer}>
        <Animated.View
          style={[
            styles.breathingCircle,
            {
              backgroundColor: getPhaseColor(),
              transform: [{ scale: scaleAnim }],
              opacity: opacityAnim,
            },
          ]}
        />
        <View style={styles.circleContent}>
          <Text style={styles.phaseText}>{getPhaseText()}</Text>
          {isActive && (
            <Text style={styles.countdownText}>
              {currentPhase === 'inhale' && `${pattern.inhale - (seconds % (pattern.inhale + pattern.hold + pattern.exhale + pattern.rest))}`}
              {currentPhase === 'hold' && `${pattern.hold - ((seconds - pattern.inhale) % (pattern.inhale + pattern.hold + pattern.exhale + pattern.rest))}`}
              {currentPhase === 'exhale' && `${pattern.exhale - ((seconds - pattern.inhale - pattern.hold) % (pattern.inhale + pattern.hold + pattern.exhale + pattern.rest))}`}
              {currentPhase === 'rest' && `${pattern.rest - ((seconds - pattern.inhale - pattern.hold - pattern.exhale) % (pattern.inhale + pattern.hold + pattern.exhale + pattern.rest))}`}
            </Text>
          )}
        </View>
      </View>

      {/* Stats */}
      {isActive && (
        <View style={styles.statsContainer}>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>{formatTime(totalSeconds)}</Text>
            <Text style={styles.statLabel}>Time</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>{breathCount}</Text>
            <Text style={styles.statLabel}>Breaths</Text>
          </View>
        </View>
      )}

      {/* Controls */}
      <View style={styles.controls}>
        {!isActive ? (
          <TouchableOpacity style={styles.startButton} onPress={startSession}>
            <Text style={styles.startButtonText}>Start Session</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.activeControls}>
            <TouchableOpacity style={styles.pauseButton} onPress={pauseSession}>
              <Text style={styles.controlButtonText}>Pause</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.endButton} onPress={endSession}>
              <Text style={styles.controlButtonText}>End Session</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Instructions */}
      {!isActive && (
        <View style={styles.instructions}>
          <Text style={styles.instructionsTitle}>Instructions</Text>
          <Text style={styles.instructionsText}>
            Follow the expanding and contracting circle with your breath. 
            Breathe in as the circle grows, hold as it stays still, and breathe out as it shrinks.
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#ECF0F1',
  },
  backButton: {
    fontSize: 24,
    color: '#3498DB',
    fontWeight: 'bold',
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#2C3E50',
  },
  placeholder: {
    width: 24,
  },
  patternSection: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 15,
  },
  patternGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  patternCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#ECF0F1',
  },
  selectedPattern: {
    borderColor: '#4ECDC4',
    backgroundColor: '#4ECDC4',
  },
  patternName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4,
  },
  patternDetails: {
    fontSize: 12,
    color: '#7F8C8D',
  },
  selectedPatternText: {
    color: '#FFFFFF',
  },
  circleContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  breathingCircle: {
    width: 200,
    height: 200,
    borderRadius: 100,
    position: 'absolute',
  },
  circleContent: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  phaseText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8,
  },
  countdownText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#3498DB',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 40,
    paddingVertical: 20,
  },
  stat: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#27AE60',
  },
  statLabel: {
    fontSize: 14,
    color: '#7F8C8D',
    marginTop: 4,
  },
  controls: {
    padding: 20,
  },
  startButton: {
    backgroundColor: '#4ECDC4',
    paddingVertical: 15,
    borderRadius: 12,
    alignItems: 'center',
  },
  startButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  activeControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  pauseButton: {
    backgroundColor: '#F39C12',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 12,
    flex: 0.45,
    alignItems: 'center',
  },
  endButton: {
    backgroundColor: '#E74C3C',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 12,
    flex: 0.45,
    alignItems: 'center',
  },
  controlButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  instructions: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
  },
  instructionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 10,
  },
  instructionsText: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
  },
});

export default BreathingExerciseScreen; 