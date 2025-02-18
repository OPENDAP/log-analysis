import unittest
import tempfile
import os
from io import StringIO
import contextlib

import json
from join_json_arrays import join_json_arrays

class TestJoinJsonArrays(unittest.TestCase):

    def setUp(self):
        # Create temporary files for left, right, and result.
        self.left_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.right_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.result_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)

    def tearDown(self):
        # Close and remove temporary files.
        self.left_file.close()
        self.right_file.close()
        self.result_file.close()
        os.remove(self.left_file.name)
        os.remove(self.right_file.name)
        os.remove(self.result_file.name)

    def test_basic_join(self):
        # Prepare test data
        left_data = [
            {"id": 1, "value": "left1"},
            {"id": 2, "value": "left2"},
            {"id": 3, "value": "left3"}
        ]
        right_data = [
            {"id": 1, "extra": "right1"},
            {"id": 2, "extra": "right2"}
        ]
        expected_output = [
            {"id": 1, "value": "left1", "extra": "right1"},
            {"id": 2, "value": "left2", "extra": "right2"},
            {"id": 3, "value": "left3"}
        ]
        # Write JSON data to temporary files
        json.dump(left_data, self.left_file)
        self.left_file.seek(0)
        json.dump(right_data, self.right_file)
        self.right_file.seek(0)

        # Call the function
        join_json_arrays(self.left_file.name, self.right_file.name, 'id', self.result_file.name)

        # Verify that the output file contains the expected joined records.
        with open(self.result_file.name, 'r') as f:
            joined_data = json.load(f)
        self.assertEqual(joined_data, expected_output)

    def test_missing_key_in_left(self):
        # Prepare test data with a left record missing the join key 'id'
        left_data = [
            {"id": 1, "value": "left1"},
            {"value": "missing id"}
        ]
        right_data = [
            {"id": 1, "extra": "right1"}
        ]
        json.dump(left_data, self.left_file)
        self.left_file.seek(0)
        json.dump(right_data, self.right_file)
        self.right_file.seek(0)

        # Since the second record in left_data does not have the key 'id',
        # we expect a KeyError to be raised.
        with self.assertRaises(KeyError):
            join_json_arrays(self.left_file.name, self.right_file.name, 'id', self.result_file.name)

    def test_print_output(self):
        # Test to capture the print output from the function.
        left_data = [{"id": 1, "value": "left1"}]
        right_data = [{"id": 1, "extra": "right1"}]
        json.dump(left_data, self.left_file)
        self.left_file.seek(0)
        json.dump(right_data, self.right_file)
        self.right_file.seek(0)

        out = StringIO()
        with contextlib.redirect_stdout(out):
            join_json_arrays(self.left_file.name, self.right_file.name, 'id', self.result_file.name)
        printed = out.getvalue()
        self.assertIn("Joined 1 records", printed)


if __name__ == '__main__':
    unittest.main()
