import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import os.path
from datetime import datetime

# Add the parent directory to sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import download_logs

class TestGetLogs(unittest.TestCase):

    @patch('boto3.client')
    def test_get_logs_success(self, mock_boto_client):
        mock_logs_client = MagicMock()
        mock_boto_client.return_value = mock_logs_client

        mock_logs_client.filter_log_events.side_effect = [
            {'events': [{'message': 'log1'}, {'message': 'log2'}], 'nextToken': 'token1'},
            {'events': [{'message': 'log3'}], 'nextToken': None},
        ]

        result = download_logs.get_logs("test_group", "2023-01-01T00:00:00", "2023-01-02T00:00:00")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['message'], 'log1')
        self.assertEqual(result[2]['message'], 'log3')

        mock_logs_client.filter_log_events.assert_called()

    @patch('boto3.client')
    def test_get_logs_no_end_time(self, mock_boto_client):
        mock_logs_client = MagicMock()
        mock_boto_client.return_value = mock_logs_client

        mock_logs_client.filter_log_events.side_effect = [
            {'events': [{'message': 'log1'}]},
        ]

        result = download_logs.get_logs("test_group", "2023-01-01T00:00:00", "")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['message'], 'log1')

    @patch('boto3.client')
    def test_get_logs_empty_result(self, mock_boto_client):
        mock_logs_client = MagicMock()
        mock_boto_client.return_value = mock_logs_client

        mock_logs_client.filter_log_events.return_value = {'events': []}

        result = download_logs.get_logs("test_group", "2023-01-01T00:00:00", "2023-01-02T00:00:00")
        self.assertEqual(len(result), 0)

    def test_get_logs_empty_start_time(self):
        with self.assertRaises(ValueError):
            download_logs.get_logs("test_group", "", "2023-01-02T00:00:00")

    def test_get_logs_none_start_time(self):
        with self.assertRaises(ValueError):
            download_logs.get_logs("test_group", None, "2023-01-02T00:00:00")

    def test_get_logs_empty_log_group_name(self):
        with self.assertRaises(ValueError):
            download_logs.get_logs("", "2023-01-01T00:00:00", "2023-01-02T00:00:00")

    def test_get_logs_none_log_group_name(self):
        with self.assertRaises(ValueError):
            download_logs.get_logs(None, "2023-01-01T00:00:00", "2023-01-02T00:00:00")

    @patch('boto3.client')
    def test_get_logs_boto3_exception(self, mock_boto_client):
        mock_logs_client = MagicMock()
        mock_boto_client.return_value = mock_logs_client
        mock_logs_client.filter_log_events.side_effect = Exception("Boto3 Error")

        with self.assertRaises(Exception) as context:
            download_logs.get_logs("test_group", "2023-01-01T00:00:00", "2023-01-02T00:00:00")

        self.assertEqual(str(context.exception), "Boto3 Error")
