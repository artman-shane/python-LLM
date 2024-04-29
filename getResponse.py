# Description: This script is used to get a response from the OpenAI API. The response is generated based on the context provided in the
# `context_file.txt` file. The response is generated based on the prompt provided in the script. The response is then printed to the console.


from openai import OpenAI
import os
import json
from dotenv import load_dotenv
load_dotenv()




# Set the OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)
with open('context_file.txt', 'r') as file:
    context = file.read()

# Define the prompt
prompt = "Based on the context provided, I want to create a flex plugin that would demonstrate a google busines chat with a prescription refill"
prompt += context

# Get the model to generate a response
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "Analyze the names of these services"},
        {"role": "user", "content": prompt},
        {"role": "system", "content": "Please ensure that responses are formated for easy reading. Provide a header for each response."},
        {"role": "system", "content": "Tell me if there are any loggers, keystroke loggers, or other malicious software on the system."}
    ]
)

# Print the result
print(response.choices[0].message.content)

# Please replace `'your-api-key'` with your actual OpenAI API key. The key is secret and should be kept confidential. The `'context_file.txt'` should contain the context information and this will be fed into GPT-3 model. The `prompt` is where you can specify the task for the AI and the `completion` contains your generated text.

# Please note: Accessing OpenAI may incur costs, and large usage may require special approval from OpenAI.
