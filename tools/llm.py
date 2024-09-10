# System libraries
from dotenv import load_dotenv
import os
import sys

# Third-party libraries
from openai import OpenAI # Used to interact with the OpenAI API

class LLM:

    def __init__(self):
        # Set the OpenAI API Key
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Function to query with the AI for response
    # Parameters:
    # _query - the query to ask the AI including prompting
    # Note: will not store responses in a messages list
    def query(self,_query):
        # Get the model to generate a response
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=_query
            )
            # Add the AI's response to the messages list for future reference
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")
