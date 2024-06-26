from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import json
load_dotenv()




# Set the OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

fileName = os.path.join(os.getenv('OUTPUT_DIR',"output/"),os.getenv("DOCUMENTS_FILE",'documents.json'))
with open(fileName, 'r') as file:
    documents = json.load(file)

print("Read in", len(documents), "documents")

# Define the prompt
prompt = "Please ensure that responses are formated for easy reading. Provide a header for each response.\n"
# prompt += "Please provide a 1 sentence summary of the following documents. Only 1 sentence per document content:\n"
document_idx=0
for document in documents:
    prompt += "document_idx: " + document['content'] + "\n"
    document_idx+=1

print("Prompt has been created.")

# Get the model to generate a response
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are going to build a flex plugin. Please construct a plugin that will provide an interface to the OpenAI API for Flex 2.0"},
        {"role": "user", "content": prompt},
    ]
)

# Print the result
print(response.choices[0].message.content)

# Please replace `'your-api-key'` with your actual OpenAI API key. The key is secret and should be kept confidential. The `'context_file.txt'` should contain the context information and this will be fed into GPT-3 model. The `prompt` is where you can specify the task for the AI and the `completion` contains your generated text.

# Please note: Accessing OpenAI may incur costs, and large usage may require special approval from OpenAI.
