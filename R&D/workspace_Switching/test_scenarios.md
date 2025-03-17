# Test Scenarios for Agent Switching

This document outlines various test scenarios designed to evaluate the agent switching capabilities. Each scenario is crafted to test different aspects of role detection, switching mechanisms, and conversation handling.

## 1. E-commerce Customer Support

**Description:** A customer has issues with a recent online purchase and needs help with refunds, technical problems, and product information.

**Required Roles:**
- Customer Service Agent
- Technical Support Specialist
- Product Specialist

**Conversation Flow:**
1. **User:** "I ordered a laptop last week, but it hasn't arrived yet. The tracking says it was delivered, but I didn't receive anything."
   - **Expected Role:** Customer Service Agent
   - **Switching Type:** Context-based

2. **User:** "Now that I have the laptop, I'm having trouble setting it up. The screen keeps flickering when I turn it on."
   - **Expected Role:** Technical Support Specialist
   - **Switching Type:** Context-based

3. **User:** "Can you tell me if this laptop model is good for video editing? I need something that can handle large files."
   - **Expected Role:** Product Specialist
   - **Switching Type:** Context-based

4. **User:** "I think I'll return it. Can you help me with the return process?"
   - **Expected Role:** Customer Service Agent
   - **Switching Type:** Context-based

## 2. Health and Financial Planning

**Description:** A user needs guidance on improving their health while also planning for retirement and understanding insurance implications.

**Required Roles:**
- Health and Wellness Coach
- Financial Advisor
- Legal Advisor

**Conversation Flow:**
1. **User:** "I've been feeling tired lately and want to improve my energy levels. Can you suggest some lifestyle changes?"
   - **Expected Role:** Health and Wellness Coach
   - **Switching Type:** Context-based

2. **User:** "I also need to start planning for retirement. I'm 35 and haven't saved much yet."
   - **Expected Role:** Financial Advisor
   - **Switching Type:** Context-based

3. **User:** "Can you switch to being a health coach again? I want to know if my health insurance would cover nutritionist visits."
   - **Expected Role:** Health and Wellness Coach
   - **Switching Type:** Explicit request

4. **User:** "What are the legal implications if I use my health savings account for gym memberships?"
   - **Expected Role:** Legal Advisor
   - **Switching Type:** Context-based

## 3. Educational Project with Creative and Data Components

**Description:** A student needs help with a school project that involves learning concepts, creative writing, and data analysis.

**Required Roles:**
- Educational Tutor
- Creative Writer
- Data Analyst

**Conversation Flow:**
1. **User:** "I need help understanding the concept of climate change for my science project."
   - **Expected Role:** Educational Tutor
   - **Switching Type:** Context-based

2. **User:** "Now I need to write a creative story about a world affected by climate change. Can you be a creative writer?"
   - **Expected Role:** Creative Writer
   - **Switching Type:** Explicit request

3. **User:** "I have some temperature data from the past 50 years. Can you help me analyze trends?"
   - **Expected Role:** Data Analyst
   - **Switching Type:** Context-based

4. **User:** "Can you explain what these trend lines mean in simple terms? I need to understand it for my presentation."
   - **Expected Role:** Educational Tutor
   - **Switching Type:** Context-based

## 4. Vacation Planning with Technical and Financial Considerations

**Description:** A user planning a vacation needs help with travel recommendations, budgeting, and technical issues with booking websites.

**Required Roles:**
- Travel Consultant
- Financial Advisor
- Technical Support Specialist

**Conversation Flow:**
1. **User:** "I'm planning a trip to Europe this summer. Can you recommend some destinations that aren't too crowded?"
   - **Expected Role:** Travel Consultant
   - **Switching Type:** Context-based

2. **User:** "I need to budget for this trip. How much should I set aside for a 2-week vacation in Europe?"
   - **Expected Role:** Financial Advisor
   - **Switching Type:** Context-based

3. **User:** "I'm having trouble with the booking website. It keeps giving me an error when I try to reserve a hotel."
   - **Expected Role:** Technical Support Specialist
   - **Switching Type:** Context-based

4. **User:** "Now that I've fixed the technical issue, can you help me as a travel consultant again? I need to know the best time to visit Italy."
   - **Expected Role:** Travel Consultant
   - **Switching Type:** Explicit request

## 5. Product Launch with Multiple Aspects

**Description:** A business owner launching a new product needs help with product details, customer service scripts, legal considerations, and marketing content.

**Required Roles:**
- Product Specialist
- Customer Service Agent
- Legal Advisor
- Creative Writer

**Conversation Flow:**
1. **User:** "I'm launching a new smart home device. Can you help me understand how it compares to competitors?"
   - **Expected Role:** Product Specialist
   - **Switching Type:** Context-based

2. **User:** "I need to train my customer service team. Can you help me create some scripts for common questions?"
   - **Expected Role:** Customer Service Agent
   - **Switching Type:** Context-based

3. **User:** "What legal disclaimers should I include in my product documentation?"
   - **Expected Role:** Legal Advisor
   - **Switching Type:** Context-based

4. **User:** "Can you switch to creative writer mode? I need compelling product descriptions for my website."
   - **Expected Role:** Creative Writer
   - **Switching Type:** Explicit request

## 6. Rapid Role Switching Test

**Description:** A stress test scenario with frequent role switches to test the system's ability to handle rapid transitions.

**Required Roles:**
- Customer Service Agent
- Technical Support Specialist
- Creative Writer
- Data Analyst
- Educational Tutor

**Conversation Flow:**
1. **User:** "I need help with my recent order."
   - **Expected Role:** Customer Service Agent
   - **Switching Type:** Context-based

2. **User:** "Actually, can you switch to technical support? My computer is crashing."
   - **Expected Role:** Technical Support Specialist
   - **Switching Type:** Explicit request

3. **User:** "Never mind that. Be a creative writer and write me a poem about technology."
   - **Expected Role:** Creative Writer
   - **Switching Type:** Explicit request

4. **User:** "Now analyze this data: 10, 15, 20, 25, 30. What's the trend?"
   - **Expected Role:** Data Analyst
   - **Switching Type:** Context-based

5. **User:** "Can you explain what a linear trend means in simple terms?"
   - **Expected Role:** Educational Tutor
   - **Switching Type:** Context-based

## 7. Ambiguous Role Requests

**Description:** Tests the system's ability to handle ambiguous requests that could be interpreted as requiring multiple roles.

**Required Roles:**
- Health and Wellness Coach
- Financial Advisor
- Product Specialist
- Educational Tutor

**Conversation Flow:**
1. **User:** "I want to improve my health and save money at the same time."
   - **Expected Role:** Health and Wellness Coach
   - **Switching Type:** Context-based
   - **Notes:** This could be interpreted as requiring either health_coach or financial_advisor. The system should choose one based on context priority.

2. **User:** "Can you tell me about investment options that also support wellness companies?"
   - **Expected Role:** Financial Advisor
   - **Switching Type:** Context-based
   - **Notes:** This combines financial_advisor and health_coach domains.

3. **User:** "I'm looking for a fitness tracker that's good value for money. Any recommendations?"
   - **Expected Role:** Product Specialist
   - **Switching Type:** Context-based
   - **Notes:** This combines product_specialist and health_coach domains.

4. **User:** "Can you explain how compound interest works and how it might affect my fitness goals over time?"
   - **Expected Role:** Educational Tutor
   - **Switching Type:** Context-based
   - **Notes:** This combines educational_tutor and financial_advisor domains with a touch of health_coach.

## 8. Contradictory Switching Signals

**Description:** Tests how the system handles messages that contain contradictory signals about which role should be active.

**Required Roles:**
- Customer Service Agent
- Technical Support Specialist
- Creative Writer
- Legal Advisor

**Conversation Flow:**
1. **User:** "I'm having a technical issue with my order. The website crashed during checkout."
   - **Expected Role:** Technical Support Specialist
   - **Switching Type:** Context-based
   - **Notes:** Contains signals for both customer_service and technical_support.

2. **User:** "Can you be a creative writer but help me with a technical problem? My printer isn't working."
   - **Expected Role:** Creative Writer
   - **Switching Type:** Explicit request
   - **Notes:** Explicit request for creative_writer but context suggests technical_support. Explicit should take precedence.

3. **User:** "I need legal advice about a creative work I'm developing. Switch to legal advisor please."
   - **Expected Role:** Legal Advisor
   - **Switching Type:** Explicit request
   - **Notes:** Contains creative context but explicit request for legal_advisor.

4. **User:** "As a customer service agent, can you explain the legal implications of returning a product after 30 days?"
   - **Expected Role:** Customer Service Agent
   - **Switching Type:** Explicit request
   - **Notes:** Explicit request for customer_service but question is about legal matters.

## 9. Multi-turn Complex Conversation

**Description:** A complex conversation that requires maintaining context across multiple turns while switching roles.

**Required Roles:**
- Educational Tutor
- Data Analyst
- Creative Writer
- Financial Advisor

**Conversation Flow:**
1. **User:** "I'm working on a project about the stock market for my economics class. Can you explain how the stock market works?"
   - **Expected Role:** Educational Tutor
   - **Switching Type:** Context-based

2. **User:** "That's helpful. Now I have some historical stock data from the S&P 500. Can you analyze the trends from the past 10 years?"
   - **Expected Role:** Data Analyst
   - **Switching Type:** Context-based

3. **User:** "Based on that analysis, can you write a creative story about a day in the life of a stock trader?"
   - **Expected Role:** Creative Writer
   - **Switching Type:** Context-based

4. **User:** "That's a great story! Now, given what we've discussed about the stock market, what would be a good investment strategy for a college student like me?"
   - **Expected Role:** Financial Advisor
   - **Switching Type:** Context-based

5. **User:** "Can you explain dollar-cost averaging in simpler terms? I'm still learning these concepts."
   - **Expected Role:** Educational Tutor
   - **Switching Type:** Context-based

## 10. No Clear Role Required

**Description:** Tests how the system handles messages that don't clearly require a specific specialized role.

**Required Roles:**
- Default (no specific role)

**Conversation Flow:**
1. **User:** "Hello, how are you today?"
   - **Expected Role:** Default
   - **Switching Type:** Context-based
   - **Notes:** General greeting with no specific role requirement.

2. **User:** "What's the weather like?"
   - **Expected Role:** Default
   - **Switching Type:** Context-based
   - **Notes:** General information request with no specific role requirement.

3. **User:** "Tell me something interesting."
   - **Expected Role:** Default
   - **Switching Type:** Context-based
   - **Notes:** Open-ended request with no specific role requirement.

4. **User:** "What's your favorite color?"
   - **Expected Role:** Default
   - **Switching Type:** Context-based
   - **Notes:** Personal preference question with no specific role requirement.