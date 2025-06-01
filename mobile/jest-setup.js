// Jest setup for React Native testing

// Mock all React Native modules BEFORE any imports
// This prevents issues with module loading order

// Mock PixelRatio first - this is critical for StyleSheet
jest.doMock('react-native/Libraries/Utilities/PixelRatio', () => ({
  get: jest.fn(() => 2),
  getFontScale: jest.fn(() => 1),
  getPixelSizeForLayoutSize: jest.fn((size) => size * 2),
  roundToNearestPixel: jest.fn((size) => size),
}));

// Mock StyleSheet to prevent PixelRatio access issues
jest.doMock('react-native/Libraries/StyleSheet/StyleSheet', () => ({
  create: jest.fn((styles) => styles),
  flatten: jest.fn((style) => style),
  compose: jest.fn((style1, style2) => [style1, style2].filter(Boolean)),
  hairlineWidth: 1,
  absoluteFill: {},
  absoluteFillObject: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
  },
}));

// Mock Dimensions
jest.doMock('react-native/Libraries/Utilities/Dimensions', () => ({
  get: jest.fn(() => ({ width: 375, height: 667, scale: 2, fontScale: 1 })),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  getConstants: () => ({
    window: { width: 375, height: 667, scale: 2, fontScale: 1 },
    screen: { width: 375, height: 667, scale: 2, fontScale: 1 },
  }),
}));

// Mock Settings
jest.doMock('react-native/Libraries/Settings/Settings', () => ({
  get: jest.fn(),
  set: jest.fn(),
  watchKeys: jest.fn(),
  clearWatch: jest.fn(),
}));

// Mock NativeDeviceInfo
jest.doMock('react-native/Libraries/Utilities/NativeDeviceInfo', () => ({
  getConstants: () => ({
    Dimensions: {
      window: { width: 375, height: 667, scale: 2, fontScale: 1 },
      screen: { width: 375, height: 667, scale: 2, fontScale: 1 },
    },
  }),
}));

// Mock TurboModuleRegistry
jest.doMock('react-native/Libraries/TurboModule/TurboModuleRegistry', () => ({
  getEnforcing: jest.fn(() => ({
    getConstants: () => ({}),
  })),
  get: jest.fn(() => ({
    getConstants: () => ({}),
  })),
}));

// Mock Platform
jest.doMock('react-native/Libraries/Utilities/Platform', () => ({
  OS: 'ios',
  Version: '14.0',
  isTV: false,
  isTesting: true,
  constants: {},
  select: jest.fn((obj) => obj.ios || obj.default),
}));

// Mock Alert
jest.doMock('react-native/Libraries/Alert/Alert', () => ({
  alert: jest.fn(),
}));

// Comprehensive React Native mock
jest.doMock('react-native', () => {
  const mockPixelRatio = {
    get: jest.fn(() => 2),
    getFontScale: jest.fn(() => 1),
    getPixelSizeForLayoutSize: jest.fn((size) => size * 2),
    roundToNearestPixel: jest.fn((size) => size),
  };

  const mockDimensions = {
    get: jest.fn(() => ({ width: 375, height: 667, scale: 2, fontScale: 1 })),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  };

  const mockStyleSheet = {
    create: jest.fn((styles) => styles),
    flatten: jest.fn((style) => style),
    compose: jest.fn((style1, style2) => [style1, style2].filter(Boolean)),
    hairlineWidth: 1,
    absoluteFill: {},
    absoluteFillObject: {
      position: 'absolute',
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
    },
  };

  return {
    // Core APIs
    Alert: { alert: jest.fn() },
    Dimensions: mockDimensions,
    PixelRatio: mockPixelRatio,
    StyleSheet: mockStyleSheet,
    Platform: {
      OS: 'ios',
      Version: '14.0',
      isTV: false,
      isTesting: true,
      constants: {},
      select: jest.fn((obj) => obj.ios || obj.default),
    },
    Settings: {
      get: jest.fn(),
      set: jest.fn(),
      watchKeys: jest.fn(),
      clearWatch: jest.fn(),
    },

    // Components as strings (will be mocked by Jest)
    ActivityIndicator: 'ActivityIndicator',
    Button: 'Button',
    FlatList: 'FlatList',
    Image: 'Image',
    RefreshControl: 'RefreshControl',
    ScrollView: 'ScrollView',
    SectionList: 'SectionList',
    Text: 'Text',
    TextInput: 'TextInput',
    TouchableHighlight: 'TouchableHighlight',
    TouchableOpacity: 'TouchableOpacity',
    TouchableWithoutFeedback: 'TouchableWithoutFeedback',
    View: 'View',

    // Native Modules
    NativeModules: {
      SettingsManager: {
        settings: {},
        getConstants: () => ({}),
      },
      DeviceInfo: {
        getConstants: () => ({}),
      },
    },
  };
});

// Mock Animated
jest.doMock('react-native/Libraries/Animated/NativeAnimatedHelper');

// Mock Expo modules
jest.doMock('expo-font', () => ({
  loadAsync: jest.fn(),
}));

jest.doMock('expo-splash-screen', () => ({
  preventAutoHideAsync: jest.fn(),
  hideAsync: jest.fn(),
}));

jest.doMock('expo-secure-store', () => ({
  setItemAsync: jest.fn(),
  getItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

jest.doMock('expo-status-bar', () => ({
  StatusBar: 'StatusBar',
  setStatusBarStyle: jest.fn(),
  setStatusBarBackgroundColor: jest.fn(),
  setStatusBarHidden: jest.fn(),
}));

// Mock React Navigation
jest.doMock('@react-navigation/native', () => ({
  NavigationContainer: ({ children }) => children,
  useNavigation: () => ({
    navigate: jest.fn(),
    replace: jest.fn(),
    goBack: jest.fn(),
  }),
  useFocusEffect: jest.fn(),
}));

jest.doMock('@react-navigation/stack', () => ({
  createStackNavigator: () => ({
    Navigator: ({ children }) => children,
    Screen: ({ children }) => children,
  }),
}));

// Silence console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
}; 