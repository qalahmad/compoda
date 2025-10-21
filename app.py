import streamlit as st
import datetime
from typing import Dict, Any

# Configure page
st.set_page_config(
    page_title="Compoda - Emotional Wellness Journey",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E7D32;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #388E3C;
        font-size: 1.8rem;
        margin: 1.5rem 0 1rem 0;
    }
    .door-button {
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .progress-bar {
        background-color: #E8F5E8;
        border-radius: 10px;
        padding: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'questionnaire_answers' not in st.session_state:
        st.session_state.questionnaire_answers = {}
    if 'entry_hall_answers' not in st.session_state:
        st.session_state.entry_hall_answers = {}
    if 'door_answers' not in st.session_state:
        st.session_state.door_answers = {}
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0

def welcome_page():
    """Welcome page with introduction to Compoda"""
    st.markdown('<h1 class="main-header">🌱 Welcome to Compoda</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Your Emotional Wellness Journey Begins Here
    
    Compoda is designed to help you explore your emotional landscape, connect with others who share similar experiences, 
    and discover personalized activities for your wellbeing.
    
    **Your Journey:**
    1. **Create Your Profile** - Tell us about yourself
    2. **Initial Questionnaire** - Help us understand your perspective
    3. **Entry Hall** - Set your baseline mood and energy
    4. **Choose Your Path** - Select from three unique experiences:
       - 🌳 **Emotional Room** - Explore your feelings in a responsive environment
       - ⭐ **Connect Hub** - Find others with similar emotional patterns
       - 🎯 **Guided Activity Spaces** - Discover personalized wellness activities
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Your Journey", type="primary", use_container_width=True):
            st.session_state.page = 'profile'
            st.rerun()

def profile_creation_page():
    """User profile creation page"""
    st.markdown('<h1 class="main-header">👤 Create Your Profile</h1>', unsafe_allow_html=True)
    
    st.markdown("Let's start by getting to know you better. This information helps us personalize your experience.")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", value=st.session_state.user_profile.get('first_name', ''))
            last_name = st.text_input("Last Name*", value=st.session_state.user_profile.get('last_name', ''))
            email = st.text_input("Email*", value=st.session_state.user_profile.get('email', ''))
            username = st.text_input("Username*", value=st.session_state.user_profile.get('username', ''))
            
        with col2:
            birthdate = st.date_input("Birth Date*", 
                                    value=st.session_state.user_profile.get('birthdate', datetime.date(1990, 1, 1)),
                                    min_value=datetime.date(1920, 1, 1),
                                    max_value=datetime.date.today())
            
            gender = st.selectbox("Gender*", 
                                ['Select...', 'Male', 'Female', 'Other'],
                                index=0 if not st.session_state.user_profile.get('gender') else 
                                ['Select...', 'Male', 'Female', 'Other'].index(st.session_state.user_profile.get('gender', 'Select...')))
            
            # Country dropdown list
            countries = ['Select...', 'United States', 'Canada', 'United Kingdom', 'Australia', 
                        'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Belgium',
                        'Switzerland', 'Austria', 'Sweden', 'Norway', 'Denmark', 'Finland',
                        'Ireland', 'New Zealand', 'Japan', 'South Korea', 'Singapore',
                        'India', 'China', 'Brazil', 'Mexico', 'Argentina', 'Other']
            
            country = st.selectbox("Country*", 
                                 countries,
                                 index=0 if not st.session_state.user_profile.get('country') else
                                 (countries.index(st.session_state.user_profile.get('country')) if st.session_state.user_profile.get('country') in countries else 0))
        
        submitted = st.form_submit_button("Continue to Questionnaire", type="primary", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not all([first_name, last_name, email, username, gender != 'Select...', country != 'Select...']):
                st.error("Please fill in all required fields marked with *")
            else:
                # Calculate age
                age = datetime.date.today().year - birthdate.year
                if datetime.date.today() < birthdate.replace(year=datetime.date.today().year):
                    age -= 1
                
                # Store profile data
                st.session_state.user_profile = {
                    'user_id': f"user_{username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'date_created': datetime.date.today().isoformat(),
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'username': username,
                    'birthdate': birthdate.isoformat(),
                    'age': age,
                    'gender': gender,
                    'country': country
                }
                
                st.success("Profile created successfully!")
                st.session_state.page = 'questionnaire'
                st.rerun()

def initial_questionnaire_page():
    """Initial questionnaire with 19 questions"""
    st.markdown('<h1 class="main-header">📋 Getting to Know You</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Let's get to know each other better. The following questions will help us understand your perspective 
    and connect you with others who share similar experiences. You can skip any question you're not 
    comfortable answering.
    """)
    
    # Progress bar
    total_questions = 19
    answered = len([k for k, v in st.session_state.questionnaire_answers.items() if v is not None])
    progress = answered / total_questions
    st.progress(progress, text=f"Progress: {answered}/{total_questions} questions answered")
    
    with st.form("questionnaire_form"):
        # Work and Academic Life
        st.markdown('<h3 class="section-header">📚 Work and Academic Life</h3>', unsafe_allow_html=True)
        
        q1 = st.selectbox("1. What's your educational background?", 
                         ['Select...', 'High School', 'Undergraduate degree', 'Postgraduate degree', 'Prefer not to say'])
        
        q2 = st.selectbox("2. What is/was your major?", 
                         ['Select...', 'Science', 'Arts', 'Medicine', 'Engineering', 'Business', 'Other', 'Prefer not to say'])
        
        q3 = st.selectbox("3. Are you currently a student?", 
                         ['Select...', 'Yes', 'No', 'Prefer not to say'])
        
        q4 = st.selectbox("4. How would you describe your academic experience?", 
                         ['Select...', "I've found academics challenging", "I've had an average academic experience", 
                          "I've generally done well academically", "I've excelled in my academic pursuits", 'Prefer not to say'])
        
        q5 = st.selectbox("5. How would you describe your current work situation?", 
                         ['Select...', "I'm a student", "I'm employed", "I'm self-employed", "I'm currently between jobs", 'Prefer not to say'])
        
        q6 = st.slider("6. How many hours do you typically work each week?", 0, 80, 
                      value=st.session_state.questionnaire_answers.get('q6', 40))
        
        # Health & Lifestyle
        st.markdown('<h3 class="section-header">🌿 Health & Lifestyle</h3>', unsafe_allow_html=True)
        
        q7 = st.selectbox("7. How do you like to fuel your body?", 
                         ['Select...', 'I follow a vegetarian diet', 'I follow a vegan lifestyle', 
                          'I enjoy a balanced, varied diet', 'I follow a keto/low-carb approach', 
                          'I tend to eat more convenience/fast foods', 'Prefer not to say'])
        
        q8 = st.slider("8. How many hours of sleep do you typically get each night?", 0, 12, 
                      value=st.session_state.questionnaire_answers.get('q8', 8))
        
        q9 = st.selectbox("9. How would you describe your sleep quality?", 
                         ['Select...', 'I often struggle with poor sleep', 'My sleep is okay, could be better', 
                          'I generally sleep quite well', 'Prefer not to say'])
        
        q10 = st.slider("10. How many hours do you typically spend being physically active each week?", 0, 20, 
                       value=st.session_state.questionnaire_answers.get('q10', 5))
        
        q11 = st.slider("11. About how much time do you spend looking at screens daily? (hours)", 0, 12, 
                       value=st.session_state.questionnaire_answers.get('q11', 6))
        
        # Mental Wellbeing
        st.markdown('<h3 class="section-header">🧠 Mental Wellbeing</h3>', unsafe_allow_html=True)
        
        q12 = st.selectbox("12. Have you been diagnosed with any mental health conditions?", 
                          ['Select...', 'Yes', 'No', 'Prefer not to say'])
        
        q13 = st.multiselect("13. If comfortable sharing, which condition(s) have you been diagnosed with?", 
                           ['None', 'Depression', 'Anxiety', 'PTSD', 'Bipolar disorder', 'ADHD', 'Other', 'Prefer not to say'])
        
        q14 = st.selectbox("14. How would you describe your overall stress level?", 
                          ['Select...', "I'm feeling relatively low stress", "I'm experiencing moderate stress", 
                           "I'm dealing with high stress levels", 'Prefer not to say'])
        
        # Your Social World
        st.markdown('<h3 class="section-header">👥 Your Social World</h3>', unsafe_allow_html=True)
        
        q15 = st.slider("15. How many close friends would you say you have?", 0, 10, 
                       value=st.session_state.questionnaire_answers.get('q15', 3))
        
        q16 = st.selectbox("16. What's your current relationship status?", 
                          ['Select...', 'Single', 'In a relationship', 'Married', 'Divorced', 'Prefer not to say'])
        
        q17 = st.slider("17. About how much time do you spend on social media daily? (hours)", 0, 20, 
                       value=st.session_state.questionnaire_answers.get('q17', 2))
        
        # Hobbies and Interests
        st.markdown('<h3 class="section-header">🎨 Hobbies and Interests</h3>', unsafe_allow_html=True)
        
        hobbies_options = ['hiking', 'music', 'art', 'cooking', 'reading', 'photography', 'journaling', 'working out', 
                          'gaming', 'travel', 'gardening', 'writing', 'meditation', 'yoga', 'dancing', 'volunteering', 
                          'crafting', 'board games', 'podcasting', 'movies', 'learning languages', 'coding', 
                          'woodworking', 'knitting', 'fishing', 'running', 'cycling', 'swimming', 'rock climbing', 'painting']
        
        q18 = st.multiselect("18. What activities make you feel most like yourself? (Select up to 5 that resonate with you)", 
                           hobbies_options, max_selections=5)
        
        q19 = st.slider("19. How much time do you typically spend on hobbies and leisure activities each day? (hours)", 0, 10, 
                       value=st.session_state.questionnaire_answers.get('q19', 2))
        
        submitted = st.form_submit_button("Continue to Entry Hall", type="primary", use_container_width=True)
        
        if submitted:
            # Store questionnaire answers
            st.session_state.questionnaire_answers = {
                'q1': q1 if q1 != 'Select...' else None,
                'q2': q2 if q2 != 'Select...' else None,
                'q3': q3 if q3 != 'Select...' else None,
                'q4': q4 if q4 != 'Select...' else None,
                'q5': q5 if q5 != 'Select...' else None,
                'q6': q6,
                'q7': q7 if q7 != 'Select...' else None,
                'q8': q8,
                'q9': q9 if q9 != 'Select...' else None,
                'q10': q10,
                'q11': q11,
                'q12': q12 if q12 != 'Select...' else None,
                'q13': q13 if q13 else None,
                'q14': q14 if q14 != 'Select...' else None,
                'q15': q15,
                'q16': q16 if q16 != 'Select...' else None,
                'q17': q17,
                'q18': q18 if q18 else None,
                'q19': q19
            }
            
            st.success("Questionnaire completed!")
            st.session_state.page = 'entry_hall'
            st.rerun()

def entry_hall_page():
    """Entry Hall with 15 baseline questions
    
    Note: All questions use consistent polarity (1=most negative, 5=most positive)
    for this prototype. In the full implementation, reverse-coded items will be adjusted.
    """
    st.markdown('<h1 class="main-header">🏛️ Entry Hall</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the Entry Hall! These questions help us understand your current emotional baseline - 
    your mood, energy, and overall state right now. This creates your **Pulse Score** that guides 
    your journey through Compoda.
    """)
    
    # Progress indicator
    current_q = st.session_state.current_question
    total_q = 15
    progress = (current_q + 1) / total_q
    st.progress(progress, text=f"Question {current_q + 1} of {total_q}")
    
    # Entry Hall questions (placeholder structure)
    entry_questions = [
        {"text": "How would you describe your current mood?", "options": ["Very low", "Low", "Neutral", "Good", "Very good"]},
        {"text": "What's your energy level right now?", "options": ["Exhausted", "Low energy", "Moderate", "High energy", "Very energetic"]},
        {"text": "How well did you sleep last night?", "options": ["Very poorly", "Poorly", "Okay", "Well", "Very well"]},
        {"text": "How motivated do you feel today?", "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"]},
        {"text": "How stressed are you feeling?", "options": ["Extremely stressed", "Very stressed", "Moderately stressed", "Slightly stressed", "Not stressed"]},
        {"text": "How lonely do you feel right now?", "options": ["Very lonely", "Somewhat lonely", "Neutral", "Connected", "Very connected"]},
        {"text": "How hopeful are you feeling about the future?", "options": ["Not hopeful", "Slightly hopeful", "Moderately hopeful", "Very hopeful", "Extremely hopeful"]},
        {"text": "How satisfied are you with your life currently?", "options": ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]},
        {"text": "How would you rate your overall health today?", "options": ["Very poor", "Poor", "Fair", "Good", "Excellent"]},
        {"text": "How balanced do you feel in your daily life?", "options": ["Very unbalanced", "Unbalanced", "Somewhat balanced", "Balanced", "Very balanced"]},
        {"text": "How secure do you feel in your current situation?", "options": ["Very insecure", "Insecure", "Neutral", "Secure", "Very secure"]},
        {"text": "How present and mindful do you feel right now?", "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"]},
        {"text": "Are you more introverted or extroverted today?", "options": ["Very introverted", "Introverted", "Balanced", "Extroverted", "Very extroverted"]},
        {"text": "How bored are you feeling?", "options": ["Extremely bored", "Very bored", "Somewhat bored", "Not very bored", "Not bored at all"]},
        {"text": "How much are you looking forward to the rest of your day?", "options": ["Not at all", "A little", "Moderately", "Quite a bit", "Very much"]}
    ]
    
    if current_q < len(entry_questions):
        question = entry_questions[current_q]
        
        st.markdown(f"### {question['text']}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            answer = st.radio("", question['options'], key=f"entry_q_{current_q}")
            
            col_prev, col_next = st.columns(2)
            
            with col_prev:
                if current_q > 0:
                    if st.button("← Previous", use_container_width=True):
                        st.session_state.current_question -= 1
                        st.rerun()
            
            with col_next:
                if st.button("Next →" if current_q < len(entry_questions) - 1 else "Complete Entry Hall", 
                           type="primary", use_container_width=True):
                    # Store answer
                    st.session_state.entry_hall_answers[f"q_{current_q}"] = answer
                    
                    if current_q < len(entry_questions) - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        # Calculate Pulse Score and Subscores (simplified)
                        # Note: Uses consistent polarity (1-5) for all questions in this prototype
                        # In production, reverse-coded items (stress, loneliness, boredom) should be reversed
                        
                        # Get all answer scores
                        scores = [list(entry_questions[i]['options']).index(st.session_state.entry_hall_answers[f"q_{i}"]) + 1 
                                 for i in range(len(entry_questions))]
                        
                        # Calculate overall Pulse Score
                        total_score = sum(scores)
                        pulse_score = total_score / (len(entry_questions) * 5) * 5  # Scale to 5
                        st.session_state.pulse_score = round(pulse_score, 1)
                        
                        # Calculate Subscores based on question groupings
                        # Mood Index: Q1 (Mood), Q7 (Hope), Q8 (Satisfaction)
                        mood_scores = [scores[0], scores[6], scores[7]]
                        st.session_state.mood_index = round(sum(mood_scores) / len(mood_scores), 2)
                        
                        # Energy Index: Q2 (Energy), Q3 (Sleep), Q4 (Motivation)
                        energy_scores = [scores[1], scores[2], scores[3]]
                        st.session_state.energy_index = round(sum(energy_scores) / len(energy_scores), 2)
                        
                        # Social Index: Q6 (Loneliness), Q13 (Intro/Extro), Q14 (Boredom), Q15 (Anticipation)
                        social_scores = [scores[5], scores[12], scores[13], scores[14]]
                        st.session_state.social_index = round(sum(social_scores) / len(social_scores), 2)
                        
                        # Security Index: Q5 (Stress), Q9 (Health), Q10 (Balance), Q11 (Security), Q12 (Presence)
                        security_scores = [scores[4], scores[8], scores[9], scores[10], scores[11]]
                        st.session_state.security_index = round(sum(security_scores) / len(security_scores), 2)
                        
                        st.success(f"Entry Hall completed! Your Pulse Score: {st.session_state.pulse_score}/5.0")
                        st.session_state.page = 'door_selection'
                        st.session_state.current_question = 0  # Reset for next section
                        st.rerun()

def door_selection_page():
    """Door selection page with three options"""
    st.markdown('<h1 class="main-header">🚪 Choose Your Path</h1>', unsafe_allow_html=True)
    
    pulse_score = st.session_state.get('pulse_score', 0)
    st.markdown(f"**Your Current Pulse Score: {pulse_score}/5.0**")
    
    st.markdown("""
    Based on your Entry Hall responses, choose one of three paths for your Compoda journey. 
    Each door offers a unique experience tailored to different aspects of emotional wellness.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="door-button">
        <h3>🌳 Door 1: Emotional Room</h3>
        <p>Explore your feelings in a responsive forest environment. 
        40 questions about emotion, intensity, context, and recency.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enter Emotional Room", key="door1", use_container_width=True, type="primary"):
            st.session_state.page = 'door1'
            st.session_state.current_door = 1
            st.session_state.current_question = 0
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="door-button">
        <h3>⭐ Door 2: Connect Hub</h3>
        <p>Find others with similar emotional patterns in our star map. 
        25 questions about social resonance and matching preferences.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enter Connect Hub", key="door2", use_container_width=True, type="primary"):
            st.session_state.page = 'door2'
            st.session_state.current_door = 2
            st.session_state.current_question = 0
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="door-button">
        <h3>🎯 Door 3: Guided Activity Spaces</h3>
        <p>Discover personalized wellness activities and micro-interventions. 
        20 questions about activity preferences and adherence.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enter Activity Spaces", key="door3", use_container_width=True, type="primary"):
            st.session_state.page = 'door3'
            st.session_state.current_door = 3
            st.session_state.current_question = 0
            st.rerun()

def door1_page():
    """Door 1: Emotional Room (40 questions)"""
    st.markdown('<h1 class="main-header">🌳 Emotional Room</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the Emotional Room! Here, you'll explore your current emotional landscape. 
    Imagine walking through a responsive forest where the environment adapts to your feelings.
    """)
    
    # Sample questions for Door 1 (placeholder)
    emotional_questions = [
        {"text": "What emotion are you feeling most strongly right now?", 
         "options": ["Joy", "Anger", "Fear", "Sadness", "Surprise", "Disgust", "Contempt"]},
        {"text": "How intense is this emotion?", 
         "options": ["Very mild", "Mild", "Moderate", "Strong", "Very strong"]},
        {"text": "What triggered this emotion?", 
         "options": ["Work/Study", "Relationships", "Health", "Future concerns", "Past memories"]},
        {"text": "How recent is this feeling?", 
         "options": ["Right now", "Past hour", "Today", "This week", "Longer ago"]},
        {"text": "How comfortable are you with this emotion?", 
         "options": ["Very uncomfortable", "Uncomfortable", "Neutral", "Comfortable", "Very comfortable"]},
        # Add more questions as needed (up to 40)
    ]
    
    # Extend to 40 questions with variations
    while len(emotional_questions) < 40:
        emotional_questions.extend([
            {"text": f"How often do you experience emotional question {len(emotional_questions)+1}?", 
             "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]},
        ])
        if len(emotional_questions) >= 40:
            break
    
    current_q = st.session_state.current_question
    total_q = min(len(emotional_questions), 40)
    
    if current_q < total_q:
        progress = (current_q + 1) / total_q
        st.progress(progress, text=f"Question {current_q + 1} of {total_q}")
        
        question = emotional_questions[current_q]
        st.markdown(f"### {question['text']}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            answer = st.radio("", question['options'], key=f"door1_q_{current_q}")
            
            col_prev, col_next = st.columns(2)
            
            with col_prev:
                if current_q > 0:
                    if st.button("← Previous", use_container_width=True):
                        st.session_state.current_question -= 1
                        st.rerun()
                else:
                    if st.button("← Back to Doors", use_container_width=True):
                        st.session_state.page = 'door_selection'
                        st.rerun()
            
            with col_next:
                if st.button("Next →" if current_q < total_q - 1 else "Complete Journey", 
                           type="primary", use_container_width=True):
                    # Store answer
                    if 'door1_answers' not in st.session_state:
                        st.session_state.door1_answers = {}
                    st.session_state.door1_answers[f"q_{current_q}"] = answer
                    
                    if current_q < total_q - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.page = 'completion'
                        st.rerun()
    
    # Show forest visualization placeholder
    st.markdown("---")
    st.markdown("### 🌲 Your Emotional Forest")
    st.info("Imagine: The forest around you shifts with your emotions - warmer colors for joy, cooler tones for calm, dynamic movements for excitement...")

def door2_page():
    """Door 2: Connect Hub (25 questions)"""
    st.markdown('<h1 class="main-header">⭐ Connect Hub</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the Connect Hub! Here, you'll help us understand how you connect with others. 
    Imagine a star map where each star represents someone with similar emotional patterns.
    """)
    
    # Sample questions for Door 2 (placeholder)
    connect_questions = [
        {"text": "How do you prefer to communicate with others?", 
         "options": ["Face-to-face", "Video calls", "Voice calls", "Text/messaging", "Mixed approaches"]},
        {"text": "What draws you to connect with someone?", 
         "options": ["Similar interests", "Shared experiences", "Complementary differences", "Emotional resonance", "Intellectual connection"]},
        {"text": "How important is emotional support in your relationships?", 
         "options": ["Not important", "Slightly important", "Moderately important", "Very important", "Extremely important"]},
        {"text": "How do you usually respond when someone shares their feelings?", 
         "options": ["Listen actively", "Offer advice", "Share similar experiences", "Ask questions", "Provide comfort"]},
        {"text": "What makes you feel most understood by others?", 
         "options": ["When they listen", "When they relate", "When they validate", "When they help", "When they accept"]}
        # Add more questions as needed (up to 25)
    ]
    
    # Extend to 25 questions
    while len(connect_questions) < 25:
        connect_questions.extend([
            {"text": f"Connection preference question {len(connect_questions)+1}?", 
             "options": ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]},
        ])
        if len(connect_questions) >= 25:
            break
    
    current_q = st.session_state.current_question
    total_q = min(len(connect_questions), 25)
    
    if current_q < total_q:
        progress = (current_q + 1) / total_q
        st.progress(progress, text=f"Question {current_q + 1} of {total_q}")
        
        question = connect_questions[current_q]
        st.markdown(f"### {question['text']}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            answer = st.radio("", question['options'], key=f"door2_q_{current_q}")
            
            col_prev, col_next = st.columns(2)
            
            with col_prev:
                if current_q > 0:
                    if st.button("← Previous", use_container_width=True):
                        st.session_state.current_question -= 1
                        st.rerun()
                else:
                    if st.button("← Back to Doors", use_container_width=True):
                        st.session_state.page = 'door_selection'
                        st.rerun()
            
            with col_next:
                if st.button("Next →" if current_q < total_q - 1 else "Complete Journey", 
                           type="primary", use_container_width=True):
                    # Store answer
                    if 'door2_answers' not in st.session_state:
                        st.session_state.door2_answers = {}
                    st.session_state.door2_answers[f"q_{current_q}"] = answer
                    
                    if current_q < total_q - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.page = 'completion'
                        st.rerun()
    
    # Show star map visualization placeholder
    st.markdown("---")
    st.markdown("### ✨ Your Connection Star Map")
    st.info("Imagine: Each star represents a person with similar emotional patterns. Brighter stars indicate stronger resonance...")

def door3_page():
    """Door 3: Guided Activity Spaces (20 questions)"""
    st.markdown('<h1 class="main-header">🎯 Guided Activity Spaces</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the Guided Activity Spaces! Here, we'll learn about your activity preferences 
    to suggest personalized micro-interventions for your wellness journey.
    """)
    
    # Sample questions for Door 3 (placeholder)
    activity_questions = [
        {"text": "What type of activities help you feel better when you're stressed?", 
         "options": ["Physical exercise", "Creative activities", "Social activities", "Quiet reflection", "Learning something new"]},
        {"text": "How much time can you typically dedicate to wellness activities?", 
         "options": ["5-10 minutes", "10-20 minutes", "20-30 minutes", "30-60 minutes", "More than 1 hour"]},
        {"text": "What environment makes you feel most calm?", 
         "options": ["Nature/outdoors", "Quiet indoor space", "Busy social setting", "Familiar home space", "New/changing environments"]},
        {"text": "How do you prefer to receive activity suggestions?", 
         "options": ["Daily reminders", "Weekly plans", "In-the-moment suggestions", "Self-directed exploration", "Guided programs"]},
        {"text": "What motivates you most to complete wellness activities?", 
         "options": ["Personal goals", "Social accountability", "Visible progress", "Immediate benefits", "Long-term health"]}
        # Add more questions as needed (up to 20)
    ]
    
    # Extend to 20 questions
    while len(activity_questions) < 20:
        activity_questions.extend([
            {"text": f"Activity preference question {len(activity_questions)+1}?", 
             "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]},
        ])
        if len(activity_questions) >= 20:
            break
    
    current_q = st.session_state.current_question
    total_q = min(len(activity_questions), 20)
    
    if current_q < total_q:
        progress = (current_q + 1) / total_q
        st.progress(progress, text=f"Question {current_q + 1} of {total_q}")
        
        question = activity_questions[current_q]
        st.markdown(f"### {question['text']}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            answer = st.radio("", question['options'], key=f"door3_q_{current_q}")
            
            col_prev, col_next = st.columns(2)
            
            with col_prev:
                if current_q > 0:
                    if st.button("← Previous", use_container_width=True):
                        st.session_state.current_question -= 1
                        st.rerun()
                else:
                    if st.button("← Back to Doors", use_container_width=True):
                        st.session_state.page = 'door_selection'
                        st.rerun()
            
            with col_next:
                if st.button("Next →" if current_q < total_q - 1 else "Complete Journey", 
                           type="primary", use_container_width=True):
                    # Store answer
                    if 'door3_answers' not in st.session_state:
                        st.session_state.door3_answers = {}
                    st.session_state.door3_answers[f"q_{current_q}"] = answer
                    
                    if current_q < total_q - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.page = 'completion'
                        st.rerun()
    
    # Show activity space visualization placeholder
    st.markdown("---")
    st.markdown("### 🏛️ Your Activity Spaces")
    st.info("Imagine: Different rooms for journaling, meditation, social connection - each adapting to your current state...")

def completion_page():
    """Journey completion page"""
    st.markdown('<h1 class="main-header">🎉 Journey Complete!</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Congratulations! You've completed your Compoda journey. Here's a summary of your experience:
    """)
    
    # Display summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Your Profile")
        if st.session_state.user_profile:
            st.write(f"**Name:** {st.session_state.user_profile.get('first_name', '')} {st.session_state.user_profile.get('last_name', '')}")
            st.write(f"**Username:** {st.session_state.user_profile.get('username', '')}")
            st.write(f"**Age:** {st.session_state.user_profile.get('age', '')}")
    
    with col2:
        st.markdown("### 📊 Your Scores")
        pulse_score = st.session_state.get('pulse_score', 0)
        st.write(f"**Pulse Score:** {pulse_score}/5.0")
        
        # Display subscores
        st.write("")  # Add spacing
        st.write("**Subscores:**")
        
        # Get subscores from session state
        mood_index = st.session_state.get('mood_index', 0)
        energy_index = st.session_state.get('energy_index', 0)
        social_index = st.session_state.get('social_index', 0)
        security_index = st.session_state.get('security_index', 0)
        
        # Display each subscore
        st.write(f"• Mood Index: {mood_index}/5.0")
        st.write(f"• Energy Index: {energy_index}/5.0")
        st.write(f"• Social Index: {social_index}/5.0")
        st.write(f"• Security Index: {security_index}/5.0")
        
        st.write("")  # Add spacing
        door = st.session_state.get('current_door', 'None')
        door_names = {1: "Emotional Room", 2: "Connect Hub", 3: "Guided Activity Spaces"}
        st.write(f"**Chosen Path:** {door_names.get(door, 'None')}")
    
    st.markdown("---")
    
    # User Matching Recommendations Section
    st.markdown("### 🔗 User Matching Recommendations")
    
    # Calculate matching recommendations based on subscores
    pulse_score = st.session_state.get('pulse_score', 0)
    mood_index = st.session_state.get('mood_index', 0)
    energy_index = st.session_state.get('energy_index', 0)
    social_index = st.session_state.get('social_index', 0)
    security_index = st.session_state.get('security_index', 0)
    
    st.info("""
    **In a full implementation, you would be matched with users based on:**
    - Similar emotional patterns and Pulse Score ranges
    - Complementary subscore profiles for mutual support
    - Shared interests and hobbies from your profile
    - Temporal patterns (morning/evening activity preferences)
    """)
    
    # Display potential match profiles (simulated)
    st.markdown("#### Potential Matches:")
    
    match_col1, match_col2 = st.columns(2)
    
    with match_col1:
        st.markdown("""
        **User Match 1: Similar Emotional State**
        - Pulse Score: Similar range to yours
        - High resonance in Mood and Social indices
        - Looking for: Emotional support and connection
        - Common interests: Based on your hobbies
        """)
    
    with match_col2:
        st.markdown("""
        **User Match 2: Complementary Support**
        - Pulse Score: Slightly higher energy levels
        - Can provide: Motivation and activity ideas
        - Seeking: Meaningful conversations
        - Shared path: Also exploring the Connect Hub
        """)
    
    st.markdown("")
    st.markdown("**Why these matches?**")
    st.write(f"• Your Pulse Score ({pulse_score}) suggests you would benefit from connections with users in similar emotional states")
    st.write(f"• Your Social Index ({social_index}) indicates your preferred level of social engagement")
    st.write(f"• Your Energy Index ({energy_index}) helps match activity compatibility")
    st.write(f"• Your chosen path (Door {st.session_state.get('current_door', 1)}) connects you with like-minded users")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Start Over", use_container_width=True):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 'welcome'
            st.rerun()
    
    with col2:
        if st.button("🚪 Try Another Door", use_container_width=True):
            st.session_state.page = 'door_selection'
            st.session_state.current_question = 0
            st.rerun()
    
    with col3:
        if st.button("📋 View Responses", use_container_width=True):
            st.session_state.show_responses = True
            st.rerun()
    
    # Show responses if requested
    if st.session_state.get('show_responses', False):
        st.markdown("---")
        st.markdown("### 📝 Your Responses")
        
        with st.expander("Entry Hall Responses"):
            st.json(st.session_state.entry_hall_answers)
        
        with st.expander("Initial Questionnaire"):
            st.json(st.session_state.questionnaire_answers)
        
        door_key = f"door{st.session_state.get('current_door', 1)}_answers"
        if door_key in st.session_state:
            with st.expander(f"Door {st.session_state.get('current_door', 1)} Responses"):
                st.json(st.session_state[door_key])

# Main app logic
def main():
    init_session_state()
    
    # Navigation
    page = st.session_state.page
    
    if page == 'welcome':
        welcome_page()
    elif page == 'profile':
        profile_creation_page()
    elif page == 'questionnaire':
        initial_questionnaire_page()
    elif page == 'entry_hall':
        entry_hall_page()
    elif page == 'door_selection':
        door_selection_page()
    elif page == 'door1':
        door1_page()
    elif page == 'door2':
        door2_page()
    elif page == 'door3':
        door3_page()
    elif page == 'completion':
        completion_page()

if __name__ == "__main__":
    main()
