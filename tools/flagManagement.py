# from dotenv import load_dotenv
import os
import sys

# Custom libraries
from tools.handleFiles import HandleFiles
from tools.systemTools import SystemTools

class FlagsMgmt:

    def __init__(self, _flags):
        # load_dotenv(override=True)
        systemTools = SystemTools()
        self.debug = systemTools.str_to_bool(os.getenv('DEBUG'))
        self.debug_data_output = systemTools.str_to_bool(os.getenv('DEBUG_DATA_OUTPUT'))
        self.debug_function_name = systemTools.str_to_bool(os.getenv('DEBUG_FUNCTION_NAME'))
        print(f"DEBUG: {self.debug}")

        if self.debug_function_name: print(f"***** BEGIN class init FlagsMgmt *****")
        self.processQuestions = False
        availableFlags = ["--processQuestions", "-pq", "--help", "-h", "--llmPrompt", "-lp", "--sigLite", "-sl"]
        fileHandler = HandleFiles()
        # Read the flags set at the command line
        # Check if multiple flags are present
        try:
            for flag in _flags:
                if flag in availableFlags:
                    if "--help" == flag or "-h" == flag:
                        print("-h or --help : this help")
                        print("-pq or --processQuestions : process the questions immediately after reading the file")
                        print("-lm or --llm_prompt : Add a custom prompt to the LLM model")
                        print("-sl or --sigLite : Use SigLite to process the questions. Only works with -pq flag")
                        sys.exit(0)
                    if "--processQuestions" == flag or "-pq" == flag:
                        print(f"Request to Process questions with answer file:")
                        self.processQuestions = True
                    if "--llmPrompt" == flag or "-lp" == flag:
                        print(f"Request to add LLM Custom Prompt with answer file:")
                        try:
                            llm_prompt_parts = []
                            for i in range(_flags.index(flag) + 1, len(_flags)):
                                if _flags[i].startswith('-'):
                                    break
                                llm_prompt_parts.append(_flags[i])
                            self.llmPrompt = ' '.join(llm_prompt_parts)
                            if self.debug: print(f"LLM Prompt: {self.llmPrompt}")
                        except IndexError:
                            print("Error: No value provided for --llm_prompt or -lp flag. Omitting LLM Custom Prompt.")
                            self.llmPrompt = ""
                    if "--sigLite" == flag or "-sl" == flag:
                        print(f"Request to use SigLite:")
                        self.sigLite = True
            if self.processQuestions:
                if self.sigLite and os.path.exists(os.path.join(fileHandler.folder_path, os.getenv('SIGLITE_ANSWER_FILE'))):
                    self.answerSource = os.getenv('SIGLITE_ANSWER_FILE')
                    validFile=True
                elif self.sigLite:
                    print(f"SigLite flag set but {os.getenv('SIGLITE_ANSWER_FILE')} not found in /{fileHandler.folder_path}/")
                    validFile = False
                else:
                    validFile = False
                while validFile == False:
                    response = fileHandler.get_input(f"Need to supply the Source of answers?\n" \
                        f"Must be in /{fileHandler.folder_path}/\n" \
                        f"Please enter filename(e.g. answers.xlsx):")
                    if os.path.exists(os.path.join(fileHandler.folder_path, response)):
                        if response.endswith('.xlsx'):
                            self.answerSource = response
                            validFile = True 
                        else:
                            print(f"\nFilename needs to end with .xlsx\n")
                            continue
                    else:
                        print(f"\nThe file was not found.\nIt must exist in /{fileHandler.folder_path}/")

        except Exception as e:
            print(f"Error in flags: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("User Cancelled in flag management")
            sys.exit(1)
        if self.debug_function_name: print(f"***** END class init FlagsMgmt *****")
