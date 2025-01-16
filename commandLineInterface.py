# System libraries
from dotenv import load_dotenv
import os
import sys

# Custom libraries
from tools.handleFiles import HandleFiles
from tools.chatApp import ChatApp
from tools.llm import LLM
from tools.systemTools import SystemTools
from tools.flagManagement import FlagsMgmt
from tools.logging import Logging

# Third-party libraries
from openai import OpenAI # Used to interact with the OpenAI API

# Load the environment variables
load_dotenv()

# Clear the screen when starting user input first time
os.system('cls' if os.name == 'nt' else 'clear')

# Configure logging
if not os.path.exists(os.getenv("LOGGING_FOLDER")):
    os.makedirs(os.getenv("LOGGING_FOLDER"), exist_ok=True)

logger = Logging().logger
systemTools = SystemTools(logger)

# Get the flags
flagMgmt = FlagsMgmt(logger,sys.argv[1:])


# Main code block
try:
    # Create an instance of the ChatApp class
    fileHandler = HandleFiles(logger)
    folder_path = fileHandler.folder_path
    filename = fileHandler.getFilename(folder_path)
    # print(f"Filename: {filename}")
    app = ChatApp(fileHandler, folder_path,filename)

    # Loop to keep asking the user for questions
    while True:
        try:
            # Prompt the user for a question
            question = input("\n\nEnter your question (or press Ctrl-C to quit): ")

            # Call the chat function with the user's question
            response = app.chat(question)

            # Print the response
            print("\n\n", response)
        # Handle exceptions for keyboard interrupt
        except KeyboardInterrupt:
            # Exit the loop if Ctrl-C is pressed
            break
        # Handle all other exceptions
        except Exception as e:  
            print(f"\nAn error occurred: {e}")
            break
except Exception as e:
    print(f"\nAn error occurred: {e}")
    sys.exit(1)