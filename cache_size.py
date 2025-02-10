import os

def get_directory_stats(directory):
    """
    Calculate the total number of files and their cumulative size in a given directory.

    :param directory: The path to the directory to analyze.
    :return: A tuple (file_count, total_size).
    """
    file_count = 0
    total_size = 0

    # Iterate over all items in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Check if the item is a file
        if os.path.isfile(item_path):
            file_count += 1
            total_size += os.path.getsize(item_path)

    return file_count, total_size

if __name__ == "__main__":
    # Path to the directory you want to analyze
    # directory_path = "/path/to/your/cache/directory"
    directory_path = "/Users/jgallag4/src/hyrax500-2/sit-efs-12-18-24-2"
    MB = 1024 * 1024

    # Get stats
    try:
        file_count, total_size = get_directory_stats(directory_path)
        print(f"The directory contains {file_count} files with a total size of {total_size} bytes {total_size/MB} MB.")
    except FileNotFoundError:
        print(f"Error: The directory '{directory_path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied when accessing the directory '{directory_path}'.")
