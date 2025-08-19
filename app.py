import streamlit as st
import re
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Preloaded values configuration
PRELOADED_VALUES = {
    'phone_numbers': [
        '14342151980',
        '18334932440', 
        '12768659060',
        '12029902006',
        '17036915201',
        '18042085260',
        '17579099544',
        '15409999324',
        '18049420185',
        '12768211095',
        '17577608278',
        '17206730123',
        '12764096013',
        '12408978820'
    ],
    'time_formats': [
        '2025-07-10T12:42:42',
        '2025-08-15T09:30:15',
        '2025-09-22T14:15:30',
        '2025-10-05T16:45:00',
        '2025-11-12T11:20:25',
        '2025-12-01T13:55:10'
    ]
}

def load_responsive_css():
    """Enhanced responsive CSS with accessibility and fluid design"""
    st.markdown("""
    <style>
    /* CSS Reset and accessibility improvements */
    * {
        box-sizing: border-box;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {display: none;}
    
    /* Responsive container with fluid design */
    .main .block-container {
        padding: clamp(1rem, 3vw, 2rem);
        max-width: 100%;
        margin: 0 auto;
    }
    
    /* Fluid typography system */
    .main-header {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 300;
        color: #1e1e1e;
        margin-bottom: clamp(0.5rem, 2vw, 1rem);
        text-align: center;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-size: clamp(1rem, 3vw, 1.3rem);
        font-weight: 400;
        color: #666;
        text-align: center;
        margin-bottom: clamp(1.5rem, 4vw, 2.5rem);
        padding: 0 clamp(1rem, 3vw, 2rem);
        line-height: 1.5;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .section-header {
        font-size: clamp(1.1rem, 2.5vw, 1.3rem);
        font-weight: 600;
        color: #2c3e50;
        margin: clamp(2rem, 5vw, 3rem) 0 clamp(1rem, 2vw, 1.5rem) 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e9ecef;
        position: relative;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: #1976d2;
    }
    
    /* Enhanced status containers */
    .status-success, .status-info, .status-warning, .status-error {
        border-left: 4px solid;
        padding: clamp(0.75rem, 2vw, 1rem);
        margin: clamp(0.5rem, 1vw, 1rem) 0;
        border-radius: 0 8px 8px 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    
    .status-success {
        background: linear-gradient(135deg, #f0f9f0 0%, #e8f5e8 100%);
        border-left-color: #4caf50;
        color: #2e7d32;
    }
    
    .status-info {
        background: linear-gradient(135deg, #f0f7ff 0%, #e3f2fd 100%);
        border-left-color: #2196f3;
        color: #1565c0;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fffaf0 0%, #fff3e0 100%);
        border-left-color: #ff9800;
        color: #ef6c00;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left-color: #f44336;
        color: #c62828;
    }
    
    /* Copy success message styling */
    .copy-success {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f9f0 100%);
        border: 2px solid #4caf50;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #2e7d32;
        font-weight: 600;
        text-align: center;
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive metrics grid */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: clamp(0.75rem, 2vw, 1.5rem);
        margin: clamp(1rem, 3vw, 2rem) 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        min-height: clamp(100px, 15vw, 120px);
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1976d2, #42a5f5);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    .metric-number {
        font-size: clamp(1.8rem, 5vw, 2.5rem);
        font-weight: 700;
        color: #1976d2;
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: clamp(0.8rem, 2vw, 0.95rem);
        color: #546e7a;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    
    /* Enhanced form elements */
    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        min-height: 52px;
        font-size: clamp(0.9rem, 2.5vw, 1rem);
        padding: clamp(0.75rem, 2vw, 1rem) clamp(1rem, 3vw, 1.5rem);
        text-transform: none;
        letter-spacing: 0.02em;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #e9ecef;
        min-height: 56px;
        font-size: clamp(0.95rem, 2.5vw, 1.1rem);
        padding: clamp(1rem, 2.5vw, 1.25rem);
        transition: all 0.3s ease;
        font-family: 'SF Pro Text', -apple-system, system-ui, sans-serif;
        line-height: 1.4;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus {
        border-color: #1976d2;
        box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
        outline: none;
    }
    
    .stTextArea > div > div > textarea {
        line-height: 1.6;
        resize: vertical;
        min-height: clamp(220px, 30vh, 320px);
        font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    }
    
    /* Enhanced selectbox styling for better visibility */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    .stSelectbox > div > div > div {
        min-height: 100px !important;
        display: flex;
        align-items: center;
        padding: clamp(1.75rem, 4vw, 2rem) !important;
        font-size: clamp(1.1rem, 3vw, 1.4rem) !important;
        line-height: 1.6 !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox dropdown styling */
    .stSelectbox > div > div > div > div {
        padding: clamp(1.25rem, 3vw, 1.5rem) !important;
        font-size: clamp(1rem, 2.8vw, 1.2rem) !important;
        min-height: 80px !important;
        display: flex;
        align-items: center;
        line-height: 1.5 !important;
    }
    
    /* Ensure selectbox text is fully visible */
    .stSelectbox label {
        font-size: clamp(1.1rem, 3vw, 1.3rem) !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Selectbox input container */
    .stSelectbox > div {
        min-height: 100px;
    }
    
    /* Make sure selected value text is prominent */
    .stSelectbox > div > div > div[data-baseweb="select"] {
        min-height: 100px !important;
        font-size: clamp(1.1rem, 3vw, 1.4rem) !important;
        font-weight: 600 !important;
        padding: clamp(1.75rem, 4vw, 2rem) !important;
    }
    
    /* Selectbox arrow and interactive elements */
    .stSelectbox > div > div > div > div > svg {
        width: clamp(20px, 4vw, 28px) !important;
        height: clamp(20px, 4vw, 28px) !important;
    }
    
    /* Enhanced code blocks */
    .stCodeBlock {
        font-size: clamp(0.8rem, 2vw, 0.9rem);
        line-height: 1.6;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stCodeBlock > div {
        border-radius: 8px;
        max-height: clamp(300px, 40vh, 500px);
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: #cbd5e0 #f7fafc;
    }
    
    /* Enhanced expander styling */
    .streamlit-expanderHeader {
        font-size: clamp(1rem, 2.5vw, 1.1rem) !important;
        font-weight: 600 !important;
        padding: clamp(1rem, 2vw, 1.25rem) !important;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #dee2e6 !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%) !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #dee2e6 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: clamp(1rem, 2vw, 1.5rem) !important;
        background: #ffffff !important;
    }
    
    /* Responsive dividers */
    .divider {
        margin: clamp(2rem, 5vw, 3rem) 0;
        border-bottom: 1px solid #e9ecef;
        position: relative;
    }
    
    .divider::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 1px;
        background: #1976d2;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.75rem;
        }
        
        .metrics-container {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .metric-card {
            min-height: 90px;
            padding: 1rem;
        }
        
        .section-header {
            margin: 1.5rem 0 1rem 0;
            font-size: 1.1rem;
            text-align: left;
        }
        
        .stCodeBlock > div {
            max-height: 250px;
        }
        
        .stColumns {
            flex-direction: column;
        }
        
        .stColumns > div {
            width: 100% !important;
            margin-bottom: 0.75rem;
        }
        
        /* Mobile form element optimizations */
        .stButton > button,
        .stDownloadButton > button {
            min-height: 56px;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            padding: 1rem 1.25rem;
        }
        
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            min-height: 60px;
            font-size: 1.1rem;
            padding: 1.25rem;
        }
        
        .stSelectbox > div > div > div {
            min-height: 120px !important;
            font-size: 1.4rem !important;
            padding: 2rem !important;
            font-weight: 700 !important;
        }
        
        .stSelectbox > div > div > div > div {
            min-height: 90px !important;
            padding: 1.75rem !important;
            font-size: 1.3rem !important;
        }
    }
    
    /* Tablet and desktop optimizations */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding: 1.5rem 2rem;
        }
        
        .metrics-container {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .metric-card {
            min-height: 110px;
        }
    }
    
    @media (min-width: 1200px) {
        .main .block-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .metrics-container {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    
    @media (min-width: 1600px) {
        .main .block-container {
            max-width: 1400px;
        }
    }
    
    /* Touch device optimizations */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button,
        .stDownloadButton > button {
            min-height: 60px;
            font-size: 1.1rem;
            padding: 1.25rem 1.5rem;
        }
        
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            min-height: 130px !important;
            font-size: 18px !important;
            padding: 2.25rem !important;
            line-height: 1.6 !important;
            font-weight: 700 !important;
        }
        
        .stSelectbox > div > div > div > div {
            min-height: 100px !important;
            padding: 2rem !important;
            font-size: 17px !important;
        }
        
        .metric-card:hover,
        .stButton > button:hover {
            transform: none;
        }
    }
    
    /* Accessibility and preference support */
    @media (prefers-contrast: high) {
        .metric-card {
            border: 2px solid #000;
        }
        
        .status-success, .status-info, .status-warning, .status-error {
            border-left-width: 6px;
        }
        
        .stButton > button {
            border: 2px solid currentColor;
        }
    }
    
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
        
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .metric-card:hover {
            transform: none;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #f8f9fa;
        }
        
        .sub-header {
            color: #adb5bd;
        }
        
        .section-header {
            color: #e9ecef;
            border-bottom-color: #495057;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #343a40 0%, #495057 100%);
            color: #f8f9fa;
            border-color: #495057;
        }
        
        .metric-number {
            color: #74c0fc;
        }
        
        .metric-label {
            color: #adb5bd;
        }
        
        .status-success {
            background: linear-gradient(135deg, #1e3a2e 0%, #2d5a3d 100%);
            color: #51cf66;
        }
        
        .status-info {
            background: linear-gradient(135deg, #1e2a3a 0%, #2d3748 100%);
            color: #74c0fc;
        }
        
        .status-warning {
            background: linear-gradient(135deg, #3a2e1e 0%, #5a4d2d 100%);
            color: #ffd43b;
        }
        
        .status-error {
            background: linear-gradient(135deg, #3a1e1e 0%, #5a2d2d 100%);
            color: #ff8787;
        }
    }
    
    /* Focus indicators */
    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible,
    .stTextInput > div > div > input:focus-visible,
    .stTextArea > div > div > textarea:focus-visible,
    .stSelectbox > div > div > div:focus-visible {
        outline: 3px solid #1976d2;
        outline-offset: 2px;
    }
    
    /* Print styles */
    @media print {
        .stButton, .stDownloadButton {
            display: none;
        }
        
        .metric-card {
            break-inside: avoid;
        }
        
        .section-header {
            break-after: avoid;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def get_current_time_formatted(company_timezone="America/New_York"):
    """Get current time in specified timezone formatted as required"""
    try:
        if company_timezone not in available_timezones():
            logger.warning(f"Unknown timezone: {company_timezone}, falling back to America/New_York")
            company_timezone = "America/New_York"
        tz = ZoneInfo(company_timezone)
    except Exception as e:
        logger.warning(f"Error with timezone {company_timezone}, falling back to America/New_York: {e}")
        company_timezone = "America/New_York"
        tz = ZoneInfo("America/New_York")
    
    current_time = datetime.now(tz)
    return current_time.strftime("%Y-%m-%dT%H:%M:%S")

def parse_yaml_content(yaml_content):
    """Parse YAML content and extract relevant information"""
    try:
        data = yaml.safe_load(yaml_content)
        return data
    except yaml.YAMLError as e:
        st.error(f"Invalid YAML format: {e}")
        return None
    except Exception as e:
        st.error(f"Processing error: {e}")
        return None

def extract_agents_info(data):
    """Extract agents information from parsed YAML"""
    if not data or 'agents' not in data:
        return None
    
    agents_info = []
    for agent in data['agents']:
        if 'name' in agent and 'system_prompt' in agent:
            agents_info.append({
                'name': agent['name'],
                'model_name': agent.get('model_name', 'Not specified'),
                'system_prompt': agent['system_prompt']
            })
    
    return agents_info

def extract_global_template(data):
    """Extract global system prompt template"""
    if not data:
        return None
    return data.get('global_system_prompt_template', None)

def detect_injectable_variables(template):
    """Detect variables in {variable_name} format, excluding only active_agent_prompt"""
    if not template:
        return []
    
    variables = re.findall(r'\{([^}]+)\}', template)
    # Only exclude active_agent_prompt, allow 'now' to be manually selected
    excluded_vars = {'active_agent_prompt'}
    injectable_vars = [var for var in variables if var not in excluded_vars]
    
    return list(set(injectable_vars))

def validate_phone_number(phone):
    """Validate that phone number contains only digits and common separators"""
    if not phone:
        return False
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    return cleaned.isdigit() and len(cleaned) >= 10

def inject_variables_into_template(template, variables_dict, agent_prompt):
    """Inject all variables into the template"""
    result = template
    
    # Replace {active_agent_prompt} with the specific agent's prompt
    result = result.replace('{active_agent_prompt}', agent_prompt)
    
    # Replace all user-provided variables (including 'now' if provided)
    for var_name, var_value in variables_dict.items():
        result = result.replace('{' + var_name + '}', str(var_value))
    
    return result

def determine_variable_type(var_name):
    """Determine the type of variable based on its name"""
    var_lower = var_name.lower()
    # Special handling for 'now' variable
    if var_name.lower() == 'now':
        return 'time'
    elif any(phone_word in var_lower for phone_word in ['phone', 'number', 'tel', 'mobile', 'cell']):
        return 'phone'
    elif any(time_word in var_lower for time_word in ['time', 'date', 'timestamp', 'when', 'datetime']):
        return 'time'
    else:
        return 'text'

def render_variable_input(var_name):
    """Render responsive variable input with ONLY preloaded options"""
    var_type = determine_variable_type(var_name)
    st.markdown(f"**{var_name.replace('_', ' ').title()}**")
    
    if var_type == 'phone':
        # Phone number selection - ONLY preloaded options
        phone_options = ["Choose a phone number..."] + PRELOADED_VALUES['phone_numbers']
        selected_phone = st.selectbox(
            "",
            options=phone_options,
            key=f"phone_{var_name}",
            label_visibility="collapsed",
            help="Select from available phone numbers",
            format_func=lambda x: x if x == "Choose a phone number..." else f"📞 {x}"
        )
        
        # Validation message right after selectbox (no spacing)
        if selected_phone != "Choose a phone number...":
            st.markdown(f'<div class="status-success" style="margin-top: 0.25rem; margin-bottom: 0.5rem;">✅ Phone number selected: <strong>{selected_phone}</strong></div>', unsafe_allow_html=True)
            return selected_phone, True
        else:
            st.markdown('<div class="status-warning" style="margin-top: 0.25rem; margin-bottom: 0.5rem;">⚠️ Please select a phone number</div>', unsafe_allow_html=True)
            return None, False
    
    elif var_type == 'time':
        # Time selection - ONLY preloaded options (including 'now' variable)
        time_options = ["Choose a timestamp..."] + PRELOADED_VALUES['time_formats']
        selected_time = st.selectbox(
            "",
            options=time_options,
            key=f"time_{var_name}",
            label_visibility="collapsed",
            help="Select from available timestamps",
            format_func=lambda x: x if x == "Choose a timestamp..." else f"🕒 {x}"
        )
        
        # Validation message right after selectbox (no spacing)
        if selected_time != "Choose a timestamp...":
            st.markdown(f'<div class="status-success" style="margin-top: 0.25rem; margin-bottom: 0.5rem;">✅ Timestamp selected: <strong>{selected_time}</strong></div>', unsafe_allow_html=True)
            return selected_time, True
        else:
            st.markdown('<div class="status-warning" style="margin-top: 0.25rem; margin-bottom: 0.5rem;">⚠️ Please select a timestamp</div>', unsafe_allow_html=True)
            return None, False
    
    else:
        # Text input for other variables
        value = st.text_input(
            "",
            key=f"text_{var_name}",
            label_visibility="collapsed",
            help=f"Enter value for {var_name.replace('_', ' ')}"
        )
        
        # Validation message right after input (no spacing)
        if value:
            st.markdown(f'<div class="status-success" style="margin-top: 0.25rem; margin-bottom: 0.5rem;">✅ Value entered: <strong>{value}</strong></div>', unsafe_allow_html=True)
            return value, True
        else:
            st.markdown('<div class="status-warning" style="margin-top: 0.25rem; margin-bottom: 0.5rem;">⚠️ This field is required</div>', unsafe_allow_html=True)
            return None, False

def render_metrics(agents_count, variables_count, has_template):
    """Render responsive metrics cards"""
    metrics_html = f"""
    <div class="metrics-container">
        <div class="metric-card">
            <div class="metric-number">{agents_count}</div>
            <div class="metric-label">Agents Found</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{variables_count}</div>
            <div class="metric-label">Variables</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{'✓' if has_template else '✗'}</div>
            <div class="metric-label">Global Template</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

def render_prompt_section(agent, complete_prompt, key_prefix=""):
    """Render responsive prompt section with improved copy functionality"""
    st.markdown(f"### 🤖 {agent['name'].replace('_', ' ').title()} Prompt")
    
    # Create unique session state key for copy feedback
    copy_key = f"copied_{key_prefix}_{agent['name']}"
    
    # Initialize copy feedback state if not exists
    if copy_key not in st.session_state:
        st.session_state[copy_key] = False
    
    # Responsive button layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Use a callback-based approach to avoid page refresh
        if st.button("📋 Copy", key=f"copy_{key_prefix}_{agent['name']}", use_container_width=True, help="Prepare prompt for copying"):
            st.session_state[copy_key] = True
    
    with col2:
        filename = f"{agent['name']}_complete_prompt.txt"
        st.download_button(
            label="💾 Download",
            data=complete_prompt,
            file_name=filename,
            mime="text/plain",
            key=f"download_{key_prefix}_{agent['name']}",
            use_container_width=True,
            type="secondary",
            help="Download prompt as text file"
        )
    
    # Show copy feedback without page refresh
    if st.session_state[copy_key]:
        st.markdown("""
        <div class="copy-success">
            ✅ <strong>Ready to Copy!</strong><br>
            📋 Select all text in the code block below (Ctrl+A) and copy (Ctrl+C)
        </div>
        """, unsafe_allow_html=True)
        
        # Reset the copy state after showing the message
        # Use a small button to dismiss the message
        if st.button("✓ Got it", key=f"dismiss_{copy_key}", help="Dismiss copy message"):
            st.session_state[copy_key] = False
            st.rerun()
    
    # Expandable prompt content
    with st.expander("📄 View Prompt Content", expanded=st.session_state.get(copy_key, False)):
        st.code(complete_prompt, language="text")
    
    st.markdown("---")

def preserve_session_state():
    """Preserve critical session state values"""
    # Store generated prompts to avoid regeneration
    if 'generated_prompts' not in st.session_state:
        st.session_state.generated_prompts = {}
    
    if 'variable_values' not in st.session_state:
        st.session_state.variable_values = {}

def main():
    # Enhanced page configuration
    st.set_page_config(
        page_title="Agent Prompt Processor",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Transform YAML configurations into complete agent prompts with professional responsive design."
        }
    )
    
    # Load enhanced responsive CSS
    load_responsive_css()
    
    # Preserve session state
    preserve_session_state()
    
    # Header with enhanced typography
    st.markdown('<h1 class="main-header">Agent Prompt Processor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform YAML configurations into complete agent prompts with professional responsive design and preloaded values</p>', unsafe_allow_html=True)
    
    # Initialize session state with proper defaults
    session_defaults = {
        'yaml_processed': False,
        'data': None,
        'agents_info': None,
        'global_template': None,
        'injectable_vars': [],
        'yaml_input': "",
        'prompts_generated': False
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Enhanced input section
    st.markdown('<div class="section-header">📄 YAML Configuration</div>', unsafe_allow_html=True)
    
    # Responsive clear button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🗑️ Clear", help="Clear the YAML input field and reset all data"):
            # Clear all session state
            for key in session_defaults:
                st.session_state[key] = session_defaults[key]
            st.session_state.generated_prompts = {}
            st.session_state.variable_values = {}
            # Clear all copy states
            keys_to_remove = [k for k in st.session_state.keys() if k.startswith('copied_')]
            for key in keys_to_remove:
                del st.session_state[key]
            st.rerun()
    
    # Enhanced text area with better UX
    yaml_input = st.text_area(
        "",
        height=250,
        placeholder="Paste your YAML configuration here...\n\nExample:\nglobal_system_prompt_template: |\n  You are {agent_name} at {company_name}.\n  Current time: {now}\n  {active_agent_prompt}\n\nagents:\n  - name: assistant\n    system_prompt: Help users with their questions.",
        label_visibility="collapsed",
        value=st.session_state.yaml_input,
        key="yaml_text_area",
        help="Paste your complete YAML configuration. The processor will detect variables and agents automatically."
    )
    
    # Update session state
    if yaml_input != st.session_state.yaml_input:
        st.session_state.yaml_input = yaml_input
    
    # Responsive process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button("Process Configuration", type="primary", use_container_width=True)
    
    # Processing logic with enhanced feedback
    if process_button:
        if st.session_state.yaml_input.strip():
            with st.spinner("Processing YAML configuration..."):
                data = parse_yaml_content(st.session_state.yaml_input)
            
            if data:
                st.session_state.data = data
                st.session_state.global_template = extract_global_template(data)
                st.session_state.agents_info = extract_agents_info(data)
                st.session_state.injectable_vars = detect_injectable_variables(st.session_state.global_template)
                st.session_state.yaml_processed = True
                st.session_state.prompts_generated = False  # Reset prompts generated flag
                
                st.markdown('<div class="status-success">✓ Configuration processed successfully</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-warning">⚠ Please provide YAML configuration</div>', unsafe_allow_html=True)
    
    # Enhanced results display
    if st.session_state.yaml_processed and st.session_state.data:
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Responsive metrics display
        if st.session_state.agents_info:
            render_metrics(
                len(st.session_state.agents_info),
                len(st.session_state.injectable_vars),
                bool(st.session_state.global_template)
            )
        
        # Enhanced agents overview
        if st.session_state.agents_info:
            st.markdown('<div class="section-header">🤖 Detected Agents</div>', unsafe_allow_html=True)
            
            for agent in st.session_state.agents_info:
                with st.expander(f"**{agent['name'].replace('_', ' ').title()}** • {agent['model_name']}", expanded=False):
                    st.code(agent['system_prompt'], language="text")
        
        # Enhanced variables input section with preloaded options only
        if st.session_state.injectable_vars:
            st.markdown('<div class="section-header">⚙️ Configuration Variables</div>', unsafe_allow_html=True)
            st.markdown('<div class="status-info">Please select values for the detected variables from the preloaded options below. The "now" variable can be manually selected from timestamps.</div>', unsafe_allow_html=True)
            
            variable_values = {}
            all_valid = True
            
            # Process variables with enhanced validation and preloaded options
            for var in st.session_state.injectable_vars:
                value, is_valid = render_variable_input(var)
                
                if is_valid and value:
                    variable_values[var] = value
                    st.session_state.variable_values[var] = value
                else:
                    all_valid = False
                
                # Reduced spacing between variable sections
                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
            
            # Enhanced generate section
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                generate_button = st.button(
                    "Generate Prompts", 
                    type="primary", 
                    disabled=not all_valid,
                    use_container_width=True,
                    help="Generate complete prompts for all agents with injected variables"
                )
            
            # Enhanced prompt generation
            if generate_button and all_valid:
                st.session_state.prompts_generated = True
                st.session_state.generated_prompts = {}
                
                # Generate and store prompts
                for agent in st.session_state.agents_info:
                    complete_prompt = inject_variables_into_template(
                        st.session_state.global_template,
                        variable_values,
                        agent['system_prompt']
                    )
                    st.session_state.generated_prompts[agent['name']] = complete_prompt
        
        else:
            # No variables case with enhanced UX
            st.markdown('<div class="status-info">No variables detected - ready to generate prompts</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Generate Prompts", type="primary", use_container_width=True):
                    st.session_state.prompts_generated = True
                    st.session_state.generated_prompts = {}
                    
                    # Generate and store prompts
                    for agent in st.session_state.agents_info:
                        complete_prompt = inject_variables_into_template(
                            st.session_state.global_template,
                            {},
                            agent['system_prompt']
                        )
                        st.session_state.generated_prompts[agent['name']] = complete_prompt
        
        # Display generated prompts if they exist
        if st.session_state.prompts_generated and st.session_state.generated_prompts:
            st.markdown('<div class="section-header">📋 Generated Prompts</div>', unsafe_allow_html=True)
            
            for agent in st.session_state.agents_info:
                if agent['name'] in st.session_state.generated_prompts:
                    complete_prompt = st.session_state.generated_prompts[agent['name']]
                    key_prefix = "vars" if st.session_state.injectable_vars else "no_vars"
                    render_prompt_section(agent, complete_prompt, key_prefix)
        
        # Enhanced footer with timestamp
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        current_time = get_current_time_formatted()
        st.markdown(f'<div class="status-info">Current timestamp: {current_time} (America/New_York)</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
