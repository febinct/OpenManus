#!/usr/bin/env python3
"""
Agent Switching Demonstration Script

This script demonstrates the agent switching capabilities by simulating
a conversation where different agent roles are activated based on user requests
and conversation context.
"""

import json
import random
import time
from agent_switcher import AgentSwitcher

def print_with_delay(text, delay=0.03):
    """Print text with a typewriter effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_header(text, char='=', width=80):
    """Print a formatted header."""
    print('\n' + char * width)
    print(text.center(width))
    print(char * width + '\n')

def simulate_conversation(agent_switcher, conversation):
    """
    Simulate a conversation with agent switching.
    
    Args:
        agent_switcher: The AgentSwitcher instance
        conversation: List of user messages
    """
    current_role = None
    
    for i, message in enumerate(conversation):
        # Print user message
        print_header(f"USER MESSAGE {i+1}", char='-', width=80)
        print_with_delay(f"{message}", delay=0.01)
        print()
        
        # Detect role from message
        explicit_role_id = agent_switcher.detect_explicit_role_request(message)
        context_role_id = agent_switcher.detect_role_from_context(message)
        
        # Print detection results (for demonstration purposes)
        explicit_role = agent_switcher.get_role_by_id(explicit_role_id) if explicit_role_id else None
        context_role = agent_switcher.get_role_by_id(context_role_id) if context_role_id else None
        
        print(f"[Detection Results]")
        print(f"  - Context-based: {context_role['name'] if context_role else 'None'}")
        print(f"  - Explicit request: {explicit_role['name'] if explicit_role else 'None'}")
        
        # Prioritize explicit requests over context detection
        role_id = explicit_role_id if explicit_role_id else context_role_id
        
        if role_id and (not current_role or role_id != current_role):
            # Role switch detected
            success, switch_message = agent_switcher.switch_to_role(role_id)
            current_role = role_id if success else current_role
            role = agent_switcher.get_role_by_id(current_role)
            
            # Print role switch notification
            print()
            print_with_delay(f"[SYSTEM: {switch_message}]", delay=0.01)
            print_with_delay(f"[Now speaking as: {role['name']}]", delay=0.01)
        
        # Get current role information for response
        role = agent_switcher.get_role_by_id(current_role) if current_role else None
        
        # Generate a response based on the current role
        print_header("AGENT RESPONSE", char='-', width=80)
        
        if role:
            # Print role name
            print(f"[{role['name']}]\n")
            
            # Get a sample phrase from the role to demonstrate the style
            if role.get('sample_phrases'):
                sample_phrase = random.choice(role.get('sample_phrases'))
                print_with_delay(sample_phrase, delay=0.01)
                print()
            
            # Generate a response based on the message and role
            response = generate_response(message, role)
            print_with_delay(response, delay=0.01)
            
            # Print communication style for demonstration
            print()
            style_text = f"[Communication style: {', '.join(role.get('communication_style', [])[:2])}...]"
            print_with_delay(style_text, delay=0.01)
        else:
            print("[Default Agent]\n")
            print_with_delay("I'll help you with that. What specific information do you need?", delay=0.01)
        
        print()
        input("Press Enter to continue...")
        print("\n" + "=" * 80 + "\n")

def generate_response(message, role):
    """
    Generate a contextual response based on the user message and current role.
    
    Args:
        message: The user message
        role: The current agent role
        
    Returns:
        A generated response
    """
    # This is a simplified response generation for demonstration
    # In a real implementation, this would use more sophisticated NLP
    
    role_name = role.get('name', '')
    primary_function = role.get('primary_function', '')
    
    # Simple response templates based on role
    templates = {
        "customer_service": [
            "I understand your concern about {topic}. Let me help you resolve this issue.",
            "I apologize for any inconvenience regarding {topic}. Here's what we can do to address this.",
            "Thank you for bringing this {topic} to our attention. I'll assist you in finding a solution."
        ],
        "technical_support": [
            "Let's troubleshoot this {topic} issue step by step to identify the root cause.",
            "I can help you resolve this {topic} problem. First, let's diagnose what's happening.",
            "This {topic} issue might be caused by several factors. Let's narrow it down systematically."
        ],
        "creative_writer": [
            "I can craft a compelling {topic} that captures the essence of what you're looking for.",
            "Let's explore creative approaches to this {topic}, considering different styles and tones.",
            "I'll weave together a {topic} that balances creativity with your specific requirements."
        ],
        "data_analyst": [
            "Analyzing this {topic} data reveals several interesting patterns worth exploring further.",
            "The {topic} metrics show a correlation between these key variables that might explain the trend.",
            "From a data perspective, this {topic} indicates potential opportunities in these specific areas."
        ],
        "educational_tutor": [
            "Let me explain this {topic} concept in a way that makes it easier to understand.",
            "This {topic} can be approached from multiple angles. Let's start with the fundamentals.",
            "Understanding {topic} becomes clearer when we break it down into these key components."
        ],
        "legal_advisor": [
            "Regarding this {topic}, there are several legal considerations to keep in mind.",
            "From a legal perspective, this {topic} involves regulations that specify certain requirements.",
            "While I can provide general information about this {topic}, specific legal advice would require consultation with an attorney."
        ],
        "health_coach": [
            "For this {topic}, a balanced approach that considers your overall wellbeing is important.",
            "Small, consistent changes to your {topic} routine often lead to the most sustainable results.",
            "Research suggests several evidence-based strategies for addressing this {topic} effectively."
        ],
        "financial_advisor": [
            "When planning for {topic}, it's important to consider both short-term needs and long-term goals.",
            "This {topic} decision involves weighing the potential risks and returns of different approaches.",
            "A strategic approach to this {topic} would include diversification and regular assessment."
        ],
        "travel_consultant": [
            "For your {topic}, I recommend considering these destinations that match your preferences.",
            "Planning this {topic} involves balancing your interests, budget, and timing considerations.",
            "Based on your {topic} requirements, these options offer the best combination of experience and value."
        ],
        "product_specialist": [
            "This product addresses your {topic} needs through its specialized features and design.",
            "Compared to alternatives, this solution offers superior {topic} capabilities in these key areas.",
            "For your specific {topic} requirements, I'd recommend this option because of these advantages."
        ]
    }
    
    # Extract a topic from the message (simplified)
    words = message.lower().split()
    nouns = [word for word in words if len(word) > 3 and word not in ['this', 'that', 'with', 'about', 'would', 'could', 'should']]
    topic = random.choice(nouns) if nouns else "request"
    
    # Get templates for the current role
    role_id = role.get('role_id', '')
    role_templates = templates.get(role_id, ["I can help you with this {topic}."])
    
    # Select and fill a template
    template = random.choice(role_templates)
    response = template.format(topic=topic)
    
    # Add a follow-up based on the primary function
    follow_up = f"As a {role_name}, I'm here to {primary_function.lower()}. How else can I assist you with this?"
    
    return f"{response}\n\n{follow_up}"

def main():
    """Main function to run the demonstration."""
    # Print welcome message
    print_header("AGENT SWITCHING DEMONSTRATION", width=80)
    print_with_delay("This demonstration shows how an AI assistant can switch between different agent roles")
    print_with_delay("based on user requests and conversation context.")
    print()
    print_with_delay("Each role has distinct characteristics, communication styles, and expertise domains.")
    print_with_delay("Watch as the agent adapts its responses to provide the most appropriate assistance.")
    print()
    input("Press Enter to begin the demonstration...")
    
    # Initialize the agent switcher
    agent_switcher = AgentSwitcher()
    
    # Create a conversation that exercises different agent roles
    conversation = [
        "I need help with a refund for my recent purchase. The item arrived damaged.",
        "Can you switch to technical support? My computer keeps crashing when I try to open the software.",
        "Thanks for the help. Now I'd like to write a complaint letter. Can you help me as a creative writer?",
        "That's a great letter. Now I need to understand some data about customer satisfaction rates. Can you analyze this as a data analyst?",
        "I also need to understand the legal implications of my warranty. Can you be a legal advisor?",
        "Now I'd like to improve my health while dealing with this stress. Can you be a health coach?",
        "I need to budget for a replacement product. Can you give me financial advice?",
        "I think I'll take a vacation after all this stress. Can you help me plan a trip?",
        "Before I go, can you tell me about alternative products I could buy? Act as a product specialist.",
        "My son is struggling with math. Can you be a tutor and explain how to solve quadratic equations?"
    ]
    
    # Run the conversation simulation
    simulate_conversation(agent_switcher, conversation)
    
    # Print conclusion
    print_header("DEMONSTRATION COMPLETE", width=80)
    print_with_delay("This demonstration showed how an AI assistant can switch between different agent roles")
    print_with_delay("to provide specialized assistance across various domains.")
    print()
    print_with_delay("Key capabilities demonstrated:")
    print_with_delay("1. Detection of explicit role requests")
    print_with_delay("2. Context-based role detection")
    print_with_delay("3. Adaptation of communication style based on role")
    print_with_delay("4. Seamless transitions between different expertise domains")
    print_with_delay("5. Specialized responses tailored to each role's function")
    print()
    print_with_delay("Thank you for watching this demonstration!")

if __name__ == "__main__":
    main()