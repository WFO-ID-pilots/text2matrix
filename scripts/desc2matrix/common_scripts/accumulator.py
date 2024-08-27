"""
Script for defining TraitAccumulator classes.
"""

from typing import List
import time
import json
import copy

from common_scripts import regularise, process_words
from common_scripts.llmcharprocessor import LLMCharProcessor

class TraitAccumulator(LLMCharProcessor):
    """
    Base trait accumulator class, used in desc2matrix_accum.py
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_accum'

    def __init__(self,
                 sys_prompt:str,
                 init_prompt:str,
                 accum_prompt:str,
                 base_llm:str,
                 llm_params:dict,
                 llm_name:str = 'desc2matrix',
                 host_url:str = 'http://localhost:11434'):
        """
        Initialise trait accumulator.

        Parameters:
            sys_prompt (str): The system prompt to use
            init_prompt (str): The prompt to use to get the initial list of traits, either by tabulation or from a single species
            accum_prompt (str): The prompt to use for trait accumulation
            base_llm (str): Name of the base LLM to use
            llm_params (dict): Dictionary specifying model parameters as specified here: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
            llm_name (str): The name of the model to create. Defaults to 'desc2matrix'
            host_url (str): The Ollama host url to use. Defaults to 'http://localhost:11434'
        """
        
        # Run super initialiser
        super().__init__(sys_prompt, base_llm, llm_params, llm_name, host_url)

        # Store parameters
        self.init_prompt = init_prompt
        self.accum_prompt = accum_prompt

        # Variable to store characteristic list history
        self.charlist_history:List[List[str]] = []

    def extract_init_chars(self, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for extracting the initial list of characteristics from a single species description.
        The initial list of characteristics is stored in the object if store_results is true.
        The resulting char_json from the processed description is returned, which is formatted as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json',
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }
        
        Parameters:
            desc (str): The description to extract the initial characteristics from
            show_log (bool): If this is set to True, show progress logs. Default is False
        
        Returns:
            char_json (dict): The resulting char_json from the processed description
        """

        # Prepare prompt
        prompt_wcontent = self.init_prompt.replace('[DESCRIPTION]', desc) # Insert species description

        # Generate LLM output for the description
        char_json = self.prompt2charjson(prompt_wcontent, show_log = show_log)

        # If we need to store the resulting list of characteristics
        if store_results:
            # Extract list of characteristics (empty list if the run didn't succeed)
            init_charlist = ([char['characteristic'] for char in char_json['data']]
                            if char_json['status'] == 'success' else [])

            # Store list of characteristics
            self.charlist_history = [init_charlist]
        
        # Return extracted initial list of characteristics
        return char_json
    
    def accum_step(self, spid:str, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for a step in the accumulation process, where the traits are extracted from an
        additional species and the list of characteristics is updated if
        the new list of characteristics is longer than the most recent list.
        This function returns the char_json from the processed description, which is formatted as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json',
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }
        
        Parameters:
            spid (str): The WFO id of the species
            desc (str): The description to extract the characteristics from
            show_log (bool): If this is set to True, show progress logs. Default is False
            store_results (bool): Whether to store the output list of characteristics and char_json to use in the following accumulation steps. Default is True
        
        Returns:
            char_json (dict): Processed char_json from the species description
        """

        # Status log
        start = 0
        if show_log:
            print('trait accumulation: processing... ', end = '', flush = True)
            start = time.time()

        # Check if charlist has been initialised
        if self.charlist_history == []:
            raise Exception("Charlist has not been initialised. You must run extract_init_chars() first before running accum_step().")

        # Get the latest list of characteristics
        last_charlist = self.charlist_history[len(self.charlist_history) - 1]

        # Prepare prompt
        prompt_wcontent = self.accum_prompt.replace('[DESCRIPTION]', desc) # Insert species description
        prompt_wcontent = prompt_wcontent.replace('[CHARACTER_LIST]', '; '.join(last_charlist)) # Insert characteristics

        # Generate output with predetermined character list
        char_json = self.prompt2charjson(prompt_wcontent, show_log = show_log)

        # If we need to store the results
        if store_results:
            # Extract list of characteristics (copy of latest list if run didn't succeed)
            new_charlist = ([char['characteristic'] for char in char_json['data']]
                            if char_json['status'] == 'success' else copy.deepcopy(last_charlist))
            
            # If the new list of characteristics is shorter than the previous one, override with the previous one
            new_charlist = new_charlist if len(new_charlist) > len(last_charlist) else copy.deepcopy(last_charlist)

            # Store list of characteristics
            self.charlist_history.append(new_charlist)

            # Update sp_chars
            self.sp_chars.append({
                'coreid': spid,
                'status': char_json['status'], # Status: one of 'success', 'bad_structure', 'invalid_json'
                'original_description': desc,
                'char_json': char_json['data'] if char_json['status'] == 'success' else None, # Only use this if parsing succeeded
                'failed_str': char_json['data'] if char_json['status'] != 'success' else None # Only use this if parsing failed
            })
        
        # Status log
        if show_log:
            elapsed_t = time.time() - start
            print(f'done in {elapsed_t:.2f} s!')

        # Return char_json
        return char_json
    
    def get_summary(self) -> dict:
        """
        Function for getting the summary of the accumulation run.
        The output dictionary is structured as follows:
        {
            'metadata': {
                'params': model parameters,
                'mode': run mode name,
                'sys_prompt': system prompt used,
                'init_prompt': initial trait extraction / tabulation prompt,
                'prompt': accumulation prompt
            },
            'data': sp_chars data,
            'charlist_len_history': list of the charlist lengths,
            'charlist_history': list of the charlists used
        }
        
        Parameters:
            None
        
        Returns:
            outdict (dict): Dictionary summary of the run
        """

        # Run super get_summary()
        outdict = super().get_summary()

        # Add some keys to metadata
        outdict['metadata'] = dict(
            outdict['metadata'],
            init_prompt = self.init_prompt,
            prompt = self.accum_prompt
        )

        # Add charlist lengths and history as data
        outdict = dict(
            outdict,
            charlist_len_history = [len(charlist) for charlist in self.charlist_history],
            charlist_history = self.charlist_history
        )

        # Return summary dictionary
        return outdict

class TabTraitAccumulator(TraitAccumulator):
    """
    Trait accumulator with initial tabulation, used in desc2matrix_accum_tab.py
    NB: For TabTraitAccumulator, init_prompt is the tabulation prompt.
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_accum_tab'

    def extract_init_chars(self, sp_ids:List[str], descs:List[str], show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for extracting the initial list of characteristics by tabulating multiple species descriptions.
        The generated initial list of characteristics is stored in the object if store_results is true.
        The resulting char_json from the processed description is returned, which is formatted as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json',
            'data': [
                {'characteristic': (characteristic), 'values': {'species id 1': '', (...)}},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }
        
        Parameters:
            sp_ids (List[str]): The species ids corresponding to the descriptions
            desc (List[str]): The descriptions to use for initial tabulation
            show_log (bool): If this is set to True, show progress logs. Default is False
            store_results (bool): If true, store the resulting list of initial characteristics in the object. Default is True
        
        Returns:
            char_json (dict): The resulting char_json from the processed description
        """

        # Build description string
        # NB: the species ID is a 'made-up' wfo id.
        desc_str = '\n\n'.join(['Species ID: {}\n\nSpecies description:\n{}'.format(spid, desc) for spid, desc in zip(sp_ids, descs)])

        # Build prompt string
        prompt_wcontent = self.init_prompt.replace('[DESCRIPTIONS]', desc_str)
        
        # Generate LLM output for the description
        # NB: The regulariser for table output must be used here.
        char_json = self.prompt2charjson(prompt_wcontent, regulariser = regularise.regularise_table, show_log = show_log)

        # If we need to store the results
        if store_results:
            # Extract list of characteristics (empty list if the run didn't succeed)
            init_charlist = ([char['characteristic'] for char in char_json['data']]
                            if char_json['status'] == 'success' else [])

            # Store list of characteristics
            self.charlist_history = [init_charlist]
        
        # Return resulting char_json
        return char_json
    
class FollowupTraitAccumulator(TraitAccumulator):
    """
    Trait accumulator with follow-up questions and without tabulation, currently only used internally
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_accum_followup'

    def __init__(self,
                 sys_prompt:str,
                 init_prompt:str,
                 accum_prompt:str,
                 f_prompt:str,
                 base_llm:str,
                 llm_params:dict,
                 llm_name:str = 'desc2matrix',
                 host_url:str = 'http://localhost:11434'):
        """
        Initialise trait accumulator.

        Parameters:
            sys_prompt (str): The system prompt to use
            init_prompt (str): The prompt to use to get the initial list of traits, either by tabulation or from a single species
            accum_prompt (str): The prompt to use for trait accumulation
            f_prompt (str): The follow-up prompt
            base_llm (str): Name of the base LLM to use
            llm_params (dict): Dictionary specifying model parameters as specified here: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
            llm_name (str): The name of the model to create. Defaults to 'desc2matrix'
            host_url (str): The Ollama host url to use. Defaults to 'http://localhost:11434'
        """

        # Store follow-up prompt
        self.f_prompt = f_prompt

        # Run superclass initiator to store parameters and initialist Ollama model
        super().__init__(sys_prompt, init_prompt, accum_prompt, base_llm, llm_params, llm_name, host_url)

    def accum_step(self, spid:str, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for a step in the accumulation process, where the traits are extracted from an
        additional species and the list of characteristics is updated if
        the new list of characteristics is longer than the most recent list.
        This version of the function asks the LLM a 'follow-up' question at each step,
        which includes a list of words in the original description that it has omitted
        in the initial response. This is to increase the completeness of characteristics retrieved.
        This function returns the char_json after the follow-up question, which is formatted as follows:
        {
            'status': 'success' | 'bad_structure' | 'invalid_json' | 'bad_structure_followup' | 'invalid_json_followup',
            'data': [
                {'characteristic': (characteristic), 'values': {'species id 1': '', (...)}},
                (...)
            ] IF STATUS IS SUCCESS ELSE (string that failed to parse)
        }

        Parameters:
            spid (str): The WFO id of the species.
            desc (str): The botanical description of the plant species.
            show_log (bool): If this is set to True, the function will output a log of the run status. Default is False.
            store_results (bool): If this is True, the processed trait list and characteristic values from the description will be stored in the object. Default is True.

        Returns:
            char_json (dict): The new list of characteristic names
        """

        # Generate initial response without storing the results by calling the super accum_step function
        char_json = super().accum_step(spid, desc, show_log = show_log, store_results = False)

        # Status log
        start = 0
        if show_log:
            print('follow-up question: processing... ', end = '', flush = True)
            start = time.time()

        # Get the latest list of characteristics
        last_charlist = self.charlist_history[len(self.charlist_history) - 1]

        if(char_json['status'] != 'success'): # If initial JSON output was invalid or badly structured
            # Just proceed to updating list of chracteristics
            pass
        else: # If the initial JSON output successfully parsed
            # Extract the char_json response
            init_charjson_dat = char_json['data']
            
            # Retrieve omissions
            omissions = process_words.get_omissions(desc, init_charjson_dat)

            # Build the follow-up prompt
            followup_prompt = self.f_prompt.replace('[DESCRIPTION]', desc).replace('[MISSING_WORDS]', '; '.join(sorted(omissions))).replace('[CHARACTER_LIST]', '; '.join(last_charlist))

            # Build the messages
            messages = [
                {'role': 'system', 'content': self.sys_prompt}, 
                {'role': 'user', 'content': self.accum_prompt.replace('[DESCRIPTION]', desc)},
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

        # If we need to store the results in the object
        if store_results:
            # Extract list of characteristics (copy of latest list if run didn't succeed)
            new_charlist = ([char['characteristic'] for char in char_json['data']]
                            if char_json['status'] == 'success' else copy.deepcopy(last_charlist))
            
            # If the new list of characteristics is shorter than the previous one, override with the previous one
            new_charlist = new_charlist if len(new_charlist) > len(last_charlist) else copy.deepcopy(last_charlist)

            # Store list of characteristics
            self.charlist_history.append(new_charlist)

            # Update sp_chars
            self.sp_chars.append({
                'coreid': spid,
                'status': char_json['status'], # Status: one of 'success', 'bad_structure', 'invalid_json', 'bad_structure_followup', 'invalid_json_followup'
                'original_description': desc,
                'char_json': char_json['data'] if char_json['status'] == 'success' else None, # Only use this if parsing succeeded
                'failed_str': char_json['data'] if char_json['status'] != 'success' else None # Only use this if parsing failed
            })

        # Status log
        if show_log:
            elapsed_t = time.time() - start
            print(f'done in {elapsed_t:.2f} s!')

        # Return char_json
        return char_json
    
    def get_summary(self) -> dict:
        """
        Function for getting the summary of the accumulation run.
        The output dictionary is structured as follows:
        {
            'metadata': {
                'params': model parameters,
                'mode': run mode name,
                'sys_prompt': system prompt,
                'init_prompt': initial trait extraction prompt,
                'f_prompt': follow-up prompt
            },
            'data': sp_chars data
            'charlist_len_history': list of the charlist lengths,
            'charlist_history': list of the charlists used
        }
        
        Parameters:
            None
        
        Returns:
            outdict (dict): Dictionary summary of the run
        """

        # Dictionary to store the final output along with metadata
        outdict = super().get_summary()

        # Add follow-up prompt
        outdict['metadata']['f_prompt'] = self.f_prompt

        # Return summary dictionary
        return outdict
    
class TFTraitAccumulator(TabTraitAccumulator, FollowupTraitAccumulator):
    """
    Trait accumulator that does both initial trait tabulation and follow-up questions.
    This is effectively used in desc2matrix_accum_followup.py.
    """

    RUN_MODE_NAME = 'desc2json_accum_tf'