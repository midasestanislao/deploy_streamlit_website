"""
Agent Prompt Processor with Enhanced Service Detection
A professional tool for parsing YAML configurations and extracting comprehensive service information.

Author: Development Team
Version: 3.0.0
License: MIT
"""

import streamlit as st

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Agent Prompt Processor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import re
import yaml
import logging
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from pathlib import Path
import platform

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VariableType(Enum):
    """Enumeration for variable types."""
    PHONE = "phone"
    TIME = "time"
    TEXT = "text"

@dataclass
class Agent:
    """Data class for agent information."""
    name: str
    model_name: str
    system_prompt: str

# ============================================================================
# ENHANCED DATA STRUCTURES FOR SERVICE DETECTION
# ============================================================================

@dataclass
class CompanyInfo:
    """Company and assistant information."""
    company_name: str = ""
    assistant_name: str = ""
    greeting: str = ""
    tagline: str = ""
    
@dataclass
class DispatchFee:
    """Dispatch fee structure."""
    service_type: str
    amount: str
    conditions: str = ""
    notes: str = ""

@dataclass
class SchedulingInfo:
    """Scheduling and hours information."""
    operating_days: List[str] = field(default_factory=list)
    total_hours: str = ""
    morning_slots: str = ""
    afternoon_slots: str = ""
    emergency_hours: str = ""
    
@dataclass
class MembershipBenefits:
    """Membership program benefits."""
    program_name: str = ""
    dispatch_fee: str = ""
    repair_discount: str = ""
    warranty: str = ""
    other_benefits: List[str] = field(default_factory=list)
    
@dataclass
class OperationalMetrics:
    """Company operational metrics."""
    same_day_resolution: str = ""
    call_ahead_notification: str = ""
    company_experience: str = ""
    customer_reviews: str = ""
    service_area: str = ""
    response_time: str = ""
    
@dataclass
class PaymentInfo:
    """Payment methods and terms."""
    accepted_methods: List[str] = field(default_factory=list)
    payment_plans: str = ""
    billing_terms: str = ""
    
@dataclass
class ServiceCategory:
    """Service category details."""
    name: str
    description: str = ""
    subcategories: List[str] = field(default_factory=list)
    
@dataclass
class SchedulingRule:
    """Critical scheduling or operational rule."""
    rule_type: str
    description: str
    priority: str = "normal"

@dataclass
class ExtractedServiceInfo:
    """Complete extracted service information."""
    company_info: CompanyInfo = field(default_factory=CompanyInfo)
    dispatch_fees: List[DispatchFee] = field(default_factory=list)
    scheduling: SchedulingInfo = field(default_factory=SchedulingInfo)
    membership: MembershipBenefits = field(default_factory=MembershipBenefits)
    metrics: OperationalMetrics = field(default_factory=OperationalMetrics)
    payment: PaymentInfo = field(default_factory=PaymentInfo)
    service_categories: List[ServiceCategory] = field(default_factory=list)
    scheduling_rules: List[SchedulingRule] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# ENHANCED PATTERN LIBRARY
# ============================================================================

class EnhancedPatternLibrary:
    """Comprehensive pattern definitions for service detection."""
    
    def __init__(self):
        # Company patterns
        self.COMPANY_PATTERNS = {
            'name': [
                r'(?:calling|working at|from|with)\s*["\']?([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s*(?:HVAC|Plumbing|Electric|Services?)?)["\']?',
                r'Thank you for calling\s+([^,\.]+)',
                r'Welcome to\s+([^,\.]+)',
            ],
            'assistant': [
                r'(?:This is|I\'m|My name is|representative named?|agent named?)\s+([A-Z][a-z]+)',
                r'([A-Z][a-z]+)\s+(?:speaking|here|at your service)',
                r'agent_greeting:.*?This is\s+([A-Z][a-z]+)',
            ],
            'greeting': [
                r'agent_greeting:\s*(.+?)(?:\n|$)',
                r'Thank you for calling.*?(?:This is\s+\w+.*?)?(?:\n|$)',
            ]
        }
        
        # Fee patterns - Enhanced for better detection
        self.FEE_PATTERNS = {
            'standard': [
                r'\$(\d+)\s*(?:dispatch|service call|service|visit)\s*fee',
                r'dispatch fee.*?\$(\d+)',
                r'\$(\d+).*?(?:for|covers?).*?(?:service|repair|diagnosis|cleaning|maintenance)',
                r'Service Call.*?\$(\d+)',
                r'(?:repair|cleaning|maintenance).*?\$(\d+)\s*dispatch',
            ],
            'emergency': [
                r'emergency.*?\$(\d+)',
                r'\$(\d+).*?emergency',
                r'Emergency Call.*?\$(\d+)',
            ],
            'estimate': [
                r'estimate.*?(?:FREE|free|no charge|\$(\d+))',
                r'(?:FREE|free|no charge|\$(\d+)).*?estimate',
                r'Estimate Visit.*?(?:FREE|\$(\d+))',
                r'(?:new installations?|upgrades?|renovations?).*?(?:FREE|\$(\d+))',
            ],
            'member': [
                r'(?:member|membership).*?(?:WAIVED|waived|no charge|free)',
                r'(?:WAIVED|waived|no charge|free).*?(?:member|membership)',
                r'(?:HEART|Fresh air)\s+Members?.*?(?:waived|free|no charge)',
            ],
            'multiple': [
                r'multiple issues.*?\$(\d+)',
                r'\$(\d+).*?covers everything.*?one visit',
            ]
        }
        
        # Scheduling patterns - Enhanced
        self.SCHEDULING_PATTERNS = {
            'days': [
                r'Monday.*?(?:through|to|-|–).*?Friday',
                r'Mon.*?(?:through|to|-|–).*?Fri',
                r'(?:Monday|Tuesday|Wednesday|Thursday|Friday)(?:\s*,\s*(?:Monday|Tuesday|Wednesday|Thursday|Friday))+',
                r'7\s*days\s*a\s*week',
                r'(?:weekdays|business days)',
            ],
            'hours': [
                r'(\d{1,2}:\d{2}\s*[AP]M).*?(?:to|-|–).*?(\d{1,2}:\d{2}\s*[AP]M)',
                r'(\d{1,2})\s*[AP]M.*?(?:to|-|–).*?(\d{1,2})\s*[AP]M',
            ],
            'slots': [
                r'(?:morning|Morning).*?(\d{1,2}:\d{2}\s*[AP]M).*?(?:to|-|–).*?(\d{1,2}:\d{2}\s*[AP]M)',
                r'(?:afternoon|Afternoon).*?(\d{1,2}:\d{2}\s*[AP]M).*?(?:to|-|–).*?(\d{1,2}:\d{2}\s*[AP]M)',
            ]
        }
        
        # Membership patterns - Enhanced
        self.MEMBERSHIP_PATTERNS = {
            'program_name': [
                r'([A-Z][A-Za-z]+)\s+(?:Member|Membership|Program|Club)',
                r'(?:Member|Membership)\s+(?:program|plan|club)\s+(?:called|named)\s+([A-Z][A-Za-z]+)',
                r'(?:HEART|Fresh air)\s+(?:Member|Membership)',
            ],
            'discount': [
                r'(\d+)%\s*(?:off|discount).*?(?:repair|service)',
                r'(?:repair|service).*?(\d+)%\s*(?:off|discount)',
                r'Members?.*?(?:receive|get|save)\s*(\d+)%',
            ],
            'warranty': [
                r'(?:lifetime|permanent|extended|unlimited).*?(?:parts.*?labor\s*)?warranty',
                r'warranty.*?(?:lifetime|permanent|extended|unlimited)',
            ],
            'benefits': [
                r'(?:waive|no|free).*?(?:dispatch|service).*?fee',
                r'(?:priority|preferred).*?(?:scheduling|service)',
                r'(?:annual|yearly).*?(?:inspection|tune-up|maintenance)',
                r'never pay.*?charge.*?(?:inspect|visit)',
            ]
        }
        
        # Metrics patterns - Enhanced
        self.METRICS_PATTERNS = {
            'experience': [
                r'(\d+)\+?\s*years?.*?(?:experience|serving|business|operation)',
                r'(?:over|more than)\s+(\d+)\s*years?',
                r'(?:established|founded|since).*?(\d{4})',
                r'serving.*?(?:for|over)\s*(\d+)\s*years?',
            ],
            'reviews': [
                r'(\d+[,\d]*)\+?\s*(?:five-star|5-star)?\s*reviews?',
                r'(?:over|more than)\s+(\d+[,\d]*)\s*(?:customer)?\s*reviews?',
                r'(?:earned|received)\s*(\d+[,\d]*)\+?\s*reviews?',
            ],
            'resolution_rate': [
                r'(\d+)\s*(?:out of|times out of)\s*(\d+)',
                r'(\d+)%\s*(?:same-day|first-visit)?\s*resolution',
                r'fix.*?same-day.*?(\d+)\s*(?:out of|times)',
            ],
            'notification': [
                r'(\d+)[-–](\d+)\s*minutes?\s*(?:before|ahead|prior)',
                r'(?:call|notify).*?(\d+).*?minutes?\s*(?:before|ahead)',
                r'call.*?ahead.*?(\d+)[-–]?(\d*)\s*minutes?',
            ],
            'service_area': [
                r'(?:serving|service area|coverage).*?([A-Za-z\s]+(?:and|&)\s*(?:surrounding|nearby)\s*(?:areas?|cities|towns))',
                r'([A-Za-z\s]+)\s*(?:metro|metropolitan)?\s*area',
                r'serves?\s+([A-Za-z\s]+\s*(?:and|&)?\s*(?:surrounding areas?)?)',
            ]
        }
        
        # Payment patterns - Enhanced
        self.PAYMENT_PATTERNS = {
            'credit_debit': r'(?:credit|debit)(?:\s*(?:and|&|/)\s*debit)?\s*cards?|major credit cards',
            'cash': r'\bcash\b',
            'check': r'\bcheck\b',
            'financing': r'(?:financing|payment plans?|installments?|no[- ]interest)',
            'online': r'(?:online payment|pay online|digital payment)',
            'ach': r'(?:ACH|bank transfer|wire transfer)',
        }
        
        # Service category patterns - Enhanced
        self.SERVICE_PATTERNS = {
            'HVAC': r'(?:HVAC|heating|cooling|air\s*conditioning|furnace|AC|heat\s*pump)',
            'Plumbing': r'(?:plumb(?:ing|er)|pipe|drain|water\s*heater|faucet|toilet|sink)',
            'Electrical': r'(?:electric(?:al|ian)?|wiring|outlet|breaker|panel|lighting)',
            'Emergency': r'emergency\s*(?:service|repair|call|response)',
            'Maintenance': r'(?:maintenance|tune[- ]up|inspection|preventive|cleaning)',
            'Installation': r'(?:installation|install|replacement|upgrade)',
            'Repair': r'(?:repair|fix|service|troubleshoot)',
        }
        
        # Critical rules patterns - Enhanced
        self.RULE_PATTERNS = {
            'scheduling': [
                r'(?:NEVER|never|ALWAYS|always|MUST|must|ONLY|only).*?(?:availability|appointment|schedule|slot|book)',
                r'(?:CRITICAL|critical).*?(?:scheduling|booking|availability)',
                r'NEVER END A CALL WITHOUT BOOKING',
            ],
            'pricing': [
                r'(?:NEVER|never|ALWAYS|always).*?(?:price|quote|estimate).*?(?:phone|call)',
                r'DO NOT provide.*?pricing',
            ],
            'service': [
                r'(?:DO NOT|don\'t|cannot|will not).*?(?:service|work on|handle)',
            ]
        }

# ============================================================================
# ENHANCED SERVICE DETECTION ENGINE
# ============================================================================

class EnhancedServiceDetector:
    """Advanced service information detection engine with comprehensive extraction."""
    
    def __init__(self):
        """Initialize the service detector with enhanced pattern library."""
        self.patterns = EnhancedPatternLibrary()
        logger.debug("EnhancedServiceDetector initialized")
    
    def detect(self, content: str) -> Optional[ExtractedServiceInfo]:
        """Detect comprehensive service information from content."""
        if not content:
            logger.warning("Empty content provided for detection")
            return None
        
        try:
            info = ExtractedServiceInfo()
            
            # Detect all components with enhanced patterns
            self._detect_company_info(content, info)
            self._detect_dispatch_fees(content, info)
            self._detect_scheduling(content, info)
            self._detect_membership_benefits(content, info)
            self._detect_metrics(content, info)
            self._detect_payment_info(content, info)
            self._detect_service_categories(content, info)
            self._detect_scheduling_rules(content, info)
            
            # Store raw data for reference
            info.raw_data = {
                'content_length': len(content),
                'extraction_complete': True,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Check if any information was detected
            if self._has_detected_info(info):
                logger.info(f"Service information detected for: {info.company_info.company_name or 'Unknown'}")
                return info
            
            logger.debug("No service information detected")
            return None
            
        except Exception as e:
            logger.error(f"Error during service detection: {e}")
            return None
    
    def _detect_company_info(self, content: str, info: ExtractedServiceInfo) -> None:
        """Detect company name and assistant information."""
        # Company name detection with multiple patterns
        for pattern in self.patterns.COMPANY_PATTERNS['name']:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                info.company_info.company_name = match.group(1).strip(' "\',')
                logger.debug(f"Company name found: {info.company_info.company_name}")
                break
        
        # Assistant name detection
        for pattern in self.patterns.COMPANY_PATTERNS['assistant']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info.company_info.assistant_name = match.group(1)
                logger.debug(f"Assistant name found: {info.company_info.assistant_name}")
                break
        
        # Greeting detection
        for pattern in self.patterns.COMPANY_PATTERNS['greeting']:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                info.company_info.greeting = match.group(0).strip()
                break
    
    def _detect_dispatch_fees(self, content: str, info: ExtractedServiceInfo) -> None:
        """Detect comprehensive dispatch and service fee information."""
        fees_found = set()
        
        # Standard fees
        for pattern in self.patterns.FEE_PATTERNS['standard']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                amount = f"${match.group(1)}"
                fee_key = f"standard_{amount}"
                if fee_key not in fees_found:
                    # Determine service type from context
                    context = content[max(0, match.start()-100):match.end()+100]
                    service_type = "Standard Service Call"
                    conditions = "credited toward work if customer proceeds"
                    
                    if 'repair' in context.lower():
                        service_type = "Service Call (Repairs)"
                    elif 'cleaning' in context.lower() or 'maintenance' in context.lower():
                        service_type = "Service Call (Cleaning/Maintenance)"
                    
                    info.dispatch_fees.append(DispatchFee(
                        service_type=service_type,
                        amount=amount,
                        conditions=conditions
                    ))
                    fees_found.add(fee_key)
        
        # Emergency fees
        for pattern in self.patterns.FEE_PATTERNS['emergency']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                amount = f"${match.group(1)}"
                info.dispatch_fees.append(DispatchFee(
                    service_type="Emergency Call",
                    amount=amount,
                    conditions="credited toward work if customer proceeds"
                ))
                break
        
        # Estimate fees
        for pattern in self.patterns.FEE_PATTERNS['estimate']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if 'free' in match.group(0).lower():
                    amount = "FREE"
                else:
                    amount = f"${match.group(1)}" if match.group(1) else "$49"
                
                info.dispatch_fees.append(DispatchFee(
                    service_type="Estimate Visit",
                    amount=amount,
                    conditions="for new installations, upgrades, renovations"
                ))
                break
        
        # Member fees
        for pattern in self.patterns.FEE_PATTERNS['member']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info.dispatch_fees.append(DispatchFee(
                    service_type="Members",
                    amount="WAIVED",
                    conditions="for program members"
                ))
                break
        
        # Multiple issues
        for pattern in self.patterns.FEE_PATTERNS['multiple']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                amount = f"${match.group(1)}"
                info.dispatch_fees.append(DispatchFee(
                    service_type="Multiple Issues",
                    amount=amount,
                    conditions="covers everything in one visit"
                ))
                break
    
    def _detect_scheduling(self, content: str, info: ExtractedServiceInfo) -> None:
        """Detect comprehensive scheduling information."""
        # Operating days
        for pattern in self.patterns.SCHEDULING_PATTERNS['days']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if '7 days' in match.group(0).lower():
                    info.scheduling.operating_days = ['Monday', 'Tuesday', 'Wednesday', 
                                                     'Thursday', 'Friday', 'Saturday', 'Sunday']
                elif 'weekday' in match.group(0).lower() or 'business day' in match.group(0).lower():
                    info.scheduling.operating_days = ['Monday', 'Tuesday', 'Wednesday', 
                                                     'Thursday', 'Friday']
                else:
                    # Default to Monday-Friday
                    info.scheduling.operating_days = ['Monday', 'Tuesday', 'Wednesday', 
                                                     'Thursday', 'Friday']
                break
        
        # Hours
        for pattern in self.patterns.SCHEDULING_PATTERNS['hours']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info.scheduling.total_hours = f"{match.group(1)} - {match.group(2)}"
                
                # Try to determine morning/afternoon slots
                start_hour = self._parse_hour(match.group(1))
                end_hour = self._parse_hour(match.group(2))
                
                if start_hour and end_hour:
                    if start_hour < 12:
                        info.scheduling.morning_slots = f"{match.group(1)} - 12:00 PM"
                    if end_hour > 12:
                        # Check for specific afternoon end time
                        if '5:00 PM' in content or '5 PM' in content:
                            info.scheduling.afternoon_slots = "12:00 PM - 5:00 PM"
                        else:
                            info.scheduling.afternoon_slots = f"12:00 PM - {match.group(2)}"
                break
    
    def _detect_membership_benefits(self, content: str, info: ExtractedServiceInfo) -> None:
        """Detect comprehensive membership program information."""
        # Program name
        for pattern in self.patterns.MEMBERSHIP_PATTERNS['program_name']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if match.group(0):
                    # Extract the actual program name
                    if 'HEART' in match.group(0):
                        info.membership.program_name = "HEART Membership"
                    elif 'Fresh air' in match.group(0):
                        info.membership.program_name = "Fresh air Membership"
                    else:
                        info.membership.program_name = match.group(1) + " Membership"
                break
        
        # Discount
        for pattern in self.patterns.MEMBERSHIP_PATTERNS['discount']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info.membership.repair_discount = f"{match.group(1)}% off all repairs"
                break
        
        # Warranty
        for pattern in self.patterns.MEMBERSHIP_PATTERNS['warranty']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info.membership.warranty = "Lifetime parts and labor warranty"
                break
        
        # Other benefits
        for pattern in self.patterns.MEMBERSHIP_PATTERNS['benefits']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'waive' in match.group(0).lower() or 'free' in match.group(0).lower():
                    info.membership.dispatch_fee = "WAIVED"
                    if "Free service visits" not in info.membership.other_benefits:
                        info.membership.other_benefits.append("Free service visits")
                elif 'priority' in match.group(0).lower():
                    if "Priority scheduling" not in info.membership.other_benefits:
                        info.membership.other_benefits.append("Priority scheduling")
                elif 'never pay' in match.group(0).lower():
                    if "No charge for expert inspections" not in info.membership.other_benefits:
                        info.membership.other_benefits.append("No charge for expert inspections")
    
    def _detect_metrics(self, content: str, info: ExtractedServiceInfo) -> None:
        """Detect comprehensive operational metrics."""
        # Experience
        for pattern in self.patterns.METRICS_PATTERNS['experience']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                years = match.group(1)
                if 'colorado' in content.lower():
                    info.metrics.company_experience = f"{years}+ years in Colorado"
                else:
                    info.metrics.company_experience = f"{years}+ years"
                break
        
        # Reviews
        for pattern in self.patterns.METRICS_PATTERNS['reviews']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                count = match.group(1).replace(',', '')
                if 'five-star' in match.group(0).lower() or '5-star' in match.group(0).lower():
                    info.metrics.customer_reviews = f"{count}+ five-star reviews"
                else:
                    info.metrics.customer_reviews = f"{count}+ reviews"
                break
        
        # Resolution rate
        for pattern in self.patterns.METRICS_PATTERNS['resolution_rate']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if 'out of' in match.group(0):
                    info.metrics.same_day_resolution = f"{match.group(1)} out of {match.group(2)} times"
                else:
                    info.metrics.same_day_resolution = f"{match.group(1)}% same-day resolution"
                break
        
        # Notification
        for pattern in self.patterns.METRICS_PATTERNS['notification']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if match.lastindex and match.lastindex > 1 and match.group(2):
                    info.metrics.call_ahead_notification = f"{match.group(1)}-{match.group(2)} minutes before arrival"
                else:
                    info.metrics.call_ahead_notification = f"{match.group(1)} minutes before arrival"
                break
        
        # Service area
        for pattern in self.patterns.METRICS_PATTERNS['service_area']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info.metrics.service_area = match.group(1).strip()
                break
    
    def _detect_payment_info(self, content: str, info: ExtractedServiceInfo) -> None:
        """Detect comprehensive payment information."""
        methods = []
        
        for method_name, pattern in self.patterns.PAYMENT_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                if method_name == 'credit_debit':
                    methods.append("Credit/Debit Cards")
                elif method_name == 'cash':
                    methods.append("Cash")
                elif method_name == 'check':
                    methods.append("Check")
                elif method_name == 'financing':
                    # Look for specific financing terms
                    if re.search(r'no[- ]interest', content, re.IGNORECASE):
                        methods.append("No-interest payment plans")
                        info.payment.payment_plans = "No-interest payment plans (for qualifying projects)"
                    else:
                        methods.append("Payment Plans")
                elif method_name == 'online':
                    methods.append("Online Payment")
                elif method_name == 'ach':
                    methods.append("ACH/Bank Transfer")
        
        info.payment.accepted_methods = methods
    
    def _detect_service_categories(self, content: str, info: ExtractedServiceInfo) -> None:
        """Detect service categories offered."""
        for category_name, pattern in self.patterns.SERVICE_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                # Find subcategories or details
                subcategories = []
                
                if category_name == 'HVAC':
                    if re.search(r'heating', content, re.IGNORECASE):
                        subcategories.append("Heating")
                    if re.search(r'cooling|air\s*conditioning|AC', content, re.IGNORECASE):
                        subcategories.append("Cooling")
                    if re.search(r'furnace', content, re.IGNORECASE):
                        subcategories.append("Furnace")
                
                elif category_name == 'Plumbing':
                    if re.search(r'drain', content, re.IGNORECASE):
                        subcategories.append("Drain Services")
                    if re.search(r'water\s*heater', content, re.IGNORECASE):
                        subcategories.append("Water Heater")
                    if re.search(r'pipe', content, re.IGNORECASE):
                        subcategories.append("Pipe Repair")
                    if re.search(r'faucet', content, re.IGNORECASE):
                        subcategories.append("Faucet Repair")
                    if re.search(r'toilet', content, re.IGNORECASE):
                        subcategories.append("Toilet Services")
                
                elif category_name == 'Electrical':
                    if re.search(r'panel', content, re.IGNORECASE):
                        subcategories.append("Panel Upgrades")
                    if re.search(r'wiring', content, re.IGNORECASE):
                        subcategories.append("Wiring")
                    if re.search(r'lighting', content, re.IGNORECASE):
                        subcategories.append("Lighting")
                    if re.search(r'outlet', content, re.IGNORECASE):
                        subcategories.append("Outlets")
                
                info.service_categories.append(ServiceCategory(
                    name=category_name,
                    subcategories=subcategories
                ))
    
    def _detect_scheduling_rules(self, content: str, info: ExtractedServiceInfo) -> None:
        """Extract critical scheduling and operational rules."""
        for rule_type, patterns in self.patterns.RULE_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    rule_text = match.group(0).strip()
                    
                    # Determine priority
                    priority = "critical" if any(word in rule_text.upper() 
                                                for word in ['CRITICAL', 'NEVER', 'ALWAYS', 'MUST']) else "normal"
                    
                    # Avoid duplicates
                    if not any(rule.description == rule_text for rule in info.scheduling_rules):
                        info.scheduling_rules.append(SchedulingRule(
                            rule_type=rule_type,
                            description=rule_text[:200],  # Limit length
                            priority=priority
                        ))
    
    def _parse_hour(self, time_str: str) -> Optional[int]:
        """Parse hour from time string."""
        try:
            # Extract hour number
            hour_match = re.match(r'(\d{1,2})', time_str)
            if hour_match:
                hour = int(hour_match.group(1))
                # Check for PM
                if 'PM' in time_str.upper() and hour != 12:
                    hour += 12
                elif 'AM' in time_str.upper() and hour == 12:
                    hour = 0
                return hour
        except:
            pass
        return None
    
    def _has_detected_info(self, info: ExtractedServiceInfo) -> bool:
        """Check if any information was detected."""
        return any([
            info.company_info.company_name,
            info.dispatch_fees,
            info.scheduling.operating_days,
            info.membership.program_name,
            info.metrics.company_experience,
            info.payment.accepted_methods,
            info.service_categories,
            info.scheduling_rules
        ])

# ============================================================================
# CONFIGURATION LOADER (Unchanged)
# ============================================================================

class ConfigurationManager:
    """Manages application configuration and preloaded values."""
    
    DEFAULT_CONFIG = {
        'phone_numbers': [
            '14342151980', '18334932440', '12768659060', '12029902006',
            '17036915201', '18042085260', '17579099544', '15409999324',
            '18049420185', '12768211095', '17577608278', '17206730123',
            '12764096013', '12408978820'
        ],
        'time_formats': [
            '2025-07-10T12:42:42', '2025-08-15T09:30:15', '2025-09-22T14:15:30',
            '2025-10-05T16:45:00', '2025-11-12T11:20:25', '2025-12-01T13:55:10'
        ],
        'default_timezone': 'America/New_York'
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager."""
        self.config = self._load_config(config_path)
        logger.info("Configuration loaded successfully")
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from file or use defaults."""
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    external_config = json.load(f)
                    return {**self.DEFAULT_CONFIG, **external_config}
            except Exception as e:
                logger.warning(f"Failed to load external config: {e}. Using defaults.")
        return self.DEFAULT_CONFIG
    
    def get_phone_numbers(self) -> List[str]:
        """Get available phone numbers."""
        return self.config.get('phone_numbers', [])
    
    def get_time_formats(self) -> List[str]:
        """Get available time formats."""
        return self.config.get('time_formats', [])
    
    def get_default_timezone(self) -> str:
        """Get default timezone."""
        return self.config.get('default_timezone', 'America/New_York')

# ============================================================================
# YAML PROCESSOR (Unchanged)
# ============================================================================

class YAMLProcessor:
    """Handles YAML parsing and data extraction."""
    
    def __init__(self):
        """Initialize the YAML processor."""
        logger.debug("YAMLProcessor initialized")
    
    def parse(self, yaml_content: str) -> Optional[Dict]:
        """Parse YAML content safely."""
        try:
            data = yaml.safe_load(yaml_content)
            logger.info("YAML content parsed successfully")
            return data
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during YAML parsing: {e}")
            raise
    
    def extract_agents(self, data: Dict) -> List[Agent]:
        """Extract agent information from parsed data."""
        if not data or 'agents' not in data:
            logger.warning("No agents found in data")
            return []
        
        agents = []
        for agent_data in data['agents']:
            if 'name' in agent_data and 'system_prompt' in agent_data:
                agent = Agent(
                    name=agent_data['name'],
                    model_name=agent_data.get('model_name', 'Not specified'),
                    system_prompt=agent_data['system_prompt']
                )
                agents.append(agent)
                logger.debug(f"Agent extracted: {agent.name}")
        
        logger.info(f"Extracted {len(agents)} agents")
        return agents
    
    def extract_global_template(self, data: Dict) -> Optional[str]:
        """Extract global system prompt template."""
        template = data.get('global_system_prompt_template') if data else None
        if template:
            logger.info("Global template extracted")
        else:
            logger.warning("No global template found")
        return template

# ============================================================================
# VARIABLE MANAGER (Unchanged)
# ============================================================================

class VariableManager:
    """Manages variable detection, validation, and injection."""
    
    EXCLUDED_VARIABLES = {'active_agent_prompt'}
    
    def __init__(self):
        """Initialize the variable manager."""
        logger.debug("VariableManager initialized")
    
    def detect_variables(self, template: str) -> List[str]:
        """Detect injectable variables in template."""
        if not template:
            return []
        
        # Pattern to find variables in {variable_name} format
        pattern = r'\{([^}]+)\}'
        variables = re.findall(pattern, template)
        injectable = [v for v in variables if v not in self.EXCLUDED_VARIABLES]
        unique_vars = list(set(injectable))
        
        logger.info(f"Detected {len(unique_vars)} injectable variables")
        return unique_vars
    
    def determine_type(self, var_name: str) -> VariableType:
        """Determine variable type based on name."""
        var_lower = var_name.lower()
        
        if var_lower == 'now':
            return VariableType.TIME
        elif any(word in var_lower for word in ['phone', 'number', 'tel', 'mobile', 'cell']):
            return VariableType.PHONE
        elif any(word in var_lower for word in ['time', 'date', 'timestamp', 'when', 'datetime']):
            return VariableType.TIME
        else:
            return VariableType.TEXT
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        # Remove common separators and check if digits
        pattern = r'[\s\-\(\)\+]'
        cleaned = re.sub(pattern, '', phone)
        return cleaned.isdigit() and len(cleaned) >= 10
    
    def inject_variables(self, template: str, variables: Dict[str, str], agent_prompt: str) -> str:
        """Inject variables into template."""
        result = template
        
        # Replace active_agent_prompt
        result = result.replace('{active_agent_prompt}', agent_prompt)
        
        # Replace user-provided variables
        for var_name, var_value in variables.items():
            placeholder = '{' + var_name + '}'
            result = result.replace(placeholder, str(var_value))
            logger.debug(f"Injected variable: {var_name}")
        
        return result

# ============================================================================
# TIME UTILITIES (Unchanged)
# ============================================================================

class TimeManager:
    """Manages timezone and time formatting operations."""
    
    def __init__(self, default_timezone: str = "America/New_York"):
        """Initialize time manager."""
        self.default_timezone = self._validate_timezone(default_timezone)
        logger.debug(f"TimeManager initialized with timezone: {self.default_timezone}")
    
    def _validate_timezone(self, timezone: str) -> str:
        """Validate and return timezone string."""
        try:
            if timezone not in available_timezones():
                logger.warning(f"Invalid timezone: {timezone}, using default")
                return "America/New_York"
            return timezone
        except Exception:
            return "America/New_York"
    
    def get_current_time(self, timezone: Optional[str] = None) -> str:
        """Get current time formatted in specified timezone."""
        tz_str = timezone or self.default_timezone
        tz_str = self._validate_timezone(tz_str)
        
        try:
            tz = ZoneInfo(tz_str)
            current_time = datetime.now(tz)
            formatted = current_time.strftime("%Y-%m-%dT%H:%M:%S")
            logger.debug(f"Generated timestamp: {formatted}")
            return formatted
        except Exception as e:
            logger.error(f"Error generating timestamp: {e}")
            return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

# ============================================================================
# CLIPBOARD UTILITY - NEW ADDITION
# ============================================================================

def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using platform-specific methods."""
    try:
        # Try pyperclip first if available
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass
    except Exception:
        pass
    
    # Try platform-specific commands
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            import subprocess
            subprocess.run("pbcopy", text=True, input=text, check=True)
            return True
        elif system == "Linux":
            import subprocess
            subprocess.run("xclip", text=True, input=text, check=True)
            return True
        elif system == "Windows":
            import subprocess
            subprocess.run("clip", text=True, input=text, check=True)
            return True
    except:
        pass
    
    return False

# ============================================================================
# ENHANCED UI RENDERER - MODIFIED FOR COPY FUNCTIONALITY
# ============================================================================

class EnhancedUIRenderer:
    """Handles all UI rendering operations with enhanced service info display."""
    
    def __init__(self):
        """Initialize UI renderer."""
        self.load_css()
        logger.debug("EnhancedUIRenderer initialized")
    
    def load_css(self):
        """Load responsive CSS styles."""
        css = """
        <style>
        * { box-sizing: border-box; }
        
        #MainMenu, footer, .stDeployButton { display: none; }
        header[data-testid="stHeader"] { display: none; }
        
        .main .block-container {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .main-header {
            font-size: 2.5rem;
            font-weight: 300;
            color: #1e1e1e;
            margin-bottom: 1rem;
            text-align: center;
            line-height: 1.2;
        }
        
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2c3e50;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e9ecef;
        }
        
        .status-success {
            background: #e8f5e8;
            border-left: 4px solid #4caf50;
            color: #2e7d32;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        
        .status-info {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            color: #1565c0;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        
        .status-warning {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            color: #ef6c00;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        
        .status-error {
            background: #ffebee;
            border-left: 4px solid #f44336;
            color: #c62828;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        
        .info-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        @media (max-width: 768px) {
            .main .block-container { padding: 1rem; }
            .main-header { font-size: 2rem; }
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def render_header(self):
        """Render application header."""
        st.markdown('<h1 class="main-header">Agent Prompt Processor</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub-header">Transform YAML configurations into complete agent prompts '
            'with comprehensive service information detection</p>',
            unsafe_allow_html=True
        )
    
    def render_metrics(self, agents_count: int, variables_count: int, 
                      has_template: bool, service_detected: bool = False):
        """Render metrics display."""
        cols = st.columns(4 if service_detected else 3)
        
        with cols[0]:
            st.metric("Agents Found", agents_count)
        with cols[1]:
            st.metric("Variables", variables_count)
        with cols[2]:
            st.metric("Global Template", "✓" if has_template else "✗")
        
        if service_detected:
            with cols[3]:
                st.metric("Service Info", "🏢 Detected")
    
    def render_enhanced_service_info(self, info: ExtractedServiceInfo):
        """Render enhanced detected service information."""
        company_name = info.company_info.company_name or 'Service Company'
        st.markdown(f'### 🏢 {company_name} Service Information')
        
        # Create tabs for organized display
        tabs = st.tabs(["📍 Company", "💰 Fees", "📅 Schedule", "⭐ Membership", 
                        "📊 Metrics", "💳 Payment", "🔧 Services", "⚠️ Rules"])
        
        # Company Information Tab
        with tabs[0]:
            if info.company_info.company_name:
                st.info(f"**Company Name:** {info.company_info.company_name}")
            if info.company_info.assistant_name:
                st.info(f"**Assistant:** {info.company_info.assistant_name}")
            if info.company_info.greeting:
                st.text_area("Greeting", info.company_info.greeting, height=100, disabled=True)
        
        # Fees Tab
        with tabs[1]:
            if info.dispatch_fees:
                for fee in info.dispatch_fees:
                    with st.container():
                        st.markdown(f"**{fee.service_type}**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success(f"Amount: {fee.amount}")
                        with col2:
                            if fee.conditions:
                                st.info(f"Conditions: {fee.conditions}")
            else:
                st.warning("No fee information detected")
        
        # Scheduling Tab
        with tabs[2]:
            if info.scheduling.operating_days:
                st.success(f"**Operating Days:** {', '.join(info.scheduling.operating_days)}")
            if info.scheduling.total_hours:
                st.info(f"**Hours:** {info.scheduling.total_hours}")
            if info.scheduling.morning_slots:
                st.info(f"**Morning:** {info.scheduling.morning_slots}")
            if info.scheduling.afternoon_slots:
                st.info(f"**Afternoon:** {info.scheduling.afternoon_slots}")
        
        # Membership Tab
        with tabs[3]:
            if info.membership.program_name:
                st.markdown(f"#### {info.membership.program_name}")
            if info.membership.dispatch_fee:
                st.success(f"**Dispatch Fee:** {info.membership.dispatch_fee}")
            if info.membership.repair_discount:
                st.info(f"**Discount:** {info.membership.repair_discount}")
            if info.membership.warranty:
                st.info(f"**Warranty:** {info.membership.warranty}")
            if info.membership.other_benefits:
                st.markdown("**Additional Benefits:**")
                for benefit in info.membership.other_benefits:
                    st.write(f"• {benefit}")
        
        # Metrics Tab
        with tabs[4]:
            metrics_cols = st.columns(2)
            with metrics_cols[0]:
                if info.metrics.company_experience:
                    st.metric("Experience", info.metrics.company_experience)
                if info.metrics.customer_reviews:
                    st.metric("Reviews", info.metrics.customer_reviews)
                if info.metrics.service_area:
                    st.info(f"**Service Area:** {info.metrics.service_area}")
            with metrics_cols[1]:
                if info.metrics.same_day_resolution:
                    st.metric("Resolution Rate", info.metrics.same_day_resolution)
                if info.metrics.call_ahead_notification:
                    st.info(f"**Notification:** {info.metrics.call_ahead_notification}")
        
        # Payment Tab
        with tabs[5]:
            if info.payment.accepted_methods:
                st.markdown("**Accepted Payment Methods:**")
                cols = st.columns(min(len(info.payment.accepted_methods), 3))
                for idx, method in enumerate(info.payment.accepted_methods):
                    with cols[idx % 3]:
                        st.success(f"✓ {method}")
            if info.payment.payment_plans:
                st.info(f"**Payment Plans:** {info.payment.payment_plans}")
        
        # Services Tab
        with tabs[6]:
            if info.service_categories:
                for category in info.service_categories:
                    with st.expander(f"🔧 {category.name}"):
                        if category.subcategories:
                            for sub in category.subcategories:
                                st.write(f"• {sub}")
                        else:
                            st.write("General services available")
        
        # Rules Tab
        with tabs[7]:
            critical_rules = [r for r in info.scheduling_rules if r.priority == "critical"]
            if critical_rules:
                st.markdown("**Critical Rules:**")
                for rule in critical_rules[:10]:  # Show top 10
                    st.warning(f"⚠️ {rule.description}")
            
            normal_rules = [r for r in info.scheduling_rules if r.priority == "normal"]
            if normal_rules:
                st.markdown("**Standard Rules:**")
                for rule in normal_rules[:5]:  # Show top 5
                    st.info(f"ℹ️ {rule.description}")
    
    def render_variable_input(self, var_name: str, var_type: VariableType, 
                            config: ConfigurationManager) -> Tuple[Optional[str], bool]:
        """Render variable input field."""
        st.markdown(f"**{var_name.replace('_', ' ').title()}**")
        
        if var_type == VariableType.PHONE:
            options = ["Select phone number..."] + config.get_phone_numbers()
            selected = st.selectbox(
                f"Select {var_name}",
                options=options,
                key=f"phone_{var_name}",
                label_visibility="collapsed"
            )
            
            if selected != options[0]:
                st.success(f"✅ Selected: {selected}")
                return selected, True
            else:
                st.warning("⚠️ Please select a phone number")
                return None, False
        
        elif var_type == VariableType.TIME:
            options = ["Select timestamp..."] + config.get_time_formats()
            selected = st.selectbox(
                f"Select {var_name}",
                options=options,
                key=f"time_{var_name}",
                label_visibility="collapsed"
            )
            
            if selected != options[0]:
                st.success(f"✅ Selected: {selected}")
                return selected, True
            else:
                st.warning("⚠️ Please select a timestamp")
                return None, False
        
        else:
            value = st.text_input(
                f"Enter {var_name}",
                key=f"text_{var_name}",
                label_visibility="collapsed",
                placeholder=f"Enter {var_name.replace('_', ' ')}"
            )
            
            if value:
                st.success(f"✅ Entered: {value}")
                return value, True
            else:
                st.warning("⚠️ This field is required")
                return None, False
    
    def render_agent_prompt(self, agent: Agent, prompt: str, key_prefix: str = ""):
        """Render agent prompt section with copy functionality."""
        st.markdown(f"### 🤖 {agent.name.replace('_', ' ').title()} Prompt")
        
        col1, col2, col3 = st.columns(3)
        
        # Copy full prompt button
        with col1:
            if st.button("📋 Copy Full Prompt", key=f"copy_{key_prefix}_{agent.name}"):
                if copy_to_clipboard(agent.system_prompt):
                    st.success("✅ Copied to clipboard!")
                else:
                    st.info("📋 Manual copy required - use Ctrl+C on the text below")
                    st.text_area("Full Prompt", agent.system_prompt, height=150, key=f"copy_area_{key_prefix}_{agent.name}")
        
        # Copy generated prompt if different
        with col2:
            if prompt != agent.system_prompt:
                if st.button("📋 Copy Generated", key=f"copy_gen_{key_prefix}_{agent.name}"):
                    if copy_to_clipboard(prompt):
                        st.success("✅ Copied to clipboard!")
                    else:
                        st.info("📋 Manual copy required - use Ctrl+C on the text below")
                        st.text_area("Generated Prompt", prompt, height=150, key=f"copy_gen_area_{key_prefix}_{agent.name}")
        
        # Download button
        with col3:
            st.download_button(
                label="💾 Download",
                data=prompt,
                file_name=f"{agent.name}_prompt.txt",
                mime="text/plain",
                key=f"download_{key_prefix}_{agent.name}"
            )
        
        # Show preview
        with st.expander("View Prompt Preview"):
            preview = agent.system_prompt[:500] + "..." if len(agent.system_prompt) > 500 else agent.system_prompt
            st.code(preview, language="text")
            if len(agent.system_prompt) > 500:
                st.caption(f"📝 Showing first 500 characters of {len(agent.system_prompt)} total")

# ============================================================================
# MAIN APPLICATION WITH ENHANCED SERVICE DETECTION - MODIFIED
# ============================================================================

class EnhancedAgentPromptProcessor:
    """Main application class with enhanced service detection."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = ConfigurationManager()
        self.yaml_processor = YAMLProcessor()
        self.service_detector = EnhancedServiceDetector()
        self.variable_manager = VariableManager()
        self.time_manager = TimeManager(self.config.get_default_timezone())
        self.ui_renderer = EnhancedUIRenderer()
        
        self._initialize_session_state()
        logger.info("Enhanced application initialized")
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state."""
        defaults = {
            'yaml_processed': False,
            'data': None,
            'agents': [],
            'global_template': None,
            'variables': [],
            'yaml_input': "",
            'prompts_generated': False,
            'service_info': None,
            'generated_prompts': {},
            'variable_values': {}
        }
        
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default
    
    def run(self):
        """Run the main application."""
        # Render header
        self.ui_renderer.render_header()
        
        # Input section
        self._render_input_section()
        
        # Process button
        if st.button("🚀 Process Configuration", type="primary", use_container_width=True):
            self._process_yaml()
        
        # Results section
        if st.session_state.yaml_processed:
            self._render_results()
    
    def _render_input_section(self):
        """Render YAML input section."""
        st.markdown("### 📄 YAML Configuration")
        
        # Clear button
        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            if st.button("🗑️ Clear All", help="Clear all data and reset"):
                self._clear_session_state()
                st.rerun()
        
        # YAML input
        yaml_input = st.text_area(
            "Paste your YAML configuration",
            height=300,
            value=st.session_state.yaml_input,
            placeholder="Paste your YAML configuration here...",
            help="The system will automatically detect agents, variables, and comprehensive service information"
        )
        
        st.session_state.yaml_input = yaml_input
    
    def _process_yaml(self):
        """Process YAML input."""
        if not st.session_state.yaml_input.strip():
            st.error("Please provide YAML configuration")
            return
        
        try:
            with st.spinner("Processing configuration and extracting service information..."):
                # Parse YAML
                data = self.yaml_processor.parse(st.session_state.yaml_input)
                st.session_state.data = data
                
                # Extract components
                st.session_state.agents = self.yaml_processor.extract_agents(data)
                st.session_state.global_template = self.yaml_processor.extract_global_template(data)
                
                # Detect variables
                if st.session_state.global_template:
                    st.session_state.variables = self.variable_manager.detect_variables(
                        st.session_state.global_template
                    )
                
                # Detect service information with enhanced detector
                st.session_state.service_info = self.service_detector.detect(
                    st.session_state.yaml_input
                )
                
                st.session_state.yaml_processed = True
                st.success("✓ Configuration processed successfully")
                
                if st.session_state.service_info:
                    company = st.session_state.service_info.company_info.company_name or 'Company'
                    st.info(f"🏢 {company} service information detected with comprehensive details!")
                
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            logger.error(f"Processing error: {e}", exc_info=True)
    
    def _render_results(self):
        """Render processing results with copy functionality."""
        st.markdown("---")
        
        # Metrics
        self.ui_renderer.render_metrics(
            len(st.session_state.agents),
            len(st.session_state.variables),
            bool(st.session_state.global_template),
            bool(st.session_state.service_info)
        )
        
        # Service information with enhanced display
        if st.session_state.service_info:
            st.markdown("---")
            self.ui_renderer.render_enhanced_service_info(st.session_state.service_info)
        
        # Agents overview with copy functionality
        if st.session_state.agents:
            st.markdown("---")
            st.markdown("### 🤖 Detected Agents")
            
            for agent in st.session_state.agents:
                with st.expander(f"{agent.name} • {agent.model_name}"):
                    # Copy and download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 Copy Full Prompt", key=f"agent_copy_{agent.name}"):
                            if copy_to_clipboard(agent.system_prompt):
                                st.success("✅ Copied!")
                            else:
                                st.info("📋 Use Ctrl+C to copy from below")
                                st.text_area("Full Prompt", agent.system_prompt, height=150, key=f"copy_area_{agent.name}")
                    
                    with col2:
                        st.download_button(
                            label="💾 Download Prompt",
                            data=agent.system_prompt,
                            file_name=f"{agent.name}_prompt.txt",
                            mime="text/plain",
                            key=f"download_agent_{agent.name}"
                        )
                    
                    # Show preview
                    st.markdown("**Preview:**")
                    preview = agent.system_prompt[:500] + "..." if len(agent.system_prompt) > 500 else agent.system_prompt
                    st.code(preview, language="text")
                    if len(agent.system_prompt) > 500:
                        st.caption(f"📝 Showing first 500 characters of {len(agent.system_prompt)} total")
        
        # Variables section
        if st.session_state.variables:
            st.markdown("---")
            st.markdown("### ⚙️ Configuration Variables")
            
            variable_values = {}
            all_valid = True
            
            for var in st.session_state.variables:
                var_type = self.variable_manager.determine_type(var)
                value, is_valid = self.ui_renderer.render_variable_input(
                    var, var_type, self.config
                )
                
                if is_valid and value:
                    variable_values[var] = value
                else:
                    all_valid = False
            
            # Generate button
            if st.button("Generate Prompts", type="primary", disabled=not all_valid):
                self._generate_prompts(variable_values)
        
        else:
            # No variables - direct generation
            if st.button("Generate Prompts", type="primary"):
                self._generate_prompts({})
        
        # Display generated prompts
        if st.session_state.prompts_generated:
            st.markdown("---")
            st.markdown("### 📋 Generated Prompts")
            
            for agent in st.session_state.agents:
                if agent.name in st.session_state.generated_prompts:
                    self.ui_renderer.render_agent_prompt(
                        agent,
                        st.session_state.generated_prompts[agent.name],
                        "final"
                    )
    
    def _generate_prompts(self, variable_values: Dict[str, str]):
        """Generate prompts with injected variables."""
        st.session_state.generated_prompts = {}
        
        for agent in st.session_state.agents:
            prompt = self.variable_manager.inject_variables(
                st.session_state.global_template or "",
                variable_values,
                agent.system_prompt
            )
            st.session_state.generated_prompts[agent.name] = prompt
        
        st.session_state.prompts_generated = True
        st.success("✓ Prompts generated successfully")
    
    def _clear_session_state(self):
        """Clear all session state."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self._initialize_session_state()
        logger.info("Session state cleared")

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    try:
        app = EnhancedAgentPromptProcessor()
        app.run()
    except Exception as e:
        logger.critical(f"Critical application error: {e}", exc_info=True)
        st.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
