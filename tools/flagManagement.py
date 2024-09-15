# from dotenv import load_dotenv
import os
import sys

# Custom libraries
from tools.handleFiles import HandleFiles
from tools.systemTools import SystemTools

class FlagsMgmt:

    def __init__(self, logging, _flags):
        self.logging = logging
        systemTools = SystemTools(self.logging)
        self.logging.info(f"Initializing handle flags")
        self.logging.debug(f"***** BEGIN class init FlagsMgmt *****")
        self.logging.debug(f"Flags: {_flags}")
        self.processQuestions = False
        self.logging.debug(f"Default Process Questions: {self.processQuestions}")
        availableFlags = ["--processQuestions", "-pq", "--help", "-h", "--llmPrompt", "-lp", "--sigLite", "-sl"]
        self.logging.debug(f"Avail Flasge: {availableFlags}")
        fileHandler = HandleFiles(self.logging)
        # Read the flags set at the command line
        # Check if multiple flags are present
        try:
            for flag in _flags:
                self.logging.info(f"Processing flag: {flag}")
                if flag in availableFlags:
                    self.logging.info(f"Found flag.")
                    if "--help" == flag or "-h" == flag:
                        self.logging.debug(f"Help requested")
                        print("-h or --help : this help")
                        print("-pq or --processQuestions : process the questions immediately after reading the file")
                        print("-lm or --llm_prompt : Add a custom prompt to the LLM model")
                        print("-sl or --sigLite : Use SigLite to process the questions. Only works with -pq flag")
                        sys.exit(0)
                    if "--processQuestions" == flag or "-pq" == flag:
                        print(f"Request to Process questions with answer file:")
                        self.processQuestions = True
                        self.logging.debug(f"Process Questions: {self.processQuestions}")
                    if "--llmPrompt" == flag or "-lp" == flag:
                        self.logging.info(f"Request to add LLM Custom Prompt")
                        print(f"Request to add LLM Custom Prompt with answer file:")
                        try:
                            llm_prompt_parts = []
                            for i in range(_flags.index(flag) + 1, len(_flags)):
                                if _flags[i].startswith('-'):
                                    break
                                llm_prompt_parts.append(_flags[i])
                            self.llmPrompt = ' '.join(llm_prompt_parts)
                            self.logging.info(f"LLM Prompt: {self.llmPrompt}")
                        except IndexError:
                            self.logging.error(f"There was an index error in initializing FlagsMgmt")
                            print("Error: No value provided for --llm_prompt or -lp flag. Omitting LLM Custom Prompt.")
                            self.llmPrompt = ""
                    if "--sigLite" == flag or "-sl" == flag:
                        self.logging.info(f"Requesting processing with SIG Lite")
                        print(f"Request to use SigLite:")
                        self.sigLite = True
            if self.processQuestions:
                self.logging.info(f"Checking for file: {os.path.join(fileHandler.folder_path, os.getenv('SIGLITE_ANSWER_FILE'))}")
                self.logging.info(f"File Exists: {os.path.exists(os.path.join(fileHandler.folder_path, os.getenv('SIGLITE_ANSWER_FILE')))}")
                if self.sigLite and os.path.exists(os.path.join(fileHandler.folder_path, os.getenv('SIGLITE_ANSWER_FILE'))):
                    self.answerSource = os.getenv('SIGLITE_ANSWER_FILE')
                    self.logging.info(f"Answer Source: {self.answerSource}")
                    validFile=True
                elif self.sigLite:
                    self.logging.info(f"SigLite flag set but {os.getenv('SIGLITE_ANSWER_FILE')} not found in /{fileHandler.folder_path}/")
                    print(f"SigLite flag set but {os.getenv('SIGLITE_ANSWER_FILE')} not found in /{fileHandler.folder_path}/")
                    validFile = False
                else:
                    validFile = False
                while validFile == False:
                    response = fileHandler.get_input(f"Need to supply the Source of answers?\n" \
                        f"Must be in /{fileHandler.folder_path}/\n" \
                        f"Please enter filename(e.g. answers.xlsx):")
                    self.logging.info(f"Answer file supplised: {response}. Does it exist?")
                    if os.path.exists(os.path.join(fileHandler.folder_path, response)):
                        self.logging.info(f"Yes, it exists.")
                        if response.endswith('.xlsx'):
                            self.logging.info(f"It is an XLSX file")
                            self.answerSource = response
                            validFile = True 
                        else:
                            self.logging.info(f"It is not an XLSX file. Repropmt")
                            print(f"\nFilename needs to end with .xlsx\n")
                            continue
                    else:
                        self.logging.info(f"File not found. Reprompt")
                        print(f"\nThe file was not found.\nIt must exist in /{fileHandler.folder_path}/")

        except Exception as e:
            self.logging.critical(f"Exception: {e}")
            print(f"Error in flags: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            self.logging.warning(f"User Cancelled during flag management")
            print("User Cancelled in flag management")
            sys.exit(1)
        self.logging.debug(f"***** END class init FlagsMgmt *****")
