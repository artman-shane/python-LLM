from dotenv import load_dotenv
import os
import sys
import traceback
import datetime
# System libraries

import json

# Custom libraries
from tools.handleFiles import HandleFiles
from tools.llm import LLM

# Load environment variables from .env file
load_dotenv()

# Main function

try:
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get the filename of the file to read
    fileHandler = HandleFiles()
    folder_path = fileHandler.folder_path
    # Setup the LLM
    llm = LLM()
    
    # set the default filenames
    questionsFilename = "questionfile.txt"
    answersFilename = "answerfile.txt"

    # Get the filename of the file to read
    while questionsFilename.endswith('.xlsx') == False and questionsFilename.endswith('.pdf') == False:
        print(f"\nFilename needs to end with .pdf or .xlsx and exist in \"{folder_path}\"\n")
        questionsFilename = fileHandler.getFilename(folder_path)
    
    # Get the filename of the file to write the answers
    while answersFilename.endswith('.xlsx') == False:
        print(f"\nPlease provide the filename for writing answers. It will be created in\"{folder_path}")
        answersFilename = fileHandler.get_input("Enter the filename for the answers file. (e.g. answers.xlsx)")
        if answersFilename.endswith('.xlsx') == False:
            print(f"\nFilename needs to end with .xlsx\n\n")

    # Now we need read the questions
    print(f"Folder and file: {os.path.join(folder_path, questionsFilename)}")

    if questionsFilename.endswith('.xlsx'):
        print("Reading xlsx file")
        questions = fileHandler.read_xlsx(os.path.join(folder_path, questionsFilename))
        questions_json = json.loads(questions)
        for sheet in questions_json:
            print(f"Sheet: {sheet} #Qs: {len(questions_json[sheet])}")

            messages = [
                {"role": "system", "content": "You are reading a document full of questions. The questions maybe in a list similar to an excel sheet or as a paragraph."},
                {"role": "system", "content": "There may be heading pages, headers and footers and links to other documents as well as definitions."},
                {"role": "system", "content": "Some of the questions may be mingled with approapriate resposes and should be numbered but may not be."},
                {"role": "system", "content": "Please ensure that questions are built in a JSON blob so that further programble responses can be worked.."},
                {"role": "system", "content": "Read the content and understand the questions. Please then extract each question as follows:"},
                {"role": "system", "content": "[Page Number] if one is provided"},
                {"role": "system", "content": "[ID] if one is provided"},
                {"role": "system", "content": "[Question Number] if one is provided"},
                {"role": "system", "content": "[Question]"},
                {"role": "system", "content": "[Description] if one is provided"},
                {"role": "system", "content": "Output must be formated as a JSON blob with the sheet name as the key and the questions as the value."},
                {"role": "system", "content": json.dumps(questions_json[sheet])},
                ]

            response = llm.query(messages)

            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(response)
            # Write the responses to an Excel file
            fileHandler.write_xlsx(os.path.join(folder_path, answersFilename), response)   
            print("\n\n*********\n\n")

    elif questionsFilename.endswith('.pdf'):
        if os.getenv('DEBUG') == True: print("Reading pdf file")
        question_pages = fileHandler.read_pdf_pages(os.path.join(folder_path, questionsFilename))
        if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"Found {len(question_pages)} pages")
        questions = {}
        for page_num,page_text in enumerate(question_pages):

            # Create a begin time to determine the processing time
            currentTime = datetime.datetime.now()
            print(f"Processing PDF page {page_num + 1} of {len(question_pages)}")

            messages = [
                    {"role": "system", "content": "You are reading a document full of questions. The questions maybe in a list similar to an excel sheet or as a paragraph."},
                    {"role": "system", "content": "There may be heading pages, headers and footers and links to other documents as well as definitions."},
                    {"role": "system", "content": "Some of the questions may be mingled with approapriate resposes and should be numbered but may not be."},
                    {"role": "system", "content": "Please ensure that questions are built in a JSON blob so that further programble responses can be worked.."},
                    {"role": "system", "content": "Read the content and understand the questions. Please then extract each question as follows:"},
                    {"role": "system", "content": "[Page Number] if one is provided"},
                    {"role": "system", "content": "[ID] or [Question Number] if one is provided"},
                    {"role": "system", "content": "[Question]"},
                    {"role": "system", "content": "[Description] if one is provided"},
                    {"role": "system", "content": "Output must be formated as a JSON blob with each question separated as an element in the array."},
                    {"role": "system", "content": "Output must be the FULL output in the json blob"},
                    {"role": "system", "content": page_text},
                ]
            if os.getenv('DEBUB') == True: print(f"LLM processing page {page_num + 1}")
            response = llm.query(messages)

            
            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"\n***** RAW BEGIN *****\n{response}\n***** RAW END *****\n")
            cleanedJson = fileHandler.clean_json(response)
            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"\n***** CLEANSED BEGIN *****\n{cleanedJson}\n***** CLEANSED END *****\n")
            if os.getenv('DEBUG') == True: print(f"VarType: (cleanedJson): {type(cleanedJson)}")
            # Append cleanedJson to json object
            questions[f"Page {page_num + 1}"] = json.loads(cleanedJson)
            if os.getenv('DEBUG') == True: print(f"VarType (questions): {type(questions)}")
            # Create an end time to determine the processing time in minutes:seconds
            print(f"Processed page {page_num+1} in {(datetime.datetime.now() - currentTime).total_seconds()} seconds\n")


        if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"\n***** QUESTIONS BEGIN *****\n{questions}\n***** QUESTIONS END *****\n")
        # Write the responses to an Excel file
        print(f"Writing output to {os.path.join(folder_path, answersFilename)}")
        fileHandler.write_xlsx(os.path.join(folder_path, answersFilename), json.dumps(questions))   
        print(f"\nComplete...\nFound {len(question_pages)} pages in the PDF {os.path.join(folder_path,questionsFilename)}. Read and interrupted as questions.\nOutput written to {os.path.join(folder_path, answersFilename)}\n\n")
except Exception as e:
    if os.getenv('DEBUG') == True:
        print(f"\nAn error occurred: {traceback.format_exc()}\n\n{e}\n")
    else:
        print(f"\n\n\n***** An error occurred *****\n{e}\n")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nUser cancelled the request. Exiting now.")
    sys.exit(0)