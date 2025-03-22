import csv

CONV_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/conv_trajectories/"
CONV_PREFIX = "trajectory"
CORRECTED_DIR = './corrected'

def fix_csv(input_file, output_file):
    try:
        # Open the input file for reading
        with open(input_file, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile, skipinitialspace=True)
            headers = next(reader)  # Read the headers
            
            # Open the output file for writing
            with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)  # Ensure all fields are quoted
                writer.writerow(headers)  # Write the headers

                # Process and rewrite each row
                for row in reader:
                    # Handle cases where rows might span across multiple lines
                    try:
                        writer.writerow(row)
                    except Exception as e:
                        print(f"Error processing row: {row} - {e}")
                        
        print(f"Corrected file written to: {output_file}")

    except FileNotFoundError:
        print(f"File not found: {input_file}")
    except Exception as e:
        print(f"Error: {e}")


# if __name__ == '__main__':
    # Run the correction
    
    # for i in range(28):
    #     fix_csv(input_file, output_file)
