import unittest
from unittest.mock import MagicMock, patch
from download_logs import get_logs
import datetime


class TestGetLogs(unittest.TestCase):

    def test_invalid_start_time_empty(self):
        """Test that an empty start_time raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            get_logs("test-log-group", "", "2023-01-01T01:00:00")
        self.assertEqual(str(context.exception), "start_time is empty")

    def test_invalid_log_group_name_empty(self):
        """Test that an empty log_group_name raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            get_logs("", "2023-01-01T00:00:00", "2023-01-01T01:00:00")
        self.assertEqual(str(context.exception), "log_group_name is empty")

    @patch('download_logs.boto3.client')
    def test_single_page_response(self, mock_boto_client):
        """Test get_logs returns events from a single page response."""
        fake_client = MagicMock()
        # Simulate a single page response with no pagination.
        fake_client.filter_log_events.return_value = {
            'events': [{'message': 'log1'}, {'message': 'log2'}],
            'nextToken': None
        }
        mock_boto_client.return_value = fake_client

        log_group_name = "test-group"
        start_time = "2023-01-01T00:00:00"
        end_time = "2023-01-01T01:00:00"
        result = get_logs(log_group_name, start_time, end_time)
        self.assertEqual(result, [{'message': 'log1'}, {'message': 'log2'}])

        # Verify that filter_log_events was called with the expected parameters.
        start_timestamp = int(datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
        end_timestamp = int(datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
        fake_client.filter_log_events.assert_called_with(
            logGroupName=log_group_name,
            startTime=start_timestamp,
            endTime=end_timestamp
        )

    @patch('download_logs.boto3.client')
    def test_paginated_response(self, mock_boto_client):
        """Test get_logs handles paginated responses correctly."""
        fake_client = MagicMock()
        # Simulate paginated responses:
        # First call returns a nextToken; second call returns no nextToken.
        fake_client.filter_log_events.side_effect = [
            {'events': [{'message': 'log1'}], 'nextToken': 'token'},
            {'events': [{'message': 'log2'}], 'nextToken': None}
        ]
        mock_boto_client.return_value = fake_client

        log_group_name = "test-group"
        start_time = "2023-01-01T00:00:00"
        end_time = "2023-01-01T01:00:00"
        result = get_logs(log_group_name, start_time, end_time)
        self.assertEqual(result, [{'message': 'log1'}, {'message': 'log2'}])

    @patch('download_logs.boto3.client')
    def test_end_time_empty(self, mock_boto_client):
        """
        Test that when end_time is an empty string,
        the 'endTime' parameter is not added to the filter_log_events call.
        """
        fake_client = MagicMock()
        fake_client.filter_log_events.return_value = {
            'events': [{'message': 'log1'}],
            'nextToken': None
        }
        mock_boto_client.return_value = fake_client

        log_group_name = "test-group"
        start_time = "2023-01-01T00:00:00"
        end_time = ""  # empty end_time
        result = get_logs(log_group_name, start_time, end_time)
        self.assertEqual(result, [{'message': 'log1'}])

        # Check that 'endTime' is not included in the parameters of the call.
        # We inspect the kwargs from the first call to filter_log_events.
        call_args = fake_client.filter_log_events.call_args[1]
        self.assertNotIn('endTime', call_args)


if __name__ == '__main__':
    unittest.main()
