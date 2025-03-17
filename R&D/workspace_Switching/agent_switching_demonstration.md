# Agent Switching Demonstration

This script demonstrates how the agent switching functionality works in a simulated conversation.
Each message is analyzed for both context-based and explicit role requests, with the agent
switching roles as needed to provide the most appropriate response.

## Agent Roles Overview

We have defined 10 distinct agent roles, each with specific characteristics:

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

## Switching Mechanisms

The agent switching system supports two primary methods of role detection:

1. **Explicit Role Requests**: When a user directly asks for a specific type of agent
   - Example: "Can you switch to technical support?"
   - Example: "I'd like to speak with a financial advisor."
   - Example: "Can you be a creative writer for this task?"

2. **Context-Based Detection**: When the conversation topic suggests a specific agent role
   - Example: "My computer keeps crashing" → Technical Support
   - Example: "I need help with my budget" → Financial Advisor
   - Example: "Can you write a poem about nature?" → Creative Writer

## Demonstration Conversation

Below is a simulated conversation demonstrating agent switching capabilities:

### Conversation 1: Customer Service → Technical Support → Creative Writer

**User**: I need help with a refund for my recent purchase. The item arrived damaged.

**System**: [Switched to Customer Service Agent role]

**Agent (Customer Service)**: I understand your frustration, and I'm here to help. I apologize for the inconvenience this has caused. Could you provide your order number so I can look into this refund request for you?

**User**: Can you switch to technical support? My computer keeps crashing when I try to open the software.

**System**: [Switched to Technical Support Specialist role]

**Agent (Technical Support)**: I'll help troubleshoot your computer crashes. Let's diagnose the issue by checking a few things first. Could you tell me what error message you're seeing, and when exactly the crashes occur? Also, what operating system are you using?

**User**: Thanks for the help. Now I'd like to write a complaint letter. Can you help me as a creative writer?

**System**: [Switched to Creative Writer role]

**Agent (Creative Writer)**: I'd be happy to help craft a compelling complaint letter. Let me create a narrative that captures your experience effectively. Would you like the tone to be firmly professional, emotionally evocative, or somewhere in between? And what specific points would you like to emphasize in the letter?

### Conversation 2: Data Analyst → Legal Advisor → Health Coach

**User**: Can you analyze this customer satisfaction data and tell me what trends you see?

**System**: [Switched to Data Analyst role]

**Agent (Data Analyst)**: I'll examine this customer satisfaction data for you. Based on this analysis, I can see several significant trends. The data indicates a correlation between response time and overall satisfaction scores. Let me break down these numbers into actionable insights for you.

**User**: I also need to understand the legal implications of my warranty. Can you be a legal advisor?

**System**: [Switched to Legal Advisor role]

**Agent (Legal Advisor)**: From a legal perspective, there are several factors to consider regarding your warranty. The relevant regulations in this area state that warranties must clearly disclose their terms and conditions. While I can provide general information, this shouldn't be considered legal advice for your specific situation.

**User**: Now I'd like to improve my health while dealing with this stress. Can you be a health coach?

**System**: [Switched to Health and Wellness Coach role]

**Agent (Health Coach)**: Small, consistent changes often lead to the best results when managing stress. Consider incorporating brief mindfulness practices throughout your day, ensuring adequate sleep, and maintaining physical activity. How does your current routine align with your personal wellness goals?

### Conversation 3: Financial Advisor → Travel Consultant → Product Specialist → Educational Tutor

**User**: I need to budget for a replacement product. Can you give me financial advice?

**System**: [Switched to Financial Advisor role]

**Agent (Financial Advisor)**: Based on your goals, you might consider several budgeting approaches for this replacement purchase. Let's analyze the potential impact on your monthly expenses. A diversified strategy typically includes setting aside small amounts regularly rather than making a large one-time withdrawal from savings.

**User**: I think I'll take a vacation after all this stress. Can you help me plan a trip?

**System**: [Switched to Travel Consultant role]

**Agent (Travel Consultant)**: Based on your preferences, you might enjoy exploring destinations that offer both relaxation and cultural experiences. Here's an itinerary that balances downtime with interesting activities. Consider visiting during the shoulder season for optimal weather and fewer crowds.

**User**: Before I go, can you tell me about alternative products I could buy? Act as a product specialist.

**System**: [Switched to Product Specialist role]

**Agent (Product Specialist)**: This product's key advantage is its reliability and user-friendly interface. Compared to similar options, it offers better performance in high-demand situations. Based on your needs, I'd recommend this specific model because it addresses your requirements for durability and functionality.

**User**: My son is struggling with math. Can you be a tutor and explain how to solve quadratic equations?

**System**: [Switched to Educational Tutor role]

**Agent (Educational Tutor)**: Let's break down quadratic equations into simpler parts. Think of it like a puzzle where we need to find what values of x make the equation true. First, we organize the equation into the standard form ax² + bx + c = 0. Then we can use the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a. Would you like me to walk through an example problem?

## Implementation Benefits

The agent switching capability provides several advantages:

1. **Specialized Expertise**: Each agent role brings domain-specific knowledge
2. **Appropriate Communication Style**: Language and tone adapt to the context
3. **Improved User Experience**: Users receive responses tailored to their needs
4. **Conversation Continuity**: Maintains context while changing expertise domains
5. **Flexible Interaction**: Supports both explicit requests and implicit detection

## Technical Implementation

The agent switching system is implemented using:

1. A JSON configuration file defining agent roles and their characteristics
2. Pattern matching for explicit role requests
3. Keyword-based context detection for implicit role suggestions
4. A role management system that handles transitions between agents
5. Response templates that adapt based on the current agent role

This implementation allows for seamless transitions between different agent personas while maintaining conversation context and providing specialized assistance across various domains.