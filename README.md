# Compoda - Emotional Wellness Journey

A Streamlit-based skeleton UI for the Compoda emotional wellness application. This is a prototype that demonstrates the user flow and interface design for the three-door emotional wellness platform.

## Features

- **User Profile Creation**: Complete registration with personal information
- **Initial Questionnaire**: 19 questions covering work, health, mental wellbeing, social life, and hobbies
- **Entry Hall**: 15 baseline questions to determine your Pulse Score
- **Three Door Experience**:
  - 🌳 **Door 1: Emotional Room** - 40 questions about emotional exploration
  - ⭐ **Door 2: Connect Hub** - 25 questions about social connection preferences
  - 🎯 **Door 3: Guided Activity Spaces** - 20 questions about wellness activities

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

## User Flow

1. **Welcome Page** - Introduction to Compoda
2. **Profile Creation** - User registration form
3. **Initial Questionnaire** - 19 questions about background and preferences
4. **Entry Hall** - 15 questions to establish emotional baseline (Pulse Score)
5. **Door Selection** - Choose one of three paths
6. **Door Experience** - Complete questionnaire for chosen path
7. **Completion** - Summary and next steps

## Project Structure

```
compoda/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── instructions.txt   # Project requirements and specifications
```

## Notes

- This is a UI skeleton/prototype - no backend logic is implemented
- Questions are placeholders to demonstrate the flow
- Scoring calculations are simplified for demonstration
- Visual elements (forest, star map, activity rooms) are described but not implemented

## Technology Used

- **Streamlit**: Web app framework for Python
- **Python**: Backend logic and data handling

## Next Steps for Full Implementation

- Connect to database for user data storage
- Implement actual scoring algorithms
- Add visual/audio gamification elements
- Create matching algorithms for user connections
- Develop recommendation engine for activities
- Add user authentication and data persistence
