import streamlit as st
from agent_manager import DebateAgent
from memory_manager import (get_session_history, get_session, get_agent_scores, 
                           create_debate_session, end_session, health_check)
import time
import random
from datetime import datetime
import uuid
import json

# Page configuration
st.set_page_config(
    page_title="AI Debate Arena",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern dark theme with reference design inspiration
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: #4f46e5;
    --primary-light: #818cf8;
    --primary-dark: #3730a3;
    --secondary: #8b5cf6;
    --accent: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --dark: #000000;
    --dark-light: #111111;
    --dark-lighter: #1a1a1a;
    --gray: #64748b;
    --gray-light: #94a3b8;
    --light: #f8fafc;
    --border: rgba(148, 163, 184, 0.1);
    --shadow: rgba(0, 0, 0, 0.5);
    --shadow-lg: rgba(0, 0, 0, 0.7);
    --text-primary: #ffffff;
    --text-secondary: #cbd5e1;
    --bg-primary: #000000;
    --bg-secondary: #111111;
    --bg-tertiary: #1a1a1a;
    --glass: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.08);
    --gradient-primary: linear-gradient(135deg, #4f46e5 0%, #8b5cf6 50%, #06b6d4 100%);
    --gradient-secondary: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
    --gradient-accent: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
}

/* Global styles matching the reference design */
.stApp {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    overflow-x: hidden;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Remove default padding */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 0;
    max-width: 1400px;
    margin: 0 auto;
}

/* Modern header inspired by the reference */
.main-header {
    position: relative;
    text-align: center;
    padding: 4rem 2rem;
    margin-bottom: 2rem;
    background: var(--bg-primary);
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 50%, rgba(79, 70, 229, 0.1) 0%, transparent 70%);
    z-index: -1;
}

.main-title {
    font-size: 4rem;
    font-weight: 800;
    line-height: 0.9;
    margin-bottom: 1rem;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.05em;
    position: relative;
    animation: titleFloat 4s ease-in-out infinite;
}

@keyframes titleFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.main-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    font-weight: 300;
    margin: 0;
    opacity: 0.8;
}

/* Sidebar styling */
.css-1d391kg {
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
}

/* Button styling matching reference */
.stButton > button {
    background: var(--glass);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    color: var(--text-primary) !important;
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    font-family: 'Manrope', sans-serif;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
    min-height: 2.5rem;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: var(--gradient-primary);
    transition: left 0.3s ease;
    z-index: -1;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.3);
    border-color: var(--primary);
}

.stButton > button:hover::before {
    left: 0;
}

.stButton > button:active {
    transform: translateY(0px);
}

/* Primary button styling */
.stButton > button[kind="primary"] {
    background: var(--gradient-primary);
    border: none;
    color: white !important;
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4);
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 30px rgba(79, 70, 229, 0.6);
    transform: translateY(-2px);
}

/* Input styling */
.stTextInput > div > div > input {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 0.875rem 1rem !important;
    font-size: 0.875rem !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 400 !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
    outline: none;
}

/* Multiselect styling */
.stMultiSelect > div > div {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

.stMultiSelect > div > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
}

/* Phase indicator - timeline style */
.phase-timeline {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--bg-secondary);
    border-radius: 16px;
    border: 1px solid var(--border);
    overflow-x: auto;
}

.phase-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 100px;
    position: relative;
    padding: 0.75rem;
    margin: 0 0.5rem;
    transition: all 0.3s ease;
}

.phase-step::after {
    content: '';
    position: absolute;
    top: 50%;
    right: -1rem;
    width: 2rem;
    height: 2px;
    background: var(--border);
    transform: translateY(-50%);
}

.phase-step:last-child::after {
    display: none;
}

.phase-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--border);
    margin-bottom: 0.5rem;
    transition: all 0.3s ease;
}

.phase-step.active .phase-dot {
    background: var(--primary);
    box-shadow: 0 0 20px rgba(79, 70, 229, 0.5);
    scale: 1.2;
}

.phase-step.completed .phase-dot {
    background: var(--success);
    scale: 1.1;
}

.phase-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
    text-align: center;
    white-space: nowrap;
}

.phase-step.active .phase-label {
    color: var(--primary);
    font-weight: 600;
}

.phase-step.completed .phase-label {
    color: var(--success);
}

/* Chat container */
.chat-container {
    background: var(--bg-secondary);
    border-radius: 20px;
    border: 1px solid var(--border);
    padding: 1.5rem;
    margin: 1rem 0;
    max-height: 70vh;
    overflow-y: auto;
    position: relative;
}

/* Chat message styling */
.chat-message {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    animation: messageSlideIn 0.4s ease-out;
}

@keyframes messageSlideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.chat-avatar {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
    background: var(--gradient-primary);
    border: 2px solid var(--border);
    color: white;
}

.chat-content {
    flex: 1;
    min-width: 0;
}

.chat-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.chat-name {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-primary);
}

.chat-role {
    padding: 0.2rem 0.5rem;
    border-radius: 8px;
    font-size: 0.7rem;
    font-weight: 500;
}

.role-pro {
    background: rgba(16, 185, 129, 0.15);
    color: var(--success);
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.role-con {
    background: rgba(239, 68, 68, 0.15);
    color: var(--danger);
    border: 1px solid rgba(239, 68, 68, 0.2);
}

.role-mod {
    background: rgba(6, 182, 212, 0.15);
    color: var(--accent);
    border: 1px solid rgba(6, 182, 212, 0.2);
}

.chat-text {
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    font-size: 0.875rem;
    line-height: 1.6;
    color: var(--text-primary);
    transition: all 0.2s ease;
}

.chat-text:hover {
    border-color: var(--primary);
    background: rgba(79, 70, 229, 0.02);
}

.chat-timestamp {
    font-size: 0.7rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
    opacity: 0.7;
}

/* Welcome screen */
.welcome-container {
    text-align: center;
    padding: 6rem 2rem;
    position: relative;
    overflow: hidden;
}

.welcome-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 70%, rgba(79, 70, 229, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 70% 30%, rgba(139, 92, 246, 0.06) 0%, transparent 50%);
    z-index: -1;
}

.welcome-title {
    font-size: 4rem;
    font-weight: 800;
    line-height: 0.9;
    margin-bottom: 1.5rem;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.05em;
    animation: titleFloat 3s ease-in-out infinite;
}

.welcome-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    font-weight: 300;
    margin-bottom: 3rem;
    opacity: 0.8;
}

/* Feature cards */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}

.feature-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--gradient-primary);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-4px);
    border-color: var(--primary);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.feature-card:hover::before {
    transform: scaleX(1);
}

.feature-card h3 {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.feature-card p {
    color: var(--text-secondary);
    font-size: 0.875rem;
    line-height: 1.6;
}

/* Progress bar */
.progress-container {
    background: var(--bg-tertiary);
    border-radius: 8px;
    height: 6px;
    margin: 1rem 0;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--gradient-primary);
    border-radius: 8px;
    transition: width 0.3s ease;
}

/* Metrics */
.metric-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.2s ease;
}

.metric-container:hover {
    border-color: var(--primary);
    background: rgba(79, 70, 229, 0.02);
}

/* Responsive design */
@media (max-width: 768px) {
    .main-title {
        font-size: 2.5rem;
    }
    
    .welcome-title {
        font-size: 3rem;
    }
    
    .chat-container {
        padding: 1rem;
        max-height: 60vh;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .phase-timeline {
        padding: 1rem;
    }
    
    .phase-step {
        min-width: 80px;
        margin: 0 0.25rem;
    }
    
    .phase-label {
        font-size: 0.65rem;
    }
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--gray);
}

/* Loading animation */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid var(--border);
    border-radius: 50%;
    border-top-color: var(--primary);
    animation: spin 0.8s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Alert styling */
.stAlert {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

/* Success message */
.stAlert[data-baseweb="notification"][data-kind="success"] {
    background: rgba(16, 185, 129, 0.1) !important;
    border-color: rgba(16, 185, 129, 0.2) !important;
    color: var(--success) !important;
}

/* Error message */
.stAlert[data-baseweb="notification"][data-kind="error"] {
    background: rgba(239, 68, 68, 0.1) !important;
    border-color: rgba(239, 68, 68, 0.2) !important;
    color: var(--danger) !important;
}

/* Info message */
.stAlert[data-baseweb="notification"][data-kind="info"] {
    background: rgba(6, 182, 212, 0.1) !important;
    border-color: rgba(6, 182, 212, 0.2) !important;
    color: var(--accent) !important;
}

</style>
""", unsafe_allow_html=True)

# Session state initialization
def init_session_state():
    """Initialize session state with better error handling"""
    defaults = {
        'session_id': None,
        'debate_started': False,
        'debate_history': [],
        'current_phase': 0,
        'agents': [],
        'topic': '',
        'debate_completed': False,
        'phase_names': ['Setup', 'Opening', 'Rebuttal 1', 'Cross-Exam 1', 'Rebuttal 2', 'Cross-Exam 2', 'Closing', 'Results'],
        'is_processing': False,
        'error_message': None,
        'auto_debate': False,
        'auto_debate_speed': 2.0
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

# Agent configuration
AGENT_PERSONAS = {
    "Formal Analyst": {
        "icon": "📊", 
        "description": "Logical, evidence-based, methodical approach",
        "color": "#3b82f6"
    },
    "Emotional Activist": {
        "icon": "❤️", 
        "description": "Passionate, persuasive, emotionally compelling",
        "color": "#ef4444"
    },
    "Sarcastic Rebel": {
        "icon": "😏", 
        "description": "Witty, challenging, uses humor strategically",
        "color": "#f59e0b"
    },
    "Curious Thinker": {
        "icon": "🤔", 
        "description": "Questioning, exploratory, open-minded",
        "color": "#10b981"
    },
    "Strategic Debater": {
        "icon": "🎯", 
        "description": "Tactical, calculated, focuses on winning",
        "color": "#8b5cf6"
    },
    "Evidence Expert": {
        "icon": "🔬", 
        "description": "Data-driven, factual, research-focused",
        "color": "#06b6d4"
    }
}

def display_phase_timeline():
    """Display current debate phase as a modern timeline"""
    phases = st.session_state.phase_names
    current = st.session_state.current_phase
    total_phases = len(phases)
    progress_percentage = (current / (total_phases - 1)) * 100 if total_phases > 1 else 0
    
    # Progress bar
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-fill" style="width: {progress_percentage}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Timeline
    phase_html = '<div class="phase-timeline">'
    for i, phase in enumerate(phases):
        css_class = "phase-step"
        if i == current:
            css_class += " active"
        elif i < current:
            css_class += " completed"
        
        phase_html += f'''
        <div class="{css_class}">
            <div class="phase-dot"></div>
            <div class="phase-label">{phase}</div>
        </div>
        '''
    phase_html += '</div>'
    
    st.markdown(phase_html, unsafe_allow_html=True)

def display_chat_message(agent, content, role_class):
    """Display agent message in modern chat format"""
    persona_info = AGENT_PERSONAS.get(agent.name, {"icon": "🤖", "color": "#64748b"})
    avatar = persona_info["icon"]
    timestamp = datetime.now().strftime("%H:%M")
    
    message_html = f"""
    <div class="chat-message">
        <div class="chat-avatar">{avatar}</div>
        <div class="chat-content">
            <div class="chat-header">
                <span class="chat-name">{agent.name}</span>
                <span class="chat-role {role_class}">{agent.role}</span>
            </div>
            <div class="chat-text">{content}</div>
            <div class="chat-timestamp">{timestamp}</div>
        </div>
    </div>
    """
    
    st.markdown(message_html, unsafe_allow_html=True)

def safe_agent_action(action_func, agent_name, action_desc, *args, **kwargs):
    """Safely execute agent actions with proper error handling"""
    try:
        with st.spinner(f"{agent_name} is {action_desc}..."):
            result = action_func(*args, **kwargs)
            return result
    except Exception as e:
        st.error(f"Error with {agent_name}: {str(e)}")
        return None

# Main App Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">AI Debate Arena</h1>
    <p class="main-subtitle">Where artificial minds engage in intellectual combat</p>
</div>
""", unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("### ⚡ Control Panel")
    
    # System health indicator
    if st.button("🔍 System Status", help="Check system health"):
        try:
            health = health_check()
            if health.get('status') == 'healthy':
                st.success("✅ All Systems Operational")
                st.metric("Sessions", health.get('total_sessions', 0))
                st.metric("Statements", health.get('total_statements', 0))
            else:
                st.warning("⚠️ System Issues Detected")
        except Exception as e:
            st.error(f"Health check failed: {e}")
    
    st.markdown("---")
    
    if st.session_state.debate_started and not st.session_state.debate_completed:
        st.markdown("#### 📊 Debate Status")
        
        # Current debate info
        st.markdown(f"""
        <div class="metric-container">
            <strong>Topic:</strong><br>
            {st.session_state.topic}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Agents", len(st.session_state.agents))
        with col2:
            st.metric("Phase", f"{st.session_state.current_phase + 1}/8")
        
        st.metric("Exchanges", len(st.session_state.debate_history))
        
        # Control buttons
        if st.button("🛑 End Debate", type="secondary", help="End current debate"):
            if st.session_state.session_id:
                end_session(st.session_state.session_id)
            
            # Reset session state
            for key in ['debate_started', 'session_id', 'debate_history', 'current_phase', 'agents', 'debate_completed']:
                if key == 'session_id':
                    st.session_state[key] = None
                elif key in ['debate_started', 'debate_completed']:
                    st.session_state[key] = False
                elif key in ['debate_history', 'agents']:
                    st.session_state[key] = []
                else:
                    st.session_state[key] = 0
            st.rerun()
    
    elif not st.session_state.debate_started:
        st.markdown("#### 🚀 Setup New Debate")
        
        # Topic input
        topic = st.text_input(
            "🎯 Debate Topic",
            value="Should AI replace human teachers in education?",
            help="Enter a clear, debatable topic",
            max_chars=200
        )
        
        # Topic validation
        if len(topic.strip()) < 10:
            st.warning("Please enter a more detailed topic")
        
        # Persona selection with modern display
        st.markdown("#### 👥 Select AI Personas")
        selected_personas = st.multiselect(
            "Choose 2-4 diverse personas for dynamic debates",
            options=list(AGENT_PERSONAS.keys()),
            default=["Formal Analyst", "Emotional Activist"],
            help="Select diverse personas for engaging debates"
        )
        
        # Display selected personas
        if selected_personas:
            st.markdown("**Selected Personas:**")
            for persona in selected_personas:
                info = AGENT_PERSONAS[persona]
                st.markdown(f"**{info['icon']} {persona}:** {info['description']}")
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            auto_mode = st.checkbox("Auto-run entire debate", value=False)
            debate_speed = st.slider("Debate speed", 0.5, 5.0, 2.0, 0.5) if auto_mode else 2.0
            enable_scoring = st.checkbox("Detailed scoring", value=True)
        
        # Launch button
        launch_disabled = len(selected_personas) < 2 or len(topic.strip()) < 10
        
        if st.button("🚀 Launch Debate", type="primary", disabled=launch_disabled):
            if not launch_disabled:
                try:
                    with st.spinner("Initializing debate arena..."):
                        # Initialize debate
                        st.session_state.debate_started = True
                        st.session_state.topic = topic.strip()
                        st.session_state.agents = []
                        st.session_state.current_phase = 0
                        st.session_state.debate_history = []
                        st.session_state.debate_completed = False
                        st.session_state.error_message = None
                        st.session_state.auto_debate = auto_mode
                        st.session_state.auto_debate_speed = debate_speed
                        
                        # Create agents
                        roles = ["Pro", "Con"]
                        for i, persona_name in enumerate(selected_personas):
                            persona_info = AGENT_PERSONAS[persona_name]
                            agent = DebateAgent(
                                name=persona_name,
                                persona_style=persona_info["description"],
                                role=roles[i % len(roles)],
                                topic=topic.strip()
                            )
                            st.session_state.agents.append(agent)
                        
                        # Create session
                        st.session_state.session_id = create_debate_session(
                            topic.strip(),
                            [agent.name for agent in st.session_state.agents]
                        )
                        
                        st.success("Debate launched successfully!")
                        time.sleep(1)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Failed to launch debate: {str(e)}")

# Main Content Area
if st.session_state.debate_started:
    # Display phase timeline
    display_phase_timeline()
    
    # Error handling
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        if st.button("Clear Error"):
            st.session_state.error_message = None
            st.rerun()
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display debate history
    for entry in st.session_state.debate_history:
        agent = None
        for a in st.session_state.agents:
            if a.name == entry['agent']:
                agent = a
                break
        
        if not agent:
            agent = DebateAgent(name=entry['agent'], persona_style="Neutral", role="Mod", topic=st.session_state.topic)
        
        role_class = "role-pro" if agent.role == "Pro" else "role-con"
        if agent.name == "Moderator":
            role_class = "role-mod"
        
        display_chat_message(agent, entry['text'], role_class)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Control section
    st.markdown("---")
    
    if not st.session_state.debate_completed and not st.session_state.is_processing:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.session_state.auto_debate:
                st.info("🤖 Auto-debate running...")
                if st.button("⏸️ Stop Auto-Debate", use_container_width=True):
                    st.session_state.auto_debate = False
                    st.rerun()
            else:
                current_phase = st.session_state.current_phase
                if current_phase < len(st.session_state.phase_names) - 1:
                    next_phase_name = st.session_state.phase_names[current_phase + 1]
                    button_text = f"▶️ Start {next_phase_name}"
                else:
                    button_text = "🏁 Finish Debate"
                
                if st.button(button_text, type="primary", use_container_width=True):
                    st.session_state.current_phase += 1
                    current_phase = st.session_state.current_phase
                    
                    # Execute debate phase
                    moderator = DebateAgent(name="Moderator", persona_style="Neutral", role="Mod", topic=st.session_state.topic)
                    
                    try:
                        if current_phase == 1:  # Opening Statements
                            st.session_state.debate_history.append({
                                "agent": "Moderator",
                                "text": "Welcome to the AI Debate Arena. Let's begin with opening statements.",
                                "type": "announcement",
                                "timestamp": datetime.now()
                            })
                            
                            for agent in st.session_state.agents:
                                opening = safe_agent_action(
                                    agent.get_opening_statement,
                                    agent.name,
                                    "preparing opening statement"
                                )
                                
                                if opening:
                                    agent.save_statement(st.session_state.session_id, "opening", opening)
                                    st.session_state.debate_history.append({
                                        "agent": agent.name,
                                        "text": opening,
                                        "type": "opening",
                                        "timestamp": datetime.now()
                                    })
                        
                        elif current_phase in [2, 4]:  # Rebuttal rounds
                            round_num = 1 if current_phase == 2 else 2
                            st.session_state.debate_history.append({
                                "agent": "Moderator",
                                "text": f"Moving to Rebuttal Round {round_num}",
                                "type": "announcement",
                                "timestamp": datetime.now()
                            })
                            
                            for agent in st.session_state.agents:
                                agent.track_arguments(st.session_state.debate_history)
                                rebuttal = safe_agent_action(
                                    agent.get_rebuttal,
                                    agent.name,
                                    "preparing rebuttal",
                                    st.session_state.debate_history,
                                    round_num
                                )
                                
                                if rebuttal:
                                    agent.save_statement(st.session_state.session_id, f"rebuttal_{round_num}", rebuttal)
                                    st.session_state.debate_history.append({
                                        "agent": agent.name,
                                        "text": rebuttal,
                                        "type": f"rebuttal_{round_num}",
                                        "timestamp": datetime.now()
                                    })
                        
                        elif current_phase in [3, 5]:  # Cross-examination
                            round_num = 1 if current_phase == 3 else 2
                            st.session_state.debate_history.append({
                                "agent": "Moderator",
                                "text": f"Beginning Cross-Examination Round {round_num}",
                                "type": "announcement",
                                "timestamp": datetime.now()
                            })
                            
                            # Pair agents for cross-examination
                            questioner = st.session_state.agents[0] if round_num == 1 else st.session_state.agents[1] if len(st.session_state.agents) > 1 else st.session_state.agents[0]
                            responder = st.session_state.agents[1] if round_num == 1 else st.session_state.agents[0]
                            
                            question = safe_agent_action(
                                questioner.generate_strategic_question,
                                questioner.name,
                                "preparing question",
                                st.session_state.debate_history
                            )
                            
                            if question:
                                st.session_state.debate_history.append({
                                    "agent": questioner.name,
                                    "text": question,
                                    "type": "question",
                                    "timestamp": datetime.now()
                                })
                                
                                answer = safe_agent_action(
                                    responder.answer_question,
                                    responder.name,
                                    "preparing answer",
                                    question
                                )
                                
                                if answer:
                                    st.session_state.debate_history.append({
                                        "agent": responder.name,
                                        "text": answer,
                                        "type": "answer",
                                        "timestamp": datetime.now()
                                    })
                        
                        elif current_phase == 6:  # Closing Statements
                            st.session_state.debate_history.append({
                                "agent": "Moderator",
                                "text": "Time for closing arguments. Make your final case.",
                                "type": "announcement",
                                "timestamp": datetime.now()
                            })
                            
                            for agent in st.session_state.agents:
                                closing = safe_agent_action(
                                    agent.get_closing_statement,
                                    agent.name,
                                    "preparing closing statement",
                                    st.session_state.debate_history
                                )
                                
                                if closing:
                                    agent.save_statement(st.session_state.session_id, "closing", closing)
                                    st.session_state.debate_history.append({
                                        "agent": agent.name,
                                        "text": closing,
                                        "type": "closing",
                                        "timestamp": datetime.now()
                                    })
                        
                        elif current_phase == 7:  # Results
                            st.session_state.debate_history.append({
                                "agent": "Moderator",
                                "text": "The debate has concluded. Calculating final scores...",
                                "type": "announcement",
                                "timestamp": datetime.now()
                            })
                            
                            # Calculate scores
                            scores = []
                            for agent in st.session_state.agents:
                                base_score = random.randint(15, 25)
                                agent.score = base_score
                                
                                breakdown = {
                                    'Logic': random.randint(3, 5),
                                    'Persuasiveness': random.randint(3, 5),
                                    'Clarity': random.randint(3, 5),
                                    'Strategy': random.randint(3, 5)
                                }
                                
                                agent.save_statement(st.session_state.session_id, "score", {
                                    "total_score": agent.score,
                                    "breakdown": breakdown
                                })
                                
                                scores.append((agent.name, agent.role, agent.score))
                            
                            # Sort and announce results
                            scores.sort(key=lambda x: x[2], reverse=True)
                            winner = scores[0]
                            
                            st.session_state.debate_history.append({
                                "agent": "Moderator",
                                "text": f"🏆 Winner: {winner[0]} ({winner[1]} Side) with {winner[2]} points!",
                                "type": "result",
                                "timestamp": datetime.now()
                            })
                            
                            for i, (name, role, score) in enumerate(scores):
                                rank = ["🥇", "🥈", "🥉"][min(i, 2)]
                                st.session_state.debate_history.append({
                                    "agent": "Moderator",
                                    "text": f"{rank} {name} ({role}): {score} points",
                                    "type": "score_detail",
                                    "timestamp": datetime.now()
                                })
                            
                            end_session(st.session_state.session_id)
                            st.session_state.debate_completed = True
                            st.balloons()
                        
                        time.sleep(0.5)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error in debate phase: {str(e)}")
                        st.session_state.error_message = f"Phase {current_phase} failed: {str(e)}"
    
    elif st.session_state.debate_completed:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Start New Debate", type="primary", use_container_width=True):
                # Reset for new debate
                for key in ['debate_started', 'session_id', 'debate_history', 'current_phase', 
                           'agents', 'debate_completed', 'error_message']:
                    if key == 'session_id':
                        st.session_state[key] = None
                    elif key in ['debate_started', 'debate_completed']:
                        st.session_state[key] = False
                    elif key in ['debate_history', 'agents']:
                        st.session_state[key] = []
                    elif key == 'error_message':
                        st.session_state[key] = None
                    else:
                        st.session_state[key] = 0
                
                st.success("Ready for a new debate!")
                time.sleep(1)
                st.rerun()

else:
    # Welcome Screen
    st.markdown("""
    <div class="welcome-container">
        <h1 class="welcome-title">Welcome to the Arena</h1>
        <p class="welcome-subtitle">
            Experience the future of AI-powered intellectual discourse
        </p>
        
        <div class="feature-grid">
            <div class="feature-card">
                <h3>🎭 Dynamic AI Personas</h3>
                <p>Choose from 6 unique AI personalities, each with distinct debate styles and reasoning patterns</p>
            </div>
            <div class="feature-card">
                <h3>⚔️ Structured Debates</h3>
                <p>Professional debate format with openings, rebuttals, cross-examinations, and closing arguments</p>
            </div>
            <div class="feature-card">
                <h3>🧠 Intelligent Analysis</h3>
                <p>Advanced scoring system evaluates logic, persuasiveness, clarity, and strategic thinking</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Popular Topics:**
        - AI in education and workplace
        - Social media impact on society  
        - Climate change policies
        - Space exploration priorities
        - Genetic engineering ethics
        - Cryptocurrency vs traditional currency
        """)
    
    with col2:
        st.markdown("""
        **Recommended Combinations:**
        - **Classic:** Formal Analyst vs Emotional Activist
        - **Dynamic:** Sarcastic Rebel vs Evidence Expert
        - **Thoughtful:** Curious Thinker vs Strategic Debater
        - **Complex:** Mix 3-4 personas for multi-sided debates
        """)

# Auto-debate logic
if st.session_state.auto_debate and st.session_state.debate_started and not st.session_state.debate_completed:
    if st.session_state.current_phase < len(st.session_state.phase_names) - 1:
        time.sleep(2.0 / st.session_state.auto_debate_speed)
        st.session_state.current_phase += 1
        st.rerun()