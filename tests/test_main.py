import pytest
import unittest
from unittest.mock import patch, MagicMock
import sys
import argparse
from fsearch.__main__ import main, DefaultArgs, StartArgs, StopArgs, BenchmarkArgs, SamplesArgs

@pytest.mark.usefixtures("config_file_cls")
class TestFsearchMain(unittest.TestCase):

    #@patch('fsearch.__main__.argparse.ArgumentParser')
    @patch('fsearch.__main__.os')
    @patch('fsearch.__main__.Server')
    @patch('fsearch.__main__.logger')
    def test_start_subcommand(self, mock_logger, mock_server, mock_os):
        #mock_argparse.add_subparsers.side_effect = MagicMock()
        #mock_argparse.parse_args.return_value = StartArgs(subcommand='start', config='test_config.yaml')
        testargs = ["fsearch", "start", "--config", self.config_file]
        with patch.object(sys, 'argv', testargs):
            
            with patch('fsearch.__main__.argparse.ArgumentParser.parse_args', return_value=StartArgs(subcommand='start', config='test_config.yaml')) as mock_parse_args:
                main()
                #mock_argparse.add_subparsers.assert_called_once()
                args = mock_parse_args.return_value
                self.assertEqual(args.subcommand, 'start')
                #mock_logger.debug.assert_called_with("Starting server with configuration file: /absolute/path/to/test_config.yaml")
                #mock_server.assert_called_with("/absolute/path/to/test_config.yaml")
                mock_logger.debug.assert_called_once()
                mock_os.path.isabs.assert_called_once()
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

    @patch('fsearch.__main__.argparse.ArgumentParser.print_help')
    @patch('fsearch.__main__.logger')
    def test_default_no_subcommand(self, mock_logger, mock_parser):
        testargs = ["fsearch"]
        with patch.object(sys, 'argv', testargs):
            with patch('fsearch.__main__.argparse.ArgumentParser') as mock_parse_args:
                #with self.assertRaises(SystemExit):
                main()
                mock_parse_args.assert_called_once()
                mock_parse_args.assert_called_once()

    @patch('fsearch.__main__.logger')
    def test_version_argument(self, mock_logger):
        testargs = ["fsearch", "--version"]
        with patch.object(sys, 'argv', testargs):
            with self.assertRaises(SystemExit):
                main()

