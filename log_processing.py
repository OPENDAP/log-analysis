import csv
from datetime import datetime
import argparse

def transform_logs_to_csv(input_file, output_file):
    """
    Transforms log lines from a custom format to CSV, converting Unix timestamps to ISO time strings
    and retaining microsecond values in 'timing' lines.

    Parameters:
    - input_file: Path to the input file containing log lines.
    - output_file: Path to the output CSV file.
    """
    def convert_to_iso(timestamp):
        """Converts Unix time in seconds to ISO 8601 format."""
        return datetime.utcfromtimestamp(int(timestamp)).isoformat() + "Z"
    
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = infile.readlines()
        writer = csv.writer(outfile)
        
        for line in reader:
            # Split the log line by '|&|'
            fields = line.strip().split('|&|')
            
            # Convert the first field (assumed to be Unix time) to ISO 8601
            try:
                fields[0] = convert_to_iso(fields[0])
            except ValueError:
                pass  # If conversion fails, keep the original value

            # Write the transformed line to the CSV file
            writer.writerow(fields)


def main():
    parser = argparse.ArgumentParser(description="blah blah blah.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-l", "--log", help="stuff.", required=True)
    parser.add_argument("-o", "--out", help="stuff.", required=True)

    # parser.add_argument("providers", nargs="*")

    args = parser.parse_args()
    transform_logs_to_csv(args.log, args.out)


if __name__ == "__main__":
    main()

# Input and output file paths
#input_file = "logs.txt"  # Replace with the path to your input file
#output_file = "transformed_logs.csv"  # Replace with the desired output file path

#transform_logs_to_csv(input_file, output_file)
