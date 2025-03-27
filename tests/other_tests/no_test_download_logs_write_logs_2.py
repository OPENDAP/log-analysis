import os
import tempfile
import unittest

from download_logs import write_logs


class TestWriteLogs(unittest.TestCase):

    def test_all_events_none(self):
        """Test that passing None for all_events raises ValueError."""
        with self.assertRaises(ValueError) as context:
            write_logs(None, "dummy.txt")
        self.assertEqual(str(context.exception), "all_events is empty")

    def test_output_file_empty(self):
        """
        Test that passing an empty string or None for output_file raises ValueError.
        I had to fix this test. jhrg 3/25/25
        """
        events = [{'message': '{"event": 1}'}, {'message': '{"event": 2}'}]
        with self.assertRaises(ValueError) as context:
            write_logs(events, "")
        self.assertEqual(str(context.exception), "output_file is empty")

        with self.assertRaises(ValueError) as context:
            write_logs(events, None)
        self.assertEqual(str(context.exception), "output_file is empty")

    def test_valid_json_events(self):
        """Test that valid JSON messages are written correctly."""
        events = [{'message': '{"event": 1}'}, {'message': '{"event": 2}'}]
        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tmp:
            filename = tmp.name
        try:
            write_logs(events, filename)
            with open(filename, 'r') as f:
                content = f.read()
            expected_output = "[\n" \
                              '{"event": 1},\n' \
                              '{"event": 2}\n' \
                              "]\n"
            self.assertEqual(content, expected_output)
        finally:
            os.remove(filename)

    def test_last_message_non_json(self):
        """Test that if the last message does not start with '{', the placeholder is written."""
        events = [{'message': '{"event": 1}'}, {'message': 'non-json'}]
        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tmp:
            filename = tmp.name
        try:
            write_logs(events, filename)
            with open(filename, 'r') as f:
                content = f.read()
            expected_output = "[\n" \
                              '{"event": 1},\n' \
                              '{"placeholder-record": "placeholder-value"}\n' \
                              "]\n"
            self.assertEqual(content, expected_output)
        finally:
            os.remove(filename)

    def test_single_event_json(self):
        """Test that a single JSON event is written correctly."""
        events = [{'message': '{"event": 1}'}]
        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tmp:
            filename = tmp.name
        try:
            write_logs(events, filename)
            with open(filename, 'r') as f:
                content = f.read()
            expected_output = "[\n" \
                              '{"event": 1}\n' \
                              "]\n"
            self.assertEqual(content, expected_output)
        finally:
            os.remove(filename)

    def test_single_event_non_json(self):
        """Test that a single non-JSON event results in the placeholder record."""
        events = [{'message': 'not a json message'}]
        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tmp:
            filename = tmp.name
        try:
            write_logs(events, filename)
            with open(filename, 'r') as f:
                content = f.read()
            expected_output = "[\n" \
                              '{"placeholder-record": "placeholder-value"}\n' \
                              "]\n"
            self.assertEqual(content, expected_output)
        finally:
            os.remove(filename)

    def test_empty_events_list(self):
        """
        Test that an empty events list raises an IndexError (due to accessing all_messages[-1]).
        I fixed this test. jhrg 3/25/25
        """
        events = []
        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tmp:
            filename = tmp.name
        try:
            with self.assertRaises(ValueError):
                write_logs(events, filename)
        finally:
            os.remove(filename)


if __name__ == '__main__':
    unittest.main()
