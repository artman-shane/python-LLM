from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import requests
import pandas as pd


# Load environment variables from .env file
load_dotenv()

# Define function to read questions from Airtable
def read_airtable_questions():
    airtable_token = os.getenv('AIRTABLE_API_TOKEN')
    
    sheet_name = 'assessment'
    base_id = 'appmVJYxFELLgzcZQ'
    url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}'
    headers = {
        'Authorization': f'Bearer {airtable_token}',
        'Content-Type': 'application/json'
    }

    try:

        # Extract the questions from the response and store them in a list
        questions = []
        offset = None
        while True:
            params={'offset': offset} if offset else {}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            # print(data)

            for record in data['records']:
                # print("\n\n",record['fields'])
                question = record['fields'].get('Question')
                description = record['fields'].get('Description')
                unique_identifier = record['fields'].get('Unique Identifier')
                questionResponse = record['fields'].get('Response')
                justification = record['fields'].get('Justification')
                referenceUrl = record['fields'].get('URL for Reference')
                id = record['id']
                questions.append({
                    'question': question,
                    'description': description,
                    'unique_identifier': unique_identifier,
                    'response': questionResponse,
                    'justification': justification,
                    'referenceUrl': referenceUrl,
                    'id': id,
                })
                # print(f"Question: {question}")
            
            if 'offset' not in data:
                break

            offset = data['offset']

        return questions
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1


# Define function to send questions to OpenAI and get responses
def send_questions(questions):
    try:
        # Set the OpenAI API Key
        api_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)

        # Get the model to generate a response
        for question in questions:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f"Here are the answers you MUST source for the questions provided:\n\n***ANSWERS***\n{answers}"},
                    {"role": "system", "content": f"DO NOT pull answers from other locations. However, you can summarize the answer based on the data found in the answer provided. Cite the sheet and Question Number or numbers used to answer the question in a [sheet name (first key of each array element): question number] format at the end of the answer."},
                    {"role": "user", "content": f"***QUESITION***\n\n{question['question']}"},
                    ]
            )
            print(f"Question: {question['question']}")
            question['response'] = response.choices[0].message.content
            print(f"Answer: {response.choices[0].message.content}")
            print()
            return questions
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1



# Update airtable with responses
def update_airtable(questions):
    airtable_token = os.getenv('AIRTABLE_API_TOKEN')
    sheet_name = 'assessment'
    base_id = 'appmVJYxFELLgzcZQ'
    url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}'
    headers = {
        'Authorization': f'Bearer {airtable_token}',
        'Content-Type': 'application/json'
    }
    try:
        for question in questions:
            update_url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}/{question["id"]}'
            update_data = {
                "fields": {
                    "Response": question['response']
                }
            }
            update_response = requests.patch(update_url, headers=headers, json=update_data)

            if update_response.status_code==200:
                print(f"Question: {question}")
                print(f"Answer: {answer}\n\n")
            else:
                print(f"Failed to update record {record_id}\n\n")
            
    except Exception as e:
        print(f"An error occurred: {e}")

# Define function to read questions from Airtable and get single response from OpenAI
def answer_question(answers):
    airtable_token = os.getenv('AIRTABLE_API_TOKEN')
    
    sheet_name = 'assessment'
    base_id = 'appmVJYxFELLgzcZQ'
    url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}'
    headers = {
        'Authorization': f'Bearer {airtable_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        # print(response, response.json())
        data = response.json()

        # Extract the questions from the response and store them in a list
        for record in data['records']:
            # print("\n\n",record['fields'])
            question = record['fields'].get('Question')
            answer = getAnswers(question, answers)

            record_id=record['id']
            update_url = f'https://api.airtable.com/v0/{base_id}/{sheet_name}/{record_id}'
            update_data = {
                "fields": {
                    "Response": answer
                }
            }
            update_response = requests.patch(update_url, headers=headers, json=update_data)

            if update_response.status_code==200:
                print(f"Question: {question}")
                print(f"Answer: {answer}\n\n")
            else:
                print(f"Failed to update record {record_id}\n\n")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Read answers from spreadsheet local xls
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

# Define function to send questions to OpenAI and get responses
def getAnswers(question,answers):
    # Set the OpenAI API Key
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)

    # Get the model to generate a response
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"Here are the answers you MUST source for the questions provided:\n\n***ANSWERS***\n{answers}"},
            {"role": "system", "content": f"DO NOT pull answers from other locations. However, you can summarize the answer based on the data found in the answer provided. Cite the sheet and Question Number or numbers used to answer the question in a [sheet name (first key of each array element): question number] format at the end of the answer."},
            {"role": "user", "content": f"***QUESITION***\n\n{question}"},
            ]
    )
    return(response.choices[0].message.content)

def getAnswers2(question,answers):
    try:
        # Set the OpenAI API Key
        api_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)

        # Get the model to generate a response
        for question in questions:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": 'The answers are formatted like this: {"sheet_name":["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]}'},
                    {"role": "system", "content": f"DO NOT pull answers from other locations. However, you can summarize the answer based on the data found in the answers. Cite the sheet and Question Number or numbers used to answer the question in a [sheet name (first key of each array element): question number] format at the end of the answer."},
                    {"role": "system", "content": f'\n\n***ANSWERS***\n{answers}'},
                    {"role": "user", "content": f"***QUESITION***\n\n{question['question']}"},
                    ]
            )
            print(f"Question: {question['question']}")
            question['response'] = response.choices[0].message.content
            print(f"Answer: {response.choices[0].message.content}")
            print()
        return questions
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1


answers = read_xls_answers()
if answers == 1:
    print("An error occurred while reading the answers from the spreadsheet")
else:
    print("Number of answers read:", len(answers))    
    # print('Answers read successfully:',answers)
    questions = read_airtable_questions()
    if questions == 1:
        print("An error occurred while reading the questions from Airtable")
    else:
        print("Number of questions read:", len(questions))
        responses = getAnswers2(questions,answers)
        if responses == 1:
            print("An error occurred while sending the questions to OpenAI")
        else:
            print("Questions were answered successfully. Processing updates to airtable")
            update_airtable(responses)
            print("Successfully updated Airtable with responses")


# if __name__ == "__main__":
#     main()