import unittest
import json
import os
import tempfile

# Assuming your function is in a file named download_logs.py
import download_logs


class TestWriteLogs(unittest.TestCase):

    def setUp(self):
        self.output_file = "test_logs.json"

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_empty_events(self):
        with self.assertRaises(ValueError):
            download_logs.write_logs([], self.output_file)

    def test_single_event(self):
        events = [{"message": '{"key": "value"}'}]
        download_logs.write_logs(events, self.output_file)
        with open(self.output_file, 'r') as f:
            content = f.read()
            self.assertEqual(content.strip(), '[\n{"key": "value"}\n]')

    def test_multiple_events(self):
        events = [{"message": '{"key1": "value1"}'}, {"message": '{"key2": "value2"}'},
                  {"message": '{"key3": "value3"}'}]
        download_logs.write_logs(events, self.output_file)
        with open(self.output_file, 'r') as f:
            content = f.read()
            self.assertEqual(content.strip(), '[\n{"key1": "value1"},\n{"key2": "value2"},\n{"key3": "value3"}\n]')

    def test_mixed_events(self):
        # I had to fix this test. jhrg 3/25/25
        events = [{"message": '{"key1": "value1"}'}, {"message": "not json"}, {"message": '{"key3": "value3"}'}]
        download_logs.write_logs(events, self.output_file)
        with open(self.output_file, 'r') as f:
            content = f.read()
            self.assertEqual(content.strip(), '[\n{"key1": "value1"},\n{"key3": "value3"}\n]')

    def test_none_events(self):
        with self.assertRaises(ValueError):
            download_logs.write_logs(None, self.output_file)

    def test_empty_output_file(self):
        events = [{"message": '{"key": "value"}'}]
        with self.assertRaises(ValueError):
            download_logs.write_logs(events, "")

    def test_none_output_file(self):
        events = [{"message": '{"key": "value"}'}]
        with self.assertRaises(ValueError):
            download_logs.write_logs(events, None)


if __name__ == '__main__':
    unittest.main()
