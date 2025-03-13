# OpenManus Tests

This directory contains tests for the OpenManus project.

## Running Tests

To run all tests:

```bash
python -m unittest discover -s tests
```

To run a specific test file:

```bash
python -m unittest tests/mcp/test_mcp_integration.py
```

To run a specific test case:

```bash
python -m unittest tests.mcp.test_mcp_integration.TestMCPClient
```

To run a specific test method:

```bash
python -m unittest tests.mcp.test_mcp_integration.TestMCPClient.test_initialize
```

## Test Structure

- `tests/mcp/`: Tests for the MCP (Model Context Protocol) integration
  - `test_mcp_integration.py`: Tests for the MCP client and tools

## Writing Tests

When writing tests for OpenManus, follow these guidelines:

1. Use the `unittest` framework
2. Use descriptive test method names that explain what is being tested
3. Use the `setUp` and `tearDown` methods to set up and clean up test fixtures
4. Use mocks to isolate the code being tested from external dependencies
5. Test both success and error cases
6. Add docstrings to test classes and methods to explain what is being tested

### Example

```python
import unittest
from unittest.mock import patch

class TestExample(unittest.TestCase):
    """Test example functionality."""

    def setUp(self):
        """Set up the test."""
        # Set up test fixtures

    def tearDown(self):
        """Clean up after the test."""
        # Clean up test fixtures

    @patch('module.dependency')
    def test_example(self, mock_dependency):
        """Test example functionality."""
        # Arrange
        mock_dependency.return_value = "mocked value"
        
        # Act
        result = function_under_test()
        
        # Assert
        self.assertEqual(result, "expected value")
