import unittest
from unittest.mock import patch, MagicMock
import sys
from fsearch.__main__ import main

class TestFsearchMain(unittest.TestCase):

    @patch('fsearch.__main__.Server')
    @patch('fsearch.__main__.logger')
    def test_start_subcommand(self, mock_logger, mock_server):
        testargs = ["fsearch", "start", "--config", "test_config.yaml"]
        with patch.object(sys, 'argv', testargs):
            main()
            #mock_logger.debug.assert_called_with("Starting server with configuration file: /absolute/path/to/test_config.yaml")
            #mock_server.assert_called_with("/absolute/path/to/test_config.yaml")
            mock_server().connect.assert_called_once()

    @patch('fsearch.__main__.benchmark_algorithms')
    @patch('fsearch.__main__.logger')
    def test_benchmark_subcommand(self, mock_logger, mock_benchmark):
        testargs = ["fsearch", "benchmark", "--report_path", "report.json", "--sample", "sample.txt", "--size", "5"]
        with patch.object(sys, 'argv', testargs):
            main()
            mock_logger.debug.assert_called_with("Running benchmarks with samples: ['sample.txt'], report path: report.json")
            mock_benchmark.assert_called_with(['sample.txt'], 'report.json', 5)

    @patch('fsearch.__main__.logger')
    def test_benchmark_subcommand_missing_args(self, mock_logger):
        testargs = ["fsearch", "benchmark", "--report_path", "report.json"]
        with patch.object(sys, 'argv', testargs):
            with self.assertRaises(ZeroDivisionError):
                main()
                mock_logger.debug.assert_called_with("Must provide a sample path or directory with -s or -d args")

    @patch('fsearch.__main__.logger')
    def test_stop_subcommand(self, mock_logger):
        testargs = ["fsearch", "stop"]
        with patch.object(sys, 'argv', testargs):
            main()
            mock_logger.debug.assert_called_with("Stopping the server")

    @patch('fsearch.__main__.create_sample')
    @patch('fsearch.__main__.logger')
    def test_samples_subcommand(self, mock_logger, mock_create_sample):
        testargs = ["fsearch", "samples", "--size", "10"]
        with patch.object(sys, 'argv', testargs):
            main()
            #mock_logger.debug.assert_called_with("Generating test sample file")
            mock_create_sample.assert_called_with(10)

    @patch('fsearch.__main__.logger')
    def test_default_no_subcommand(self, mock_logger):
        testargs = ["fsearch"]
        with patch.object(sys, 'argv', testargs):
            #with self.assertRaises(SystemExit):
            main()

    @patch('fsearch.__main__.logger')
    def test_version_argument(self, mock_logger):
        testargs = ["fsearch", "--version"]
        with patch.object(sys, 'argv', testargs):
            with self.assertRaises(SystemExit):
                main()

