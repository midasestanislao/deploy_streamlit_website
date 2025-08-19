import streamlit as st
import re
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Custom CSS for professional styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Responsive base */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Typography - Responsive */
    .main-header {
        font-size: clamp(1.8rem, 4vw, 2.5rem);
        font-weight: 300;
        color: #1e1e1e;
        margin-bottom: 0.5rem;
        text-align: center;
        line-height: 1.2;
    }
    
    .sub-header {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        font-weight: 400;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        padding: 0 1rem;
        line-height: 1.4;
    }
    
    .section-header {
        font-size: clamp(1rem, 2vw, 1.1rem);
        font-weight: 500;
        color: #333;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Status containers - Responsive */
    .status-success, .status-info, .status-warning {
        border-left: 4px solid;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0 4px 4px 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .status-success {
        background: #f0f9f0;
        border-left-color: #4caf50;
    }
    
    .status-info {
        background: #f5f5f5;
        border-left-color: #2196f3;
    }
    
    .status-warning {
        background: #fff3e0;
        border-left-color: #ff9800;
    }
    
    /* Metric cards - Responsive grid */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-number {
        font-size: clamp(1.5rem, 4vw, 2rem);
        font-weight: 600;
        color: #1976d2;
        line-height: 1;
    }
    
    .metric-label {
        font-size: clamp(0.8rem, 2vw, 0.9rem);
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }
    
    .divider {
        margin: 2rem 0;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Button styling - Mobile friendly */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        border: none;
        font-weight: 500;
        transition: all 0.2s;
        min-height: 44px; /* Touch-friendly minimum */
        font-size: clamp(0.9rem, 2vw, 1rem);
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Download button specific */
    .stDownloadButton > button {
        width: 100%;
        border-radius: 6px;
        border: none;
        font-weight: 500;
        transition: all 0.2s;
        min-height: 44px;
        font-size: clamp(0.9rem, 2vw, 1rem);
        padding: 0.5rem 1rem;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Input styling - Responsive */
    .stTextInput > div > div > input {
        border-radius: 6px;
        min-height: 44px;
        font-size: clamp(0.9rem, 2vw, 1rem);
        padding: 0.5rem 0.75rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        font-size: clamp(0.9rem, 2vw, 1rem);
        line-height: 1.4;
        padding: 0.75rem;
    }
    
    /* Code blocks - Responsive */
    .stCodeBlock {
        font-size: clamp(0.8rem, 1.5vw, 0.9rem);
        line-height: 1.4;
    }
    
    .stCodeBlock > div {
        border-radius: 6px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Expander styling - Mobile friendly */
    .streamlit-expanderHeader {
        font-size: clamp(0.95rem, 2vw, 1.1rem) !important;
        font-weight: 500 !important;
        padding: 0.75rem 0 !important;
    }
    
    .streamlit-expanderContent {
        border: none !important;
        padding: 0.5rem 0 !important;
    }
    
    /* Mobile specific adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .metric-card {
            margin: 0.25rem 0;
            padding: 0.75rem;
        }
        
        .section-header {
            margin: 1rem 0 0.75rem 0;
            font-size: 1rem;
        }
        
        .stCodeBlock > div {
            max-height: 300px;
        }
        
        /* Stack columns on mobile */
        .stColumns {
            flex-direction: column;
        }
        
        .stColumns > div {
            width: 100% !important;
            margin-bottom: 0.5rem;
        }
    }
    
    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        .metric-card {
            min-height: 90px;
        }
    }
    
    /* Large screen adjustments */
    @media (min-width: 1200px) {
        .main .block-container {
            max-width: 1200px;
            margin: 0 auto;
        }
    }
    
    /* Touch improvements */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button,
        .stDownloadButton > button {
            min-height: 48px; /* Larger touch targets */
            font-size: 1rem;
        }
        
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            min-height: 48px;
            font-size: 16px; /* Prevents zoom on iOS */
        }
    }
    
    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        .stButton > button,
        .stDownloadButton > button {
            transition: none;
        }
        
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: none;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #e1e1e1;
        }
        
        .sub-header {
            color: #b0b0b0;
        }
        
        .section-header {
            color: #d1d1d1;
            border-bottom-color: #444;
        }
        
        .metric-card {
            background: #2d2d2d;
            color: #e1e1e1;
        }
        
        .metric-number {
            color: #64b5f6;
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
    """Detect variables in {variable_name} format, excluding specific ones"""
    if not template:
        return []
    
    variables = re.findall(r'\{([^}]+)\}', template)
    excluded_vars = {'active_agent_prompt', 'now'}
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
    
    current_time = get_current_time_formatted()
    result = result.replace('{now}', current_time)
    result = result.replace('{active_agent_prompt}', agent_prompt)
    
    for var_name, var_value in variables_dict.items():
        result = result.replace('{' + var_name + '}', str(var_value))
    
    return result

def main():
    st.set_page_config(
        page_title="Agent Prompt Processor",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Header
    st.markdown('<h1 class="main-header">Agent Prompt Processor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform YAML configurations into complete agent prompts</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'yaml_processed' not in st.session_state:
        st.session_state.yaml_processed = False
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'agents_info' not in st.session_state:
        st.session_state.agents_info = None
    if 'global_template' not in st.session_state:
        st.session_state.global_template = None
    if 'injectable_vars' not in st.session_state:
        st.session_state.injectable_vars = []
    
    # Input section
    st.markdown('<div class="section-header">📄 YAML Configuration</div>', unsafe_allow_html=True)
    
    # Clear button
    col1, col2, col3 = st.columns([5, 1, 5])
    with col2:
        if st.button("🗑️ Clear", help="Clear the YAML input field"):
            st.session_state.yaml_input = ""
            st.session_state.yaml_processed = False
            st.session_state.data = None
            st.session_state.agents_info = None
            st.session_state.global_template = None
            st.session_state.injectable_vars = []
            st.rerun()
    
    # Initialize yaml_input in session state if not exists
    if 'yaml_input' not in st.session_state:
        st.session_state.yaml_input = ""
    
    yaml_input = st.text_area(
        "",
        height=250,
        placeholder="Paste your YAML configuration here...",
        label_visibility="collapsed",
        value=st.session_state.yaml_input,
        key="yaml_text_area"
    )
    
    # Update session state when text area changes
    if yaml_input != st.session_state.yaml_input:
        st.session_state.yaml_input = yaml_input
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button("Process Configuration", type="primary")
    
    if process_button:
        if st.session_state.yaml_input.strip():
            with st.spinner("Processing..."):
                data = parse_yaml_content(st.session_state.yaml_input)
            
            if data:
                st.session_state.data = data
                st.session_state.global_template = extract_global_template(data)
                st.session_state.agents_info = extract_agents_info(data)
                st.session_state.injectable_vars = detect_injectable_variables(st.session_state.global_template)
                st.session_state.yaml_processed = True
                
                st.markdown('<div class="status-success">✓ Configuration processed successfully</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-warning">⚠ Please provide YAML configuration</div>', unsafe_allow_html=True)
    
    # Show processed information
    if st.session_state.yaml_processed and st.session_state.data:
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Metrics
        if st.session_state.agents_info:
            # Responsive columns for metrics
            if st.session_state.get('mobile_view', False):
                # Single column for mobile
                for i, (label, value) in enumerate([
                    ("Agents Found", len(st.session_state.agents_info)),
                    ("Variables", len(st.session_state.injectable_vars)),
                    ("Global Template", '✓' if st.session_state.global_template else '✗')
                ]):
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-number">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                # Three columns for desktop/tablet
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-number">{len(st.session_state.agents_info)}</div>
                        <div class="metric-label">Agents Found</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-number">{len(st.session_state.injectable_vars)}</div>
                        <div class="metric-label">Variables</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-number">{'✓' if st.session_state.global_template else '✗'}</div>
                        <div class="metric-label">Global Template</div>
                    </div>
                    ''', unsafe_allow_html=True)
        
        # Agents overview
        if st.session_state.agents_info:
            st.markdown('<div class="section-header">🤖 Detected Agents</div>', unsafe_allow_html=True)
            
            for agent in st.session_state.agents_info:
                with st.expander(f"**{agent['name'].replace('_', ' ').title()}** • {agent['model_name']}", expanded=False):
                    st.code(agent['system_prompt'], language="text")
        
        # Variables input
        if st.session_state.injectable_vars:
            st.markdown('<div class="section-header">⚙️ Configuration Variables</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="status-info">Please provide values for the detected variables</div>', unsafe_allow_html=True)
            
            variable_values = {}
            all_valid = True
            
            for var in st.session_state.injectable_vars:
                st.markdown(f"**{var.replace('_', ' ').title()}**")
                
                if 'phone' in var.lower():
                    # Responsive layout for phone validation
                    value = st.text_input(
                        "",
                        key=f"var_{var}",
                        placeholder="e.g., +1-555-123-4567",
                        label_visibility="collapsed"
                    )
                    
                    # Validation feedback
                    if value:
                        if validate_phone_number(value):
                            st.success("✅ Valid phone number")
                            variable_values[var] = value
                        else:
                            st.error("❌ Invalid phone number - only numbers and separators allowed")
                            all_valid = False
                    else:
                        st.warning("⚠️ Phone number required")
                        all_valid = False
                else:
                    value = st.text_input(
                        "",
                        key=f"var_{var}",
                        label_visibility="collapsed"
                    )
                    if value:
                        variable_values[var] = value
                    else:
                        st.warning("⚠️ This field is required")
                        all_valid = False
                
                # Add spacing between fields
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Generate prompts
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                generate_button = st.button("Generate Prompts", type="primary", disabled=not all_valid)
            
            if generate_button and all_valid:
                st.markdown('<div class="section-header">📋 Generated Prompts</div>', unsafe_allow_html=True)
                
                for agent in st.session_state.agents_info:
                    complete_prompt = inject_variables_into_template(
                        st.session_state.global_template,
                        variable_values,
                        agent['system_prompt']
                    )
                    
                    # Agent prompt section
                    st.markdown(f"### 🤖 {agent['name'].replace('_', ' ').title()} Prompt")
                    
                    # Action buttons ABOVE the prompt
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button("📋 Copy", key=f"copy_{agent['name']}", use_container_width=True):
                            st.success("✅ Ready to copy!")
                    
                    with col2:
                        filename = f"{agent['name']}_complete_prompt.txt"
                        st.download_button(
                            label="💾 Download",
                            data=complete_prompt,
                            file_name=filename,
                            mime="text/plain",
                            key=f"download_{agent['name']}",
                            use_container_width=True,
                            type="secondary"
                        )
                    
                    # Show the prompt in an expander
                    with st.expander("📄 View Prompt Content", expanded=False):
                        st.code(complete_prompt, language="text")
                    
                    st.markdown("---")  # Separator between agents
        
        else:
            # No variables case
            st.markdown('<div class="status-info">No variables detected - ready to generate prompts</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Generate Prompts", type="primary"):
                    st.markdown('<div class="section-header">📋 Generated Prompts</div>', unsafe_allow_html=True)
                    
                    for agent in st.session_state.agents_info:
                        complete_prompt = inject_variables_into_template(
                            st.session_state.global_template,
                            {},
                            agent['system_prompt']
                        )
                        
                        with st.expander(f"**{agent['name'].replace('_', ' ').title()} Prompt**", expanded=True):
                            st.code(complete_prompt, language="text")
                            
                            st.markdown("**Actions:**")
                            
                            # Responsive button layout
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                if st.button("📋 Copy to Clipboard", key=f"copy_no_vars_{agent['name']}", use_container_width=True):
                                    st.success("✅ Ready to copy!")
                                    st.info("💡 Select all text above and copy")
                            
                            with col2:
                                filename = f"{agent['name']}_complete_prompt.txt"
                                st.download_button(
                                    label="💾 Download Prompt",
                                    data=complete_prompt,
                                    file_name=filename,
                                    mime="text/plain",
                                    key=f"download_no_vars_{agent['name']}",
                                    use_container_width=True
                                )
        
        # Footer info
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        current_time = get_current_time_formatted()
        st.markdown(f'<div class="status-info">Current timestamp: {current_time} (America/New_York)</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
# import streamlit as st
# import yaml
# import re
# from datetime import datetime
# from zoneinfo import ZoneInfo, available_timezones
# import logging

# # Set up logging
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)

# # Custom CSS for professional styling
# def load_custom_css():
#     st.markdown("""
#     <style>
#     /* Hide Streamlit default elements */
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     .stDeployButton {display:none;}
    
#     /* Custom styling */
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: 300;
#         color: #1e1e1e;
#         margin-bottom: 0.5rem;
#         text-align: center;
#     }
    
#     .sub-header {
#         font-size: 1.2rem;
#         font-weight: 400;
#         color: #666;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
    
#     .section-header {
#         font-size: 1.1rem;
#         font-weight: 500;
#         color: #333;
#         margin: 1.5rem 0 1rem 0;
#         padding-bottom: 0.5rem;
#         border-bottom: 1px solid #e0e0e0;
#     }
    
#     .status-success {
#         background: #f0f9f0;
#         border-left: 4px solid #4caf50;
#         padding: 0.75rem;
#         margin: 0.5rem 0;
#         border-radius: 0 4px 4px 0;
#     }
    
#     .status-info {
#         background: #f5f5f5;
#         border-left: 4px solid #2196f3;
#         padding: 0.75rem;
#         margin: 0.5rem 0;
#         border-radius: 0 4px 4px 0;
#     }
    
#     .status-warning {
#         background: #fff3e0;
#         border-left: 4px solid #ff9800;
#         padding: 0.75rem;
#         margin: 0.5rem 0;
#         border-radius: 0 4px 4px 0;
#     }
    
#     .metric-card {
#         background: white;
#         padding: 1rem;
#         border-radius: 8px;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.1);
#         margin: 0.5rem 0;
#         text-align: center;
#     }
    
#     .metric-number {
#         font-size: 2rem;
#         font-weight: 600;
#         color: #1976d2;
#     }
    
#     .metric-label {
#         font-size: 0.9rem;
#         color: #666;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#     }
    
#     .divider {
#         margin: 2rem 0;
#         border-bottom: 1px solid #e0e0e0;
#     }
    
#     /* Button styling */
#     .stButton > button {
#         width: 100%;
#         border-radius: 6px;
#         border: none;
#         font-weight: 500;
#         transition: all 0.2s;
#     }
    
#     .stButton > button:hover {
#         transform: translateY(-1px);
#         box-shadow: 0 4px 8px rgba(0,0,0,0.15);
#     }
    
#     /* Input styling */
#     .stTextInput > div > div > input {
#         border-radius: 6px;
#     }
    
#     .stTextArea > div > div > textarea {
#         border-radius: 6px;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# def get_current_time_formatted(company_timezone="America/New_York"):
#     """Get current time in specified timezone formatted as required"""
#     try:
#         if company_timezone not in available_timezones():
#             logger.warning(f"Unknown timezone: {company_timezone}, falling back to America/New_York")
#             company_timezone = "America/New_York"
#         tz = ZoneInfo(company_timezone)
#     except Exception as e:
#         logger.warning(f"Error with timezone {company_timezone}, falling back to America/New_York: {e}")
#         company_timezone = "America/New_York"
#         tz = ZoneInfo("America/New_York")
    
#     current_time = datetime.now(tz)
#     return current_time.strftime("%Y-%m-%dT%H:%M:%S")

# def parse_yaml_content(yaml_content):
#     """Parse YAML content and extract relevant information"""
#     try:
#         data = yaml.safe_load(yaml_content)
#         return data
#     except yaml.YAMLError as e:
#         st.error(f"Invalid YAML format: {e}")
#         return None
#     except Exception as e:
#         st.error(f"Processing error: {e}")
#         return None

# def extract_agents_info(data):
#     """Extract agents information from parsed YAML"""
#     if not data or 'agents' not in data:
#         return None
    
#     agents_info = []
#     for agent in data['agents']:
#         if 'name' in agent and 'system_prompt' in agent:
#             agents_info.append({
#                 'name': agent['name'],
#                 'model_name': agent.get('model_name', 'Not specified'),
#                 'system_prompt': agent['system_prompt']
#             })
    
#     return agents_info

# def extract_global_template(data):
#     """Extract global system prompt template"""
#     if not data:
#         return None
#     return data.get('global_system_prompt_template', None)

# def detect_injectable_variables(template):
#     """Detect variables in {variable_name} format, excluding specific ones"""
#     if not template:
#         return []
    
#     variables = re.findall(r'\{([^}]+)\}', template)
#     excluded_vars = {'active_agent_prompt', 'now'}
#     injectable_vars = [var for var in variables if var not in excluded_vars]
    
#     return list(set(injectable_vars))

# def validate_phone_number(phone):
#     """Validate that phone number contains only digits and common separators"""
#     if not phone:
#         return False
#     cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
#     return cleaned.isdigit() and len(cleaned) >= 10

# def inject_variables_into_template(template, variables_dict, agent_prompt):
#     """Inject all variables into the template"""
#     result = template
    
#     current_time = get_current_time_formatted()
#     result = result.replace('{now}', current_time)
#     result = result.replace('{active_agent_prompt}', agent_prompt)
    
#     for var_name, var_value in variables_dict.items():
#         result = result.replace('{' + var_name + '}', str(var_value))
    
#     return result

# def main():
#     st.set_page_config(
#         page_title="Agent Prompt Processor",
#         page_icon="⚡",
#         layout="centered",
#         initial_sidebar_state="collapsed"
#     )
    
#     # Load custom CSS
#     load_custom_css()
    
#     # Header
#     st.markdown('<h1 class="main-header">Agent Prompt Processor</h1>', unsafe_allow_html=True)
#     st.markdown('<p class="sub-header">Transform YAML configurations into complete agent prompts</p>', unsafe_allow_html=True)
    
#     # Initialize session state
#     if 'yaml_processed' not in st.session_state:
#         st.session_state.yaml_processed = False
#     if 'data' not in st.session_state:
#         st.session_state.data = None
#     if 'agents_info' not in st.session_state:
#         st.session_state.agents_info = None
#     if 'global_template' not in st.session_state:
#         st.session_state.global_template = None
#     if 'injectable_vars' not in st.session_state:
#         st.session_state.injectable_vars = []
    
#     # Input section
#     st.markdown('<div class="section-header">📄 YAML Configuration</div>', unsafe_allow_html=True)
    
#     yaml_input = st.text_area(
#         "",
#         height=250,
#         placeholder="Paste your YAML configuration here...",
#         label_visibility="collapsed"
#     )
    
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         process_button = st.button("Process Configuration", type="primary")
    
#     if process_button:
#         if yaml_input.strip():
#             with st.spinner("Processing..."):
#                 data = parse_yaml_content(yaml_input)
            
#             if data:
#                 st.session_state.data = data
#                 st.session_state.global_template = extract_global_template(data)
#                 st.session_state.agents_info = extract_agents_info(data)
#                 st.session_state.injectable_vars = detect_injectable_variables(st.session_state.global_template)
#                 st.session_state.yaml_processed = True
                
#                 st.markdown('<div class="status-success">✓ Configuration processed successfully</div>', unsafe_allow_html=True)
#         else:
#             st.markdown('<div class="status-warning">⚠ Please provide YAML configuration</div>', unsafe_allow_html=True)
    
#     # Show processed information
#     if st.session_state.yaml_processed and st.session_state.data:
        
#         st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
#         # Metrics
#         if st.session_state.agents_info:
#             col1, col2, col3 = st.columns(3)
            
#             with col1:
#                 st.markdown(f'''
#                 <div class="metric-card">
#                     <div class="metric-number">{len(st.session_state.agents_info)}</div>
#                     <div class="metric-label">Agents Found</div>
#                 </div>
#                 ''', unsafe_allow_html=True)
            
#             with col2:
#                 st.markdown(f'''
#                 <div class="metric-card">
#                     <div class="metric-number">{len(st.session_state.injectable_vars)}</div>
#                     <div class="metric-label">Variables</div>
#                 </div>
#                 ''', unsafe_allow_html=True)
            
#             with col3:
#                 st.markdown(f'''
#                 <div class="metric-card">
#                     <div class="metric-number">{'✓' if st.session_state.global_template else '✗'}</div>
#                     <div class="metric-label">Global Template</div>
#                 </div>
#                 ''', unsafe_allow_html=True)
        
#         # Agents overview
#         if st.session_state.agents_info:
#             st.markdown('<div class="section-header">🤖 Detected Agents</div>', unsafe_allow_html=True)
            
#             for agent in st.session_state.agents_info:
#                 with st.expander(f"**{agent['name'].replace('_', ' ').title()}** • {agent['model_name']}", expanded=False):
#                     st.code(agent['system_prompt'], language="text")
        
#         # Variables input
#         if st.session_state.injectable_vars:
#             st.markdown('<div class="section-header">⚙️ Configuration Variables</div>', unsafe_allow_html=True)
            
#             st.markdown('<div class="status-info">Please provide values for the detected variables</div>', unsafe_allow_html=True)
            
#             variable_values = {}
#             all_valid = True
            
#             for var in st.session_state.injectable_vars:
#                 st.markdown(f"**{var.replace('_', ' ').title()}**")
                
#                 if 'phone' in var.lower():
#                     col1, col2 = st.columns([3, 1])
#                     with col1:
#                         value = st.text_input(
#                             "",
#                             key=f"var_{var}",
#                             placeholder="e.g., +1-555-123-4567",
#                             label_visibility="collapsed"
#                         )
#                     with col2:
#                         if value:
#                             if validate_phone_number(value):
#                                 st.success("Valid")
#                                 variable_values[var] = value
#                             else:
#                                 st.error("Invalid")
#                                 all_valid = False
#                         else:
#                             st.warning("Required")
#                             all_valid = False
#                 else:
#                     value = st.text_input(
#                         "",
#                         key=f"var_{var}",
#                         label_visibility="collapsed"
#                     )
#                     if value:
#                         variable_values[var] = value
#                     else:
#                         all_valid = False
            
#             # Generate prompts
#             st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
#             col1, col2, col3 = st.columns([1, 2, 1])
#             with col2:
#                 generate_button = st.button("Generate Prompts", type="primary", disabled=not all_valid)
            
#             if generate_button and all_valid:
#                 st.markdown('<div class="section-header">📋 Generated Prompts</div>', unsafe_allow_html=True)
                
#                 for agent in st.session_state.agents_info:
#                     complete_prompt = inject_variables_into_template(
#                         st.session_state.global_template,
#                         variable_values,
#                         agent['system_prompt']
#                     )
                    
#                     with st.expander(f"**{agent['name'].replace('_', ' ').title()} Prompt**", expanded=True):
#                         st.code(complete_prompt, language="text")
                        
#                         col1, col2 = st.columns(2)
#                         with col1:
#                             if st.button("📋 Copy", key=f"copy_{agent['name']}", use_container_width=True):
#                                 st.success("Ready to copy!")
#                         with col2:
#                             filename = f"{agent['name']}_prompt.txt"
#                             st.download_button(
#                                 "💾 Download",
#                                 data=complete_prompt,
#                                 file_name=filename,
#                                 mime="text/plain",
#                                 key=f"download_{agent['name']}",
#                                 use_container_width=True
#                             )
        
#         else:
#             # No variables case
#             st.markdown('<div class="status-info">No variables detected - ready to generate prompts</div>', unsafe_allow_html=True)
            
#             st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
#             col1, col2, col3 = st.columns([1, 2, 1])
#             with col2:
#                 if st.button("Generate Prompts", type="primary"):
#                     st.markdown('<div class="section-header">📋 Generated Prompts</div>', unsafe_allow_html=True)
                    
#                     for agent in st.session_state.agents_info:
#                         complete_prompt = inject_variables_into_template(
#                             st.session_state.global_template,
#                             {},
#                             agent['system_prompt']
#                         )
                        
#                         with st.expander(f"**{agent['name'].replace('_', ' ').title()} Prompt**", expanded=True):
#                             st.code(complete_prompt, language="text")
                            
#                             col1, col2 = st.columns(2)
#                             with col1:
#                                 if st.button("📋 Copy", key=f"copy_no_vars_{agent['name']}", use_container_width=True):
#                                     st.success("Ready to copy!")
#                             with col2:
#                                 filename = f"{agent['name']}_prompt.txt"
#                                 st.download_button(
#                                     "💾 Download",
#                                     data=complete_prompt,
#                                     file_name=filename,
#                                     mime="text/plain",
#                                     key=f"download_no_vars_{agent['name']}",
#                                     use_container_width=True
#                                 )
        
#         # Footer info
#         st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
#         current_time = get_current_time_formatted()
#         st.markdown(f'<div class="status-info">Current timestamp: {current_time} (America/New_York)</div>', unsafe_allow_html=True)

# if __name__ == "__main__":
#     main()
