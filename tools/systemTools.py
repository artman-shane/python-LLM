import os
import re
import sys
import json

class SystemTools:
    def __init__(self,logger):
        self.logger = logger
    
    def set_file_handler(self, fileHandler):
        self.fileHandler = fileHandler

    def str_to_bool(self, _string):
            if _string.lower() in ("true","1","yes","on"):
                return True
            else:
                return False
            
    # Get Question from Questions. Must be JSON object
    # Parameters:
    #   questions: JSON object containing the questions
    def getFlatJson(self, _questions):
        self.logger.debug(f"***** BEGIN func getFlatJson *****")
        # Test if object is json
        try:
            # Check if there is a parent key. Could be a sheet or page key.
            self.logger.info(f"Checking if questions is a dictionary")
            if isinstance(_questions, dict):
                self.logger.info(f"Questions is a dictionary. Collapsing...")
                collapsedQuestions = []
                for key in _questions:
                    self.logger.debug(f"Processing Key: {key}")
                    # Combine the sheet as a key in the questions.
                    # Iterate over the list and add the new key to each dictionary
                    new_items = []
                    for item in _questions[key]:
                        # self.logger.debug(f"Item: {item}")
                        # item['new_id'] = key
                        new_items.append(item)
                    collapsedQuestions.extend(new_items)
        except Exception as e:
            print(f"Error: Questions must be a JSON Dictionary object {e}")
        self.logger.debug(f"***** END func getFlatJson *****")
        return collapsedQuestions
    
    # Function to clean up a JSON string
    # Parameters:
    # json_str - the JSON string to clean up
    def clean_json(self, json_str):
        # Clean JSON
        # Use regular expression to find the first '{' and the last '}'
        match = re.search(r'[\{,\[].*[\},\]]', json_str, re.DOTALL)
        if match:
            return match.group(0)
        else:
            raise ValueError("Invalid JSON format")
        
    # Read the questions from the json input and process them
    # Processing could include sending the questions to LLM and getting the answers or simply rewritng the questions to an output file
    # Parameters:
    # _question - as a JSON object. Ensure that the _question is formatted with: {"Question": "Question Text"} optional: {"Question": "Question Text", "Choices": ["Choice 1", "Choice 2", "Choice 3"]}
    # _knowledge - The knowledge to answer the question as a JSON object
    # flagMgmt - the flag management class reference
    # llm - the LLM class reference
    # returns - json object of the question and response
    # TODO: Need to see if when skipping a question it still ends up in the output. If so, I need to ensure that a notation is made in the output that potential questions were skipped and specifically which ones..
    def process_question(self, _question, _answers, flagMgmt, llm):
        self.logger.info(f"Process Question")

        # Convert the question JSON string into object in python
        question_json = json.loads(_question)

        # Flatten the JSON object to single level for easy processing
        self.logger.info(f"question_json type: {type(question_json)}")
        self.logger.debug(f"question_json: {question_json}")

        # Here we have the Questions in a JSON object from xlsx. We are in the loop to process each question.
        # If the -pq flag is set, we need to send the question to LLM and get the response when we get the answers together.
        print(f"Processing questions and answers")
        try:
            for key in question_json: self.logger.debug(f"{key}: {question_json[key]}")
            returned_results = json.loads(llm.getAnswers(question_json, _answers, flagMgmt.llmPromptAnswers))

        except Exception as e:
            print(f"Could not process question.")
            print(f"Question: {question_json}")
            print(f"Skipping...")
            # TODO: need to add the question to the output file with a note that it was skipped

        # Returns JSON Object
        return returned_results

    # Read the questions from the json input and process them
    # Processing could include sending the questions to LLM and getting the answers or simply rewritng the questions to an output file
    # Parameters:
    # questionsFilename - the filename of the questions file
    # outputFilename - the filename of the output file
    # flagMgmt - the flag management class reference
    # llm - the LLM class reference
    # returns - json object of the questions and answers
    # TODO: Need to see if when skipping a question it still ends up in the output. If so, I need to ensure that a notation is made in the output that potential questions were skipped and specifically which ones..
    def process_questions(self, questions, flagMgmt, llm):
        max_questions = int(os.getenv('MAX_QUESTIONS_TO_ANSWER', 0))
        self.logger.debug(f"***** BEGIN func process_questions *****")

        self.logger.info("Processing questions")
        # Convert the question JSON string into object in python
        questions_json = json.loads(questions)

        # Placeholder for responses
        responses = {}

        # Flatten the JSON object to single level for easy processing
        self.logger.info(f"questions_json type: {type(questions_json)}")
        self.logger.debug(f"questions_json: {questions_json}")
        questions_json = self.getFlatJson(questions_json)
        if max_questions > 0:
            print(f"Restricting questions to process to {max_questions} per .env")
        else:
            print(f"Processing {len(questions_json)} questions")

        # Here we have the Questions in a JSON object from xlsx. We are in the loop to process each question.
        # If the -pq flag is set, we need to send the question to LLM and get the response when we get the answers together.
        print(f"Reading answers from {os.path.join(self.fileHandler.folder_path, flagMgmt.answerSource)}")
        answers = json.loads(self.fileHandler.read_sigLite_answers(f"{os.path.join(self.fileHandler.folder_path, flagMgmt.answerSource)}"))
        print(f"Processing questions and answers")
        results = []
        x=0
        self.logger.debug(f"questions_json type: {type(questions_json)}")
        for question in questions_json:
            try:
                x+=1
                if max_questions > 0 and x > max_questions:
                    print(f"Reached the maximum number of questions to process ({max_questions}).\nSkipping remaining questions...")
                    break

                self.logger.debug(f"Question: {question}")
                # _question = ""
                # _choices = ""
                # _question_to_llm = {}
                # for key in question:
                #     if str.upper(key) == "QUESTION":
                #         _question = question[key]
                #         self.logger.debug(f"{key}: {_question}")
                #         # print(f"{key}: {_question}")
                #         _question_to_llm[key] = _question
                #     if str.upper(key) == "CHOICES":
                #         _choices = question[key]
                #         self.logger.debug(f"{key}: {_choices}")
                #         # print(f"{key}: {_choices}")
                #         _question_to_llm[key] = _choices
                #     if str.upper(key) == "ID":
                #         _id = question[key]
                #         self.logger.debug(f"{key}: {_id}")
                #         # print(f"{key}: {_id}")
                #         _question_to_llm[key] = _id
                    
                print(f"Processing question: {x} of {len(questions_json)}")
                returned_results = llm.getAnswers(question, answers, flagMgmt.llmPromptAnswers)
                results.append(json.loads(returned_results))

            except Exception as e:
                print(f"Could not process question {x} of {len(questions_json)}.")
                print(f"Question: {question}")
                print(f"Skipping...")
                results.append({"Question": question, "Response": "Skipped"})
                # TODO: need to add the question to the output file with a note that it was skipped
        return results