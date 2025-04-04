import argparse

# Create the parser
parser = argparse.ArgumentParser(description="A simple command-line program")

# Define the arguments
parser.add_argument("filename", help="The name of the file to process")
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")

# Parse the arguments
args = parser.parse_args()

# Use the arguments in the program
if args.verbose:
    print(f"Processing the file: {args.filename} with verbose output.")
else:
    print(f"Processing the file: {args.filename}")
