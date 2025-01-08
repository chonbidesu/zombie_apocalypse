import os
import csv

def combine_text_files_to_csv(output_filename="block_names.csv"):
    """
    Combines all .txt files in the current folder into a single CSV file.
    
    The filenames (without extensions) are used as column headers, and the text file contents
    are populated below the respective headers.

    Args:
        output_filename (str): Name of the output CSV file.
    """
    # Get a list of all .txt files in the current directory
    text_files = [f for f in os.listdir('.') if f.endswith('.txt')]

    if not text_files:
        print("No .txt files found in the current directory.")
        return

    # Read the contents of each file into a dictionary
    data = {}
    max_lines = 0  # Track the maximum number of lines among the files
    for file in text_files:
        with open(file, 'r', encoding='utf-8') as f:
            # Use the filename without the extension as the column header
            column_header = os.path.splitext(file)[0]
            lines = [line.strip() for line in f.readlines()]
            data[column_header] = lines
            max_lines = max(max_lines, len(lines))

    # Write the combined data to a CSV file
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write the headers (filenames without extensions)
        writer.writerow(data.keys())

        # Write the data row by row
        for i in range(max_lines):
            row = [data[header][i] if i < len(data[header]) else '' for header in data]
            writer.writerow(row)

    print(f"CSV file '{output_filename}' has been created successfully.")

# Uncomment the line below to execute the function
combine_text_files_to_csv()
