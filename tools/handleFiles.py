# System libraries
import datetime
from io import StringIO
import re
# from dotenv import load_dotenv
import os
import json
import traceback # Used to convert the DataFrame to a JSON object

from tools.systemTools import SystemTools

# Third-party libraries
import PyPDF2 # Used to read PDF files
import pandas as pd # Used to read Excel files


# Class to handle file operations
class HandleFiles:
    def __init__(self, logger):
        self.logger = logger
        # load_dotenv(override=True)
        self.systemTools = SystemTools(logger)

        self.logger.debug(f"***** BEGIN class init HandleFiles *****")
        self.folder_path = os.getenv('DOCUMENTS_FOLDER_PATH')
        self.logger.info(f"Documents folder path: {self.folder_path}")
        self.logger.debug(f"***** END class init HandleFiles *****")

    def getFilename(self, _folder_path):
        self.logger.debug(f"***** BEGIN func getFilename *****")
        while True:
            try:
                # Prompt the user for a filename
                response = input(f"Enter the filename to read: (in ./{self.folder_path}/ folder):")
                if os.path.exists(f"{_folder_path}/{response}"):
                    # print(f"Filename found...")
                    self.logger.info(f"***** END func getFilename *****")
                    return response
                else:
                    print(f"Invalid filename {response}. Please try again.")
            # Handle exceptions for keyboard interrupt
            except KeyboardInterrupt:
                # Exit the loop if Ctrl-C is pressed
                raise ValueError("\nUser cancelled in filename collection")
            # Handle all other exceptions
            except Exception as e:  
                raise ValueError({e})
    
    # Function to get input from the user
    # Parameters:
    # prompt - the message to display to the user
    def get_input(self, prompt):
        self.logger.debug(f"***** BEGIN func get_input *****")
        try:
            # Prompt the user for input
            response = input(prompt)
            self.logger.debug(f"***** END func get_input *****")
            return response
        except KeyboardInterrupt:
            # Exit the loop if Ctrl-C is pressed
            raise ValueError("\nUser cancelled during input")
        except Exception as e:
            raise ValueError({e})
    
    # Function to read a PDF file
    def read_pdf_file(self, file_path):
        self.logger.debug(f"***** BEGIN func read_pdf_file *****")
        print(f"\n\nReading pdf file: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                print(f"Number of pages in the PDF: {num_pages}")
                if int(os.getenv('MAX_PDF_PAGES')) > 0: print(f"Processing limited to {os.getenv('MAX_PDF_PAGES')} pages per .env")
                text = ""
                x=0
                for page in reader.pages:
                    if x < 78:
                        text += page.extract_text()
                    x+=1
            self.logger.debug(f"***** END func read_pdf_file *****")
            return text
        except Exception as e:
            raise ValueError({e})
    
    # Function to read a PDF file
    def read_pdf_pages(self, file_path):
        self.logger.debug(f"***** BEGIN func read_pdf_pages *****")
        print(f"\n\nReading pdf file: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                pages_text = []
                print(f"Number of pages in the PDF: {num_pages}")
                if int(os.getenv('MAX_PDF_PAGES')) > 0: print(f"Processing limited to {os.getenv('MAX_PDF_PAGES')} pages")
                x=0
                for page in reader.pages:
                    pages_text.append(page.extract_text())
            self.logger.debug(f"***** END func read_pdf_pages *****")
            return pages_text
        except Exception as e:
            raise ValueError({e})
    
    # Returning the answers as a JSON object
    # Parameters:
    # file_path - the path to the Excel file including the filename
    def read_sigLite_answers(self,file_path):
        self.logger.debug(f"***** BEGIN func read_sigLite_answers *****")
        data_dict = {}
        
        try:
            dfs = pd.read_excel(file_path, sheet_name=['Full'], header=2)
            for sheet_name, df in dfs.items():
                data_dict[sheet_name] = json.loads(df.to_json(orient='records'))

            # Convert the DataFrame to a JSON object
            self.logger.debug(f"***** END func read_sigLite_answers *****")
            return json.dumps(data_dict)

        except Exception as e:
            raise ValueError({e})

    # Function to read an Excel file
    # Parameters:
    # file_path - the path to the Excel file including the filename
    # Optional parameter:
    # headers - Header Row 0-Indexed (default = 0 - first row)
    # sheet_name - Sheetnames to read - "None" to read all sheets. String or array of string (None = default)
    def read_xlsx(self, file_path, header=0, sheet_name=None):
        self.logger.debug(f"***** BEGIN func read_xlsx *****")
        self.logger.info(f"\n\nReading Excel file: {file_path}")
        data_dict = {}
        
        try:
            if not os.path.exists(file_path):
                raise ValueError(f"\nFile not found: {file_path}")
            if file_path.endswith(".xlsx") == False:
                raise ValueError(f"\nInvalid file format. Please provide an Excel file.")
            
            self.logger.info(f"Processing...")
            dfs = pd.read_excel(file_path, sheet_name, header=header)
            self.logger.info(f"Number of sheets: {len(dfs)}")
            for sheet_name, df in dfs.items():
                data_dict[sheet_name] = json.loads(df.to_json(orient='records'))

            # Convert the DataFrame to a JSON object
            answers = json.dumps(data_dict)
            self.logger.debug(f"***** END func read_xlsx *****")
            return answers

        except Exception as e:
            raise ValueError(f"\nAn error occurred: {e}")
        
    def _create_xlsx(self, file_path):
        self.logger.debug(f"***** BEGIN func _create_xlsx *****")
        try:
            self.logger.info(f"Creating file: {file_path}")
            self.logger.info(f"Creating empty data frame...")
            # Create a DataFrame with no data.
            df = pd.DataFrame()
            self.logger.info(f"Writing to Excel file...")
            # Write the DataFrame to an Excel file
            df.to_excel(file_path, index=False)
            self.logger.info(f"File created: {file_path}")
            self.logger.debug(f"***** END func _create_xlsx *****")
            return True
        except Exception as e:
            raise ValueError({e})
    
    # Function to clean up a JSON string
    # Parameters:
    # json_str - the JSON string to clean up
    def clean_json(self, json_str):
        self.logger.debug(f"***** BEGIN func clean_json *****")
        # Clean JSON
        self.logger.info(f"Is JSON dirty?")
        # Use regular expression to find the first '{' and the last '}'
        self.logger.info(f"\n***** BEGIN DIRTY *****\n{json_str}\n***** END DIRTY *****\n")
        match = re.search(r'[\{,\[].*[\},\]]', json_str, re.DOTALL)
        if match:
            self.logger.info(f"Match Found. Cleaning JSON...")
            self.logger.info(f"JSON cleaned:\n*****BEGIN CLEANED*****\n{match.group(0)}\n***** END CLENAED *****\n")
            self.logger.debug(f"***** END func clean_json *****")
            return match.group(0)
        else:
            raise ValueError("Invalid JSON format")
        
    # Function to write to an Excel file
    # Parameters:
    # file_path - the path to the Excel file including the filename
    # data_dict - the data to write to the Excel file as a JSON object as string
    def write_xlsx(self, file_path, data_dict):
        self.logger.debug(f"func write_xlsx")
        self.logger.info(f"file_path: {file_path}")
        self.logger.info(f"data_dict type:{type(data_dict)}")
        try:
            self.logger.debug(f"***** DATA *****\n{data_dict}")

            # Clean up json string
            if isinstance(data_dict, str):
                self.logger.info(f"Data is not a string. Converting to string...")
                self.logger.info(f"Data being cleaned...")
                data_dict = self.clean_json(data_dict)

            self.logger.info(f"Checking if file exists...")
            if not os.path.exists(file_path):
                self.logger.info(f"File not found: {file_path} must be created...")
                filename = os.path.basename(file_path)
                self.logger.info(f"Filename full path to create: {filename}")
                self._create_xlsx(os.path.join(self.folder_path, filename))
                self.logger.info(f"Successfully created file: {file_path}")
            else:
                self.logger.info(f"File found: {file_path}")
            self.logger.info(f"Data to write:\n{data_dict}")
            if isinstance(data_dict, str):
                self.logger.info(f"Data is a string. Loading as JSON...")
                data = json.loads(data_dict)
            else:
                self.logger.info(f"Data is not a string.")
                self.logger.info(f"varType: data_dict: {type(data_dict)}")
                data = data_dict
            self.logger.info(f"VarType:\ndata_dict: {type(data_dict)}\ndata: {type(data)}")
            self.logger.info(f"Data as JSON: {data}")

            # Convert the JSON object to a DataFrame
            # df = pd.read_json(json.loads(data_dict))

            self.logger.info(f"Creating Blank DataFrame array...")
            combined_df = pd.DataFrame()
            self.logger.info(f"Checking number of sheets...")
            if isinstance(data, dict):
                self.logger.info(f"Dictionary Found...")
                for sheet_name in data.keys():
                    self.logger.info(f"Sheet Name: {sheet_name}")
                    df = pd.DataFrame(data[sheet_name])
                    self.logger.info(f"Inserting sheet name...")
                    df.insert(0, 'Sheet Name', sheet_name)
                    self.logger.info(f"Combining DataFrames...")
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
            else:
                self.logger.info(f"List of items found...")
                self.logger.info(f"Creating DataFrame...")
                df = pd.DataFrame(data)
                self.logger.info(f"Inserting sheet...")
                if 'Sheet Name' not in df.columns:
                    df.insert(0, 'Sheet Name', "Responses")
                self.logger.info(f"Combining DataFrames...")
                combined_df = pd.concat([combined_df, df], ignore_index=True)

            self.logger.info(f"Converting df to logic excel file...")
            self.logger.debug(f"\n***** BEGIN Data to write *****\n{combined_df}\n***** END Data to write *****\n")
            # Write the DataFrame to an Excel file
            print(f"Writing to Excel file: {file_path}")
            # If the file exists, overwrite it
            combined_df.to_excel(file_path, index=False)

            # self.logger.info(f"Writing to Excel file...")
            # # Write the DataFrame to an Excel file
            # df.to_excel(file_path, index=False)
            self.logger.debug(f"Writing to Excel is complete.")
            return True
        except Exception as e:
            raise ValueError({e})
        
    # Function to read a text file
    def read_txt_file(self, file_path):
        self.logger.debug(f"***** BEGIN func read_txt_files *****")
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            self.logger.debug(f"***** END func read_txt_files *****")
            return text
        except Exception as e:
            raise ValueError({e})
        
    # Read the questions from the json input and process them
    # Processing could include sending the questions to LLM and getting the answers or simply rewritng the questions to an output file
    # Parameters:
    # questionsFilename - the filename of the questions file
    # outputFilename - the filename of the output file
    # flagMgmt - the flag management class reference
    # llm - the LLM class reference
    # returns - json object of the questions and answers
    # TODO: Need to see if when skipping a question it still ends up in the output. If so, I need to ensure that a notation is made in the output that potential questions were skipped and specifically which ones..
    def process_questions(self, questions, flagMgmt, llm):
        self.logger.debug(f"***** BEGIN func process_questions *****")

        self.logger.info("Processing questions")
        # Convert the question JSON string into object in python
        questions_json = json.loads(questions)

        # Placeholder for responses
        responses = {}

        # Flatten the JSON object to single level for easy processing
        self.logger.info(f"questions_json type: {type(questions_json)}")
        questions_json = self.systemTools.getFlatJson(questions_json)
        print(f"Processing {len(questions_json)} questions")

        # Here we have the Questions in a JSON object from xlsx. We are in the loop to process each question.
        # If the -pq flag is set, we need to send the question to LLM and get the response when we get the answers together.
        print(f"Reading answers from {os.path.join(self.folder_path, flagMgmt.answerSource)}")
        answers = json.loads(self.read_sigLite_answers(f"{os.path.join(self.folder_path, flagMgmt.answerSource)}"))
        print(f"Processing questions and answers")
        results = []
        x=0
        for question in questions_json:
            try:
                x+=1
                # Pause the processing for testing.
                # if x==4:
                #     print("\n\n*********\nLimiting output for testing\n*********\n\n")
                #     break
                # Only output if debugging is on
                self.logger.debug(f"Question: {question}")
                for key in question: self.logger.debug(f"{key}: {question[key]}")
                # # This ONLY works for SIG LITE QUESTIONS - NEED TO FIX for Others
                # print(f"\n\n\nQuestion:\n{question}\nAnswers:\n{answers['Full']}\n\n\n")
                print(f"Processing question: {x} of {len(questions_json)}")
                returned_results = llm.getAnswers(question, answers, flagMgmt.llmPromptAnswers)

                results.append(json.loads(returned_results))
            except Exception as e:
                print(f"Could not process question {x} of {len(questions_json)}.")
                print(f"Question: {question}")
                print(f"Skipping...")
                results.append({"Question": question, "Response": "Skipped"})
                # TODO: need to add the question to the output file with a note that it was skipped
        self.logger.debug(f"GetAnswers appended Results:\n{results}")
        self.logger.debug(f"***** END func process_questions *****")

        return results
    
    # Read the questions from the json input and process them
    # Processing could include sending the questions to LLM and getting the answers or simply rewritng the questions to an output file
    # Parameters:
    # inputFilename - the filename of the input file
    # outputFilename - the filename of the output file
    # flagMgmt - the flag management class reference
    # llm - the LLM class reference
    def process_pdf(self, inputFilename, flagMgmt, llm):
        
        self.logger.debug(f"***** BEGIN func process_pdf *****")

        self.logger.info("Reading pdf file")

        # Read the input from the pdf file.
        question_pages = self.read_pdf_pages(os.path.join(self.folder_path, inputFilename))

        self.logger.debug(f"Found {len(question_pages)} pages")

        # Placeholder for questions
        questions = {}
        for page_num,page_text in enumerate(question_pages):

            try:
                # Create a begin time to determine the processing time
                currentTime = datetime.datetime.now()
                max_pdf_pages = int(os.getenv('MAX_PDF_PAGES', 0))
                # If the max_pdf_pages is set and we have reached the limit, stop processing
                # The page_num is 0-indexed. By keeping it as page_num and not adding 1, when we get to the next page we stop.
                # For example if the MAX_PDF_PAGES = 5, we will process page_num 0, 1, 2, 3, 4 and stop at 5 which is actually the 6th page.
                # If the max_pdf_pages is 0 or does not exist, we process all pages
                if max_pdf_pages > 0 and (page_num) >= max_pdf_pages:
                    print(f"Reached the maximum number of pages to process ({max_pdf_pages}) per .env.\nSkipping remaining pages...")
                    break

                print(f"Processing PDF page {page_num + 1} of {len(question_pages)}")
                messages = [
                        {"role": "system", "content": f'***Special Considerations*** {flagMgmt.llmPromptQuestions}'},
                        {"role": "system", "content": f"***General Instructions*** {os.getenv('PDF_GENERAL_INSTRUCTIONS')}"},
                        {"role": "system", "content": f"***Response Format*** {os.getenv('PDF_RESPONSE_FORMAT')}"},
                        {"role": "system", "content": f"***PDF Page Number*** {page_num + 1}"},
                        {"role": "system", "content": f"***Input to Process*** {page_text}"},
                    ]

                self.logger.info(f"LLM processing page {page_num + 1}")
                response = llm.query(messages)
            except Exception as e:
                print(f"Could not discern the questions. Skipping page {page_num + 1}...")
                self.logger.info(f"Error: {e}\ntraceback: {traceback.format_exc()}")
            
            self.logger.debug(f"Response from LLM:\n{response}")
            try:
                self.logger.info(f"Cleaning JSON")
                cleanedJson = self.clean_json(response)
                self.logger.info(f"VarType: (cleanedJson): {type(cleanedJson)}")
                # Append cleanedJson to json object
                questions[f"Page {page_num + 1}"] = json.loads(cleanedJson)
                self.logger.info(f"VarType (questions): {type(questions)}")
                # Create an end time to determine the processing time in minutes:seconds
                self.logger.info(f"Processed page {page_num+1} in {(datetime.datetime.now() - currentTime).total_seconds()} seconds\n")

            except Exception as e:
                print(f"We could not discern any questions on page {page_num + 1}. Skipping...")


        self.logger.debug(f"\n***** QUESTIONS BEGIN *****\n{questions}\n***** QUESTIONS END *****\n")
        # Returns a json string of the questions
        return json.dumps(questions)