from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import requests
import pandas as pd


# Load environment variables from .env file
load_dotenv()

# Define function to read Google Sheets spreadsheet
def answer_question(answers):
    # Add your code here to read the spreadsheet from Airtable
    # Make sure to replace 'YOUR_API_KEY' and 'YOUR_BASE_ID' with your actual API key and base ID
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

# Define function to read questions from Airtable
def answer_question(answers):
    # Add your code here to read the spreadsheet from Airtable
    # Make sure to replace 'YOUR_API_KEY' and 'YOUR_BASE_ID' with your actual API key and base ID
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
    # Add your code here to read the spreadsheet from Google Sheets
    # Make sure to replace 'YOUR_SP
    dfs = pd.read_excel('Twilio-SIG Lite-2023.xlsx', sheet_name=["A. Risk Management","B. Security Policy","C. Organizational Security","D. Asset and Info Management","E. Human Resource Security","F. Physical and Environmental","G. Operations Mgmt","H. Access Control","I. Application Security","J. Incident Event & Comm Mgmt","K. Business Resiliency","L. Compliance","M. End User Device Security","N. Network Security","P. Privacy","T. Threat Management","U. Server Security","V. Cloud Hosting"], header=3)
    for sheet_name, df in dfs.items():
        # print(sheet_name)
        # print(df)
        data_dict[sheet_name] = json.loads(df.to_json(orient='records'))

    # Convert the DataFrame to a JSON object
    answers = json.dumps(data_dict)
    return(answers)

    # # Write the JSON object to a new file
    # with open('output.json', 'w') as file:
    #     file.write(json_object)

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


    # # Load the document data from the file
    # with open("output/documents.json", "r") as file:
    #     documents = json.load(file)

    # # Train the OpenAI instance with the document data
    # openai_instance.train(documents)

    # # Ask OpenAI the questions and print the answers
    # for question in questions:
    #     answer = openai_instance.answer(question)
    #     print(f"Question: {question}")
    #     print(f"Answer: {answer}")
    #     print()


# Assuming you have already created an instance of the OpenAI class named 'openai_instance'
answers = read_xls_answers()
questions = read_airtable_questions()
answer_question(answers)

    # Add your code here to call the read_spreadsheet() function and get the questions
    # Add your code here to call the send_questions() function and get the responses

# if __name__ == "__main__":
#     main()