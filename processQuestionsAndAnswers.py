from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import requests
import pandas as pd


# Load environment variables from .env file
load_dotenv()

# Update airtable with responses
def update_airtable(_questions):
    airtable_token = os.getenv('AIRTABLE_API_TOKEN')
    sheet_name = 'assessment'
    base_id = 'appmVJYxFELLgzcZQ'
    url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}'
    headers = {
        'Authorization': f'Bearer {airtable_token}',
        'Content-Type': 'application/json'
    }
    try:
        for _question in _questions:
            update_url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}/{_question["id"]}'
            update_data = {
                "fields": {
                    "Response": question['response']
                }
            }
            update_response = requests.patch(update_url, headers=headers, json=update_data)

            if update_response.status_code==200:
                print(f"Question: {_question['question']}\n-----------\n")
                print(f"Answer: {_question['response']}\n-----------\n\n")
            else:
                print(f"Failed to update record {_question['id']}\n\n")
            
    except Exception as e:
        print(f"An error occurred: {e}")

# Define function to send questions to OpenAI and get responses
# This function is used to get responses for multiple questions one at a time restricting output to the answers provided.
def getAnswers(_questions,_answers):
    try:
        # Set the OpenAI API Key
        api_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)

        num_questions = len(_questions)
        print(f"Number of questions to be answered: {num_questions}")
        questions_answered = 0
        # Get the model to generate a response
        for _question in _questions:
            questions_answered += 1
            print(f"\n\n\nProcessing Question # {questions_answered} of {num_questions}")
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f'\n\n***SIG Lite Documentation***\n{_answers}'},
                    {"role": "system", "content": 'When encountering questions about security, links to documents, requests for documents such as SOC2, ISO, compliance, pen testing, etc., please link to https://security.twilio.com. Explain that to acquire a copy of these documents they must register and request access to the documents from this portal.'},
                    {"role": "system", "content": 'You can also reference https://www.twilio.com/en-us/security for general security information overviews.'},
                    {"role": "system", "content": 'Any questions directly related to HIPAA and not found in the SIG Lite Documentation should reference this link for information about what products and how architecting for HIPAA is achieved at Twilio here: https://www.twilio.com/en-us/hipaa and https://www.twilio.com/content/dam/twilio-com/global/en/other/hippa/pdf/Hipaa_eligible_products_and_services-323.pdf'},
                    {"role": "system", "content": 'Any questions directly related to GDPR and not found in the SIG Lite Documentation should reference this link for information: https://www.twilio.com/en-us/gdpr'},
                    {"role": "system", "content": 'Any questions directly related to SLA (service level agreements) and not found in the SIG Lite Documentation  should reference this link for information: https://www.twilio.com/en-us/legal/service-level-agreement'},
                    {"role": "system", "content": "Answers should always be generated from either the SIG Lite Documentation or summarization from that documentation or referencing links listed in this prompt. You can summarize the answer based on the data found in the SIG Lite Documentation."},
                    {"role": "system", "content": 'The SIG Lite Documentation is formatted as JSON like this: {"sheet_name":["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]}'},
                    {"role": "system", "content": "If you do not have enough information to generate an appropriate response, ONLY respond with 'TODO - UNKNOWN' and nothing else so we will know we need to manually respond"},
                    {"role": "system", "content": "When responding to questions please format every response in the following way: [yes/no], [generated response from SIG Lite Documentation or provided links] (new line)SCA reference: [SCA reference number] (new line) ISO 27002:2013 Relevance: [Relevance number] (new line) SIG Lite Reference: [From SIG Light Documentation the SHEET NAME - QUES NUM] so that formatting is consistent across all responses."},
                    {"role": "user", "content": f"***QUESITION***\n\n{_question['question']}"},
                    ]
            )
            print(f"\nQuestion: {_question['question']}\n")
            _question['response'] = response.choices[0].message.content
            print(f"Answer: {response.choices[0].message.content}")
            print()
        return questions
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1
    
# Define function to read questions from Airtable
# Using airtable as the source of questions from the customer's security assessment.
# It is important to understand how the questions are structured in the airtable.
# The questions are stored in the "assessment" sheet of the airtable base.
def getQuestions():
    # Load the Airtable API token from the environment variables
    airtable_token = os.getenv('AIRTABLE_API_TOKEN')
    
    # Define the base id and the sheet name
    sheet_name = 'assessment'
    base_id = 'appmVJYxFELLgzcZQ'
    url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}'
    # Define the headers for the request including the authorization token read from environment variables
    headers = {
        'Authorization': f'Bearer {airtable_token}',
        'Content-Type': 'application/json'
    }

    try:
        # Send a request to the airtable API to get the questions
        # The response is paginated so we need to loop through the pages to get all the questions "offset"
        # Offset returns a value that is used to get the next page of results.
        _questions = []
        offset = None
        # Loop through the pages of the response to get all the questions
        while True:
            params={'offset': offset} if offset else {}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            print("In the read_airtable_questions function\n",data) if os.getenv('DEBUG') == 'True' else None

            # Extract the questions from the response and store them in a list
            for record in data['records']:
                # print("\n\n",record['fields'])
                _question = record['fields'].get('Question')
                _description = record['fields'].get('Description')
                _unique_identifier = record['fields'].get('Unique Identifier')
                _questionResponse = record['fields'].get('Response')
                _justification = record['fields'].get('Justification')
                _referenceUrl = record['fields'].get('URL for Reference')
                _id = record['id']
                _questions.append({
                    'question': _question,
                    'description': _description,
                    'unique_identifier': _unique_identifier,
                    'response': _questionResponse,
                    'justification': _justification,
                    'referenceUrl': _referenceUrl,
                    'id': _id,
                })
            
            if 'offset' not in data:
                break

            offset = data['offset']

        return _questions
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1

# Read answers from spreadsheet local xls.
# Used the spreadsheet "Twilio-SIG Lite-2023.xlsx" as the source of answers
# Returning the answers as a JSON object
def read_xls_answers():
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
        return 1

# initialize variables
questions=[]
answers=[]
responses=[]

answers = read_xls_answers()
if answers == 1:
    print("An error occurred while reading the answers from the spreadsheet")
else:
    print("Number of answers read:", len(answers))    
    questions = getQuestions()   

    # Test for any errors in reading the questions from airtable
    if questions == 1:
        print("An error occurred while reading the questions from Airtable")
    else:
        print("Number of questions read in:", len(questions))
        responses = getAnswers(questions,answers)
        # Test for any errors in reading the questions from airtable
        if responses == 1:
            print("An error occurred while sending the questions to OpenAI")
        else:
            print("Questions were answered successfully. Processing updates to airtable")
            update_airtable(responses)
            print("Successfully updated Airtable with responses")

            # Write responses to a file
            with open('output/responses.txt', 'w') as file:
                for response in responses:
                    file.write(f"Question: {response['question']}\n")
                    file.write(f"Answer: {response['response']}\n\n")
            print("Responses written to file: output/responses.txt")
# if __name__ == "__main__":
#     main()