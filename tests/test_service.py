import unittest
from unittest.mock import patch, call, mock_open
import os
import sys
from fsearch.service import create_service, main, ParserArgs

class TestServiceCreation(unittest.TestCase):

    @patch('fsearch.__main__.os.makedirs')
    @patch('fsearch.__main__.shutil.which', return_value='/usr/local/bin/fsearch')
    @patch('fsearch.__main__.open', new_callable=mock_open)
    @patch('fsearch.__main__.call')
    @patch('fsearch.__main__.os.getcwd', return_value='/home/user')
    def test_create_service(self, mock_getcwd, mock_call, mock_open, mock_which, mock_makedirs):
        config_file = 'test_config.yaml'
        port = 9090

        with patch('fsearch.__main__.service_template', "{exec_path} {config_file} {working_dir} {port}"):
            create_service(config_file, port)

        target_service_dir = os.path.expanduser('~/.config/systemd/user')
        target_service_file = os.path.join(target_service_dir, 'fsearch.service')

        mock_makedirs.assert_called_once_with(target_service_dir, exist_ok=True)
        mock_which.assert_called_once_with('fsearch')
        mock_getcwd.assert_called_once()
        
        mock_open.assert_called_once_with(target_service_file, 'w')
        mock_open().write.assert_called_once_with("/usr/local/bin/fsearch test_config.yaml /home/user 9090")
        
        expected_calls = [
            call(['systemctl', '--user', 'daemon-reload']),
            call(['systemctl', '--user', 'start', 'fsearch.service'])
        ]
        mock_call.assert_has_calls(expected_calls, any_order=False)

    @patch('fsearch.__main__.create_service')
    @patch('fsearch.__main__.argparse.ArgumentParser.parse_args', return_value=ParserArgs(config='test_config.yaml', port=9090))
    def test_main(self, mock_parse_args, mock_create_service):
        testargs = ["fsearch_service", "--config", "test_config.yaml", "--port", "9090"]
        with patch.object(sys, 'argv', testargs):
            main()

        mock_parse_args.assert_called_once()
        args = mock_parse_args.return_value
        self.assertEqual(args.config, 'test_config.yaml')
        self.assertEqual(args.port, 9090)
        mock_create_service.assert_called_once_with('test_config.yaml', 9090)

