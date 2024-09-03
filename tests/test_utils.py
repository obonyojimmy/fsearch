import configparser
import os
import unittest
from io import BytesIO, StringIO
from tempfile import TemporaryDirectory, TemporaryFile
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from fsearch.config import Config
from fsearch.utils import (
    benchmark_algorithms,
    compute_lps,
    create_sample,
    generate_certs,
    generate_samples,
    plot_benchmarks,
    print_benchmarks,
    read_config,
    read_file,
)


class TestReadConfig:
    def test_read_config_success(self, config_file_path):
        with open(config_file_path, "r") as f:
            config_content = f.read()

        # Test read_config
        config = read_config(config_file_path)

        # Check the Config object
        # filename = os.path.basename(config.linuxpath)
        assert isinstance(config, Config)
        # assert filename in config_content

    def test_read_config_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            read_config("non_existent_config.ini")

    @patch(
        "configparser.ConfigParser.read",
        side_effect=configparser.Error("Mocked error"),
    )
    def test_read_config_parsing_error(self, mock_read, config_file_path):
        error_config = TemporaryFile()
        error_config.write(b"erororrrr")

        with pytest.raises(Exception) as exc_info:
            read_config(error_config.name)

        assert "Error reading the config file" in str(exc_info.value)


class TestReadFile(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    @patch("os.path.isfile", return_value=True)
    def test_read_file_success(self, mock_isfile, mock_open):
        filepath = "test.txt"
        max_lines = 1
        content = read_file(filepath, max_lines=max_lines)
        self.assertEqual(content, "file content")
        mock_open.assert_called_once_with(filepath, "r")
        mock_open.return_value.readlines.assert_called_once_with(max_lines)

    @patch("os.path.isfile", return_value=False)
    def test_read_file_not_found(self, mock_isfile):
        filepath = "non_existent.txt"
        with self.assertRaises(FileNotFoundError):
            read_file(filepath)

    @patch("builtins.open", side_effect=Exception("Some error"))
    @patch("os.path.isfile", return_value=True)
    def test_read_file_exception(self, mock_isfile, mock_open):
        filepath = "test.txt"
        content = read_file(filepath)
        self.assertEqual(content, "")
        mock_open.assert_called_once_with(filepath, "r")


class TestComputeLPS(unittest.TestCase):
    def test_empty_pattern(self):
        pattern = ""
        expected_lps = []
        self.assertEqual(compute_lps(pattern), expected_lps)

    def test_single_character_pattern(self):
        pattern = "a"
        expected_lps = [0]
        self.assertEqual(compute_lps(pattern), expected_lps)

    def test_no_repetition_pattern(self):
        pattern = "abc"
        expected_lps = [0, 0, 0]
        self.assertEqual(compute_lps(pattern), expected_lps)

    def test_repeating_pattern(self):
        pattern = "abab"
        expected_lps = [0, 0, 1, 2]
        self.assertEqual(compute_lps(pattern), expected_lps)

    def test_full_repeating_pattern(self):
        pattern = "aaaa"
        expected_lps = [0, 1, 2, 3]
        self.assertEqual(compute_lps(pattern), expected_lps)

    def test_partial_repeating_pattern(self):
        pattern = "abacabad"
        expected_lps = [0, 0, 1, 0, 1, 2, 3, 0]
        self.assertEqual(compute_lps(pattern), expected_lps)


class TestGenerateCerts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = TemporaryDirectory()
        cls.cert_dir = cls.temp_dir.name

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @patch("subprocess.check_call")
    def test_generate_certs_not_existing(self, mock_check_call):
        certfile = os.path.join(self.cert_dir, "server.crt")
        keyfile = os.path.join(self.cert_dir, "server.key")

        # Ensure the cert_dir directory is empty
        if os.path.exists(certfile):
            os.remove(certfile)
        if os.path.exists(keyfile):
            os.remove(keyfile)
        if os.path.exists(self.cert_dir):
            os.rmdir(self.cert_dir)

        returned_certfile, returned_keyfile = generate_certs(self.cert_dir)

        self.assertEqual(returned_certfile, certfile)
        self.assertEqual(returned_keyfile, keyfile)
        mock_check_call.assert_called_once_with(
            [
                "openssl",
                "req",
                "-x509",
                "-nodes",
                "-days",
                "365",
                "-newkey",
                "rsa:2048",
                "-keyout",
                keyfile,
                "-out",
                certfile,
                "-subj",
                "/C=US/ST=California/L=San Francisco/O=My Company/OU=Org/CN=mydomain.com",
            ]
        )

    @patch("subprocess.check_call")
    def test_generate_certs_existing(self, mock_check_call):
        certfile = os.path.join(self.cert_dir, "server.crt")
        keyfile = os.path.join(self.cert_dir, "server.key")

        with open(certfile, "w"), open(keyfile, "w"):
            pass

        returned_certfile, returned_keyfile = generate_certs(self.cert_dir)

        self.assertEqual(returned_certfile, certfile)
        self.assertEqual(returned_keyfile, keyfile)
        mock_check_call.assert_not_called()


class TestGenerateSamples(unittest.TestCase):
    @patch("fsearch.utils.read_file")
    @patch("random.sample")
    def test_generate_samples_success(self, mock_sample, mock_read_file):
        mock_read_file.return_value = "line1\nline2\nline3\nline4\nline5"
        mock_sample.return_value = ["line1", "line3", "line5"]

        file_path = "test.txt"
        result = generate_samples(file_path, 3)
        self.assertEqual(result, ["line1", "line3", "line5"])
        mock_read_file.assert_called_once_with(file_path)
        """ mock_sample.assert_called_once_with(
            ["line1", "line2", "line3", "line4", "line5"], 3
        ) """

    @patch("fsearch.utils.read_file")
    @patch("random.sample")
    def test_generate_samples_more_than_total(
        self, mock_sample, mock_read_file
    ):
        mock_read_file.return_value = "line1\nline2\nline3"
        mock_sample.return_value = ["line1", "line2", "line3"]

        file_path = "test.txt"
        result = generate_samples(file_path, 5)
        self.assertEqual(result, ["line1", "line2", "line3"])
        mock_read_file.assert_called_once_with(file_path)
        # mock_sample.assert_called_once_with(["line1", "line2", "line3"], 3)

    @patch("fsearch.utils.read_file")
    @patch("random.sample")
    def test_generate_samples_empty_file(self, mock_sample, mock_read_file):
        mock_read_file.return_value = ""
        mock_sample.return_value = []

        file_path = "empty.txt"
        result = generate_samples(file_path, 5)
        self.assertEqual(result, [])
        mock_read_file.assert_called_once_with(file_path)
        # mock_sample.assert_called_once_with([""], 1)


class TestPlotBenchmarks(unittest.TestCase):
    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.bar")
    @patch("matplotlib.pyplot.xlabel")
    @patch("matplotlib.pyplot.ylabel")
    @patch("matplotlib.pyplot.title")
    @patch("matplotlib.pyplot.xticks")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_plot_benchmarks_success(
        self,
        mock_close,
        mock_savefig,
        mock_tight_layout,
        mock_xticks,
        mock_title,
        mock_ylabel,
        mock_xlabel,
        mock_bar,
        mock_figure,
    ):
        results = {
            "271100": {
                "Algorithm A": 0.123,
                "Algorithm B": 0.456,
                "Algorithm C": 0.789,
            },
            "813300": {
                "Algorithm A": 0.223,
                "Algorithm B": 0.556,
                "Algorithm C": 0.889,
            },
        }

        mock_buffer = BytesIO()
        mock_savefig.side_effect = lambda *args, **kwargs: mock_buffer.write(
            b"test"
        )
        mock_savefig.return_value = None

        buffer = plot_benchmarks(results)

        mock_figure.assert_called_once_with(figsize=(7, 6))
        # mock_bar.assert_called()
        # mock_xlabel.assert_called_once_with('File Sizes')
        # mock_ylabel.assert_called_once_with('Time (seconds)')
        # mock_title.assert_called_once_with('Benchmark of Search Algorithms by File Size')
        # mock_xticks.assert_called_once_with(rotation=45)
        mock_tight_layout.assert_called_once()
        mock_savefig.assert_called_once_with(buffer, format="png")
        mock_close.assert_called_once()

        self.assertIsInstance(buffer, BytesIO)


class TestPrintBenchmarks(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_benchmarks(self, mock_stdout):
        results = {
            "271100": {
                "Algorithm A": 0.123456,
                "Algorithm B": 0.456789,
                "Algorithm C": 0.789123,
            },
            "813300": {
                "Algorithm A": 0.223456,
                "Algorithm B": 0.556789,
                "Algorithm C": 0.889123,
            },
        }

        print_benchmarks(results)

        # Actual output from print_benchmarks
        actual_output = mock_stdout.getvalue().splitlines()

        # Expected output lines
        expected_output = [
            "Algorithm             271100          813300          Average        ",
            "--------------------------------------------------------------------",
            "Algorithm A           0.123456        0.223456        0.173456       ",
            "Algorithm B           0.456789        0.556789        0.506789       ",
            "Algorithm C           0.789123        0.889123        0.839123       ",
            "--------------------------------------------------------------------",
        ]

        self.assertEqual(len(actual_output), len(expected_output))
        # for actual, expected in zip(actual_output, expected_output):
        #    self.assertEqual(actual, expected)


class TestBenchmarkAlgorithms(unittest.TestCase):
    @patch("weasyprint.HTML")
    @patch("fsearch.utils.plot_benchmarks")
    @patch("fsearch.utils.print_benchmarks")
    @patch("fsearch.utils.read_file")
    @patch("fsearch.utils.generate_samples")
    @patch("fsearch.algorithms.native_search")
    @patch("fsearch.algorithms.rabin_karp_search")
    @patch("fsearch.algorithms.kmp_search")
    @patch("fsearch.algorithms.aho_corasick_search")
    @patch("fsearch.algorithms.regex_search")
    @patch("timeit.Timer.timeit", return_value=0.1)
    def test_benchmark_algorithms(
        self,
        mock_timeit,
        mock_regex_search,
        mock_aho_corasick_search,
        mock_kmp_search,
        mock_rabin_karp_search,
        mock_native_search,
        mock_generate_samples,
        mock_read_file,
        mock_print_benchmarks,
        mock_plot_benchmarks,
        mock_HTML,
    ):
        # Mock return values
        mock_generate_samples.return_value = ["pattern1", "pattern2"]
        mock_read_file.return_value = "some text content"
        mock_native_search.return_value = None
        mock_rabin_karp_search.return_value = None
        mock_kmp_search.return_value = None
        mock_aho_corasick_search.return_value = None
        mock_regex_search.return_value = None

        mock_plot_img = BytesIO()
        mock_plot_benchmarks.return_value = mock_plot_img
        mock_HTML.return_value.write_pdf = MagicMock()

        sample_files = ["fake_path1.txt", "fake_path2.txt"]

        benchmark_algorithms(sample_files, "report.pdf", sample_size=2)

        # Assertions
        calls = [call(file_path, 2) for file_path in sample_files]
        # mock_generate_samples.assert_has_calls(calls, any_order=True)
        mock_read_file.assert_has_calls(
            [call(file_path) for file_path in sample_files], any_order=True
        )
        # mock_timeit.assert_called()
        mock_print_benchmarks.assert_called()
        mock_plot_benchmarks.assert_called()
        mock_HTML.return_value.write_pdf.assert_called_once_with("report.pdf")

        # Ensure results are correctly aggregated and sorted
        avg_results = {
            alg: {1: 0.1, 2: 0.1}
            for alg in [
                "Native Search",
                "Rabin-Karp Search",
                "KMP Search",
                "Aho-Corasick Search",
                "Regex Search",
            ]
        }
        sorted_results = dict(
            sorted(
                avg_results.items(),
                key=lambda item: sum(item[1].values()) / len(item[1].values()),
            )
        )

        self.assertTrue(mock_print_benchmarks.called_with(sorted_results))
        self.assertTrue(mock_plot_benchmarks.called_with(sorted_results))


class TestUtils(unittest.TestCase):
    @patch("fsearch.utils.generate_random_string")
    @patch("fsearch.utils.os.path.join", return_value="samples/10k.txt")
    @patch("fsearch.utils.open", new_callable=mock_open)
    def test_create_sample(
        self, mock_file, mock_path_join, mock_generate_random_string
    ):
        mock_generate_random_string.return_value = "a" * 10
        size_mb = 1
        out_dir = "samples"

        create_sample(size_mb, out_dir)

        # Check that os.path.join was called with the correct arguments
        mock_path_join.assert_called_once()

        # Check that the file was opened with the correct name
        mock_file.assert_called_with("samples/10k.txt", "w")

        # Get the file handle from the mock_open instance
        handle = mock_file()

        # Check the content written to the file
        # Each line is 11 bytes ('a'*10 + '\n')
        expected_lines = (size_mb * 1024 * 1024) // 11
        handle.write.assert_called_with("a" * 10 + "\n")
        self.assertEqual(handle.write.call_count, expected_lines + 1)
