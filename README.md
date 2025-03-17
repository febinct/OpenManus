# Agent Switching System

This project implements a system for testing and demonstrating agent switching capabilities in conversational AI. The system allows an AI assistant to seamlessly transition between different specialized roles based on user requests or conversation context.

## Overview

The agent switching system enables an AI to adapt its expertise, communication style, and response patterns to better serve user needs across different domains. This implementation includes:

1. A set of 10 distinct agent roles with well-defined characteristics
2. A role detection system that works through both explicit requests and context analysis
3. A switching mechanism that handles transitions between roles
4. A demonstration script that showcases the system's capabilities

## Files in this Project

- `agent_roles.md` - Detailed descriptions of each agent role in markdown format
- `agent_roles.json` - Structured data representation of agent roles for programmatic use
- `agent_switcher.py` - Core implementation of the agent switching functionality
- `agent_switching_demo.py` - Interactive demonstration script
- `agent_switching_demonstration.md` - Comprehensive documentation of the system

## Agent Roles

The system includes the following agent roles:

1. **Customer Service Agent** - Assists with inquiries, complaints, and service issues
2. **Technical Support Specialist** - Troubleshoots and resolves technical problems
3. **Creative Writer** - Generates creative content across various formats and styles
4. **Data Analyst** - Interprets data, identifies patterns, and provides insights
5. **Educational Tutor** - Explains concepts, answers questions, and facilitates learning
6. **Legal Advisor** - Provides information on legal matters and considerations
7. **Health and Wellness Coach** - Guides on health-related topics and wellness practices
8. **Financial Advisor** - Provides guidance on financial matters and planning
9. **Travel Consultant** - Assists with travel planning, recommendations, and logistics
10. **Product Specialist** - Provides detailed information about products and applications

Each role has defined characteristics, communication styles, knowledge domains, and sample phrases that demonstrate their unique approach.

## How to Use

### Running the Demonstration

To see the agent switching system in action, run the demonstration script:

```bash
python agent_switching_demo.py
```

This will simulate a conversation that exercises different agent roles, showing how the system detects role requests and adapts responses accordingly.

### Using the AgentSwitcher Class

To integrate the agent switching functionality into your own application:

```python
from agent_switcher import AgentSwitcher

# Initialize the agent switcher
agent_switcher = AgentSwitcher()

# Get all available roles
roles = agent_switcher.get_all_role_ids()
print(f"Available roles: {roles}")

# Switch to a specific role
success, message = agent_switcher.switch_to_role("technical_support")
print(message)  # "Switched to Technical Support Specialist role"

# Get the current role information
current_role = agent_switcher.get_current_role()
print(f"Current role: {current_role['name']}")

# Detect role from user message
user_message = "Can you help me troubleshoot my network connection?"
detected_role_id = agent_switcher.detect_role_from_context(user_message)
print(f"Detected role: {detected_role_id}")  # "technical_support"

# Check for explicit role requests
user_request = "Can you switch to creative writer mode?"
explicit_role_id = agent_switcher.detect_explicit_role_request(user_request)
print(f"Explicit request: {explicit_role_id}")  # "creative_writer"

# Get response template for current role
template = agent_switcher.get_response_template()
print(f"Response style: {template['style']}")
print(f"Sample phrases: {template['sample_phrases']}")
```

## Detection Methods

The system uses two primary methods to determine which agent role should be active:

1. **Explicit Role Requests** - Detects when a user directly asks for a specific type of agent
   - Example: "Can you switch to technical support?"
   - Example: "I'd like to speak with a financial advisor."

2. **Context-Based Detection** - Analyzes the message content to infer the most appropriate role
   - Example: "My computer keeps crashing" → Technical Support
   - Example: "I need help with my budget" → Financial Advisor

## Extending the System

### Adding New Roles

To add a new agent role:

1. Update the `agent_roles.json` file with the new role definition
2. Add appropriate detection patterns in the `_map_role_type_to_id` method
3. Add response templates for the new role in your implementation

### Improving Detection

The current implementation uses keyword matching and pattern recognition. To enhance detection:

1. Implement more sophisticated NLP techniques
2. Add machine learning-based classification
3. Incorporate conversation history for better context awareness

## Implementation Details

The agent switching system is built around the `AgentSwitcher` class, which provides methods for:

- Loading and managing agent role definitions
- Detecting explicit role requests through pattern matching
- Identifying appropriate roles based on message context
- Switching between roles and tracking the current active role
- Generating response templates based on the current role

The implementation prioritizes explicit role requests over context-based detection when both are present.

## Future Improvements

Potential enhancements to the system include:

1. More sophisticated NLP for better role detection
2. Learning from user feedback to improve role selection
3. Hybrid roles that combine aspects of multiple agent types
4. Personalization based on user preferences and history
5. Expanded role definitions with more specialized domains

## License

This project is available for educational and research purposes.

## Acknowledgments

This system was developed as part of a project to test agent switching skills in conversational AI assistants.
