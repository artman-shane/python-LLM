import logging
from logging.handlers import RotatingFileHandler
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

# Configure logging
if not os.path.exists(os.getenv("LOGGING_FOLDER")):
    os.makedirs(os.getenv("LOGGING_FOLDER"), exist_ok=True)
log_file = os.path.join(os.getenv("LOGGING_FOLDER"),os.getenv("LOGGING_FILE"))
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=10) # 5MB log files, 10 files
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)

systemTools = SystemTools(logging)

# Main function

try:
    # set the default filenames
    inputFilename = ""
    outputFilename = ""
    
    # Get the filename of the file to read
    fileHandler = HandleFiles(logging)

    # Get the flags
    flagMgmt = FlagsMgmt(logging,sys.argv[1:])
 
    folder_path = fileHandler.folder_path
    logging.info(f"Folder path: {folder_path}")
    # Setup the LLM
    llm = LLM(logging)

    # Get the filename of the file to read
    while inputFilename.endswith('.xlsx') == False and inputFilename.endswith('.pdf') == False:
        print(f"Input Filename - needs to end with .pdf or .xlsx and exist in /{folder_path}/: ")
        inputFilename = fileHandler.getFilename(folder_path)
    
    logging.info(f"Input Filename: {inputFilename}")
    
    # Get the filename of the file to write the answers
    while outputFilename.endswith('.xlsx') == False:
        print(f"\nOutput Filename - it will be created in /{folder_path}/")
        outputFilename = fileHandler.get_input("Enter the filename for the answers file. (e.g. answers.xlsx): ")
        if outputFilename.endswith('.xlsx') == False:
            print(f"\nPlease try again. The filename needs to end with .xlsx\n\n")
    
    logging.info(f"Output Filename: {outputFilename}")

    # Now we need read the questions
    logging.info(f"Folder and file: {os.path.join(folder_path, inputFilename)}")

    if inputFilename.endswith('.xlsx'):
        logging.info("Reading xlsx file")

        # Read the input from the excel file
        # Output is a JSON str
        questions = fileHandler.read_xlsx(os.path.join(folder_path, inputFilename))
        logging.debug(f"Questions:\n{questions}\n\n")
        logging.info(f"Process questions")
        
        if flagMgmt.processQuestions:
            logging.info("Flag to process questions is set")
            results = fileHandler.process_questions(questions, flagMgmt, llm)
            logging.debug(f"Results:\n{results}\n\n")
            print(f"Writing questions and answers to file...")
            logging.ingo(f"Writing questions and answers to file...")
            fileHandler.write_xlsx(os.path.join(fileHandler.folder_path, outputFilename), json.dumps(results))
            logging.debug(f"Results sent to write_xlsx:\ntype(results): {type(results)}\n{json.dumps(results)}\n\n")
        else:
            # Flatten questions
            questions_json = json.loads(questions)
            logging.debug(f"Questions JSON:\n{questions_json}\n\n")
            logging.info(f"Flatten questions")
            flat_questions = systemTools.getFlatJson(questions_json)
            logging.debug(f"Flat questions:\n{flat_questions}\n\n")

            logging.info(f"Writing questions to file...")
            logging.info(f"Path and Filename: {os.path.join(fileHandler.folder_path, outputFilename)}")
            print(f"Writing questions to file...")
            fileHandler.write_xlsx(os.path.join(fileHandler.folder_path, outputFilename), flat_questions)

    elif inputFilename.endswith('.pdf'):
        logging.info("Reading pdf file")
        print("Reading pdf file")
        # Read the input from the pdf file and process questions
        logging.info(f"Input Filename: {inputFilename}")
        logging.info(f"Output Filename: {outputFilename}")
        results = fileHandler.process_pdf(inputFilename, flagMgmt, llm)
        # Results is a json string of questions. NOT object
        # Check if we should answer questions now or just write the questions to a file.
        logging.debug(f"PDF Results:\nPDF Results Type: {type(results)}\n{results}\n\n")
        if flagMgmt.processQuestions:
            logging.info("Flag to process questions is set")
            print(f"Getting answers to questions...")
            logging.info("Getting answers to questions...")
            logging.debug(f"Output Filename: {outputFilename}")
            results = fileHandler.process_questions(results, flagMgmt, llm)
            logging.debug(f"Question Results:\n{results}\n\n")

        # Write the results to an Excel file.
        # results could be a list of questions or a list of questions and answers
        logging.info(f"Writing results to {os.path.join(fileHandler.folder_path, outputFilename)}")
        fileHandler.write_xlsx(os.path.join(fileHandler.folder_path, outputFilename), json.dumps(results))   

except Exception as e:
    logging.critical(f"\nAn error occurred: {traceback.format_exc()}\n\n{e}\n")
    print(f"\n\nError: {e}\n")
    sys.exit(1)
except KeyboardInterrupt:
    logging.warning("\nUser cancelled the request. Exiting now.")
    print("\nUser cancelled the request. Exiting now.")
    sys.exit(0)