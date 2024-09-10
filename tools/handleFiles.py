# System libraries
from io import StringIO
import re
from dotenv import load_dotenv
import os
import json # Used to convert the DataFrame to a JSON object

# Third-party libraries
import PyPDF2 # Used to read PDF files
import pandas as pd # Used to read Excel files

# Load the environment variables
load_dotenv()

class HandleFiles:
    def __init__(self):
        self.folder_path = os.getenv('DOCUMENTS_FOLDER_PATH')
        if os.getenv('DEBUG') == True: print(f"Documents folder path: {self.folder_path}")

    def getFilename(self, _folder_path):
        while True:
            try:
                # Prompt the user for a filename
                response = input(f"Enter the filename to read: (in ./{self.folder_path}/ folder):")
                if os.path.exists(f"{_folder_path}/{response}"):
                    # print(f"Filename found...")
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
        try:
            # Prompt the user for input
            response = input(prompt)
            return response
        except KeyboardInterrupt:
            # Exit the loop if Ctrl-C is pressed
            raise ValueError("\nUser cancelled during input")
        except Exception as e:
            raise ValueError({e})      


    # Function to read a PDF file
    def read_pdf_file(self, file_path):
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
            return text
        except Exception as e:
            raise ValueError({e})
    
    # Function to read a PDF file
    def read_pdf_pages(self, file_path):
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
            return pages_text
        except Exception as e:
            raise ValueError({e})
    
    # Returning the answers as a JSON object
    def read_sigLite_answers(self,file_path):
        json_object = {}
        data_dict = {}
        
        try:
            dfs = pd.read_excel(file_path, sheet_name=["A. Risk Management","B. Security Policy","C. Organizational Security","D. Asset and Info Management","E. Human Resource Security","F. Physical and Environmental","G. Operations Mgmt","H. Access Control","I. Application Security","J. Incident Event & Comm Mgmt","K. Business Resiliency","L. Compliance","M. End User Device Security","N. Network Security","P. Privacy","T. Threat Management","U. Server Security","V. Cloud Hosting"], header=3)
            for sheet_name, df in dfs.items():
                # print(sheet_name)
                # print(df)
                data_dict[sheet_name] = json.loads(df[["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]].to_json(orient='records'))

            # Convert the DataFrame to a JSON object
            answers = json.dumps(data_dict)
            return answers

        except Exception as e:
            raise ValueError({e})

    # Function to read an Excel file
    # Parameters:
    # file_path - the path to the Excel file including the filename
    # Optional parameter: headers - to specify the row number where the headers are located
    def read_xlsx(self, file_path, headers=0):
        if os.getenv('DEBUG') == True: print(f"\n\nReading Excel file: {file_path}")
        data_dict = {}
        
        try:
            if not os.path.exists(file_path):
                raise ValueError(f"\nFile not found: {file_path}")
            if file_path.endswith(".xlsx") == False:
                raise ValueError(f"\nInvalid file format. Please provide an Excel file.")
            
            if os.getenv('DEBUG') == True: print(f"Processing...")
            dfs = pd.read_excel(file_path, sheet_name=None)
            if os.getenv('DEBUG') == True: print(f"Number of sheets: {len(dfs)}")
            for sheet_name, df in dfs.items():
                data_dict[sheet_name] = json.loads(df.to_json(orient='records'))

            # Convert the DataFrame to a JSON object
            answers = json.dumps(data_dict)
            return answers

        except Exception as e:
            raise ValueError(f"\nAn error occurred: {e}")
        
    def _create_xlsx(self, file_path):
        try:
            if os.getenv('DEBUG') == True: print(f"Creating file: {file_path}")
            if os.getenv('DEBUG') == True: print(f"Creating empty data frame...")
            # Create a DataFrame with no data.
            df = pd.DataFrame()
            if os.getenv('DEBUG') == True: print(f"Writing to Excel file...")
            # Write the DataFrame to an Excel file
            df.to_excel(file_path, index=False)
            if os.getenv('DEBUG') == True: print(f"File created: {file_path}")
            return True
        except Exception as e:
            raise ValueError({e})
    
    # Function to clean up a JSON string
    # Parameters:
    # json_str - the JSON string to clean up
    def clean_json(self, json_str):
        # Clean JSON
        if os.getenv('DEBUG') == True: print(f"Is JSON dirty?")
        # Use regular expression to find the first '{' and the last '}'
        if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"\n***** BEGIN DIRTY *****\n{json_str}\n***** END DIRTY *****\n")
        match = re.search(r'[\{,\[].*[\},\]]', json_str, re.DOTALL)
        if match:
            if os.getenv('DEBUG') == True: print(f"Match Found. Cleaning JSON...")
            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"JSON cleaned:\n*****BEGIN CLEANED*****\n{match.group(0)}\n***** END CLENAED *****\n")
            return match.group(0)
        else:
            raise ValueError("Invalid JSON format")
    
    # Function to write to an Excel file
    # Parameters:
    # file_path - the path to the Excel file including the filename
    # data_dict - the data to write to the Excel file as a JSON object
    def write_xlsx(self, file_path, data_dict):
        if os.getenv('DEBUG') == True: print(f"\n\nWriting to Excel file: {file_path}")
        try:
            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"\n\n***** DATA *****\n{data_dict}\n\n***** DATA *****\n\n")
            # Clean up json string
            data_dict = self.clean_json(data_dict)
            if os.getenv('DEBUG') == True: print(f"JSON Clean")
            if os.getenv('DEBUG') == True: print(f"Checking if file exists...")
            if not os.path.exists(file_path):
                if os.getenv('DEBUG') == True: print(f"File not found: {file_path} must be created...")
                filename = os.path.basename(file_path)
                if os.getenv('DEBUG') == True: print(f"Filename full path to create: {filename}")
                self._create_xlsx(os.path.join(self.folder_path, filename))
                if os.getenv('DEBUG') == True: print(f"Successfully created file: {file_path}")
            else:
                if os.getenv('DEBUG') == True: print(f"File found: {file_path}")
            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"Data to write: *****\n{data_dict}\n*****")
            if os.getenv('DEBUG') == True: print(f"Converting to DataFrame...")
            data = json.loads(data_dict)
            if os.getenv('DEBUG') == True: print(f"VarType:\ndata_dict: {type(data_dict)}\ndata: {type(data)}")
            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"Data as JSON: {data}")

            # Convert the JSON object to a DataFrame
            # df = pd.read_json(json.loads(data_dict))

            if os.getenv('DEBUG') == True: print(f"Creating Blank DataFrame array...")
            combined_df = pd.DataFrame()
            if os.getenv('DEBUG') == True: print(f"Checking number of sheets...")
            if len(data.keys()) > 1:
                if os.getenv('DEBUG') == True: print(f"More than one sheet found...")
                for sheet_name in data.keys():
                    if os.getenv('DEBUG') == True: print(f"Sheet Name: {sheet_name}")
                    df = pd.DataFrame(data[sheet_name])
                    if os.getenv('DEBUG') == True: print(f"Inserting sheet name...")
                    df.insert(0, 'Sheet Name', sheet_name)
                    if os.getenv('DEBUG') == True: print(f"Combining DataFrames...")
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
            else:
                if os.getenv('DEBUG') == True: print(f"Only one sheet found...")
                if os.getenv('DEBUG') == True: print(f"Creating DataFrame...")
                df = pd.DataFrame(data[list(data.keys())[0]])
                if os.getenv('DEBUG') == True: print(f"Inserting sheet name...")
                df.insert(0, 'Sheet Name', list(data.keys())[0])
                if os.getenv('DEBUG') == True: print(f"Combining DataFrames...")
                combined_df = pd.concat([combined_df, df], ignore_index=True)

            if os.getenv('DEBUG') == True: print(f"Converting df to logic excel file...")
            if os.getenv('DEBUG_DATA_OUTPUT') == True: print(f"\n***** BEGIN Data to write *****\n{combined_df}\n***** END Data to write *****\n")
            # Write the DataFrame to an Excel file
            combined_df.to_excel(file_path, index=False)

            # if os.getenv('DEBUG') == True: print(f"Writing to Excel file...")
            # # Write the DataFrame to an Excel file
            # df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            raise ValueError({e})
        
    # Function to read a text file
    def read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            return text
        except Exception as e:
            raise ValueError({e})
    
    