import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Linking,
  RefreshControl,
} from 'react-native';
import {
  CrisisService,
  EmergencyContact,
  SafetyResource,
} from '../../services/CrisisService';

interface CrisisHelpScreenProps {
  navigation: any;
}

const CrisisHelpScreen: React.FC<CrisisHelpScreenProps> = ({ navigation }) => {
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>([]);
  const [safetyResources, setSafetyResources] = useState<SafetyResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadCrisisData();
  }, []);

  const loadCrisisData = async () => {
    try {
      setLoading(true);
      const [contactsResponse, resourcesResponse] = await Promise.all([
        CrisisService.getEmergencyContacts(),
        CrisisService.getSafetyResources(),
      ]);

      setEmergencyContacts(contactsResponse.contacts);
      setSafetyResources(resourcesResponse.resources);
    } catch (error) {
      console.error('Error loading crisis data:', error);
      Alert.alert('Error', 'Failed to load crisis resources');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCrisisData();
    setRefreshing(false);
  };

  const handleEmergencyCall = async (contact: EmergencyContact) => {
    try {
      const phoneUrl = `tel:${contact.phone}`;
      const canOpen = await Linking.canOpenURL(phoneUrl);
      
      if (canOpen) {
        if (contact.relationship === 'emergency' || contact.relationship === 'crisis_hotline') {
          Alert.alert(
            'Emergency Call',
            `Are you sure you want to call ${contact.name}?`,
            [
              { text: 'Cancel', style: 'cancel' },
              { 
                text: 'Call Now', 
                style: 'destructive',
                onPress: () => Linking.openURL(phoneUrl)
              },
            ]
          );
        } else {
          await Linking.openURL(phoneUrl);
        }
      } else {
        Alert.alert('Error', 'Unable to make phone calls on this device');
      }
    } catch (error) {
      console.error('Error making call:', error);
      Alert.alert('Error', 'Failed to make call');
    }
  };

  const handleResourceAccess = async (resource: SafetyResource) => {
    try {
      let url = resource.contact;
      
      if (resource.type === 'hotline') {
        url = `tel:${resource.contact}`;
      } else if (resource.type === 'text') {
        url = `sms:${resource.contact}`;
      } else if (!url.startsWith('http')) {
        url = `https://${url}`;
      }

      const canOpen = await Linking.canOpenURL(url);
      if (canOpen) {
        await Linking.openURL(url);
      } else {
        Alert.alert('Error', 'Unable to access this resource');
      }
    } catch (error) {
      console.error('Error accessing resource:', error);
      Alert.alert('Error', 'Failed to access resource');
    }
  };

  const EmergencyContactCard: React.FC<{ contact: EmergencyContact }> = ({ contact }) => {
    const getContactColor = () => {
      switch (contact.relationship) {
        case 'emergency': return '#E74C3C';
        case 'crisis_hotline': return '#E67E22';
        case 'crisis_text': return '#F39C12';
        default: return '#3498DB';
      }
    };

    const getContactIcon = () => {
      switch (contact.relationship) {
        case 'emergency': return '🚨';
        case 'crisis_hotline': return '📞';
        case 'crisis_text': return '💬';
        default: return '📋';
      }
    };

    return (
      <TouchableOpacity
        style={[styles.contactCard, { borderLeftColor: getContactColor() }]}
        onPress={() => handleEmergencyCall(contact)}
      >
        <View style={styles.contactHeader}>
          <Text style={styles.contactIcon}>{getContactIcon()}</Text>
          <View style={styles.contactInfo}>
            <Text style={styles.contactName}>{contact.name}</Text>
            <Text style={styles.contactPhone}>
              {CrisisService.formatPhoneNumber(contact.phone)}
            </Text>
          </View>
          <View style={[styles.priorityBadge, { backgroundColor: getContactColor() }]}>
            <Text style={styles.priorityText}>#{contact.priority}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  const SafetyResourceCard: React.FC<{ resource: SafetyResource }> = ({ resource }) => {
    const getResourceIcon = () => {
      switch (resource.type) {
        case 'hotline': return '📞';
        case 'text': return '💬';
        case 'chat': return '💭';
        case 'website': return '🌐';
        case 'app': return '📱';
        default: return '📋';
      }
    };

    return (
      <TouchableOpacity
        style={[
          styles.resourceCard,
          resource.is_emergency && styles.emergencyResource
        ]}
        onPress={() => handleResourceAccess(resource)}
      >
        <View style={styles.resourceHeader}>
          <Text style={styles.resourceIcon}>{getResourceIcon()}</Text>
          <View style={styles.resourceInfo}>
            <Text style={styles.resourceName}>{resource.name}</Text>
            <Text style={styles.resourceType}>{resource.type.toUpperCase()}</Text>
          </View>
          {resource.is_emergency && (
            <View style={styles.emergencyBadge}>
              <Text style={styles.emergencyText}>EMERGENCY</Text>
            </View>
          )}
        </View>
        <Text style={styles.resourceDescription} numberOfLines={2}>
          {resource.description}
        </Text>
        <Text style={styles.resourceAvailability}>{resource.availability}</Text>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading crisis resources...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Crisis Help</Text>
        <Text style={styles.headerSubtitle}>
          Immediate support when you need it most
        </Text>
      </View>

      {/* Crisis Warning */}
      <View style={styles.warningCard}>
        <Text style={styles.warningEmoji}>⚠️</Text>
        <Text style={styles.warningTitle}>If you're in immediate danger</Text>
        <Text style={styles.warningText}>
          Call 911 or go to your nearest emergency room. You are not alone, and help is available.
        </Text>
      </View>

      {/* Emergency Contacts */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Emergency Contacts</Text>
        <Text style={styles.sectionSubtitle}>
          Immediate crisis support available 24/7
        </Text>
        {emergencyContacts
          .filter(contact => contact.is_active)
          .sort((a, b) => a.priority - b.priority)
          .map((contact) => (
            <EmergencyContactCard key={contact.id} contact={contact} />
          ))}
      </View>

      {/* Safety Resources */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Safety Resources</Text>
        <Text style={styles.sectionSubtitle}>
          Additional support and information
        </Text>
        {safetyResources.map((resource) => (
          <SafetyResourceCard key={resource.id} resource={resource} />
        ))}
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Crisis Tools</Text>
        <View style={styles.quickActionsGrid}>
          <TouchableOpacity
            style={[styles.quickActionCard, { backgroundColor: '#8E44AD' }]}
            onPress={() => navigation.navigate('SafetyPlan')}
          >
            <Text style={styles.quickActionEmoji}>🛡️</Text>
            <Text style={styles.quickActionTitle}>Safety Plan</Text>
            <Text style={styles.quickActionSubtitle}>Create your plan</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.quickActionCard, { backgroundColor: '#27AE60' }]}
            onPress={() => navigation.navigate('CopingStrategies')}
          >
            <Text style={styles.quickActionEmoji}>🧘</Text>
            <Text style={styles.quickActionTitle}>Coping Tools</Text>
            <Text style={styles.quickActionSubtitle}>Immediate relief</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.quickActionCard, { backgroundColor: '#E67E22' }]}
            onPress={() => navigation.navigate('RiskFactors')}
          >
            <Text style={styles.quickActionEmoji}>⚡</Text>
            <Text style={styles.quickActionTitle}>Warning Signs</Text>
            <Text style={styles.quickActionSubtitle}>Learn to recognize</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.quickActionCard, { backgroundColor: '#34495E' }]}
            onPress={() => navigation.navigate('CrisisHistory')}
          >
            <Text style={styles.quickActionEmoji}>📊</Text>
            <Text style={styles.quickActionTitle}>My History</Text>
            <Text style={styles.quickActionSubtitle}>Track progress</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Footer Message */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Remember: You are not alone. Crisis is temporary, but help is always available.
          Your life has value and meaning.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    fontSize: 16,
    color: '#7F8C8D',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#ECF0F1',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#E74C3C',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#7F8C8D',
  },
  warningCard: {
    backgroundColor: '#FFE5E5',
    margin: 20,
    padding: 20,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#E74C3C',
    alignItems: 'center',
  },
  warningEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  warningTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#C0392B',
    marginBottom: 8,
    textAlign: 'center',
  },
  warningText: {
    fontSize: 14,
    color: '#E74C3C',
    textAlign: 'center',
    lineHeight: 20,
  },
  section: {
    margin: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 15,
  },
  contactCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  contactHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  contactIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 2,
  },
  contactPhone: {
    fontSize: 14,
    color: '#7F8C8D',
    fontFamily: 'monospace',
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  resourceCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  emergencyResource: {
    borderLeftWidth: 4,
    borderLeftColor: '#E74C3C',
  },
  resourceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  resourceIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  resourceInfo: {
    flex: 1,
  },
  resourceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 2,
  },
  resourceType: {
    fontSize: 10,
    color: '#7F8C8D',
    fontWeight: '600',
  },
  emergencyBadge: {
    backgroundColor: '#E74C3C',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  emergencyText: {
    fontSize: 8,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  resourceDescription: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 8,
    lineHeight: 18,
  },
  resourceAvailability: {
    fontSize: 12,
    color: '#27AE60',
    fontWeight: '500',
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionCard: {
    width: '48%',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionEmoji: {
    fontSize: 28,
    marginBottom: 8,
  },
  quickActionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 4,
    textAlign: 'center',
  },
  quickActionSubtitle: {
    fontSize: 12,
    color: '#FFFFFF',
    opacity: 0.9,
    textAlign: 'center',
  },
  footer: {
    margin: 20,
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
    lineHeight: 20,
    fontStyle: 'italic',
  },
});

export default CrisisHelpScreen; 