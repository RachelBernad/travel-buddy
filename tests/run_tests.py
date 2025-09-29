#!/usr/bin/env python3
"""Simple test runner for travel buddy tests."""

import sys
import pytest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main(["-v", "--tb=short", __file__.replace("run_tests.py", "test_routing.py")])

