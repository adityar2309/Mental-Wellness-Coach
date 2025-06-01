import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';
import MoodCheckInScreen from '../../../src/screens/mood/MoodCheckInScreen';
import { MoodApi } from '../../../src/services/ApiClient';

// Mock dependencies
jest.mock('../../../src/services/ApiClient');
jest.mock('@react-navigation/stack');

// Mock Alert
jest.spyOn(Alert, 'alert').mockImplementation(() => {});

// Mock navigation
const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  replace: jest.fn(),
};

describe('MoodCheckInScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('UI Rendering', () => {
    it('renders all required elements', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Check header elements
      expect(screen.getByText('How are you feeling today?')).toBeTruthy();
      expect(screen.getByText('Select your current mood')).toBeTruthy();

      // Check mood options
      expect(screen.getByText('😰')).toBeTruthy();
      expect(screen.getByText('Very Bad')).toBeTruthy();
      expect(screen.getByText('😞')).toBeTruthy();
      expect(screen.getByText('Bad')).toBeTruthy();
      expect(screen.getByText('😐')).toBeTruthy();
      expect(screen.getByText('Okay')).toBeTruthy();
      expect(screen.getByText('🙂')).toBeTruthy();
      expect(screen.getByText('Good')).toBeTruthy();
      expect(screen.getByText('😊')).toBeTruthy();
      expect(screen.getByText('Great')).toBeTruthy();

      // Check submit button
      expect(screen.getByText('Save Mood')).toBeTruthy();
    });

    it('renders submit button as disabled initially', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      const submitButton = screen.getByText('Save Mood').parent;
      expect(submitButton?.props.accessibilityState?.disabled).toBe(true);
    });

    it('renders mood cards with correct styling', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      const moodCards = screen.getAllByText(/Very Bad|Bad|Okay|Good|Great/);
      expect(moodCards).toHaveLength(5);

      // Check that mood cards are touchable
      moodCards.forEach(card => {
        expect(card.parent?.props.accessible).toBe(true);
      });
    });
  });

  describe('Mood Selection', () => {
    it('allows selecting a mood option', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      const goodMoodCard = screen.getByText('Good').parent;
      fireEvent.press(goodMoodCard!);

      // The button should become enabled after selection
      waitFor(() => {
        const submitButton = screen.getByText('Save Mood').parent;
        expect(submitButton?.props.accessibilityState?.disabled).toBe(false);
      });
    });

    it('allows changing mood selection', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select first mood
      const badMoodCard = screen.getByText('Bad').parent;
      fireEvent.press(badMoodCard!);

      // Select different mood
      const greatMoodCard = screen.getByText('Great').parent;
      fireEvent.press(greatMoodCard!);

      // Button should still be enabled
      waitFor(() => {
        const submitButton = screen.getByText('Save Mood').parent;
        expect(submitButton?.props.accessibilityState?.disabled).toBe(false);
      });
    });

    it('provides visual feedback for selected mood', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      const okayMoodCard = screen.getByText('Okay').parent;
      fireEvent.press(okayMoodCard!);

      // Check that selected style is applied
      waitFor(() => {
        expect(okayMoodCard?.props.style).toEqual(
          expect.arrayContaining([
            expect.objectContaining({
              borderColor: '#6366f1',
              backgroundColor: '#f0f9ff',
            })
          ])
        );
      });
    });
  });

  describe('Form Submission', () => {
    it('shows validation alert when no mood is selected', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      expect(Alert.alert).toHaveBeenCalledWith(
        'Please select your mood',
        'Choose how you\'re feeling today.'
      );
    });

    it('submits mood data when mood is selected', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockResolvedValue({ success: true });

      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const goodMoodCard = screen.getByText('Good').parent;
      fireEvent.press(goodMoodCard!);

      // Submit form
      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(MoodApi.quickCheckIn).toHaveBeenCalledWith(4); // Good = value 4
      });
    });

    it('shows loading state during submission', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const greatMoodCard = screen.getByText('Great').parent;
      fireEvent.press(greatMoodCard!);

      // Submit form
      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      // Check loading state
      await waitFor(() => {
        expect(screen.getByText('Saving...')).toBeTruthy();
      });
    });

    it('navigates to Home on successful submission', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockResolvedValue({ success: true });

      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const okayMoodCard = screen.getByText('Okay').parent;
      fireEvent.press(okayMoodCard!);

      // Submit form
      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(mockNavigation.navigate).toHaveBeenCalledWith('Home');
      });
    });

    it('does not navigate when submission fails', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockRejectedValue(new Error('API Error'));

      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const badMoodCard = screen.getByText('Bad').parent;
      fireEvent.press(badMoodCard!);

      // Submit form
      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(mockNavigation.navigate).not.toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    it('shows error alert on submission failure', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const veryBadMoodCard = screen.getByText('Very Bad').parent;
      fireEvent.press(veryBadMoodCard!);

      // Submit form
      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Error',
          'Failed to save your mood. Please try again.'
        );
      });
    });

    it('resets loading state after error', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockRejectedValue(new Error('API Error'));

      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const goodMoodCard = screen.getByText('Good').parent;
      fireEvent.press(goodMoodCard!);

      // Submit form
      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      // Wait for error and check that loading is reset
      await waitFor(() => {
        expect(screen.getByText('Save Mood')).toBeTruthy();
        expect(screen.queryByText('Saving...')).toBeNull();
      });
    });
  });

  describe('Accessibility', () => {
    it('disables submit button during loading', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const okayMoodCard = screen.getByText('Okay').parent;
      fireEvent.press(okayMoodCard!);

      // Submit form
      const submitButton = screen.getByText('Save Mood');
      fireEvent.press(submitButton);

      await waitFor(() => {
        const loadingButton = screen.getByText('Saving...').parent;
        expect(loadingButton?.props.accessibilityState?.disabled).toBe(true);
      });
    });

    it('provides proper accessibility labels for mood options', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Check that mood cards are accessible
      const moodCards = [
        screen.getByText('Very Bad').parent,
        screen.getByText('Bad').parent,
        screen.getByText('Okay').parent,
        screen.getByText('Good').parent,
        screen.getByText('Great').parent,
      ];

      moodCards.forEach(card => {
        expect(card?.props.accessible).toBe(true);
      });
    });
  });

  describe('User Experience', () => {
    it('maintains selected mood after screen interactions', () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Select a mood
      const greatMoodCard = screen.getByText('Great').parent;
      fireEvent.press(greatMoodCard!);

      // Interact with another element (should not clear selection)
      const title = screen.getByText('How are you feeling today?');
      fireEvent.press(title);

      // Check that selection is maintained
      waitFor(() => {
        expect(greatMoodCard?.props.style).toEqual(
          expect.arrayContaining([
            expect.objectContaining({
              borderColor: '#6366f1',
            })
          ])
        );
      });
    });

    it('shows appropriate button text states', async () => {
      render(<MoodCheckInScreen navigation={mockNavigation as any} />);

      // Initial state
      expect(screen.getByText('Save Mood')).toBeTruthy();

      // Select mood to enable button
      const goodMoodCard = screen.getByText('Good').parent;
      fireEvent.press(goodMoodCard!);

      // Should still show "Save Mood"
      expect(screen.getByText('Save Mood')).toBeTruthy();
    });
  });

  describe('Mood Values', () => {
    it('submits correct mood values for each option', async () => {
      (MoodApi.quickCheckIn as jest.Mock).mockResolvedValue({ success: true });

      const moodTests = [
        { label: 'Very Bad', expectedValue: 1 },
        { label: 'Bad', expectedValue: 2 },
        { label: 'Okay', expectedValue: 3 },
        { label: 'Good', expectedValue: 4 },
        { label: 'Great', expectedValue: 5 },
      ];

      for (const { label, expectedValue } of moodTests) {
        render(<MoodCheckInScreen navigation={mockNavigation as any} />);

        const moodCard = screen.getByText(label).parent;
        fireEvent.press(moodCard!);

        const submitButton = screen.getByText('Save Mood');
        fireEvent.press(submitButton);

        await waitFor(() => {
          expect(MoodApi.quickCheckIn).toHaveBeenCalledWith(expectedValue);
        });

        // Clear mocks for next iteration
        jest.clearAllMocks();
      }
    });
  });
}); 