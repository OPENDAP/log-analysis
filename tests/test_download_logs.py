import unittest
import tempfile
import os
import json
from datetime import datetime
from io import StringIO
import contextlib
from unittest.mock import patch, MagicMock

# Import the function from the module.
from download_logs import download_logs


class TestDownloadLogs(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for output.
        self.output_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.output_file.close()  # We'll use its name for the function.
        self.log_group_name = "test-log-group"
        self.start_time = "2025-01-01T00:00:00"
        self.end_time = "2025-01-01T01:00:00"

    def tearDown(self):
        # Remove the temporary file if it exists.
        if os.path.exists(self.output_file.name):
            os.remove(self.output_file.name)

    @patch('download_logs.boto3.client')
    def test_download_logs_with_pagination(self, mock_boto_client):
        """
        Test the download_logs function with simulated pagination (two pages of events).
        """
        # Set up the mock client and its responses.
        mock_client_instance = MagicMock()
        mock_boto_client.return_value = mock_client_instance

        # Simulate two pages: first call returns a nextToken; second call ends pagination.
        first_response = {
            "events": [{"message": '{"log": "entry1"}'}],
            "nextToken": "token1"
        }
        second_response = {
            "events": [{"message": '{"log": "entry2"}'}]
            # No nextToken means the pagination is done.
        }
        mock_client_instance.filter_log_events.side_effect = [first_response, second_response]

        # Capture printed output.
        with StringIO() as out, contextlib.redirect_stdout(out):
            download_logs(self.log_group_name, self.start_time, output_file=self.output_file.name)
            printed_output = out.getvalue()

        # Verify that the printed output contains expected messages.
        self.assertIn(f"Fetching logs from '{self.log_group_name}' starting at {self.start_time}", printed_output)
        self.assertIn("Logs saved to", printed_output)

        # Read the output file and verify its content.
        with open(self.output_file.name, 'r') as f:
            file_content = f.read()

        # Based on the function’s logic:
        #   For two events, all_messages = ['{"log": "entry1"}', '{"log": "entry2"}'].
        #   The for-loop processes only the first element,
        #   then the if-block erroneously prints the variable 'message'
        #   (still set to the first element) instead of the last message.
        # Therefore, we expect '{"log": "entry1"}' to appear twice,
        # and '{"log": "entry2"}' should not be present.
        self.assertIn('{"log": "entry1"}', file_content)
        self.assertEqual(file_content.count('{"log": "entry1"}'), 2)
        self.assertNotIn('{"log": "entry2"}', file_content)
        self.assertIn('{"placeholder-record": "placeholder-value"}', file_content)
        self.assertIn("[", file_content)
        self.assertIn("]", file_content)

    @patch('download_logs.boto3.client')
    def test_download_logs_with_end_time(self, mock_boto_client):
        """
        Test that providing an end_time results in filter_log_events being called
        with the correct 'endTime' parameter.
        """
        mock_client_instance = MagicMock()
        mock_boto_client.return_value = mock_client_instance

        # Simulate a response with two events and no pagination.
        response = {
            "events": [
                {"message": '{"log": "entry1"}'},
                {"message": '{"log": "entry2"}'}
            ]
        }
        mock_client_instance.filter_log_events.return_value = response

        with StringIO() as out, contextlib.redirect_stdout(out):
            download_logs(self.log_group_name, self.start_time, end_time=self.end_time,
                          output_file=self.output_file.name)
            printed_output = out.getvalue()

        # Compute the expected endTime (in milliseconds since epoch).
        expected_end_timestamp = int(datetime.strptime(self.end_time, "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)

        # Check that at least one call to filter_log_events included the correct 'endTime'.
        calls = mock_client_instance.filter_log_events.call_args_list
        end_time_found = any(
            'endTime' in call.kwargs and call.kwargs['endTime'] == expected_end_timestamp for call in calls)
        self.assertTrue(end_time_found, "filter_log_events was not called with the correct 'endTime' parameter.")

    @patch('download_logs.boto3.client')
    def test_download_logs_single_event_error(self, mock_boto_client):
        """
        Test that if only a single event is returned the function raises an error.

        Note: With a single event, the for-loop does not iterate so that the variable 'message'
        is never set before it is used in the if-block. This should raise an UnboundLocalError.
        """
        mock_client_instance = MagicMock()
        mock_boto_client.return_value = mock_client_instance

        response = {
            "events": [{"message": '{"log": "single entry"}'}]
        }
        mock_client_instance.filter_log_events.return_value = response

        with self.assertRaises(UnboundLocalError):
            download_logs(self.log_group_name, self.start_time, output_file=self.output_file.name)

    @patch('download_logs.boto3.client')
    def test_download_logs_empty_events_error(self, mock_boto_client):
        """
        Test that if no events are returned, the function raises an error when
        attempting to access the last element of an empty list.
        """
        mock_client_instance = MagicMock()
        mock_boto_client.return_value = mock_client_instance

        response = {
            "events": []  # No events returned.
        }
        mock_client_instance.filter_log_events.return_value = response

        with self.assertRaises(IndexError):
            download_logs(self.log_group_name, self.start_time, output_file=self.output_file.name)


if __name__ == '__main__':
    unittest.main()
