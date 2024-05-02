import os
from dotenv import load_dotenv
import requests
import pandas as pd
from openai import OpenAI
import json

# Load environment variables from .env file
load_dotenv()

# create a cli chat application using open ai gpt4-turbo
# Set up OpenAI API credentials
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


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

def generate_response(question):

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f'\n\n***SIG Lite Documentation***\n{answers}'},
            {"role": "system", "content": 'When encountering questions about security, links to documents, requests for documents such as SOC2, ISO, compliance, pen testing, etc., please link to https://security.twilio.com. Explain that to acquire a copy of these documents they must register and request access to the documents from this portal.'},
            {"role": "system", "content": 'You can also reference https://www.twilio.com/en-us/security for general security information overviews.'},
            {"role": "system", "content": 'Any questions directly related to HIPAA and not found in the SIG Lite Documentation should reference this link for information about what products and how architecting for HIPAA is achieved at Twilio here: https://www.twilio.com/en-us/hipaa and https://www.twilio.com/content/dam/twilio-com/global/en/other/hippa/pdf/Hipaa_eligible_products_and_services-323.pdf'},
            {"role": "system", "content": 'Any questions directly related to GDPR and not found in the SIG Lite Documentation should reference this link for information: https://www.twilio.com/en-us/gdpr'},
            {"role": "system", "content": 'Any questions directly related to SLA (service level agreements) and not found in the SIG Lite Documentation  should reference this link for information: https://www.twilio.com/en-us/legal/service-level-agreement'},
            {"role": "system", "content": "Answers should always be generated from either the SIG Lite Documentation or summarization from that documentation or referencing links listed in this prompt. You can summarize the answer based on the data found in the SIG Lite Documentation."},
            {"role": "system", "content": 'The SIG Lite Documentation is formatted as JSON like this: {"sheet_name":["Ques Num","Question/Request","Response","Additional Information","Category","Sub-category","SCA Reference","ISO 27002:2013 Relevance"]}'},
            {"role": "system", "content": "If you do not have enough information to generate an appropriate response, ONLY respond with 'TODO - UNKNOWN' and nothing else so we will know we need to manually respond"},
            {"role": "system", "content": "When responding to questions please format every response in the following way: [yes/no (sourced from the Response field from the SIG Lite Documentation)], [generated response from SIG Lite Documentation or provided links] (new line)SCA reference: [SCA reference number] (new line) ISO 27002:2013 Relevance: [Relevance number] (new line) SIG Lite Reference: [From SIG Light Documentation the SHEET NAME - QUES NUM] so that formatting is consistent across all responses."},
            {"role": "user", "content": f"***QUESITION***\n\n{question}"},
            ]
    )
    
    # Extract the generated response from the API response
    generated_text = response.choices[0].message.content.strip()

    
    return generated_text

# Main loop for the chat application
answers = read_xls_answers()
print(f'Found {len(answers)} answers')
# Define the function to generate a response
print("\n\n***SIG Lite Documentation Search***\n\n")

while True:

    # Get user input
    user_input = input("What is your question?:\n")
    
    # Generate a response based on the user input
    response = generate_response(user_input)
    
    # Print the generated response
    print("\nResponse:\n" + response + "\n\n\n")