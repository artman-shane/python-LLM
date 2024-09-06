# System libraries
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
        print(f"Documents folder path: {self.folder_path}")

    def getFilename(self,_folder_path):
        while True:
            try:
                # Prompt the user for a filename
                response = input(f"\n\nEnter the filename to read: (in {self.folder_path} folder):")
                if os.path.exists(f"{_folder_path}/{response}"):
                    # print(f"Filename found...")
                    return response
                else:
                    print(f"Invalid filename {response}. Please try again.")
            # Handle exceptions for keyboard interrupt
            except KeyboardInterrupt:
                # Exit the loop if Ctrl-C is pressed
                raise ValueError("\nUser cancelled...")
            # Handle all other exceptions
            except Exception as e:  
                raise ValueError(f"\nAn error occurred: {e}")
      

    # Function to read a PDF file
    def read_pdf_file(self,file_path):
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
            raise ValueError(f"\nAn error occurred: {e}")
    
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
            raise ValueError(f"\nAn error occurred: {e}")
    
    # Function to read a text file
    def read_txt_file(self,file_path):
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            return text
        except Exception as e:
            raise ValueError(f"\nAn error occurred: {e}")
    
    