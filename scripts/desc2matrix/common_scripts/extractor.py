"""
Script for defining TraitExtractor classes.
"""

from typing import List
import time
import json

from common_scripts import process_words
from common_scripts.llmcharprocessor import LLMCharProcessor

class TraitExtractor(LLMCharProcessor):
    """
    Base trait extractor class, used in desc2matrix_wcharlist.py
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_wcharlist'

    def __init__(self,
                 sys_prompt:str,
                 ext_prompt:str,
                 ext_chars:List[str],
                 base_llm:str,
                 llm_params:dict,
                 llm_name:str = 'desc2matrix',
                 host_url:str = 'http://localhost:11434'):
        """
        Initialise trait extractor.

        Parameters:
            sys_prompt (str): The system prompt to use
            ext_prompt (str): The prompt to use for trait extraction
            ext_chars (List[str]): The list of characteristics to extract
            base_llm (str): Name of the base LLM to use
            llm_params (dict): Dictionary specifying model parameters as specified here: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
            llm_name (str): The name of the model to create. Defaults to 'desc2matrix'
            host_url (str): The Ollama host url to use. Defaults to 'http://localhost:11434'
        """

        # Run super initialiser
        super().__init__(sys_prompt, base_llm, llm_params, llm_name, host_url)

        # Store ext_prompt and ext_chars
        self.ext_prompt = ext_prompt
        self.ext_chars = ext_chars
    
    def ext_step(self, spid:str, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for a step in the extraction process, where the traits are extracted from an
        additional species. The traits are stored if store_results is True.
        This function returns the charjson produced by the given description structured as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json',
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }
        
        Parameters:
            spid (str): The WFO species id corresponding to the description
            desc (str): The description to extract the characteristics from
            show_log (bool): If this is set to True, show progress logs. Default is False
            store_results (bool): If this is True, store the extracted characteristics and values in the object. Default is True
        
        Returns:
            char_json (dict): The char_json produced from the given description
        """

        # Variable to store the extracted characteristics and values
        char_json = {}

        # Start log
        start = 0
        if show_log:
            print('trait extraction: processing... ', end = '', flush = True)
            start = time.time()

        # Prepare prompt
        prompt_wcontent = self.ext_prompt.replace('[DESCRIPTION]', desc) # Insert species description
        prompt_wcontent = prompt_wcontent.replace('[CHARACTER_LIST]', '; '.join(self.ext_chars)) # Insert characteristics
        
        # Generate output
        char_json = self.prompt2charjson(prompt_wcontent, show_log = show_log)
        
        # If we need to store the outputs
        if store_results:
            # Update sp_chars
            self.sp_chars.append({
                'coreid': spid,
                'status': char_json['status'], # Status: one of 'success', 'bad_structure', 'invalid_json'
                'original_description': desc,
                'char_json': char_json['data'] if char_json['status'] == 'success' else None, # Only use this if parsing succeeded
                'failed_str': char_json['data'] if char_json['status'] != 'success' else None # Only use this if parsing failed
            })

        # Finish log
        if show_log:
            elapsed_t = time.time() - start
            print(f'done in {elapsed_t:.2f} s!')

        # Return extracted characteristics
        return char_json
    
    def get_summary(self) -> dict:
        """
        Function for getting the summary of the extraction run.
        The output dictionary is structured as follows:
        {
            'metadata': {
                'params': model parameters,
                'mode': run mode name,
                'sys_prompt': system prompt,
                'prompt': extraction prompt,
                'charlist': list of characteristics used
            },
            'data': sp_chars data
        }
        
        Parameters:
            None
        
        Returns:
            outdict (dict): Dictionary summary of the run
        """

        # Run super get_summary()
        outdict = super().get_summary()

        # Add some keys
        outdict['metadata'] = dict(outdict['metadata'],
                       prompt = self.ext_prompt,
                       charlist = self.ext_chars)

        # Return summary dictionary
        return outdict
    
class FollowupTraitExtractor(TraitExtractor):
    """
    Trait extractor with follow-up questions, used in desc2matrix_wcharlist_followup.py
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_wcharlist_followup'

    def __init__(self,
                 sys_prompt:str,
                 ext_prompt:str,
                 f_prompt:str,
                 ext_chars:List[str],
                 base_llm:str,
                 llm_params:dict,
                 llm_name:str = 'desc2matrix',
                 host_url:str = 'http://localhost:11434'):
        """
        Initialise trait extractor.

        Parameters:
            sys_prompt (str): The system prompt to use
            ext_prompt (str): The prompt to use for trait extraction
            f_prompt (str): The prompt to use for follow-up questions
            ext_chars (List[str]): The list of characteristics to extract
            base_llm (str): Name of the base LLM to use
            llm_params (dict): Dictionary specifying model parameters as specified here: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
            llm_name (str): The name of the model to create. Defaults to 'desc2matrix'
            host_url (str): The Ollama host url to use. Defaults to 'http://localhost:11434'
        """

        # Run super initialiser
        super().__init__(sys_prompt, ext_prompt, ext_chars, base_llm, llm_params, llm_name, host_url)

        # Store follow-up prompt
        self.f_prompt = f_prompt

    def ext_step(self, spid:str, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for a step in the extraction process, where the traits are extracted from an
        additional species. The traits are stored if store_results is True.
        This function returns the charjson produced by the given description structured as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json' | 'bad_structure_followup' | 'invalid_json_followup',
            'data': [
                {'characteristic': (characteristic), 'values': {'species id 1': '', (...)}},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }
        
        Parameters:
            spid (str): The WFO species id corresponding to the description
            desc (str): The description to extract the characteristics from
            show_log (bool): If this is set to True, show progress logs. Default is False
            store_results (bool): If this is True, store the extracted characteristics and values in the object. Default is True
        
        Returns:
            char_json (dict): The char_json produced from the given description
        """

        # Generate initial response without storing the results
        char_json = super().ext_step(spid, desc, show_log=show_log, store_results=False)

        # Start log
        start = 0
        if show_log:
            print('follow-up question: processing... ', end = '', flush = True)
            start = time.time()

        if(char_json['status'] != 'success'): # If initial JSON output was invalid or badly structured
            # Just proceed to updating list of chracteristics
            pass
        else: # If the initial JSON output successfully parsed
            # Extract the char_json response
            init_charjson_dat = char_json['data']
            
            # Retrieve omissions
            omissions = process_words.get_omissions(desc, init_charjson_dat)

            # Build the follow-up prompt
            followup_prompt = self.f_prompt.replace('[DESCRIPTION]', desc).replace('[MISSING_WORDS]', '; '.join(sorted(omissions))).replace('[CHARACTER_LIST]', '; '.join(self.ext_chars))

            # Build the messages
            messages = [
                {'role': 'system', 'content': self.sys_prompt}, 
                {'role': 'user', 'content': self.ext_prompt.replace('[DESCRIPTION]', desc)},
                {'role': 'assistant', 'content': json.dumps(init_charjson_dat, indent=4)}, # 'Simulate' the previous model output
                {'role': 'user', 'content': followup_prompt}
            ]

            # Generate followup response
            f_char_json = self.messages2charjson(messages, show_log = show_log)

            # Add '_followup' to status code if the output failed to parse
            if f_char_json['status'] != 'success':
                f_char_json['status'] = '{}_followup'.format(f_char_json['status'])

            # Set char_json as f_char_json
            char_json = f_char_json
        
        # If we need to store the outputs
        if store_results:
            # Update sp_chars
            self.sp_chars.append({
                'coreid': spid,
                'status': char_json['status'], # Status: one of 'success', 'bad_structure', 'invalid_json'
                'original_description': desc,
                'char_json': char_json['data'] if char_json['status'] == 'success' else None, # Only use this if parsing succeeded
                'failed_str': char_json['data'] if char_json['status'] != 'success' else None # Only use this if parsing failed
            })

        # Finish log
        if show_log:
            elapsed_t = time.time() - start
            print(f'done in {elapsed_t:.2f} s!')

        # Return extracted characteristics
        return char_json
    
    def get_summary(self) -> dict:
        """
        Function for getting the summary of the extraction run.
        The output dictionary is structured as follows:
        {
            'metadata': {
                'params': model parameters,
                'mode': run mode name,
                'sys_prompt': system prompt,
                'prompt': extraction prompt,
                'charlist': list of characteristics used,
                'f_prompt': followup prompt,
            },
            'data': sp_chars data
        }
        
        Parameters:
            None
        
        Returns:
            outdict (dict): Dictionary summary of the run
        """

        # Run super get_summary()
        outdict = super().get_summary()

        # Add follow-up prompt
        outdict['metadata'] = dict(outdict['metadata'],
                       f_prompt = self.f_prompt)

        # Return summary dictionary
        return outdict