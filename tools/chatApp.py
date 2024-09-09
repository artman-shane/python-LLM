# System libraries
from dotenv import load_dotenv
import os
import sys

# Third-party libraries
from openai import OpenAI # Used to interact with the OpenAI API

class ChatApp:
    def __init__(self,fileHandler, folder_path,filename):
        full_path = os.path.join(folder_path, filename)
        # Set the OpenAI API Key
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        try:
            if not os.path.exists(full_path) == False:
                print(f"Reading file {filename}")
                if filename.endswith('.txt'):
                    print(f"Reading txt file: {filename}")
                    self.context = fileHandler.read_txt_file(full_path)
                elif filename.endswith('.pdf'):
                    print(f"Reading pdf file: {filename}")
                    self.context = fileHandler.read_pdf_file(full_path)
                elif filename=="Twilio-SIG Lite-2023.xlsx":
                    print(f"Reading SIG Lite file: {filename}")
                    self.context = fileHandler.read_sigLite_answers(full_path)
                    print("Number of answers read:", len(self.context))
                else:
                    print(f"Invalid filename")
                    raise ValueError("Invalid file extension. Only .txt, .pdf, and \"Twilio-SIG Lite-2023.xlsx\" files are supported.")
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
            print(f"\nAn error occurred: {e}")
            sys.exit(1)

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