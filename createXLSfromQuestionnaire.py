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
try:
    log_file = os.path.join(os.getenv("LOGGING_FOLDER"),os.getenv("LOGGING_FILE"))
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=10) # 5MB log files, 10 files
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(str.upper(os.getenv("LOGGING_LEVEL")))
except Exception as e:
    print(f"An error occurred while setting up the logging: {e}")
    print(f"Check the .env file for the LOGGING_FOLDER, LOGGING_FILE, and LOGGING_LEVEL for accuracies.")
    sys.exit(1)

systemTools = SystemTools(logger)

# Main function

try:
    # set the default filenames
    inputFilename = ""
    outputFilename = ""
    
    # Get the filename of the file to read
    fileHandler = HandleFiles(logger)

    # Get the flags
    flagMgmt = FlagsMgmt(logger,sys.argv[1:])
 
    folder_path = fileHandler.folder_path
    logger.info(f"Folder path: {folder_path}")
    # Setup the LLM
    llm = LLM(logger)

    # Get the filename of the file to read
    while inputFilename.endswith('.xlsx') == False and inputFilename.endswith('.pdf') == False:
        print(f"Input Filename - needs to end with .pdf or .xlsx and exist in /{folder_path}/: ")
        inputFilename = fileHandler.getFilename(folder_path)
    
    logger.info(f"Input Filename: {inputFilename}")
    
    # Get the filename of the file to write the answers
    while outputFilename.endswith('.xlsx') == False:
        print(f"\nOutput Filename - it will be created in /{folder_path}/")
        outputFilename = fileHandler.get_input("Enter the filename for the answers file. (e.g. answers.xlsx): ")
        if outputFilename.endswith('.xlsx') == False:
            print(f"\nPlease try again. The filename needs to end with .xlsx\n\n")
    
    logger.info(f"Output Filename: {outputFilename}")

    # Now we need read the questions
    logger.info(f"Folder and file: {os.path.join(folder_path, inputFilename)}")

    if inputFilename.endswith('.xlsx'):
        logger.info("Reading xlsx file")

        # Read the input from the excel file
        # Output is a JSON str
        questions = fileHandler.read_xlsx(os.path.join(folder_path, inputFilename))
        logger.debug(f"Questions:\n{questions}\n\n")
        logger.info(f"Process questions")
        
        if flagMgmt.processQuestions:
            logger.info("Flag to process questions is set")
            results = fileHandler.process_questions(questions, flagMgmt, llm)
            logger.debug(f"Results:\n{results}\n\n")
            print(f"Writing questions and answers to file...")
            logger.ingo(f"Writing questions and answers to file...")
            fileHandler.write_xlsx(os.path.join(fileHandler.folder_path, outputFilename), json.dumps(results))
            logger.debug(f"Results sent to write_xlsx:\ntype(results): {type(results)}\n{json.dumps(results)}\n\n")
        else:
            # Flatten questions
            questions_json = json.loads(questions)
            logger.debug(f"Questions JSON:\n{questions_json}\n\n")
            logger.info(f"Flatten questions")
            flat_questions = systemTools.getFlatJson(questions_json)
            logger.debug(f"Flat questions:\n{flat_questions}\n\n")

            logger.info(f"Writing questions to file...")
            logger.info(f"Path and Filename: {os.path.join(fileHandler.folder_path, outputFilename)}")
            print(f"Writing questions to file...")
            fileHandler.write_xlsx(os.path.join(fileHandler.folder_path, outputFilename), flat_questions)

    elif inputFilename.endswith('.pdf'):
        logger.info("Reading pdf file")
        print("Reading pdf file")
        # Read the input from the pdf file and process questions
        logger.info(f"Input Filename: {inputFilename}")
        logger.info(f"Output Filename: {outputFilename}")
        results = fileHandler.process_pdf(inputFilename, flagMgmt, llm)
        # Results is a json string of questions. NOT an object
        # Check if we should answer questions now or just write the questions to a file.
        logger.debug(f"PDF Results:\nPDF Results Type: {type(results)}\n{results}\n\n")
        if flagMgmt.processQuestions:
            logger.info("Flag to process questions is set")
            print(f"Getting answers to questions...")
            logger.info("Getting answers to questions...")
            logger.info(f"Output Filename: {outputFilename}")
            results = fileHandler.process_questions(results, flagMgmt, llm)
            logger.debug(f"Question Results:\n{results}\n\n")

        # Write the results to an Excel file.
        # Process results to output file
        if not isinstance(results, str):
            logger.info(f"Results is not a string. Converting to string.")
            results = json.dumps(results)
        logger.info(f"Writing questions and answers to excel")
        fileHandler.write_xlsx(os.path.join(fileHandler.folder_path, outputFilename), results)
        logger.info(f"Processing is complete.")
        print(f"Processing is complete.\n\n\n\n")
        # This is to shut down the logger or it might result in a memory leak and exepction.
        logger.removeHandler(handler)
except Exception as e:
    logger.critical(f"\nAn error occurred: {traceback.format_exc()}\n\n{e}\n")
    print(f"\n\nError: {e}\n")
    sys.exit(1)
except KeyboardInterrupt:
    logger.warning("\nUser cancelled the request. Exiting now.")
    print("\nUser cancelled the request. Exiting now.")
    sys.exit(0)