#!/usr/bin/env python3
"""
Test runner for OpenManus.

This script runs the tests for the OpenManus project.
"""
import argparse
import os
import sys
import unittest


def run_tests(test_path=None, verbose=False):
    """
    Run the tests.
    
    Args:
        test_path: Path to the test file or directory to run
        verbose: Whether to run tests in verbose mode
    """
    if test_path:
        # Convert path to module format if it's a file path
        if os.path.isfile(test_path):
            # Remove .py extension if present
            if test_path.endswith('.py'):
                test_path = test_path[:-3]
            # Replace / with . to convert to module format
            test_path = test_path.replace('/', '.')
        
        # Run the specified tests
        suite = unittest.defaultTestLoader.loadTestsFromName(test_path)
    else:
        # Run all tests
        suite = unittest.defaultTestLoader.discover('tests')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Return exit code based on test result
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OpenManus tests")
    parser.add_argument(
        "test_path", nargs="?", help="Path to the test file or directory to run"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Run tests in verbose mode"
    )
    
    args = parser.parse_args()
    
    sys.exit(run_tests(args.test_path, args.verbose))
