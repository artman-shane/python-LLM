import json
import sys
import os
from dotenv import load_dotenv
# Custom libraries
from tools.handleFiles import HandleFiles
from tools.llm import LLM
from tools.systemTools import SystemTools
from tools.flagManagement import FlagsMgmt
from tools.logging import Logging
import csv

# Load the environment variablese
load_dotenv()
# Clear screen
os.system('cls' if os.name == 'nt' else 'clear')

# Configure logging
if not os.path.exists(os.getenv("LOGGING_FOLDER")):
    os.makedirs(os.getenv("LOGGING_FOLDER"), exist_ok=True)

logger = Logging().logger
systemTools = SystemTools(logger)

# set the default filenames
inputFilename = ""
outputFilename = ""

# Get the filename of the file to read
fileHandler = HandleFiles(logger)
systemTools.set_file_handler(fileHandler)

# Get the flags
flagMgmt = FlagsMgmt(logger,sys.argv[1:])

folder_path = 'output/'
logger.info(f"Folder path: {folder_path}")
# Setup the LLM
llm = LLM(logger)

# Get the filename of the file to read
inputFilename = 'output/documents.json'

logger.info(f"Input Filename: {inputFilename}")

# Read the JSON file and load it into a Python object
try:
    with open(inputFilename, 'r') as json_file:
        data = json.load(json_file)
        print(f"\n\n\n\n\n{data}")
        logger.info("JSON data successfully loaded into a Python object.")

except FileNotFoundError:
    logger.error(f"File {inputFilename} not found.")
    print(f"File {inputFilename} not found.")
    sys.exit(1)
except json.JSONDecodeError:
    logger.error(f"Error decoding JSON from file {inputFilename}.")
    print(f"Error decoding JSON from file {inputFilename}.")
    sys.exit(1)
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

# Define the output CSV filename
outputFilename = 'output.csv'
logger.info(f"Output Filename: {outputFilename}")

# Check if data is a list of dictionaries
def write_dict_to_csv(data_dict, csv_writer):
    for key, value in data_dict.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    write_dict_to_csv(item, csv_writer)
                else:
                    csv_writer.writerow({key: item})
        elif isinstance(value, dict):
            write_dict_to_csv(value, csv_writer)
        else:
            csv_writer.writerow({key: value})

if isinstance(data, dict):
    headers = set()

    # Collect all possible headers
    def collect_headers(d):
        for key, value in d.items():
            headers.add(key)
            if isinstance(value, dict):
                collect_headers(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        collect_headers(item)

    collect_headers(data)

    try:
        # Write the data to a CSV file
        with open(outputFilename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            write_dict_to_csv(data, writer)
            logger.info("Data successfully written to CSV.")
    except IOError as e:
        logger.error(f"An I/O error occurred: {e}")
else:
    logger.error("Data is not in the expected format (dictionary).")