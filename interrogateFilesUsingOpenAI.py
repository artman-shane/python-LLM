# Description: This script is used to get a response from the OpenAI API. The response is generated based on the context provided in the
# `context_file.txt` file. The response is generated based on the prompt provided in the script. The response is then printed to the console.

from openai import OpenAI
from dotenv import load_dotenv
import os
import PyPDF2
import sys
import pandas as pd
import json


# Load the environment variables
load_dotenv()

# Define the filename for reading the document
filename="Twilio-SIG Lite-2023.xlsx"


class ChatApp:
    def __init__(self):
        # Set the OpenAI API Key
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        try:
            print(f"Reading file")
            if not os.path.exists(filename) == False:
                print(f"Filename found")
                if filename.endswith('.txt'):
                    print(f"Reading txt file: {filename}")
                    self.context = self.read_txt_file(filename)
                elif filename.endswith('.pdf'):
                    print(f"Reading pdf file: {filename}")
                    self.context = self.read_pdf_file(filename)
                elif filename=="Twilio-SIG Lite-2023.xlsx":
                    print(f"Reading SIG Lite file: {filename}")
                    self.context = self.read_sigLite_answers()
                    print("Number of answers read:", len(self.context))
                else:
                    print(f"Invalid file extension")
                    raise ValueError("Invalid file extension. Only .txt and .pdf files are supported.")
            else:
                print(f"File not found")
                raise FileNotFoundError("File not found. Please check the file path and try again.")

            print(f"File read and context created...\n\nReady to answer questions about file: {filename}...\n\n\n")
            self.messages = [
                {"role": "system", "content": "You are a helpful assistant that is consuming a document and providing insights on the context of that document. Please provide a response to the following question."},
                {"role": "system", "content": "Please ensure that responses are formated for easy reading. Each response should have a clear header."},
                {"role": "system", "content": self.context}
                ]
            if filename=="Twilio-SIG Lite-2023.xlsx":
                self.messages.append(
                    {"role": "system", "content": 'When encountering questions about security, links to documents, requests for documents such as SOC2, ISO, compliance, pen testing, etc., please link to https://security.twilio.com. Explain that to acquire a copy of these documents they must register and request access to the documents from this portal.'})
                self.messages.append({"role": "system", "content": 'You can also reference https://www.twilio.com/en-us/security for general security information overviews.'})
                self.messages.append({"role": "system", "content": 'Any questions directly related to HIPAA and not found in the SIG Lite Documentation should reference this link for information about what products and how architecting for HIPAA is achieved at Twilio here: https://www.twilio.com/en-us/hipaa and https://www.twilio.com/content/dam/twilio-com/global/en/other/hippa/pdf/Hipaa_eligible_products_and_services-323.pdf'})
                self.messages.append({"role": "system", "content": 'Any questions directly related to GDPR and not found in the SIG Lite Documentation should reference this link for information: https://www.twilio.com/en-us/gdpr'})
                self.messages.append({"role": "system", "content": 'Any questions directly related to SLA (service level agreements) and not found in the SIG Lite Documentation  should reference this link for information: https://www.twilio.com/en-us/legal/service-level-agreement'})
                self.messages.append({"role": "system", "content": "Answers should always be generated from either the SIG Lite Documentation or summarization from that documentation or referencing links listed in this prompt. You can summarize the answer based on the data found in the SIG Lite Documentation."})
                self.messages.append({"role": "system", "content": 'The SIG Lite Documentation is formatted as JSON like this: {"sheet_name":["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]}'})
                self.messages.append({"role": "system", "content": "When responding to questions please format every response in the following way: [yes/no (sourced from the Response field from the SIG Lite Documentation)], [generated response from SIG Lite Documentation or provided links] (new line)SCA reference: [SCA reference number] (new line) ISO 27002:2013 Relevance: [Relevance number] (new line) SIG Lite Reference: [From SIG Light Documentation the SHEET NAME - QUES NUM] so that formatting is consistent across all responses."})
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)

    # Function to read a PDF file
    def read_pdf_file(self,file_path):
        print(f"\n\nReading pdf file: {file_path}")
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
    
    # Returning the answers as a JSON object
    def read_sigLite_answers(self):
        json_object = {}
        data_dict = {}
        
        try:
            dfs = pd.read_excel('Twilio-SIG Lite-2023.xlsx', sheet_name=["A. Risk Management","B. Security Policy","C. Organizational Security","D. Asset and Info Management","E. Human Resource Security","F. Physical and Environmental","G. Operations Mgmt","H. Access Control","I. Application Security","J. Incident Event & Comm Mgmt","K. Business Resiliency","L. Compliance","M. End User Device Security","N. Network Security","P. Privacy","T. Threat Management","U. Server Security","V. Cloud Hosting"], header=3)
            for sheet_name, df in dfs.items():
                # print(sheet_name)
                # print(df)
                data_dict[sheet_name] = json.loads(df[["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]].to_json(orient='records'))

            # Convert the DataFrame to a JSON object
            answers = json.dumps(data_dict)
            return answers

        except Exception as e:
            print(f"An error occurred: {e}")
            raise ValueError("An error occurred while reading the Excel file. Please check the file and try again.")
            # return 1
    
    # Function to read a text file
    def read_txt_file(self,file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        return text

    # Function to chat with the AI
    def chat(self,message):
        # Add the user's message to the messages list for future reference
        self.messages.append({"role": "user", "content": message})
        # Get the model to generate a response
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=self.messages
        )
        # Add the AI's response to the messages list for future reference
        self.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        return response.choices[0].message.content
        # Please replace `'your-api-key'` with your actual OpenAI API key. The key is secret and should be kept confidential. The `'context_file.txt'` should contain the context information and this will be fed into GPT-3 model. The `prompt` is where you can specify the task for the AI and the `completion` contains your generated text.
        # Please note: Accessing OpenAI may incur costs, and large usage may require special approval from OpenAI.


# Clear the screen when starting user input first time
os.system('cls' if os.name == 'nt' else 'clear')

# Create an instance of the ChatApp class
app = ChatApp()

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
        print(f"An error occurred: {e}")
        break
