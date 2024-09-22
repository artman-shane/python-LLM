# from dotenv import load_dotenv
import os
import sys

# Custom libraries
from tools.handleFiles import HandleFiles
from tools.systemTools import SystemTools

class FlagsMgmt:

    def __init__(self, logger, _flags):
        self.logger = logger
        systemTools = SystemTools(self.logger)
        self.logger.info(f"Initializing handle flags")
        self.logger.debug(f"***** BEGIN class init FlagsMgmt *****")
        self.logger.debug(f"Flags: {_flags}")
        self.processQuestions = False
        self.logger.debug(f"Default Process Questions: {self.processQuestions}")
        availableFlags = ["--processQuestions", "-pq", "--help", "-h", "--llmPromptQuestions", "-lpq", "--llmPromptAnswers", "-lpa", "--sigLite", "-sl"]
        self.logger.debug(f"Avail Flasge: {availableFlags}")
        fileHandler = HandleFiles(self.logger)
        self.llmPromptQuestions = ""
        self.llmPromptAnswers = ""

        # Read the flags set at the command line
        # Check if multiple flags are present
        try:
            for flag in _flags:
                self.logger.info(f"Processing flag: {flag}")
                if flag in availableFlags:
                    self.logger.info(f"Found flag.")
                    if "--help" == flag or "-h" == flag:
                        self.logger.debug(f"Help requested")
                        print("-h or --help : this help")
                        print("-pq or --processQuestions : process the questions immediately after reading the file")
                        print("-lpa or --llmPromptAnswers : Add a custom prompt to the LLM model when answering ")
                        print("-lpq or --llmPromptQuestions : Add a custom prompt to the LLM model when generating questions ")
                        print("-sl or --sigLite : Use SigLite to process the questions. Only works with -pq flag")
                        sys.exit(0)
                    if "--processQuestions" == flag or "-pq" == flag:
                        print(f"Request to Process questions with answer file:")
                        self.processQuestions = True
                        self.logger.debug(f"Process Questions: {self.processQuestions}")
                    if "--llmPromptQuestions" == flag or "-lpq" == flag:
                        self.logger.info(f"Request to add LLM Questions Custom Prompt")
                        try:
                            llm_prompt_parts = []
                            for i in range(_flags.index(flag) + 1, len(_flags)):
                                if _flags[i].startswith('-'):
                                    break
                                llm_prompt_parts.append(_flags[i])
                            self.llmPromptQuestions = ' '.join(llm_prompt_parts)
                            self.logger.info(f"LLM Prompt: {self.llmPromptQuestions}")
                        except IndexError:
                            self.logger.error(f"There was an index error in initializing FlagsMgmt")
                            print("Error: No value provided for --llm_prompt or -lp flag. Omitting LLM Custom Prompt.")
                            self.llmPromptQuestions = ""
                    if "--llmPromptAnswers" == flag or "-lpa" == flag:
                        self.logger.info(f"Request to add LLM Answers Custom Prompt")
                        try:
                            llm_prompt_parts = []
                            for i in range(_flags.index(flag) + 1, len(_flags)):
                                if _flags[i].startswith('-'):
                                    break
                                llm_prompt_parts.append(_flags[i])
                            self.llmPromptAnswers = ' '.join(llm_prompt_parts)
                            self.logger.info(f"LLM Prompt: {self.llmPromptAnswers}")
                        except IndexError:
                            self.logger.error(f"There was an index error in initializing FlagsMgmt")
                            print("Error: No value provided for --llm_prompt or -lp flag. Omitting LLM Custom Prompt.")
                            self.llmPromptAnswers = ""
                    if "--sigLite" == flag or "-sl" == flag:
                        self.logger.info(f"Requesting processing with SIG Lite")
                        print(f"Request to use SigLite:")
                        self.sigLite = True
            if self.processQuestions:
                self.logger.info(f"Checking for file: {os.path.join(fileHandler.folder_path, os.getenv('SIGLITE_ANSWER_FILE'))}")
                self.logger.info(f"File Exists: {os.path.exists(os.path.join(fileHandler.folder_path, os.getenv('SIGLITE_ANSWER_FILE')))}")
                if self.sigLite and os.path.exists(os.path.join(fileHandler.folder_path, os.getenv('SIGLITE_ANSWER_FILE'))):
                    self.answerSource = os.getenv('SIGLITE_ANSWER_FILE')
                    self.logger.info(f"Answer Source: {self.answerSource}")
                    validFile=True
                elif self.sigLite:
                    self.logger.info(f"SigLite flag set but {os.getenv('SIGLITE_ANSWER_FILE')} not found in /{fileHandler.folder_path}/")
                    print(f"SigLite flag set but {os.getenv('SIGLITE_ANSWER_FILE')} not found in /{fileHandler.folder_path}/")
                    validFile = False
                else:
                    validFile = False
                while validFile == False:
                    response = fileHandler.get_input(f"Need to supply the Source of answers?\n" \
                        f"Must be in /{fileHandler.folder_path}/\n" \
                        f"Please enter filename(e.g. answers.xlsx):")
                    self.logger.info(f"Answer file supplised: {response}. Does it exist?")
                    if os.path.exists(os.path.join(fileHandler.folder_path, response)):
                        self.logger.info(f"Yes, it exists.")
                        if response.endswith('.xlsx'):
                            self.logger.info(f"It is an XLSX file")
                            self.answerSource = response
                            validFile = True 
                        else:
                            self.logger.info(f"It is not an XLSX file. Repropmt")
                            print(f"\nFilename needs to end with .xlsx\n")
                            continue
                    else:
                        self.logger.info(f"File not found. Reprompt")
                        print(f"\nThe file was not found.\nIt must exist in /{fileHandler.folder_path}/")

        except Exception as e:
            self.logger.critical(f"Exception: {e}")
            print(f"Error in flags: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            self.logger.warning(f"User Cancelled during flag management")
            print("User Cancelled in flag management")
            sys.exit(1)
        self.logger.debug(f"***** END class init FlagsMgmt *****")
