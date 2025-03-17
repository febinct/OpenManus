"""
Agent Switching Utility

This module provides functionality for managing and switching between different agent roles.
It includes utilities for loading agent role definitions, identifying appropriate agents for
different contexts, and handling the transition between agents.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple, Union

class AgentSwitcher:
    """
    A class to manage agent roles and facilitate switching between them based on
    conversation context or explicit requests.
    """
    
    def __init__(self, roles_file_path: str = "agent_roles.json"):
        """
        Initialize the AgentSwitcher with agent roles from a JSON file.
        
        Args:
            roles_file_path: Path to the JSON file containing agent role definitions
        """
        self.roles_file_path = roles_file_path
        self.agent_roles = self._load_agent_roles()
        self.current_role_id = None
        
    def _load_agent_roles(self) -> Dict:
        """
        Load agent roles from the JSON file.
        
        Returns:
            Dictionary containing agent role definitions
        """
        try:
            with open(self.roles_file_path, 'r') as file:
                data = json.load(file)
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading agent roles: {e}")
            return {"agent_roles": []}
    
    def get_role_by_id(self, role_id: str) -> Optional[Dict]:
        """
        Get an agent role by its ID.
        
        Args:
            role_id: The ID of the role to retrieve
            
        Returns:
            The agent role dictionary or None if not found
        """
        for role in self.agent_roles.get("agent_roles", []):
            if role.get("role_id") == role_id:
                return role
        return None
    
    def get_all_role_ids(self) -> List[str]:
        """
        Get a list of all available role IDs.
        
        Returns:
            List of role IDs
        """
        return [role.get("role_id") for role in self.agent_roles.get("agent_roles", [])]
    
    def switch_to_role(self, role_id: str) -> Tuple[bool, str]:
        """
        Switch to a specified agent role.
        
        Args:
            role_id: The ID of the role to switch to
            
        Returns:
            Tuple of (success, message)
        """
        role = self.get_role_by_id(role_id)
        if role:
            self.current_role_id = role_id
            return True, f"Switched to {role.get('name')} role"
        return False, f"Role with ID '{role_id}' not found"
    
    def get_current_role(self) -> Optional[Dict]:
        """
        Get the current agent role.
        
        Returns:
            The current agent role dictionary or None if no role is set
        """
        if self.current_role_id:
            return self.get_role_by_id(self.current_role_id)
        return None
    
    def detect_role_from_context(self, message: str) -> Optional[str]:
        """
        Detect the most appropriate agent role based on message context.
        
        Args:
            message: The user message to analyze
            
        Returns:
            The ID of the most appropriate role or None if no clear match
        """
        # Simple keyword-based detection for demonstration purposes
        # In a real implementation, this would use more sophisticated NLP techniques
        
        role_scores = {}
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Define keywords associated with each role
        role_keywords = {
            "customer_service": ["refund", "order", "complaint", "purchase", "delivery", "customer"],
            "technical_support": ["error", "bug", "troubleshoot", "install", "update", "technical", "software", "hardware"],
            "creative_writer": ["story", "write", "creative", "poem", "narrative", "character"],
            "data_analyst": ["data", "statistics", "analysis", "trend", "graph", "correlation"],
            "educational_tutor": ["learn", "explain", "concept", "understand", "homework", "study"],
            "legal_advisor": ["legal", "law", "contract", "rights", "regulation", "compliance"],
            "health_coach": ["health", "exercise", "diet", "nutrition", "wellness", "fitness"],
            "financial_advisor": ["money", "invest", "finance", "budget", "saving", "retirement"],
            "travel_consultant": ["travel", "vacation", "trip", "destination", "flight", "hotel"],
            "product_specialist": ["product", "feature", "model", "specification", "compare", "recommendation"]
        }
        
        # Score each role based on keyword matches
        for role_id, keywords in role_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                role_scores[role_id] = score
        
        # Return the role with the highest score, if any
        if role_scores:
            return max(role_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def detect_explicit_role_request(self, message: str) -> Optional[str]:
        """
        Detect if the user is explicitly requesting a specific agent role.
        
        Args:
            message: The user message to analyze
            
        Returns:
            The ID of the requested role or None if no explicit request
        """
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Direct role mentions (e.g., "I need a creative writer")
        direct_role_patterns = [
            # Patterns for requesting to speak with an agent
            r"(?:speak|talk|connect|chat) (?:to|with) (?:a|an|the) ([a-z\s]+) (?:agent|specialist|advisor|consultant|coach|tutor|writer|expert|person|professional)",
            
            # Patterns for requesting or wanting an agent
            r"(?:I need|I want|I'd like|I require|I wish for) (?:a|an|the) ([a-z\s]+) (?:agent|specialist|advisor|consultant|coach|tutor|writer|expert|person|professional)",
            
            # Patterns for switching to an agent
            r"(?:switch|change|transfer) (?:to|me to) (?:a|an|the) ([a-z\s]+) (?:agent|specialist|advisor|consultant|coach|tutor|writer|expert|person|professional)",
            
            # Patterns for requesting to have/get an agent
            r"(?:can I|could I|may I) (?:have|get|speak with|talk to) (?:a|an|the) ([a-z\s]+) (?:agent|specialist|advisor|consultant|coach|tutor|writer|expert|person|professional)",
            
            # Patterns for direct role requests
            r"(?:I need|I want|get me|I'd like) (?:the|a|an) ([a-z\s]+) (?:role|persona|mode)"
        ]
        
        # Check for direct role patterns
        for pattern in direct_role_patterns:
            matches = re.search(pattern, message_lower)
            if matches:
                role_type = matches.group(1).strip()
                return self._map_role_type_to_id(role_type)
        
        # Check for direct mentions of role names without context
        # This handles cases like "switch to health coach" or "I need financial advisor"
        for role in self.agent_roles.get("agent_roles", []):
            role_name = role.get("name", "").lower()
            role_id = role.get("role_id")
            
            # Check if the role name appears in the message with switching context
            switch_patterns = [
                f"switch to {role_name}",
                f"change to {role_name}",
                f"talk to {role_name}",
                f"speak with {role_name}",
                f"connect me with {role_name}",
                f"i need {role_name}",
                f"i want {role_name}",
                f"i'd like {role_name}"
            ]
            
            for pattern in switch_patterns:
                if pattern in message_lower:
                    return role_id
        
        # Additional patterns for more flexible role detection
        flexible_patterns = [
            # "Can you be a [role]" pattern
            r"(?:can|could) you (?:be|act as|function as|serve as|work as) (?:a|an|the) ([a-z\s]+)",
            
            # "I need [domain] advice/help" pattern
            r"I need ([a-z\s]+) (?:advice|help|assistance|guidance|support)",
            
            # "Switch to [domain] mode" pattern
            r"(?:switch|change) to ([a-z\s]+) (?:mode|role|persona)"
        ]
        
        for pattern in flexible_patterns:
            matches = re.search(pattern, message_lower)
            if matches:
                role_type = matches.group(1).strip()
                role_id = self._map_role_type_to_id(role_type)
                if role_id:
                    return role_id
        
        return None
    
    def _map_role_type_to_id(self, role_type: str) -> Optional[str]:
        """
        Map an extracted role type string to a role ID.
        
        Args:
            role_type: The extracted role type string
            
        Returns:
            The mapped role ID or None if no mapping found
        """
        # Map common role type strings to role IDs
        role_type_mapping = {
            # Customer Service variations
            "customer service": "customer_service",
            "customer support": "customer_service",
            "customer care": "customer_service",
            "customer representative": "customer_service",
            "customer agent": "customer_service",
            "customer": "customer_service",
            
            # Technical Support variations
            "technical support": "technical_support",
            "tech support": "technical_support",
            "it support": "technical_support",
            "technical help": "technical_support",
            "tech specialist": "technical_support",
            "technical specialist": "technical_support",
            "tech": "technical_support",
            
            # Creative Writer variations
            "creative writer": "creative_writer",
            "writer": "creative_writer",
            "storyteller": "creative_writer",
            "content creator": "creative_writer",
            "creative": "creative_writer",
            "poet": "creative_writer",
            "novelist": "creative_writer",
            
            # Data Analyst variations
            "data analyst": "data_analyst",
            "analyst": "data_analyst",
            "data scientist": "data_analyst",
            "statistics": "data_analyst",
            "data": "data_analyst",
            "analytics": "data_analyst",
            
            # Educational Tutor variations
            "educational tutor": "educational_tutor",
            "tutor": "educational_tutor",
            "teacher": "educational_tutor",
            "educator": "educational_tutor",
            "instructor": "educational_tutor",
            "education": "educational_tutor",
            
            # Legal Advisor variations
            "legal advisor": "legal_advisor",
            "legal consultant": "legal_advisor",
            "lawyer": "legal_advisor",
            "legal expert": "legal_advisor",
            "attorney": "legal_advisor",
            "legal": "legal_advisor",
            
            # Health Coach variations
            "health coach": "health_coach",
            "wellness coach": "health_coach",
            "health advisor": "health_coach",
            "fitness coach": "health_coach",
            "nutrition advisor": "health_coach",
            "nutritionist": "health_coach",
            "health": "health_coach",
            "wellness": "health_coach",
            "fitness": "health_coach",
            "nutrition": "health_coach",
            
            # Financial Advisor variations
            "financial advisor": "financial_advisor",
            "finance expert": "financial_advisor",
            "financial consultant": "financial_advisor",
            "money advisor": "financial_advisor",
            "investment advisor": "financial_advisor",
            "financial planner": "financial_advisor",
            "finance": "financial_advisor",
            "financial": "financial_advisor",
            
            # Travel Consultant variations
            "travel consultant": "travel_consultant",
            "travel agent": "travel_consultant",
            "travel advisor": "travel_consultant",
            "trip planner": "travel_consultant",
            "vacation planner": "travel_consultant",
            "travel": "travel_consultant",
            
            # Product Specialist variations
            "product specialist": "product_specialist",
            "product expert": "product_specialist",
            "product advisor": "product_specialist",
            "product consultant": "product_specialist",
            "product": "product_specialist"
        }
        
        # Check for exact matches first
        if role_type in role_type_mapping:
            return role_type_mapping[role_type]
        
        # Check for partial matches (more specific matches first)
        # Sort keys by length (descending) to prioritize longer, more specific matches
        sorted_keys = sorted(role_type_mapping.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in role_type:
                return role_type_mapping[key]
        
        # If no match found, try matching with role names directly
        for role in self.agent_roles.get("agent_roles", []):
            role_name = role.get("name", "").lower()
            if role_name in role_type or role_type in role_name:
                return role.get("role_id")
        
        return None
    
    def get_response_template(self, role_id: Optional[str] = None) -> Dict:
        """
        Get a response template for the specified role or current role.
        
        Args:
            role_id: The ID of the role to get a template for (uses current role if None)
            
        Returns:
            A dictionary with response template information
        """
        role_id = role_id or self.current_role_id
        if not role_id:
            return {
                "role": "default",
                "style": "neutral",
                "sample_phrases": []
            }
        
        role = self.get_role_by_id(role_id)
        if not role:
            return {
                "role": "default",
                "style": "neutral",
                "sample_phrases": []
            }
        
        return {
            "role": role.get("name"),
            "style": role.get("communication_style", []),
            "sample_phrases": role.get("sample_phrases", [])
        }


# Example usage
if __name__ == "__main__":
    # Initialize the agent switcher
    agent_switcher = AgentSwitcher()
    
    # Print all available roles
    print("Available roles:")
    for role_id in agent_switcher.get_all_role_ids():
        role = agent_switcher.get_role_by_id(role_id)
        print(f"- {role['name']} (ID: {role_id})")
    
    # Test switching to a role
    success, message = agent_switcher.switch_to_role("customer_service")
    print(f"\n{message}")
    
    # Get current role information
    current_role = agent_switcher.get_current_role()
    if current_role:
        print(f"Current role: {current_role['name']}")
        print(f"Primary function: {current_role['primary_function']}")
        print("Communication style:")
        for style in current_role['communication_style']:
            print(f"- {style}")
    
    # Test context-based role detection
    test_messages = [
        "I'm having trouble with my recent order, it hasn't arrived yet.",
        "Can you help me troubleshoot why my software keeps crashing?",
        "I need help writing a creative story about space exploration.",
        "Could you analyze this dataset and tell me what trends you see?",
        "I want to speak to a financial advisor about retirement planning."
    ]
    
    print("\nTesting context-based role detection:")
    for message in test_messages:
        detected_role_id = agent_switcher.detect_role_from_context(message)
        detected_role = agent_switcher.get_role_by_id(detected_role_id) if detected_role_id else None
        
        explicit_role_id = agent_switcher.detect_explicit_role_request(message)
        explicit_role = agent_switcher.get_role_by_id(explicit_role_id) if explicit_role_id else None
        
        print(f"\nMessage: {message}")
        print(f"Context-based detection: {detected_role['name'] if detected_role else 'No clear match'}")
        print(f"Explicit request detection: {explicit_role['name'] if explicit_role else 'No explicit request'}")