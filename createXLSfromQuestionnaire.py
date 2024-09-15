from dotenv import load_dotenv, find_dotenv
import os
import sys
import traceback
import datetime
# System libraries

import json

# Custom libraries
from tools.handleFiles import HandleFiles
from tools.llm import LLM
from tools.systemTools import SystemTools
from tools.flagManagement import FlagsMgmt

# Load environment variables from .env file
load_dotenv(override=True)

# Clear screen
os.system('cls' if os.name == 'nt' else 'clear')

systemTools = SystemTools()
debug = systemTools.str_to_bool(os.getenv('DEBUG'))
debug_data_output = systemTools.str_to_bool(os.getenv('DEBUG_DATA_OUTPUT'))
debug_function_name = systemTools.str_to_bool(os.getenv('DEBUG_FUNCTION_NAME'))
if debug: print(f"DEBUG on = {debug}")
if debug_data_output: print(f"DEBUG on = {debug_data_output}")
if debug_function_name: print(f"DEBUG on = {debug_function_name}")

# Main function

try:
    # set the default filenames
    inputFilename = ""
    outputFilename = ""
    
    # Get the filename of the file to read
    fileHandler = HandleFiles()

    # Get the flags
    flagMgmt = FlagsMgmt(sys.argv[1:])

    folder_path = fileHandler.folder_path
    # Setup the LLM
    llm = LLM()

    # Get the filename of the file to read
    while inputFilename.endswith('.xlsx') == False and inputFilename.endswith('.pdf') == False:
        print(f"\n\nNeed the filename of the input to process.\n" \
              f"Filename needs to end with .pdf or .xlsx and exist in \"{folder_path}\"\n")
        inputFilename = fileHandler.getFilename(folder_path)
    
    # Get the filename of the file to write the answers
    while outputFilename.endswith('.xlsx') == False:
        print(f"\nPlease provide the filename for writing output. It will be created in\"{folder_path}")
        outputFilename = fileHandler.get_input("Enter the filename for the answers file. (e.g. answers.xlsx)\n")
        if outputFilename.endswith('.xlsx') == False:
            print(f"\nPlease try again. The filename needs to end with .xlsx\n\n")

    # Now we need read the questions
    print(f"Folder and file: {os.path.join(folder_path, inputFilename)}")

    if inputFilename.endswith('.xlsx'):
        print("Reading xlsx file")

        # Read the input from the excel file
        # Output is a JSON str
        questions = fileHandler.read_xlsx(os.path.join(folder_path, inputFilename))
        print(f"Process questions")
        fileHandler.process_questions(questions, outputFilename, flagMgmt, llm)

    elif inputFilename.endswith('.pdf'):
        print("Reading pdf file")
        # Read the input from the pdf file and process questions
        fileHandler.process_pdf(inputFilename, outputFilename, flagMgmt, llm)

except Exception as e:
    if debug:
        print(f"\nAn error occurred: {traceback.format_exc()}\n\n{e}\n")
    else:
        print(f"\n\n\n***** An error occurred *****\n{e}\n")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nUser cancelled the request. Exiting now.")
    sys.exit(0)