# System libraries
# from dotenv import load_dotenv
import os
import sys
import json

from tools.handleFiles import HandleFiles
from tools.systemTools import SystemTools

# Third-party libraries
from openai import OpenAI # Used to interact with the OpenAI API

class LLM:

    def __init__(self, logger):
        # load_dotenv(override=True)
        self.logger = logger
        self.systemTools = SystemTools(self.logger)
        # load_dotenv(override=True)
        self.logger.debug(f"***** BEGIN class init LLM *****")
        # Set the OpenAI API Key
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.handleFiles = HandleFiles(self.logger)
        self.logger.debug(f"***** END class init LLM *****")


    # Function to query with the AI for response
    # Parameters:
    # _query - the query to ask the AI including prompting
    # Note: will not store responses in a messages list
    def query(self,_query):
        self.logger.debug(f"***** BEGIN func query *****")
        # Get the model to generate a response
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=_query
            )
            # TODO: There are other ways to get JSON responses back. response_format={ "type": "json_object" },
            # Add the AI's response to the messages list for future reference
            self.logger.debug(f"***** END func query *****")
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")
    # Define function to send questions to OpenAI and get responses


    # This function is used to get responses for multiple questions one at a time restricting output to the answers provided. Send json.
    # Parameters:
    # _questions - JSON Object questions and answers to ask the AI
    # _answers - JSON Object answers to the questions
    def getAnswers(self, _question, _answers, _llmPrompt=""):
        if _llmPrompt == "":
            _llmPrompt = "None"
        self.logger.debug(f"***** BEGIN func getAnswers *****")
        try:
            self.logger.debug(f"Questions: {_question}\nQuestions Type: {type(_question)}")
            self.logger.debug(f"Answers: {_answers}\nAnswers Type: {type(_answers)}")
            # Set the OpenAI API Key
            api_key = os.getenv('OPENAI_API_KEY')
            client = OpenAI(api_key=api_key)
            # Get the model to generate a response
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": 'This is a JSON object of Answers:'},
                    {"role": "system", "content": f'***SIG Lite Answer Sheet Format*** {os.getenv("GET_ANSWERS_SIG_LITE_ANSWER_SHEET_FORMAT")}'},
                    {"role": "system", "content": f'***Answers*** {_answers}'},
                    {"role": "system", "content": f'***Special Considerations*** {_llmPrompt}'},
                    {"role": "system", "content": f'***HIPAA Question Instruction*** {os.getenv("GET_ANSWERS_HIPAA")}'},
                    {"role": "system", "content": f'***GDPR Question Instruction*** {os.getenv("GET_ANSWERS_GDPR")}'},
                    {"role": "system", "content": f'***SLA Question Instruction*** {os.getenv("GET_ANSWERS_SLAS")}'},
                    {"role": "system", "content": f'***Compliance Question Instruction*** {os.getenv("GET_ANSWERS_COMPLIANCE")}'},
                    {"role": "system", "content": f'***Respose Format*** {os.getenv("GET_ANSWER_RESPONSE_FORMAT")}'},
                    # {"role": "system", "content": f'***Question Format*** {os.getenv("GET_ANSWERS_QUESTION_FORMAT")}'},
                    {"role": "user", "content": f"***QUESITION*** {_question}"},
                    ]
            )
        
            # The response comes out with a lot of extra characters. Clean it up then return it.
            # response = self.systemTools.clean_json(response.choices[0].message.content)
            response = response.choices[0].message.content
            self.logger.debug(f"Response: {response}")
            # Return the questions with responses.
            self.logger.debug(f"***** END func getAnswers *****")
            return response
        
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return 1
