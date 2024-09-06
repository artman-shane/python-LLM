# System libraries
from dotenv import load_dotenv
import os
import sys

# Custom libraries
import handleFiles
import chatApp

# Third-party libraries
from openai import OpenAI # Used to interact with the OpenAI API

# Load the environment variables
load_dotenv()

# Clear the screen when starting user input first time
os.system('cls' if os.name == 'nt' else 'clear')

# Main code block
try:
    # Create an instance of the ChatApp class
    fileHandler = handleFiles.HandleFiles()
    folder_path = fileHandler.folder_path
    filename = fileHandler.getFilename(folder_path)
    # print(f"Filename: {filename}")
    app = chatApp.ChatApp(fileHandler, folder_path,filename)

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