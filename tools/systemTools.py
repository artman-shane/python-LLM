import os
import re
import sys
import json

class SystemTools:
    def __init__(self,logging):
        self.logging = logging

    def str_to_bool(self, _string):
            if _string.lower() in ("true","1","yes","on"):
                return True
            else:
                return False
            
    # Get Question from Questions. Must be JSON object
    # Parameters:
    #   questions: JSON object containing the questions
    def getFlatJson(self, _questions):
        self.logging.debug(f"***** BEGIN func getFlatJson *****")
        # Test if object is json
        try:
            # Check if there is a parent key. Could be a sheet or page key.
            self.logging.info(f"Checking if questions is a dictionary")
            if isinstance(_questions, dict):
                self.logging.info(f"Questions is a dictionary. Collapsing...")
                collapsedQuestions = []
                for key in _questions:
                    # Combine the sheet as a key in the questions.
                    # Iterate over the list and add the new key to each dictionary
                    new_items = []
                    for item in _questions[key]:
                        item['new_id'] = key
                        new_items.append(item)
                    collapsedQuestions.extend(new_items)
        except Exception as e:
            print(f"Error: Questions must be a JSON Dictionary object {e}")
        self.logging.debug(f"***** END func getFlatJson *****")
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