# Baseline Conversation Flow Implementation

This document describes the baseline conversation flow implementation for testing agent switching capabilities. The implementation provides a structured way to run predefined conversation scenarios that require switching between different agent roles.

## Overview

The baseline conversation flow is implemented in `baseline_conversation_flow.py`, which provides a framework for:

1. Loading and running predefined test scenarios from `test_scenarios.json`
2. Processing user messages and detecting appropriate agent roles
3. Switching between agent roles based on context or explicit requests
4. Generating appropriate responses based on the current agent role
5. Evaluating the accuracy of role selection against expected roles

## Implementation Details

### BaselineConversationFlow Class

The main class that implements the conversation flow functionality:

- **Initialization**: Loads test scenarios and initializes the agent switcher
- **Scenario Management**: Functions to select and run specific test scenarios
- **Message Processing**: Detects roles from messages and generates appropriate responses
- **Role Switching**: Handles transitions between different agent roles
- **Evaluation**: Compares actual role selection with expected roles

### Key Functions

- `run_scenario(scenario_id, interactive, delay)`: Runs a complete scenario conversation flow
- `process_message(message)`: Processes a user message and generates an agent response
- `_generate_response(message, role)`: Generates a response based on the current role
- `_print_scenario_summary(results)`: Prints a summary of the scenario results

### Command-line Interface

The script can be run from the command line with various options:

```bash
# List all available test scenarios
python baseline_conversation_flow.py --list

# Run a specific scenario
python baseline_conversation_flow.py --scenario ecommerce_support

# Run all scenarios
python baseline_conversation_flow.py --all

# Run in interactive mode (pauses between turns)
python baseline_conversation_flow.py --scenario ecommerce_support --interactive
```

## Test Scenarios

The implementation uses test scenarios defined in `test_scenarios.json` and documented in `test_scenarios.md`. Each scenario includes:

1. A description of the scenario
2. Required agent roles
3. A conversation flow with user messages
4. Expected roles for each message
5. Switching type (context-based or explicit request)

### Example Scenario

```json
{
  "scenario_id": "ecommerce_support",
  "name": "E-commerce Customer Support",
  "description": "A customer has issues with a recent online purchase...",
  "required_roles": ["customer_service", "technical_support", "product_specialist"],
  "conversation_flow": [
    {
      "user_message": "I ordered a laptop last week, but it hasn't arrived yet...",
      "expected_role": "customer_service",
      "switching_type": "context"
    },
    ...
  ]
}
```

## Role Detection and Switching

The implementation uses two methods for role detection:

1. **Context-based Detection**: Analyzes the message content to infer the appropriate role
2. **Explicit Role Requests**: Detects when a user directly asks for a specific agent role

When processing messages, explicit requests take precedence over context-based detection.

## Response Generation

Responses are generated based on the current agent role:

1. Uses sample phrases from the role definition when available
2. Includes the role's primary function in the response
3. Maintains a consistent communication style for each role

## Evaluation Metrics

The implementation tracks and reports:

1. Total number of conversation turns
2. Number of correct role selections
3. Accuracy percentage (correct selections / total turns)
4. Detailed results for each turn

## Usage Examples

### Running a Specific Scenario

```python
from baseline_conversation_flow import BaselineConversationFlow

# Create an instance of the BaselineConversationFlow
flow = BaselineConversationFlow()

# Run the ecommerce_support scenario
flow.run_scenario("ecommerce_support", interactive=False, delay=0.5)
```

### Processing Individual Messages

```python
from baseline_conversation_flow import BaselineConversationFlow

# Create an instance of the BaselineConversationFlow
flow = BaselineConversationFlow()

# Process a message
response_data = flow.process_message("I need help with my recent order")
print(f"Response: {response_data['response']}")
print(f"Role: {response_data['role_name']}")
```

## Extending the Implementation

To add new scenarios:

1. Add the scenario definition to `test_scenarios.json`
2. Update `test_scenarios.md` with documentation
3. Run the scenario using the BaselineConversationFlow class

To modify role detection or response generation:

1. Update the relevant methods in the BaselineConversationFlow class
2. Test with existing scenarios to ensure compatibility

## Conclusion

This baseline conversation flow implementation provides a solid foundation for testing agent switching capabilities. It allows for structured testing of different scenarios and evaluation of role detection and switching accuracy.