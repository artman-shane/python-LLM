from dotenv import load_dotenv
import os
import sys
# System libraries

from openai import OpenAI
import json
import requests
import pandas as pd


# Custom libraries
from tools.handleFiles import HandleFiles
from tools.chatApp import ChatApp

# Load environment variables from .env file
load_dotenv()

# # Function to chat with the AI
# def chat(self,message):
#     # Add the user's message to the messages list for future reference
#     self.messages.append({"role": "user", "content": message})
#     # Get the model to generate a response
#     response = self.client.chat.completions.create(
#         model="gpt-4-turbo",
#         messages=self.messages
#     )
#     # Add the AI's response to the messages list for future reference
#     self.messages.append({"role": "assistant", "content": response.choices[0].message.content})
#     return response.choices[0].message.content
#     # Please replace `'your-api-key'` with your actual OpenAI API key. The key is secret and should be kept confidential. The `'context_file.txt'` should contain the context information and this will be fed into GPT-3 model. The `prompt` is where you can specify the task for the AI and the `completion` contains your generated text.
#     # Please note: Accessing OpenAI may incur costs, and large usage may require special approval from OpenAI.

try:
    # Get the filename of the file to read
    fileHandler = HandleFiles()
    folder_path = fileHandler.folder_path
    questionsFilename = "questionfile.txt"
    answersFilename = "answerfile.txt"

    # Set the OpenAI API Key
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)

    # Get the filename of the file to read
    while questionsFilename.endswith('.xlsx') == False and questionsFilename.endswith('.pdf') == False:
        print(f"\nFilename needs to end with .pdf or .xlsx and exist in \"{folder_path}\"\n\n")
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

            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages
            )

            if os.getenv("DEBUG_DATA_OUTPUT"): print(response.choices[0].message.content)
            # Write the responses to an Excel file
            fileHandler.write_xlsx(os.path.join(folder_path, answersFilename), response.choices[0].message.content)   
            print("\n\n*********\n\n")

    elif questionsFilename.endswith('.pdf'):
        if os.getenv("DEBUG"): print("Reading pdf file")
        question_pages = fileHandler.read_pdf_pages(os.path.join(folder_path, questionsFilename))
        if os.getenv("DEBUG_DATA_OUTPUT"): print(f"Found {len(question_pages)} pages")
        questions = {}
        for page_num,page_text in enumerate(question_pages):
            if os.getenv("DEBUG"): print(f"Processing page {page_num + 1}")

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

            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages
            )
            
            if os.getenv("DEBUG_DATA_OUTPUT"): print(f"\n***** RAW BEGIN *****\n{response.choices[0].message.content}\n***** RAW END *****\n")
            cleanedJson = fileHandler.clean_json(response.choices[0].message.content)
            if os.getenv("DEBUG_DATA_OUTPUT"): print(f"\n***** CLEANSED BEGIN *****\n{cleanedJson}\n***** CLEANSED END *****\n")
            if os.getenv("DEBUG"): print(f"VarType: (cleanedJson): {type(cleanedJson)}")
            # Append cleanedJson to json object
            questions[f"Page {page_num + 1}"] = json.loads(cleanedJson)
            if os.getenv("DEBUG"): print(f"VarType (questions): {type(questions)}")


        if os.getenv("DEBUG_DATA_OUTPUT"): print(f"\n***** QUESTIONS BEGIN *****\n{questions}\n***** QUESTIONS END *****\n")
        # Write the responses to an Excel file
        fileHandler.write_xlsx(os.path.join(folder_path, answersFilename), json.dumps(questions))   
        print("\n\n*********\n\n")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    sys.exit(1)

# # Update airtable with responses
# def update_airtable(_questions):
#     airtable_token = os.getenv('AIRTABLE_API_TOKEN')
#     sheet_name = 'assessment'
#     base_id = 'appmVJYxFELLgzcZQ'
#     url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}'
#     headers = {
#         'Authorization': f'Bearer {airtable_token}',
#         'Content-Type': 'application/json'
#     }
#     try:
#         for _question in _questions:
#             update_url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}/{_question["id"]}'
#             update_data = {
#                 "fields": {
#                     "Response": _question['response']
#                 }
#             }
#             update_response = requests.patch(update_url, headers=headers, json=update_data)

#             if update_response.status_code==200:
#                 print(f"Question: {_question['question']}\n-----------\n")
#                 print(f"Answer: {_question['response']}\n-----------\n\n")
#             else:
#                 print(f"Failed to update record {_question['id']}\n\n")
            
#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Define function to send questions to OpenAI and get responses
# # This function is used to get responses for multiple questions one at a time restricting output to the answers provided.
# def getAnswers(_questions,_answers):
#     try:
#         # Set the OpenAI API Key
#         api_key = os.getenv('OPENAI_API_KEY')
#         client = OpenAI(api_key=api_key)

#         num_questions = len(_questions)
#         print(f"Number of questions to be answered: {num_questions}")
#         questions_answered = 0
#         # Get the model to generate a response
#         for _question in _questions:
#             questions_answered += 1
#             print(f"\n\n\nProcessing Question # {questions_answered} of {num_questions}")
#             response = client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": f'\n\n***SIG Lite Documentation***\n{_answers}'},
#                     {"role": "system", "content": 'When encountering questions about security, links to documents, requests for documents such as SOC2, ISO, compliance, pen testing, etc., please link to https://security.twilio.com. Explain that to acquire a copy of these documents they must register and request access to the documents from this portal.'},
#                     {"role": "system", "content": 'You can also reference https://www.twilio.com/en-us/security for general security information overviews.'},
#                     {"role": "system", "content": 'Any questions directly related to HIPAA and not found in the SIG Lite Documentation should reference this link for information about what products and how architecting for HIPAA is achieved at Twilio here: https://www.twilio.com/en-us/hipaa and https://www.twilio.com/content/dam/twilio-com/global/en/other/hippa/pdf/Hipaa_eligible_products_and_services-323.pdf'},
#                     {"role": "system", "content": 'Any questions directly related to GDPR and not found in the SIG Lite Documentation should reference this link for information: https://www.twilio.com/en-us/gdpr'},
#                     {"role": "system", "content": 'Any questions directly related to SLA (service level agreements) and not found in the SIG Lite Documentation  should reference this link for information: https://www.twilio.com/en-us/legal/service-level-agreement'},
#                     {"role": "system", "content": "Answers should always be generated from either the SIG Lite Documentation or summarization from that documentation or referencing links listed in this prompt. You can summarize the answer based on the data found in the SIG Lite Documentation."},
#                     {"role": "system", "content": 'The SIG Lite Documentation is formatted as JSON like this: {"sheet_name":["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]}'},
#                     {"role": "system", "content": "When responding to questions please format every response in the following way: [yes/no (sourced from the Response field from the SIG Lite Documentation)], [generated response from SIG Lite Documentation or provided links] (new line)SCA reference: [SCA reference number] (new line) ISO 27002:2013 Relevance: [Relevance number] (new line) SIG Lite Reference: [From SIG Light Documentation the SHEET NAME - QUES NUM] so that formatting is consistent across all responses."},
#                     {"role": "user", "content": f"***QUESITION***\n\n{_question['question']}"},
#                     ]
#             )
#             print(f"\nQuestion: {_question['question']}\n")
#             _question['response'] = response.choices[0].message.content
#             print(f"Answer: {response.choices[0].message.content}")
#             print()

#         # Write responses to file for backup
#         output_dir = os.getenv('OUTPUT_DIR')
#         output_file = os.getenv('OUTPUT_QA_FILE')
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)
#         file_path = os.path.join(os.getenv('OUTPUT_DIR'), os.getenv('OUTPUT_QA_FILE'))
#         with open(file_path, 'w') as file:
#             file.write(json.dumps(questions))

#         # Return the questions with responses.
#         return questions
    
    
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return 1
    
# # Define function to read questions from Airtable
# # Using airtable as the source of questions from the customer's security assessment.
# # It is important to understand how the questions are structured in the airtable.
# # The questions are stored in the "assessment" sheet of the airtable base.
# def getQuestions():
#     # Load the Airtable API token from the environment variables
#     airtable_token = os.getenv('AIRTABLE_API_TOKEN')
    
#     # Define the base id and the sheet name
#     sheet_name = 'assessment'
#     base_id = 'appmVJYxFELLgzcZQ'
#     url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}'
#     # Define the headers for the request including the authorization token read from environment variables
#     headers = {
#         'Authorization': f'Bearer {airtable_token}',
#         'Content-Type': 'application/json'
#     }

#     try:
#         # Send a request to the airtable API to get the questions
#         # The response is paginated so we need to loop through the pages to get all the questions "offset"
#         # Offset returns a value that is used to get the next page of results.
#         _questions = []
#         offset = None
#         # Loop through the pages of the response to get all the questions
#         while True:
#             params={'offset': offset} if offset else {}
#             response = requests.get(url, headers=headers, params=params)
#             data = response.json()
#             print("In the read_airtable_questions function\n",data) if os.getenv('DEBUG') == 'True' else None

#             # Extract the questions from the response and store them in a list
#             for record in data['records']:
#                 # print("\n\n",record['fields'])
#                 _question = record['fields'].get('Question')
#                 _description = record['fields'].get('Desc')
#                 _questionResponse = record['fields'].get('Response')
#                 _justification = record['fields'].get('Justification')
#                 _referenceUrl = record['fields'].get('URL for Reference')
#                 _id = record['id']
#                 _questions.append({
#                     'question': _question,
#                     'description': _description,
#                     'response': _questionResponse,
#                     'justification': _justification,
#                     'referenceUrl': _referenceUrl,
#                     'id': _id,
#                 })
            
#             if 'offset' not in data:
#                 break

#             offset = data['offset']

#         return _questions
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return 1

# # Read answers from spreadsheet local xls.
# # Used the spreadsheet "Twilio-SIG Lite-2023.xlsx" as the source of answers
# # Returning the answers as a JSON object
# def read_xls_answers():
#     json_object = {}
#     data_dict = {}
    
#     try:
#         dfs = pd.read_excel('Documents/Twilio-SIG Lite-2023.xlsx', sheet_name=["A. Risk Management","B. Security Policy","C. Organizational Security","D. Asset and Info Management","E. Human Resource Security","F. Physical and Environmental","G. Operations Mgmt","H. Access Control","I. Application Security","J. Incident Event & Comm Mgmt","K. Business Resiliency","L. Compliance","M. End User Device Security","N. Network Security","P. Privacy","T. Threat Management","U. Server Security","V. Cloud Hosting"], header=3)
#         for sheet_name, df in dfs.items():
#             # print(sheet_name)
#             # print(df)
#             data_dict[sheet_name] = json.loads(df[["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]].to_json(orient='records'))

#         # Convert the DataFrame to a JSON object
#         answers = json.dumps(data_dict)
#         return answers

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return 1

# # initialize variables
# questions=[]
# answers=[]
# responses=[]

# answers = read_xls_answers()
# if answers == 1:
#     print("An error occurred while reading the answers from the spreadsheet")
# else:
#     print("Number of answers read:", len(answers))    
#     questions = getQuestions()   

#     # Test for any errors in reading the questions from airtable
#     if questions == 1:
#         print("An error occurred while reading the questions from Airtable")
#     else:
#         print("Number of questions read in:", len(questions))
#         responses = getAnswers(questions,answers)
#         # Test for any errors in reading the questions from airtable
#         if responses == 1:
#             print("An error occurred while sending the questions to OpenAI")
#         else:
#             print("Questions were answered successfully. Processing updates to airtable")
#             update_airtable(responses)
#             print("Successfully updated Airtable with responses")

#             # Write responses to a file
#             with open('output/responses.txt', 'w') as file:
#                 for response in responses:
#                     file.write(f"Question: {response['question']}\n")
#                     file.write(f"Answer: {response['response']}\n\n")
#             print("Responses written to file: output/responses.txt")
# # if __name__ == "__main__":
# #     main()