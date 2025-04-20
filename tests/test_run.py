"""
Tests for the backtest.run module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.run import parse_arguments, main

class TestRun:
    """Test cases for backtest.run module."""
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        """Test parsing command line arguments."""
        # Set up mock parse_args
        mock_args = MagicMock()
        mock_args.config = 'config/test_config.yaml'
        mock_args.data = 'data/test_data.csv'
        mock_parse_args.return_value = mock_args
        
        # Parse arguments
        args = parse_arguments()
        
        # Verify the arguments
        assert args.config == 'config/test_config.yaml'
        assert args.data == 'data/test_data.csv'
    
    @patch('backtest.run.parse_arguments')
    @patch('backtest.run.run_backtest')
    def test_main(self, mock_run_backtest, mock_parse_arguments):
        """Test the main function."""
        # Set up mock parse_arguments
        mock_args = MagicMock()
        mock_args.config = 'config/test_config.yaml'
        mock_args.data = 'data/test_data.csv'
        mock_parse_arguments.return_value = mock_args
        
        # Set up mock run_backtest
        mock_run_backtest.return_value = 0
        
        # Run main
        result = main()
        
        # Verify the result
        assert result == 0
        
        # Verify that run_backtest was called
        mock_run_backtest.assert_called_once()
