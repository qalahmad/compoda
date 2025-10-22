import streamlit as st
import datetime
from typing import Dict, Any
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# Matching Engine Functions (from User Matching Engine.ipynb)
# ============================================================================

# Global variables for loaded models and data
loaded_model = None
encoders = None
df_clusters = None
df_user_profiles = None
df_matrix = None

def load_matching_data():
    """Load all required data for matching engine"""
    global loaded_model, encoders, df_clusters, df_user_profiles, df_matrix
    
    try:
        # Load classifier model
        with open('new_user_classifier.pkl', 'rb') as file:
            loaded_model = pickle.load(file)
        
        # Load label encoders
        with open('label_encoders.pkl', 'rb') as file:
            encoders = pickle.load(file)
        
        # Load cluster data
        df_clusters = pd.read_csv("user_clusters_6_clusters.csv")
        
        # Load user profiles
        df_user_profiles = pd.read_csv("user_profiles.csv")
        
        # Preprocess all users
        df_matrix = pre_processing(df_clusters.copy())
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load matching data: {e}")
        return False

def pre_processing(user_temp):
    """Preprocess user data - encode categorical features (from notebook)"""
    cluster_df = user_temp.copy()
    
    for col in ['gender','education_level','occupation_status','diet_type','stress_level', 'mental_health_condition','relationship_status',
                'age_groups','work_hours_groups', 'sleep_hours_groups','physical_activity_groups','screen_time_groups','friends_groups']:
        
        if col in cluster_df.columns:
            mapping_dict = encoders[col]
            original_value = cluster_df[col].values[0] if cluster_df.shape[0] == 1 else None
            cluster_df[col] = cluster_df[col].map(mapping_dict)
            
            # Check for NaN after mapping
            if cluster_df[col].isna().any():
                print(f"[WARNING] NaN found in {col} after mapping (original value: {original_value})")
                print(f"[WARNING] Available mappings for {col}: {list(mapping_dict.keys())}")
                # Fill NaN with a default value (0)
                cluster_df[col] = cluster_df[col].fillna(0)
    
    if cluster_df.shape[0] == 1:
        cluster_df.drop(['user_id', 'Class Name'], axis=1, inplace=True, errors='ignore')
    else:
        cluster_df.set_index('user_id', inplace=True)
    
    return cluster_df

def recommendations_based_on_user_profile(user_target, df_target, k_nearest_neighbors):
    """Find similar users using cosine similarity (from notebook)"""
    similarity_scores = cosine_similarity(df_target, user_target)
    
    similarity_df = pd.DataFrame(similarity_scores, index=df_target.index, columns=['matching_score'])
    
    similarity_df.sort_values(by=["matching_score"], ascending=False, inplace=True)
    
    top_users = similarity_df.iloc[0:k_nearest_neighbors]
    
    return top_users

def build_new_user_row(user_profile, entry_hall_answers, door2_answers):
    """Build a new user row matching the exact structure of user_clusters_6_clusters.csv"""
    
    # Start with a row from the CSV to get the exact structure
    template_row = df_clusters.iloc[0:1].copy()
    
    # Update with new user data
    template_row['user_id'] = 9999
    
    # Categorical features
    template_row['gender'] = user_profile.get('gender', 'Other')
    template_row['education_level'] = user_profile.get('education_level', 'Undergraduate')
    template_row['occupation_status'] = user_profile.get('occupation_status', 'Employed')
    template_row['diet_type'] = user_profile.get('diet_type', 'Balanced')
    template_row['stress_level'] = user_profile.get('stress_level', 'Medium')
    template_row['has_mental_health_condition'] = user_profile.get('has_mental_health_condition', 0)
    template_row['mental_health_condition'] = user_profile.get('mental_health_condition', 'Not Applicable')
    template_row['relationship_status'] = user_profile.get('relationship_status', 'Single')
    
    # Door 2 answers (answer_code_56 to answer_code_80)
    for i in range(25):
        answer_key = f'q_{i}'
        if answer_key in door2_answers:
            template_row[f'answer_code_{56 + i}'] = int(door2_answers[answer_key])
        else:
            template_row[f'answer_code_{56 + i}'] = 3
    
    # Matching score
    door2_codes = [template_row[f'answer_code_{56 + i}'].values[0] for i in range(25)]
    template_row['matching_score'] = round(sum(door2_codes) / len(door2_codes), 2)
    
    # Entry Hall answers (entry_hall_answer_code_1 to entry_hall_answer_code_15)
    for i in range(15):
        answer_key = f'q_{i}'
        if answer_key in entry_hall_answers:
            template_row[f'entry_hall_answer_code_{i + 1}'] = int(entry_hall_answers[answer_key])
        else:
            template_row[f'entry_hall_answer_code_{i + 1}'] = 3
    
    # Entry Hall subscores
    template_row['entry_hall_pulse_score'] = user_profile.get('pulse_score', 3.0)
    template_row['entry_hall_mood_index'] = user_profile.get('mood_index', 3.0)
    template_row['entry_hall_energy_index'] = user_profile.get('energy_index', 3.0)
    template_row['entry_hall_social_index'] = user_profile.get('social_index', 3.0)
    template_row['entry_hall_security_index'] = user_profile.get('security_index', 3.0)
    
    # Group features
    template_row['age_groups'] = user_profile.get('age_groups', '25-34')  # regular hyphen
    template_row['work_hours_groups'] = user_profile.get('work_hours_groups', '31–40 hrs')
    template_row['sleep_hours_groups'] = user_profile.get('sleep_hours_groups', '6–8 hrs')
    template_row['physical_activity_groups'] = user_profile.get('physical_activity_groups', 'Moderate (4–5)')
    template_row['screen_time_groups'] = user_profile.get('screen_time_groups', '4–6 hrs')
    template_row['friends_groups'] = user_profile.get('friends_groups', '3–4')
    
    # Class Name will be predicted
    template_row['Class Name'] = -1
    
    return template_row

def get_user_matches(user_profile, entry_hall_answers, door2_answers, top_n=5):
    """Main function to get user matches (simplified from notebook)"""
    try:
        print("\n=== Starting User Matching ===")
        
        # Build new user row
        new_user_row = build_new_user_row(user_profile, entry_hall_answers, door2_answers)
        print(f"Built new user row with shape: {new_user_row.shape}")
        
        # Debug: Check for NaN in original row
        nan_cols = new_user_row.columns[new_user_row.isna().any()].tolist()
        if nan_cols:
            print(f"[WARNING] NaN found in columns before preprocessing: {nan_cols}")
            for col in nan_cols:
                print(f"  {col}: {new_user_row[col].values[0]}")
        
        # Preprocess
        X_new = pre_processing(new_user_row)
        print(f"Preprocessed shape: {X_new.shape}")
        
        # Check for NaN after preprocessing
        if X_new.isna().any().any():
            nan_cols_after = X_new.columns[X_new.isna().any()].tolist()
            print(f"[ERROR] NaN still present after preprocessing in: {nan_cols_after}")
            for col in nan_cols_after:
                print(f"  {col}: {X_new[col].values[0]}")
        else:
            print("[OK] No NaN values in preprocessed data")
        
        # Predict cluster
        predicted_cluster = loaded_model.predict(X_new)[0]
        print(f"[OK] Predicted cluster: {predicted_cluster}")
        
        # Get users in same cluster
        df_target = df_matrix.loc[df_matrix['Class Name'] == predicted_cluster].copy()
        
        if len(df_target) == 0:
            print("[WARNING] No users in this cluster")
            return None, None
        
        print(f"[OK] Found {len(df_target)} users in cluster {predicted_cluster}")
        
        # Drop Class Name for similarity
        df_target_features = df_target.drop('Class Name', axis=1)
        
        # Find similar users
        top_users_df = recommendations_based_on_user_profile(X_new, df_target_features, top_n)
        
        # Get full profiles
        matched_users = []
        for user_id in top_users_df.index:
            similarity_score = top_users_df.loc[user_id, 'matching_score']
            
            user_info = df_user_profiles[df_user_profiles['user_id'] == user_id]
            
            if len(user_info) > 0:
                user_dict = user_info.iloc[0].to_dict()
                user_dict['similarity_score'] = similarity_score
                user_dict['cluster'] = predicted_cluster
                matched_users.append(user_dict)
        
        print(f"[SUCCESS] Found {len(matched_users)} matches")
        
        return matched_users, predicted_cluster
        
    except Exception as e:
        print(f"[ERROR] Matching failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def format_match_profile(match_dict):
    """Format a match dictionary for display"""
    return {
        'user_id': int(match_dict['user_id']),
        'first_name': match_dict.get('first_name', 'Anonymous'),
        'last_name': match_dict.get('last_name', 'User'),
        'age': match_dict.get('age', 25),
        'gender': match_dict.get('gender', 'Other'),
        'education_level': match_dict.get('education_level', 'Undergraduate'),
        'occupation_status': match_dict.get('occupation_status', 'Employed'),
        'relationship_status': match_dict.get('relationship_status', 'Single'),
        'similarity_score': match_dict.get('similarity_score', 0.0),
        'cluster': match_dict.get('cluster', 0)
    }

# ============================================================================
# End of Matching Engine Functions
# ============================================================================

# Configure page
st.set_page_config(
    page_title="Vita Nova - Emotional Wellness Journey",
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
    if 'matching_data_loaded' not in st.session_state:
        st.session_state.matching_data_loaded = False
    if 'user_matches' not in st.session_state:
        st.session_state.user_matches = None
    if 'user_cluster' not in st.session_state:
        st.session_state.user_cluster = None

def process_questionnaire_data():
    """
    Process questionnaire answers and store them in user_profile for matching
    """
    q_answers = st.session_state.questionnaire_answers
    
    # Map questionnaire answers to profile fields needed for matching
    
    # Calculate age and age_groups from birthdate
    if 'birthdate' in st.session_state.user_profile:
        from datetime import datetime
        birthdate = st.session_state.user_profile['birthdate']
        if isinstance(birthdate, str):
            birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()
        age = (datetime.today().date() - birthdate).days // 365
        st.session_state.user_profile['age'] = age
        
        # Map to age groups (using regular hyphen to match CSV)
        if age < 18:
            st.session_state.user_profile['age_groups'] = 'Under 18'
        elif age < 25:
            st.session_state.user_profile['age_groups'] = '18-24'  # regular hyphen
        elif age < 35:
            st.session_state.user_profile['age_groups'] = '25-34'  # regular hyphen
        elif age < 45:
            st.session_state.user_profile['age_groups'] = '35-44'  # regular hyphen
        elif age < 55:
            st.session_state.user_profile['age_groups'] = '45-54'  # regular hyphen
        else:
            st.session_state.user_profile['age_groups'] = '55-64'  # Changed from '55+' to match CSV
    
    # Education level
    education_map = {
        'High School': 'High School',
        'Undergraduate degree': 'Undergraduate',
        'Postgraduate degree': 'Postgraduate'
    }
    st.session_state.user_profile['education_level'] = education_map.get(
        q_answers.get('q1'), 'Undergraduate'
    )
    
    # Occupation status
    occupation_map = {
        "I'm a student": 'Student',
        "I'm employed": 'Employed',
        "I'm self-employed": 'Self-employed',
        "I'm currently between jobs": 'Unemployed'
    }
    st.session_state.user_profile['occupation_status'] = occupation_map.get(
        q_answers.get('q5'), 'Employed'
    )
    
    # Diet type
    diet_map = {
        'I follow a vegetarian diet': 'Vegetarian',
        'I follow a vegan lifestyle': 'Vegan',
        'I enjoy a balanced, varied diet': 'Balanced',
        'I follow a keto/low-carb approach': 'Keto',
        'I tend to eat more convenience/fast foods': 'Fast Food'
    }
    st.session_state.user_profile['diet_type'] = diet_map.get(
        q_answers.get('q7'), 'Balanced'
    )
    
    # Stress level
    stress_map = {
        "I'm feeling relatively low stress": 'Low',
        "I'm experiencing moderate stress": 'Medium',
        "I'm dealing with high stress levels": 'High'
    }
    st.session_state.user_profile['stress_level'] = stress_map.get(
        q_answers.get('q14'), 'Medium'
    )
    
    # Mental health condition
    has_condition = q_answers.get('q12') == 'Yes'
    st.session_state.user_profile['has_mental_health_condition'] = 1 if has_condition else 0
    
    conditions = q_answers.get('q13', [])
    if conditions and 'None' not in conditions and 'Prefer not to say' not in conditions:
        st.session_state.user_profile['mental_health_condition'] = conditions[0]
    else:
        st.session_state.user_profile['mental_health_condition'] = 'Not Applicable'
    
    # Relationship status
    st.session_state.user_profile['relationship_status'] = q_answers.get('q16', 'Single')
    
    # Group mappings for continuous variables
    
    # Work hours (using en-dash to match CSV format)
    work_hours = q_answers.get('q6', 40)
    if work_hours <= 10:
        work_hours_group = '0–10 hrs'  # en-dash
    elif work_hours <= 20:
        work_hours_group = '11–20 hrs'  # en-dash
    elif work_hours <= 30:
        work_hours_group = '21–30 hrs'  # en-dash
    elif work_hours <= 40:
        work_hours_group = '31–40 hrs'  # en-dash
    elif work_hours <= 50:
        work_hours_group = '41–50 hrs'  # en-dash
    elif work_hours <= 60:
        work_hours_group = '51–60 hrs'  # en-dash
    else:
        work_hours_group = '60+ hrs'
    st.session_state.user_profile['work_hours_groups'] = work_hours_group
    
    # Sleep hours (using en-dash to match CSV format)
    sleep_hours = q_answers.get('q8', 7)
    if sleep_hours < 4:
        sleep_hours_group = '<4 hrs'
    elif sleep_hours <= 6:
        sleep_hours_group = '4–6 hrs'  # en-dash
    elif sleep_hours <= 8:
        sleep_hours_group = '6–8 hrs'  # en-dash
    elif sleep_hours <= 10:
        sleep_hours_group = '8–10 hrs'  # en-dash
    else:
        sleep_hours_group = '10+ hrs'
    st.session_state.user_profile['sleep_hours_groups'] = sleep_hours_group
    
    # Physical activity (using en-dash to match CSV format)
    activity_hours = q_answers.get('q10', 5)
    if activity_hours <= 1:
        activity_group = 'Rarely (0–1)'  # en-dash
    elif activity_hours <= 3:
        activity_group = 'Light (2–3)'  # en-dash
    elif activity_hours <= 5:
        activity_group = 'Moderate (4–5)'  # en-dash - matches CSV
    elif activity_hours <= 7:
        activity_group = 'Active (6–7)'  # en-dash - matches CSV
    elif activity_hours <= 14:
        activity_group = 'Very Active (8–14)'  # en-dash
    else:
        activity_group = 'Extremely Active (15+)'
    st.session_state.user_profile['physical_activity_groups'] = activity_group
    
    # Screen time (using en-dash to match CSV format)
    screen_hours = q_answers.get('q11', 6)
    if screen_hours <= 2:
        screen_group = '<2 hrs'  # matches CSV
    elif screen_hours <= 4:
        screen_group = '2–4 hrs'  # en-dash
    elif screen_hours <= 6:
        screen_group = '4–6 hrs'  # en-dash
    elif screen_hours <= 8:
        screen_group = '6–8 hrs'  # en-dash
    elif screen_hours <= 12:
        screen_group = '8–12 hrs'  # en-dash
    else:
        screen_group = '12+ hrs'
    st.session_state.user_profile['screen_time_groups'] = screen_group
    
    # Friends groups (using en-dash to match CSV format)
    friends = q_answers.get('q15', 3)
    if friends <= 0:
        friends_group = '0'
    elif friends <= 2:
        friends_group = '0–2'  # en-dash - matches CSV
    elif friends <= 4:
        friends_group = '3–4'  # en-dash
    elif friends <= 6:
        friends_group = '5–6'  # en-dash
    elif friends <= 8:
        friends_group = '7–8'  # en-dash
    else:
        friends_group = '9 plus'
    st.session_state.user_profile['friends_groups'] = friends_group

def welcome_page():
    """Welcome page with introduction to Vita Nova"""
    st.markdown('<h1 class="main-header">🌱 Welcome to Vita Nova</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Your Emotional Wellness Journey Begins Here
    
    Vita Nova is designed to help you explore your emotional landscape, connect with others who share similar experiences, 
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
            
            # Process questionnaire data for matching
            process_questionnaire_data()
            
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
    your journey through Vita Nova.
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
                        
                        # Get all answer scores and store numeric codes
                        scores = []
                        for i in range(len(entry_questions)):
                            answer_text = st.session_state.entry_hall_answers[f"q_{i}"]
                            answer_code = list(entry_questions[i]['options']).index(answer_text) + 1
                            scores.append(answer_code)
                            # Store numeric code for matching engine
                            st.session_state.entry_hall_answers[f"q_{i}_code"] = answer_code
                        
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
                        
                        # Store scores in user_profile for matching engine
                        st.session_state.user_profile['pulse_score'] = st.session_state.pulse_score
                        st.session_state.user_profile['mood_index'] = st.session_state.mood_index
                        st.session_state.user_profile['energy_index'] = st.session_state.energy_index
                        st.session_state.user_profile['social_index'] = st.session_state.social_index
                        st.session_state.user_profile['security_index'] = st.session_state.security_index
                        
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
    Based on your Entry Hall responses, choose one of three paths for your Vita Nova journey. 
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
                        # Calculate Matching Score for Door 2 (Connect Hub)
                        # This represents how well the user's profile matches for connections
                        door2_scores = []
                        door2_answers_coded = {}
                        
                        for i in range(min(len(connect_questions), 25)):
                            if f"q_{i}" in st.session_state.door2_answers:
                                answer_text = st.session_state.door2_answers[f"q_{i}"]
                                answer_code = connect_questions[i]['options'].index(answer_text) + 1
                                door2_scores.append(answer_code)
                                # Store numeric code for matching engine
                                door2_answers_coded[f"q_{i}"] = answer_code
                        
                        # Calculate matching score (average of all responses)
                        if door2_scores:
                            matching_score = sum(door2_scores) / len(door2_scores)
                            st.session_state.matching_score = round(matching_score, 2)
                        
                        # Run matching engine to find similar users
                        try:
                            # Load matching data if not already loaded
                            if not st.session_state.matching_data_loaded:
                                if load_matching_data():
                                    st.session_state.matching_data_loaded = True
                                else:
                                    st.error("Failed to load matching models. Using placeholder recommendations.")
                                    st.session_state.user_matches = None
                                    st.session_state.user_cluster = None
                            
                            if st.session_state.matching_data_loaded:
                                # Prepare entry hall answers coded
                                entry_hall_coded = {}
                                for i in range(15):
                                    key = f"q_{i}_code"
                                    if key in st.session_state.entry_hall_answers:
                                        entry_hall_coded[f"q_{i}"] = st.session_state.entry_hall_answers[key]
                                
                                # Get match recommendations
                                matches, cluster = get_user_matches(
                                    user_profile=st.session_state.user_profile,
                                    entry_hall_answers=entry_hall_coded,
                                    door2_answers=door2_answers_coded,
                                    top_n=5
                                )
                                
                                if matches is not None:
                                    st.session_state.user_matches = matches
                                    st.session_state.user_cluster = cluster
                                else:
                                    st.session_state.user_matches = None
                                    st.session_state.user_cluster = None
                        except Exception as e:
                            st.error(f"Matching engine error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            st.session_state.user_matches = None
                            st.session_state.user_cluster = None
                        
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
    Congratulations! You've completed your Vita Nova journey. Here's a summary of your experience:
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
        
        # Display Matching Score if Door 2 (Connect Hub) was completed
        door = st.session_state.get('current_door', 'None')
        if door == 2 and 'matching_score' in st.session_state:
            st.write("")  # Add spacing
            matching_score = st.session_state.get('matching_score', 0)
            st.write(f"**Matching Score:** {matching_score}/5.0")
            st.caption("Based on your Connect Hub responses")
        
        st.write("")  # Add spacing
        door_names = {1: "Emotional Room", 2: "Connect Hub", 3: "Guided Activity Spaces"}
        st.write(f"**Chosen Path:** {door_names.get(door, 'None')}")
    
    st.markdown("---")
    
    # User Matching Recommendations Section
    st.markdown("### 🔗 User Matching Recommendations")
    
    # Get current values
    pulse_score = st.session_state.get('pulse_score', 0)
    mood_index = st.session_state.get('mood_index', 0)
    energy_index = st.session_state.get('energy_index', 0)
    social_index = st.session_state.get('social_index', 0)
    security_index = st.session_state.get('security_index', 0)
    door = st.session_state.get('current_door', 1)
    
    # Check if we have real matches (from Door 2)
    if door == 2 and st.session_state.user_matches is not None and len(st.session_state.user_matches) > 0:
        # Display REAL matched users
        cluster = st.session_state.user_cluster
        
        st.success(f"✨ Found {len(st.session_state.user_matches)} compatible users in your emotional wellness cluster (Cluster {cluster})!")
        
        st.info("""
        **You've been matched with users based on:**
        - ML-powered clustering using your Entry Hall and Connect Hub responses
        - Cosine similarity analysis of emotional patterns and preferences
        - Shared Pulse Score ranges and subscore profiles
        - Similar connection priorities and communication styles
        """)
        
        st.markdown("#### 🌟 Your Top Matches:")
        
        # Display top 5 matches (user_matches is now a list of dicts)
        for idx, match_dict in enumerate(st.session_state.user_matches, 1):
            match = format_match_profile(match_dict)
            
            # Create expandable section for each match
            similarity_pct = match['similarity_score'] * 100
            with st.expander(f"**Match #{idx}: {match['first_name']} {match['last_name']}** (Similarity: {similarity_pct:.1f}%)", expanded=(idx <= 2)):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Profile:**")
                    st.write(f"• Name: {match['first_name']} {match['last_name']}")
                    st.write(f"• Age: {match['age']}")
                    st.write(f"• Gender: {match['gender']}")
                    st.write(f"• Education: {match['education_level']}")
                    st.write(f"• Occupation: {match['occupation_status']}")
                    st.write(f"• Relationship: {match['relationship_status']}")
                
                with col_b:
                    st.markdown("**Compatibility:**")
                    st.write(f"• Similarity Score: {similarity_pct:.1f}%")
                    st.write(f"• Cluster: {match['cluster']}")
                    st.write("")
                    
                    # Show general compatibility notes
                    st.markdown("**Why this match?**")
                    if match['similarity_score'] > 0.95:
                        st.write("✓ Exceptionally high similarity score (>95%)")
                    elif match['similarity_score'] > 0.90:
                        st.write("✓ Very high similarity score (>90%)")
                    elif match['similarity_score'] > 0.85:
                        st.write("✓ Strong similarity score (>85%)")
                    
                    st.write(f"✓ Same emotional wellness cluster ({match['cluster']})")
                    st.write(f"✓ Similar connection preferences and communication style")
        
        st.markdown("")
        st.markdown("**Matching Algorithm:**")
        st.write(f"• Your cluster: {cluster} (grouped with users sharing similar emotional patterns)")
        st.write(f"• Similarity metric: Cosine similarity on {15+25} dimensional feature space")
        st.write(f"• Features used: Entry Hall responses, Connect Hub responses, and wellness subscores")
        
    else:
        # Display placeholder info if no matches (Door 1, Door 3, or matching failed)
        if door == 2:
            st.warning("⚠️ Matching system temporarily unavailable. Showing example recommendations below.")
        else:
            st.info("💡 Complete Door 2 (Connect Hub) to receive personalized user matches based on ML clustering!")
        
        st.info("""
        **When you complete Door 2, you'll be matched based on:**
        - Similar emotional patterns and Pulse Score ranges
        - Complementary subscore profiles for mutual support
        - Shared connection preferences and communication styles
        - ML-powered clustering and cosine similarity analysis
        """)
        
        # Display example matches
        st.markdown("#### Example Potential Matches:")
        
        match_col1, match_col2 = st.columns(2)
        
        with match_col1:
            st.markdown("""
            **Example Match 1: Similar Emotional State**
            - Pulse Score: Similar range to yours
            - High resonance in Mood and Social indices
            - Looking for: Emotional support and connection
            - Based on ML clustering of emotional patterns
            """)
        
        with match_col2:
            st.markdown("""
            **Example Match 2: Complementary Support**
            - Pulse Score: Slightly higher energy levels
            - Can provide: Motivation and activity ideas
            - Seeking: Meaningful conversations
            - Same emotional wellness cluster
            """)
        
        st.markdown("")
        st.markdown("**How matching works:**")
        st.write(f"• Your Pulse Score ({pulse_score}) helps find users in similar emotional states")
        st.write(f"• Your Social Index ({social_index}) indicates preferred social engagement level")
        st.write(f"• Your Energy Index ({energy_index}) helps match activity compatibility")
        st.write(f"• ML clustering groups users by emotional patterns and preferences")
    
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
