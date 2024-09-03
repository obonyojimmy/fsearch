import argparse
import sys
import unittest
from unittest.mock import MagicMock, patch

import pytest

from fsearch.__main__ import (
    DefaultArgs,
    SamplesArgs,
    StartArgs,
    StopArgs,
    main,
)


@pytest.mark.usefixtures("config_file_cls")
class TestFsearchMain(unittest.TestCase):
    # @patch('fsearch.__main__.argparse.ArgumentParser')
    @patch("fsearch.__main__.os")
    @patch("fsearch.__main__.Server")
    @patch("fsearch.__main__.logger")
    def test_start_subcommand(self, mock_logger, mock_server, mock_os):
        testargs = ["fsearch", "start", "--config", self.config_file]  # type: ignore
        with patch.object(sys, "argv", testargs):
            with patch(
                "fsearch.__main__.argparse.ArgumentParser.parse_args",
                return_value=StartArgs(
                    subcommand="start", config="test_config.yaml"
                ),
            ) as mock_parse_args:
                main()
                # mock_argparse.add_subparsers.assert_called_once()
                args = mock_parse_args.return_value
                self.assertEqual(args.subcommand, "start")
                mock_logger.debug.assert_called_once()
                mock_os.path.isabs.assert_called_once()
                mock_server().connect.assert_called_once()

    @patch("fsearch.__main__.logger")
    def test_stop_subcommand(self, mock_logger):
        testargs = ["fsearch", "stop"]
        with patch.object(sys, "argv", testargs):
            main()
            mock_logger.debug.assert_called_with("Stopping the server")

    @patch("fsearch.__main__.create_sample")
    @patch("fsearch.__main__.logger")
    def test_samples_subcommand(self, mock_logger, mock_create_sample):
        testargs = ["fsearch", "samples", "--size", "10"]
        with patch.object(sys, "argv", testargs):
            main()
            # mock_logger.debug.assert_called_with("Generating test sample file")
            mock_create_sample.assert_called_with(10)

    @patch("fsearch.__main__.argparse.ArgumentParser.print_help")
    @patch("fsearch.__main__.logger")
    def test_default_no_subcommand(self, mock_logger, mock_parser):
        testargs = ["fsearch"]
        with patch.object(sys, "argv", testargs):
            with patch(
                "fsearch.__main__.argparse.ArgumentParser"
            ) as mock_parse_args:
                # with self.assertRaises(SystemExit):
                main()
                mock_parse_args.assert_called_once()
                mock_parse_args.assert_called_once()

    @patch("fsearch.__main__.logger")
    def test_version_argument(self, mock_logger):
        testargs = ["fsearch", "--version"]
        with patch.object(sys, "argv", testargs):
            with self.assertRaises(SystemExit):
                main()
