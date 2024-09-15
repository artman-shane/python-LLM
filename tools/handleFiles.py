# System libraries
import datetime
from io import StringIO
import re
# from dotenv import load_dotenv
import os
import json # Used to convert the DataFrame to a JSON object

from tools.systemTools import SystemTools

# Third-party libraries
import PyPDF2 # Used to read PDF files
import pandas as pd # Used to read Excel files


# Class to handle file operations
class HandleFiles:
    def __init__(self):
        # load_dotenv(override=True)
        self.systemTools = SystemTools()
        self.debug = self.systemTools.str_to_bool(os.getenv('DEBUG'))
        self.debug_data_output = self.systemTools.str_to_bool(os.getenv('DEBUG_DATA_OUTPUT'))
        self.debug_function_name = self.systemTools.str_to_bool(os.getenv('DEBUG_FUNCTION_NAME'))

        if self.debug_function_name: print(f"***** BEGIN class init HandleFiles *****")
        self.folder_path = os.getenv('DOCUMENTS_FOLDER_PATH')
        if self.debug: print(f"Documents folder path: {self.folder_path}")
        if self.debug_function_name: print(f"***** END class init HandleFiles *****")

    def getFilename(self, _folder_path):
        if self.debug_function_name: print(f"***** BEGIN func getFilename *****")
        while True:
            try:
                # Prompt the user for a filename
                response = input(f"Enter the filename to read: (in ./{self.folder_path}/ folder):")
                if os.path.exists(f"{_folder_path}/{response}"):
                    # print(f"Filename found...")
                    if self.debug: print(f"***** END func getFilename *****")
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
        if self.debug_function_name: print(f"***** BEGIN func get_input *****")
        try:
            # Prompt the user for input
            response = input(prompt)
            if self.debug_function_name: print(f"***** END func get_input *****")
            return response
        except KeyboardInterrupt:
            # Exit the loop if Ctrl-C is pressed
            raise ValueError("\nUser cancelled during input")
        except Exception as e:
            raise ValueError({e})
    
    # Function to read a PDF file
    def read_pdf_file(self, file_path):
        if self.debug_function_name: print(f"***** BEGIN func read_pdf_file *****")
        print(f"\n\nReading pdf file: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                print(f"Number of pages in the PDF: {num_pages}")
                text = ""
                x=0
                for page in reader.pages:
                    if x < 78:
                        text += page.extract_text()
                    x+=1
            if self.debug_function_name: print(f"***** END func read_pdf_file *****")
            return text
        except Exception as e:
            raise ValueError({e})
    
    # Function to read a PDF file
    def read_pdf_pages(self, file_path):
        if self.debug_function_name: print(f"***** BEGIN func read_pdf_pages *****")
        print(f"\n\nReading pdf file: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                pages_text = []
                print(f"Number of pages in the PDF: {num_pages}")
                x=0
                for page in reader.pages:
                    pages_text.append(page.extract_text())
            if self.debug_function_name: print(f"***** END func read_pdf_pages *****")
            return pages_text
        except Exception as e:
            raise ValueError({e})
    
    # Returning the answers as a JSON object
    # Parameters:
    # file_path - the path to the Excel file including the filename
    def read_sigLite_answers(self,file_path):
        if self.debug_function_name: print(f"***** BEGIN func read_sigLite_answers *****")
        data_dict = {}
        
        try:
            dfs = pd.read_excel(file_path, sheet_name=['Full'], header=2)
            for sheet_name, df in dfs.items():
                data_dict[sheet_name] = json.loads(df.to_json(orient='records'))

            # Convert the DataFrame to a JSON object
            if self.debug_function_name: print(f"***** END func read_sigLite_answers *****")
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
        if self.debug_function_name: print(f"***** BEGIN func read_xlsx *****")
        if self.debug: print(f"\n\nReading Excel file: {file_path}")
        data_dict = {}
        
        try:
            if not os.path.exists(file_path):
                raise ValueError(f"\nFile not found: {file_path}")
            if file_path.endswith(".xlsx") == False:
                raise ValueError(f"\nInvalid file format. Please provide an Excel file.")
            
            if self.debug: print(f"Processing...")
            dfs = pd.read_excel(file_path, sheet_name, header=header)
            if self.debug: print(f"Number of sheets: {len(dfs)}")
            for sheet_name, df in dfs.items():
                data_dict[sheet_name] = json.loads(df.to_json(orient='records'))

            # Convert the DataFrame to a JSON object
            answers = json.dumps(data_dict)
            if self.debug_function_name: print(f"***** END func read_xlsx *****")
            return answers

        except Exception as e:
            raise ValueError(f"\nAn error occurred: {e}")
        
    def _create_xlsx(self, file_path):
        if self.debug_function_name: print(f"***** BEGIN func _create_xlsx *****")
        try:
            if self.debug: print(f"Creating file: {file_path}")
            if self.debug: print(f"Creating empty data frame...")
            # Create a DataFrame with no data.
            df = pd.DataFrame()
            if self.debug: print(f"Writing to Excel file...")
            # Write the DataFrame to an Excel file
            df.to_excel(file_path, index=False)
            if self.debug: print(f"File created: {file_path}")
            if self.debug_function_name: print(f"***** END func _create_xlsx *****")
            return True
        except Exception as e:
            raise ValueError({e})
    
    # Function to clean up a JSON string
    # Parameters:
    # json_str - the JSON string to clean up
    def clean_json(self, json_str):
        if self.debug_function_name: print(f"***** BEGIN func clean_json *****")
        # Clean JSON
        if self.debug: print(f"Is JSON dirty?")
        # Use regular expression to find the first '{' and the last '}'
        if self.debug: print(f"\n***** BEGIN DIRTY *****\n{json_str}\n***** END DIRTY *****\n")
        match = re.search(r'[\{,\[].*[\},\]]', json_str, re.DOTALL)
        if match:
            if self.debug: print(f"Match Found. Cleaning JSON...")
            if self.debug: print(f"JSON cleaned:\n*****BEGIN CLEANED*****\n{match.group(0)}\n***** END CLENAED *****\n")
            if self.debug_function_name: print(f"***** END func clean_json *****")
            return match.group(0)
        else:
            raise ValueError("Invalid JSON format")
        
    # Function to write to an Excel file
    # Parameters:
    # file_path - the path to the Excel file including the filename
    # data_dict - the data to write to the Excel file as a JSON object as string
    def write_xlsx(self, file_path, data_dict):
        if self.debug_function_name: print(f"***** BEGIN func write_xlsx *****")
        if self.debug: print(f"\n\nWriting to Excel file: {file_path}")
        try:
            if self.debug: print(f"\ndata_dict type:{type(data_dict)}")
            if self.debug_data_output: print(f"\n\n***** DATA *****{data_dict}\n\n***** DATA *****\n\n")

            # Clean up json string
            data_dict = self.clean_json(data_dict)
            if self.debug: print(f"Checking if file exists...")
            if not os.path.exists(file_path):
                if self.debug: print(f"File not found: {file_path} must be created...")
                filename = os.path.basename(file_path)
                if self.debug: print(f"Filename full path to create: {filename}")
                self._create_xlsx(os.path.join(self.folder_path, filename))
                if self.debug: print(f"Successfully created file: {file_path}")
            else:
                if self.debug: print(f"File found: {file_path}")
            if self.debug: print(f"Data to write: *****\n{data_dict}\n*****")
            if self.debug: print(f"Converting to DataFrame...")
            data = json.loads(data_dict)
            if self.debug: print(f"VarType:\ndata_dict: {type(data_dict)}\ndata: {type(data)}")
            if self.debug: print(f"Data as JSON: {data}")

            # Convert the JSON object to a DataFrame
            # df = pd.read_json(json.loads(data_dict))

            if self.debug: print(f"Creating Blank DataFrame array...")
            combined_df = pd.DataFrame()
            if self.debug: print(f"Checking number of sheets...")
            if isinstance(data, dict):
                if self.debug: print(f"Dictionary Found...")
                for sheet_name in data.keys():
                    if self.debug: print(f"Sheet Name: {sheet_name}")
                    df = pd.DataFrame(data[sheet_name])
                    if self.debug: print(f"Inserting sheet name...")
                    df.insert(0, 'Sheet Name', sheet_name)
                    if self.debug: print(f"Combining DataFrames...")
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
            else:
                if self.debug: print(f"List of items found...")
                if self.debug: print(f"Creating DataFrame...")
                df = pd.DataFrame(data)
                if self.debug: print(f"Inserting sheet...")
                df.insert(0, 'Sheet Name', "Responses")
                if self.debug: print(f"Combining DataFrames...")
                combined_df = pd.concat([combined_df, df], ignore_index=True)

            if self.debug: print(f"Converting df to logic excel file...")
            if self.debug_data_output: print(f"\n***** BEGIN Data to write *****\n{combined_df}\n***** END Data to write *****\n")
            # Write the DataFrame to an Excel file
            combined_df.to_excel(file_path, index=False)

            # if self.debug: print(f"Writing to Excel file...")
            # # Write the DataFrame to an Excel file
            # df.to_excel(file_path, index=False)
            if self.debug_function_name: print(f"***** END func write_xlsx *****")
            return True
        except Exception as e:
            raise ValueError({e})
        
    # Function to read a text file
    def read_txt_file(self, file_path):
        if self.debug_function_name: print(f"***** BEGIN func read_txt_files *****")
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            if self.debug_function_name: print(f"***** END func read_txt_files *****")
            return text
        except Exception as e:
            raise ValueError({e})
        
    # Read the questions from the json input and process them
    # Processing could include sending the questions to LLM and getting the answers or simply rewritng the questions to an output file
    # Parameters:
    # questionsFilename - the filename of the questions file
    # outputFilename - the filename of the output file
    # flagMgmt - the flag management class reference
    def process_questions(self, questions, outputFilename, flagMgmt, llm):
        # Convert the question JSON string into object in python
        questions_json = json.loads(questions)

        # Placeholder for responses
        responses = {}

        # Flatten the JSON object to single level for easy processing
        questions_json = self.systemTools.getFlatJson(questions_json)
        print(f"Processing {len(questions_json)} questions")

        # Here we have the Questions in a JSON object from xlsx. We are in the loop to process each question.
        # If the -pq flag is set, we need to send the question to LLM and get the response when we get the answers together.
        if flagMgmt.processQuestions:
            print(f"Reading answers from {os.path.join(self.folder_path, flagMgmt.answerSource)}")
            answers = json.loads(self.read_sigLite_answers(f"{os.path.join(self.folder_path, flagMgmt.answerSource)}"))
            print(f"Processing questions and answers")
            results = []
            x=0
            for question in questions_json:
                x+=1
                # Pause the processing for testing.
                # if x==3:
                #     print("\n\n*********\nLimiting output for testing\n*********\n\n")
                #     break
                # Only output if debugging is on
                if self.debug_data_output:
                    print(f"Question: {question}")
                    for key in question:
                        print(f"{key}: {question[key]}")
                    print('\n')
                # # This ONLY works for SIG LITE QUESTIONS - NEED TO FIX for Others
                # print(f"\n\n\nQuestion:\n{question}\nAnswers:\n{answers['Full']}\n\n\n")
                print(f"Processing question: {x} of {len(questions_json)}")
                returned_results = llm.getAnswers(question, answers, flagMgmt.llmPrompt)

                results.append(json.loads(returned_results))
            if self.debug_data_output: print(f"GetAnswers appended Results:\n{results}")
            self.write_xlsx(os.path.join(self.folder_path, outputFilename), json.dumps(results))
        else:
            self.write_xlsx(os.path.join(self.folder_path, outputFilename), questions_json)
        return 0
    
    # Read the questions from the json input and process them
    # Processing could include sending the questions to LLM and getting the answers or simply rewritng the questions to an output file
    # Parameters:
    # inputFilename - the filename of the input file
    # outputFilename - the filename of the output file
    # flagMgmt - the flag management class reference
    # llm - the LLM class reference
    def process_pdf(self, inputFilename, outputFilename, flagMgmt, llm):
        if self.debug: print("Reading pdf file")
        question_pages = self.read_pdf_pages(os.path.join(self.folder_path, inputFilename))
        if self.debug_data_output: print(f"Found {len(question_pages)} pages")
        questions = {}
        for page_num,page_text in enumerate(question_pages):

            # Create a begin time to determine the processing time
            currentTime = datetime.datetime.now()
            print(f"Processing PDF page {page_num + 1} of {len(question_pages)}")
            # if page_num==4:
            #     print("\n\n*********\nLimiting output for testing\n*********\n\n")
            #     break

            messages = [
                    {"role": "system", "content": "You are reading a questionnaire. We need to get the questions into a different format. You are NOT answering questions, only extracting them."},
                    {"role": "system", "content": "The questions maybe in a list similar to an excel sheet or as a paragraph."},
                    {"role": "system", "content": "There may be heading pages, headers and footers and links to other documents as well as definitions."},
                    {"role": "system", "content": "Some of the questions may be mingled with approapriate resposes and should be numbered but may not be."},
                    {"role": "system", "content": "Please ensure that questions are built in a JSON blob so that further programble responses can be worked.."},
                    {"role": "system", "content": "Please then extract each question as follows:"},
                    {"role": "system", "content": "[Page Number] if one is provided"},
                    {"role": "system", "content": "[ID] or [Question Number] - but only if one is provided. Do not add one if it is not there."},
                    {"role": "system", "content": "[Question] - We are looking for the literal text of the question. DO NOT embellish the question. "},
                    {"role": "system", "content": "[Description] - ONLY if one is provided"},
                    {"role": "system", "content": "[Choices] - If there are supplied suggested answers, please put them in this item."},
                    {"role": "system", "content": "Output must be formated as a JSON blob with each question separated as an item in the list."},
                    {"role": "system", "content": page_text},
                ]
            if self.debug: print(f"LLM processing page {page_num + 1}")
            response = llm.query(messages)

            
            if self.debug_data_output: print(f"\n***** RAW BEGIN *****\n{response}\n***** RAW END *****\n")
            try:
                cleanedJson = self.clean_json(response)
                if self.debug_data_output: print(f"\n***** CLEANSED BEGIN *****\n{cleanedJson}\n***** CLEANSED END *****\n")
                if self.debug: print(f"VarType: (cleanedJson): {type(cleanedJson)}")
                # Append cleanedJson to json object
                questions[f"Page {page_num + 1}"] = json.loads(cleanedJson)
                if self.debug: print(f"VarType (questions): {type(questions)}")
                # Create an end time to determine the processing time in minutes:seconds
                if self.debug: print(f"Processed page {page_num+1} in {(datetime.datetime.now() - currentTime).total_seconds()} seconds\n")

            except Exception as e:
                print(f"We could not discern any questions on page {page_num + 1}. Skipping...")


        if self.debug_data_output: print(f"\n***** QUESTIONS BEGIN *****\n{questions}\n***** QUESTIONS END *****\n")
        # Write the responses to an Excel file
        self.write_xlsx(os.path.join(self.folder_path, outputFilename), json.dumps(questions))   
        print(f"\nComplete...\nFound {len(question_pages)} pages in the PDF {os.path.join(self.folder_path,inputFilename)}. Read and interrupted as questions.\nOutput written to {os.path.join(folder_path, outputFilename)}\n\n")
    
    