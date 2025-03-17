#!/usr/bin/env python3
"""
Baseline Conversation Flow

This script implements a baseline conversation flow that requires agent switching.
It uses the test scenarios defined in test_scenarios.json and the agent switching
functionality from agent_switcher.py to create a structured conversation flow.
"""

import json
import random
import time
import os
import sys
from typing import Dict, List, Optional, Tuple, Any

from agent_switcher import AgentSwitcher

class BaselineConversationFlow:
    """
    A class to implement and test baseline conversation flows that require agent switching.
    """
    
    def __init__(self, scenarios_file: str = "test_scenarios.json"):
        """
        Initialize the BaselineConversationFlow with test scenarios and agent switcher.
        
        Args:
            scenarios_file: Path to the JSON file containing test scenarios
        """
        self.scenarios_file = scenarios_file
        self.scenarios = self._load_scenarios()
        self.agent_switcher = AgentSwitcher()
        self.current_scenario = None
        self.current_role_id = None
        self.conversation_history = []
        
    def _load_scenarios(self) -> Dict:
        """
        Load test scenarios from the JSON file.
        
        Returns:
            Dictionary containing test scenarios
        """
        try:
            with open(self.scenarios_file, 'r') as file:
                data = json.load(file)
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading test scenarios: {e}")
            return {"test_scenarios": []}
    
    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict]:
        """
        Get a test scenario by its ID.
        
        Args:
            scenario_id: The ID of the scenario to retrieve
            
        Returns:
            The test scenario dictionary or None if not found
        """
        for scenario in self.scenarios.get("test_scenarios", []):
            if scenario.get("scenario_id") == scenario_id:
                return scenario
        return None
    
    def get_all_scenario_ids(self) -> List[str]:
        """
        Get a list of all available scenario IDs.
        
        Returns:
            List of scenario IDs
        """
        return [scenario.get("scenario_id") for scenario in self.scenarios.get("test_scenarios", [])]
    
    def select_scenario(self, scenario_id: str) -> Tuple[bool, str]:
        """
        Select a scenario to run.
        
        Args:
            scenario_id: The ID of the scenario to select
            
        Returns:
            Tuple of (success, message)
        """
        scenario = self.get_scenario_by_id(scenario_id)
        if scenario:
            self.current_scenario = scenario
            self.conversation_history = []
            return True, f"Selected scenario: {scenario.get('name')}"
        return False, f"Scenario with ID '{scenario_id}' not found"
    
    def run_scenario(self, scenario_id: str, interactive: bool = False, delay: float = 0.5) -> List[Dict]:
        """
        Run a complete scenario conversation flow.
        
        Args:
            scenario_id: The ID of the scenario to run
            interactive: Whether to run in interactive mode (wait for user input between messages)
            delay: Delay between messages in non-interactive mode
            
        Returns:
            List of conversation turns with messages and responses
        """
        success, message = self.select_scenario(scenario_id)
        if not success:
            print(f"Error: {message}")
            return []
        
        print(f"\n{'='*80}")
        print(f"RUNNING SCENARIO: {self.current_scenario.get('name')}")
        print(f"Description: {self.current_scenario.get('description')}")
        print(f"{'='*80}\n")
        
        conversation_flow = self.current_scenario.get("conversation_flow", [])
        conversation_results = []
        
        for i, turn in enumerate(conversation_flow):
            user_message = turn.get("user_message", "")
            expected_role = turn.get("expected_role", "")
            switching_type = turn.get("switching_type", "context")
            
            print(f"\n{'-'*80}")
            print(f"TURN {i+1}/{len(conversation_flow)}")
            print(f"{'-'*80}")
            
            # Display user message
            print(f"\nUser: {user_message}")
            
            # Process the message and get agent response
            response_data = self.process_message(user_message)
            
            # Display agent response
            role_name = response_data.get("role_name", "Default")
            response_text = response_data.get("response", "")
            
            print(f"\nAgent ({role_name}): {response_text}")
            
            # Display detection and switching information
            detected_context_role = response_data.get("detected_context_role", "None")
            detected_explicit_role = response_data.get("detected_explicit_role", "None")
            
            print(f"\nDetection Results:")
            print(f"- Context-based: {detected_context_role}")
            print(f"- Explicit request: {detected_explicit_role}")
            print(f"- Expected role: {expected_role}")
            print(f"- Switching type: {switching_type}")
            
            # Check if the correct role was selected
            actual_role_id = response_data.get("role_id", "")
            role_match = actual_role_id == expected_role
            
            print(f"- Role match: {'✓' if role_match else '✗'}")
            
            # Add to conversation results
            conversation_results.append({
                "turn": i+1,
                "user_message": user_message,
                "agent_response": response_text,
                "expected_role": expected_role,
                "actual_role": actual_role_id,
                "role_match": role_match,
                "switching_type": switching_type,
                "detected_context_role": response_data.get("detected_context_role_id", ""),
                "detected_explicit_role": response_data.get("detected_explicit_role_id", "")
            })
            
            # In interactive mode, wait for user input
            if interactive:
                input("\nPress Enter to continue...")
            else:
                time.sleep(delay)
        
        # Print summary
        self._print_scenario_summary(conversation_results)
        
        return conversation_results
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate an agent response.
        
        Args:
            message: The user message to process
            
        Returns:
            Dictionary with response data
        """
        # Detect role from message
        explicit_role_id = self.agent_switcher.detect_explicit_role_request(message)
        context_role_id = self.agent_switcher.detect_role_from_context(message)
        
        # Get role information
        explicit_role = self.agent_switcher.get_role_by_id(explicit_role_id) if explicit_role_id else None
        context_role = self.agent_switcher.get_role_by_id(context_role_id) if context_role_id else None
        
        # Prioritize explicit requests over context detection
        role_id = explicit_role_id if explicit_role_id else context_role_id
        
        # Switch role if needed
        if role_id and (not self.current_role_id or role_id != self.current_role_id):
            success, switch_message = self.agent_switcher.switch_to_role(role_id)
            self.current_role_id = role_id if success else self.current_role_id
        
        # Get current role
        current_role = self.agent_switcher.get_role_by_id(self.current_role_id) if self.current_role_id else None
        
        # Generate response based on the current role
        response = self._generate_response(message, current_role)
        
        # Add to conversation history
        self.conversation_history.append({
            "user": message,
            "agent": response,
            "role_id": self.current_role_id
        })
        
        # Return response data
        return {
            "response": response,
            "role_id": self.current_role_id,
            "role_name": current_role.get("name", "Default") if current_role else "Default",
            "detected_context_role_id": context_role_id,
            "detected_explicit_role_id": explicit_role_id,
            "detected_context_role": context_role.get("name", "None") if context_role else "None",
            "detected_explicit_role": explicit_role.get("name", "None") if explicit_role else "None"
        }
    
    def _generate_response(self, message: str, role: Optional[Dict]) -> str:
        """
        Generate a response based on the user message and current role.
        
        Args:
            message: The user message
            role: The current agent role
            
        Returns:
            Generated response text
        """
        if not role:
            return "I'll help you with that. What specific information do you need?"
        
        # Get role information
        role_name = role.get("name", "")
        primary_function = role.get("primary_function", "")
        sample_phrases = role.get("sample_phrases", [])
        
        # Use a sample phrase if available
        if sample_phrases:
            sample_phrase = random.choice(sample_phrases)
            return f"{sample_phrase} As a {role_name}, I'm here to {primary_function.lower()}. How can I assist you further?"
        
        # Fallback response
        return f"As a {role_name}, I'm here to {primary_function.lower()}. How can I assist you with this?"
    
    def _print_scenario_summary(self, results: List[Dict]) -> None:
        """
        Print a summary of the scenario results.
        
        Args:
            results: List of conversation turn results
        """
        if not results:
            return
        
        total_turns = len(results)
        correct_roles = sum(1 for turn in results if turn.get("role_match", False))
        accuracy = (correct_roles / total_turns) * 100 if total_turns > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"SCENARIO SUMMARY: {self.current_scenario.get('name')}")
        print(f"{'='*80}")
        print(f"Total turns: {total_turns}")
        print(f"Correct role selections: {correct_roles}/{total_turns} ({accuracy:.1f}%)")
        print(f"{'='*80}\n")
        
        # Print detailed results for each turn
        print("Detailed Results:")
        for turn in results:
            turn_num = turn.get("turn", 0)
            expected = turn.get("expected_role", "")
            actual = turn.get("actual_role", "")
            match = "✓" if turn.get("role_match", False) else "✗"
            
            print(f"Turn {turn_num}: Expected {expected}, Got {actual} {match}")


def list_scenarios():
    """
    List all available test scenarios.
    """
    flow = BaselineConversationFlow()
    scenarios = flow.scenarios.get("test_scenarios", [])
    
    print("\nAvailable Test Scenarios:")
    print("------------------------")
    
    for i, scenario in enumerate(scenarios):
        scenario_id = scenario.get("scenario_id", "")
        name = scenario.get("name", "")
        description = scenario.get("description", "")
        
        print(f"{i+1}. {name} (ID: {scenario_id})")
        print(f"   {description}")
        print()


def run_specific_scenario(scenario_id: str, interactive: bool = False):
    """
    Run a specific test scenario.
    
    Args:
        scenario_id: The ID of the scenario to run
        interactive: Whether to run in interactive mode
    """
    flow = BaselineConversationFlow()
    flow.run_scenario(scenario_id, interactive)


def run_all_scenarios(interactive: bool = False):
    """
    Run all available test scenarios.
    
    Args:
        interactive: Whether to run in interactive mode
    """
    flow = BaselineConversationFlow()
    scenario_ids = flow.get_all_scenario_ids()
    
    for scenario_id in scenario_ids:
        flow.run_scenario(scenario_id, interactive)
        print("\n\n")


def main():
    """
    Main function to run the baseline conversation flow.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Run baseline conversation flows for agent switching testing")
    parser.add_argument("--list", action="store_true", help="List all available test scenarios")
    parser.add_argument("--scenario", type=str, help="Run a specific scenario by ID")
    parser.add_argument("--all", action="store_true", help="Run all available scenarios")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.list:
        list_scenarios()
    elif args.scenario:
        run_specific_scenario(args.scenario, args.interactive)
    elif args.all:
        run_all_scenarios(args.interactive)
    else:
        # Default: list scenarios and run the first one
        list_scenarios()
        flow = BaselineConversationFlow()
        scenario_ids = flow.get_all_scenario_ids()
        if scenario_ids:
            print(f"\nRunning first scenario ({scenario_ids[0]})...\n")
            flow.run_scenario(scenario_ids[0], args.interactive)
        else:
            print("No scenarios found.")


if __name__ == "__main__":
    main()