"""
Script for defining the LLMCharProcessor class, which forms the basis of TraitAccumulator and TraitExtractor.
"""

from typing import List, Dict, Optional, Any
from collections.abc import Callable
from ollama import Client
import json
import copy

from common_scripts import regularise

class LLMCharProcessor:
    """
    Base LLMCharProcessor class, which is extended by TraitAccumulator and TraitExtractor.
    Initialisation, charjson generation, and summary generation are defined here.
    """

    # Model reset timeout
    LLM_TIMEOUT = 60 * 5

    # Run mode name in the summary output; will never be used
    RUN_MODE_NAME = 'desc2json_primitive'

    def __init__(self,
                 sys_prompt:str,
                 base_llm:str,
                 llm_params:dict,
                 llm_name:str = 'desc2matrix',
                 host_url:str = 'http://localhost:11434'):
        """
        Initialise trait extractor.

        Parameters:
            sys_prompt (str): The system prompt to use
            base_llm (str): Name of the base LLM to use
            llm_params (dict): Dictionary specifying model parameters as specified here: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
            llm_name (str): The name of the model to create. Defaults to 'desc2matrix'
            host_url (str): The Ollama host url to use. Defaults to 'http://localhost:11434'
        """

        # Save the parameters
        self.sys_prompt:str = sys_prompt
        self.base_llm:str = base_llm
        self.llm_params:dict = llm_params
        self.llm_name:str = llm_name

        # Build Ollama modelfile
        modelfile = '{}\n{}'.format(
            'FROM {}'.format(self.base_llm),
            '\n'.join(['PARAMETER {} {}'.format(param, value) for param, value in self.llm_params.items() if value != None])
        )

        # Make connection to client and store Ollama client
        self.client:Client = Client(host = host_url, timeout = self.LLM_TIMEOUT)

        # Create model with the specified params
        self.client.create(model = self.llm_name, modelfile = modelfile)

        # Variable to store the extracted characteristics data
        self.sp_chars:List[dict] = []

    def parse_llm_response(self, resp:str, regulariser:Callable[[Any], Optional[Any]]) -> dict:
        """
        Internal function used to parse the LLM response into charjson.
        The output is structured as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json',
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }

        Parameters:
            resp (str): The LLM response string
            regulariser (Callable[[Any], Optional[Any]]): Regulariser / validator function that returns either a regularised charjson or None if the JSON has bad structure. E.g. regularise.regularise_charjson().
        
        Return:
            char_json (dict): Output dict structured as specified above
        """

        # Attempt to parse prompt as JSON
        char_json = {} # Output JSON
        try:
            resp_json = json.loads(resp) # Parse output as JSON
            # Check validity / regularise output
            reg_resp_json = regulariser(resp_json)
            if reg_resp_json != None:
                char_json = {'status': 'success', 'data': reg_resp_json} # Save parsed JSON with status
            else:
                char_json = {'status': 'bad_structure', 'data': str(resp_json)} # Save string with status
        except json.decoder.JSONDecodeError as decode_err: # If LLM returns bad string
            char_json = {'status': 'invalid_json', 'data': resp} # Save string with status
        
        # Return result
        return char_json
    
    def print_status_log(self, status:str, end:str = '') -> None:
        """
        Simple internal function for showing the status log depending on the status code.

        Parameters:
            status (str): The status code from parse_llm_response, either 'success', 'bad_structure', or 'invalid_json'
            end (str): Character to add to the end of the log.
            
        Returns:
            None
        """

        if status == 'invalid_json': # If run returned invalid string that cannot be parsed to JSON
            print('ollama output is not JSON... ', end = end, flush = True)
        elif status == 'bad_structure': # If run returned badly structured JSON
            print('ollama output is JSON but is structured badly... ', end = end, flush = True)
        if status == 'success': # If run succeeded
            print('ollama output successfully parsed! ', end = end, flush = True)

    def prompt2charjson(self, prompt:str, regulariser:Callable[[Any], Optional[Any]] = regularise.regularise_charjson, show_log:bool = False) -> dict:
        """
        Internal function used for extracting charjson with a fully-constructed prompt string.
        The output is structured as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json',
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }

        Parameters:
            prompt (str): The fully constructed prompt string, with descriptions / character lists filled in
            regulariser (Callable[[Any], Optional[Any]]): Regulariser / validator function that returns either a regularised charjson or None if the JSON has bad structure. E.g. regularise.regularise_charjson().
            show_log (bool): If this is set to True, the function will output a log showing parse status. Default is False.

        Returns:
            char_json (dict): The output dict
        """

        resp = self.client.generate(model = self.llm_name,
                                    prompt = prompt,
                                    system = self.sys_prompt)['response']

        # Attempt to parse prompt as JSON
        char_json = self.parse_llm_response(resp, regulariser)

        # Show status log accordingly, if needed
        if show_log:
            self.print_status_log(char_json['status'])
        
        # Return output JSON
        return char_json
    
    def messages2charjson(self, messages:List[Dict[str,str]], regulariser:Callable[[Any], Optional[Any]] = regularise.regularise_charjson, show_log:bool = False) -> dict:
        """
        Internal function used for extracting charjson with fully-constructed messages including the species descriptions, etc.
        The input message must be structured as follows, as used in the ollama.chat function (https://github.com/ollama/ollama-python):
        [
            {'role': 'system' | 'user' | 'assistant', 'content': (message content)},
            (...)
        ]

        Parameters:
            messages (List[Dict[str,str]]): Fully constructed list of messages, with descriptions / character lists filled in
            regulariser (Callable[[Any], Optional[Any]]): Regulariser / validator function that returns either a regularised charjson or None if the JSON has bad structure. E.g. regularise.regularise_charjson().
            show_log (bool): If this is set to True, the function will output a log showing task completion and elapsed time. Default is False.

        Returns:
            char_json (dict): The output containing the status code (['status'] = 'success' | 'bad_structure' | 'invalid_json') and the extracted characteristics(['data'])
        """
        
        # Generate response message
        resp = self.client.chat(model = self.llm_name, stream = False, messages = messages)['message']['content']

        # Attempt to parse prompt as JSON
        char_json = self.parse_llm_response(resp, regulariser)

        # Show status log accordingly, if needed
        if show_log:
            self.print_status_log(char_json['status'])
        
        # Return output JSON
        return char_json
    
    def get_summary(self) -> dict:
        """
        Function for getting the summary of the LLM run outputs.
        The output dictionary is structured as follows:
        {
            'metadata': {
                'params': model parameters,
                'mode': run mode name,
                'sys_prompt': system prompt
            },
            'data': sp_chars data
        }
        
        Parameters:
            None
        
        Returns:
            outdict (dict): Dictionary summary of the run
        """

        # Dictionary to store the final output along with metadata
        outdict = copy.deepcopy({
            'metadata': {
                'params': self.llm_params,
                'mode': self.RUN_MODE_NAME,
                'sys_prompt': self.sys_prompt
            },
            'data': self.sp_chars
        })

        # Return summary dictionary
        return outdict