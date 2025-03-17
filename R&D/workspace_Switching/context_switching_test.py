#!/usr/bin/env python3
"""
Context-Based Agent Switching Test

This script tests the automatic agent switching based on conversation context.
It focuses on evaluating how well the system can detect appropriate agent roles
from the content of user messages without explicit role requests.
"""

import json
import random
import time
import os
import sys
from typing import Dict, List, Optional, Tuple, Any
import re
import csv
from collections import Counter

from agent_switcher import AgentSwitcher
from baseline_conversation_flow import BaselineConversationFlow

class ContextSwitchingTest:
    """
    A class to test and evaluate automatic agent switching based on conversation context.
    """
    
    def __init__(self, scenarios_file: str = "test_scenarios.json"):
        """
        Initialize the ContextSwitchingTest with test scenarios and agent switcher.
        
        Args:
            scenarios_file: Path to the JSON file containing test scenarios
        """
        self.scenarios_file = scenarios_file
        self.scenarios = self._load_scenarios()
        self.agent_switcher = AgentSwitcher()
        self.baseline_flow = BaselineConversationFlow(scenarios_file)
        self.test_results = []
        
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
    
    def get_context_based_scenarios(self) -> List[Dict]:
        """
        Get scenarios that include context-based switching.
        
        Returns:
            List of scenarios with context-based switching
        """
        context_scenarios = []
        
        for scenario in self.scenarios.get("test_scenarios", []):
            # Check if the scenario has any context-based switching
            has_context_switching = False
            for turn in scenario.get("conversation_flow", []):
                if turn.get("switching_type") == "context":
                    has_context_switching = True
                    break
            
            if has_context_switching:
                context_scenarios.append(scenario)
        
        return context_scenarios
    
    def test_context_detection(self, message: str) -> Dict:
        """
        Test context-based role detection for a single message.
        
        Args:
            message: The user message to test
            
        Returns:
            Dictionary with detection results
        """
        # Detect role from context
        context_role_id = self.agent_switcher.detect_role_from_context(message)
        context_role = self.agent_switcher.get_role_by_id(context_role_id) if context_role_id else None
        
        # Also check for explicit requests (for comparison)
        explicit_role_id = self.agent_switcher.detect_explicit_role_request(message)
        explicit_role = self.agent_switcher.get_role_by_id(explicit_role_id) if explicit_role_id else None
        
        return {
            "message": message,
            "context_role_id": context_role_id,
            "context_role_name": context_role.get("name", "None") if context_role else "None",
            "explicit_role_id": explicit_role_id,
            "explicit_role_name": explicit_role.get("name", "None") if explicit_role else "None",
            "has_explicit_request": explicit_role_id is not None
        }
    
    def test_keyword_coverage(self) -> Dict:
        """
        Test keyword coverage by analyzing which keywords are most frequently detected.
        
        Returns:
            Dictionary with keyword coverage statistics
        """
        # Extract the role_keywords dictionary from the agent_switcher
        role_keywords = {}
        
        # This is a bit of a hack to get the role_keywords dictionary
        # In a real implementation, we would make this accessible through a method
        with open('agent_switcher.py', 'r') as f:
            content = f.read()
            
            # Find the role_keywords dictionary
            start_idx = content.find("role_keywords = {")
            if start_idx != -1:
                # Extract the dictionary definition
                dict_content = content[start_idx:]
                end_idx = dict_content.find("}")
                if end_idx != -1:
                    dict_content = dict_content[:end_idx+1]
                    
                    # Parse the dictionary (this is a simplified approach)
                    lines = dict_content.split("\n")
                    for line in lines:
                        if ":" in line and "[" in line and "]" in line:
                            role_part = line.split(":")[0].strip().strip('"\'')
                            keywords_part = line.split("[")[1].split("]")[0]
                            keywords = [k.strip().strip('"\'') for k in keywords_part.split(",")]
                            role_keywords[role_part] = keywords
        
        # Count how many times each keyword appears in our test scenarios
        keyword_counts = Counter()
        
        # Get all context-based messages from scenarios
        context_messages = []
        for scenario in self.scenarios.get("test_scenarios", []):
            for turn in scenario.get("conversation_flow", []):
                if turn.get("switching_type") == "context":
                    context_messages.append(turn.get("user_message", ""))
        
        # Count keyword occurrences
        for message in context_messages:
            message_lower = message.lower()
            for role_id, keywords in role_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        keyword_counts[f"{role_id}:{keyword}"] += 1
        
        # Calculate coverage statistics
        total_keywords = sum(len(keywords) for keywords in role_keywords.values())
        used_keywords = sum(1 for k in keyword_counts.keys())
        coverage_percentage = (used_keywords / total_keywords) * 100 if total_keywords > 0 else 0
        
        return {
            "total_keywords": total_keywords,
            "used_keywords": used_keywords,
            "coverage_percentage": coverage_percentage,
            "keyword_counts": keyword_counts
        }
    
    def run_context_switching_tests(self) -> List[Dict]:
        """
        Run tests on all context-based switching scenarios.
        
        Returns:
            List of test results
        """
        self.test_results = []
        
        # Get scenarios with context-based switching
        context_scenarios = self.get_context_based_scenarios()
        
        print(f"\nRunning context-based switching tests on {len(context_scenarios)} scenarios...")
        
        for scenario in context_scenarios:
            scenario_id = scenario.get("scenario_id")
            scenario_name = scenario.get("name")
            
            print(f"\nTesting scenario: {scenario_name} (ID: {scenario_id})")
            
            # Run the scenario
            results = self.baseline_flow.run_scenario(scenario_id, interactive=False, delay=0.1)
            
            # Filter for context-based turns
            context_turns = []
            for turn in results:
                if turn.get("switching_type") == "context":
                    context_turns.append(turn)
            
            # Calculate accuracy for context-based turns
            total_context_turns = len(context_turns)
            correct_context_turns = sum(1 for turn in context_turns if turn.get("role_match", False))
            accuracy = (correct_context_turns / total_context_turns) * 100 if total_context_turns > 0 else 0
            
            print(f"Context-based switching accuracy: {accuracy:.1f}% ({correct_context_turns}/{total_context_turns})")
            
            # Add to test results
            self.test_results.append({
                "scenario_id": scenario_id,
                "scenario_name": scenario_name,
                "total_context_turns": total_context_turns,
                "correct_context_turns": correct_context_turns,
                "accuracy": accuracy,
                "context_turns": context_turns
            })
        
        return self.test_results
    
    def analyze_failure_cases(self) -> List[Dict]:
        """
        Analyze cases where context-based switching failed.
        
        Returns:
            List of failure cases with analysis
        """
        if not self.test_results:
            print("No test results available. Run tests first.")
            return []
        
        failure_cases = []
        
        for scenario_result in self.test_results:
            for turn in scenario_result.get("context_turns", []):
                if not turn.get("role_match", True):
                    # This is a failure case
                    user_message = turn.get("user_message", "")
                    expected_role = turn.get("expected_role", "")
                    actual_role = turn.get("actual_role", "")
                    
                    # Test the message directly to get more details
                    detection_result = self.test_context_detection(user_message)
                    
                    # Add to failure cases
                    failure_cases.append({
                        "scenario_id": scenario_result.get("scenario_id"),
                        "scenario_name": scenario_result.get("scenario_name"),
                        "user_message": user_message,
                        "expected_role": expected_role,
                        "actual_role": actual_role,
                        "detection_details": detection_result
                    })
        
        return failure_cases
    
    def generate_report(self, output_file: str = "context_switching_report.md") -> None:
        """
        Generate a comprehensive report on context-based switching tests.
        
        Args:
            output_file: Path to the output report file
        """
        if not self.test_results:
            print("No test results available. Run tests first.")
            return
        
        # Calculate overall statistics
        total_turns = sum(result.get("total_context_turns", 0) for result in self.test_results)
        correct_turns = sum(result.get("correct_context_turns", 0) for result in self.test_results)
        overall_accuracy = (correct_turns / total_turns) * 100 if total_turns > 0 else 0
        
        # Get keyword coverage statistics
        keyword_stats = self.test_keyword_coverage()
        
        # Get failure cases
        failure_cases = self.analyze_failure_cases()
        
        # Generate the report
        with open(output_file, 'w') as f:
            f.write("# Context-Based Agent Switching Test Report\n\n")
            
            f.write("## Overview\n\n")
            f.write(f"This report presents the results of testing automatic agent switching based on conversation context.\n")
            f.write(f"The tests evaluate how well the system can detect appropriate agent roles from the content of user messages without explicit role requests.\n\n")
            
            f.write("## Summary Statistics\n\n")
            f.write(f"- **Total scenarios tested:** {len(self.test_results)}\n")
            f.write(f"- **Total context-based turns:** {total_turns}\n")
            f.write(f"- **Correctly detected roles:** {correct_turns}\n")
            f.write(f"- **Overall accuracy:** {overall_accuracy:.1f}%\n\n")
            
            f.write("## Scenario Results\n\n")
            f.write("| Scenario | Context Turns | Correct | Accuracy |\n")
            f.write("|----------|---------------|---------|----------|\n")
            for result in self.test_results:
                f.write(f"| {result.get('scenario_name')} | {result.get('total_context_turns')} | {result.get('correct_context_turns')} | {result.get('accuracy'):.1f}% |\n")
            f.write("\n")
            
            f.write("## Keyword Coverage\n\n")
            f.write(f"- **Total keywords defined:** {keyword_stats.get('total_keywords')}\n")
            f.write(f"- **Keywords used in scenarios:** {keyword_stats.get('used_keywords')}\n")
            f.write(f"- **Coverage percentage:** {keyword_stats.get('coverage_percentage'):.1f}%\n\n")
            
            f.write("### Most Frequently Used Keywords\n\n")
            f.write("| Role | Keyword | Count |\n")
            f.write("|------|---------|-------|\n")
            for (role_keyword), count in keyword_stats.get('keyword_counts', {}).most_common(10):
                role, keyword = role_keyword.split(":")
                f.write(f"| {role} | {keyword} | {count} |\n")
            f.write("\n")
            
            f.write("## Failure Analysis\n\n")
            if failure_cases:
                f.write(f"Found {len(failure_cases)} cases where context-based role detection failed:\n\n")
                for i, case in enumerate(failure_cases):
                    f.write(f"### Failure Case {i+1}\n\n")
                    f.write(f"- **Scenario:** {case.get('scenario_name')}\n")
                    f.write(f"- **User Message:** \"{case.get('user_message')}\"\n")
                    f.write(f"- **Expected Role:** {case.get('expected_role')}\n")
                    f.write(f"- **Actual Role:** {case.get('actual_role')}\n")
                    f.write(f"- **Has Explicit Request:** {'Yes' if case.get('detection_details', {}).get('has_explicit_request') else 'No'}\n\n")
            else:
                f.write("No failure cases found. All context-based role detections were successful.\n\n")
            
            f.write("## Conclusion\n\n")
            if overall_accuracy >= 90:
                f.write("The context-based agent switching mechanism performs very well, with high accuracy across different scenarios.\n")
            elif overall_accuracy >= 70:
                f.write("The context-based agent switching mechanism performs reasonably well, but there is room for improvement in certain scenarios.\n")
            else:
                f.write("The context-based agent switching mechanism needs significant improvement to reliably detect appropriate roles from context.\n")
            
            f.write("\nRecommendations for improvement:\n\n")
            f.write("1. Expand the keyword lists for roles with lower detection accuracy\n")
            f.write("2. Implement more sophisticated NLP techniques beyond simple keyword matching\n")
            f.write("3. Consider the conversation history for better context awareness\n")
            f.write("4. Add domain-specific entity recognition for better role matching\n")
        
        print(f"\nReport generated: {output_file}")


def main():
    """
    Main function to run the context-based switching tests.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Test automatic agent switching based on conversation context")
    parser.add_argument("--report", type=str, default="context_switching_report.md", help="Path to the output report file")
    
    args = parser.parse_args()
    
    # Run the tests
    tester = ContextSwitchingTest()
    tester.run_context_switching_tests()
    
    # Generate the report
    tester.generate_report(args.report)


if __name__ == "__main__":
    main()