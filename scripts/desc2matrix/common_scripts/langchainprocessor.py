"""
Script for classes that process plant descriptions using LangChain.
"""

from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
import json
import copy
import time
import ast
import re

# ===== Data schema =====

class PlantCharacteristic(BaseModel):
    """A characteristic of a plant species extracted from a botanical description."""

    characteristic: str = Field(
        default = None, description = "Name of the characteristic written in all lowercase; for example, 'fruit color' or 'plant height'"
    )
    value: str = Field(
        default = None, description = "The corresponding value for the characteristic; for example, '15-30 cm', '2-5', or 'red'"
    )

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class Species(BaseModel):
    """Extracted list of characteristics about the provided plant species."""

    traits: List[PlantCharacteristic]

# ===== Base description processor =====

class LangChainCharProcessor:
    """
    Base LangChainCharProcessor class, which is extended by LCTraitAccumulator and LCTraitExtractor.
    Initialisation of prompts and summary generation are defined here.
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_lc_primitive'

    def __init__(self,
                 base_llm:str,
                 llm_params:dict):
        """
        Initialise trait extractor.

        Parameters:
            base_llm (str): Name of the LLM to use
            llm_params (dict): Dictionary specifying model parameters as seen here: https://api.python.langchain.com/en/latest/chat_models/langchain_groq.chat_models.ChatGroq.html
        """

        # Save the parameters
        self.base_llm:str = base_llm
        self.llm_params:str = llm_params

        # Create & store ChatGroq object
        self.llm:ChatGroq = ChatGroq(
            model = self.base_llm,
            **self.llm_params
        )

        # Variable to store the extracted characteristics data
        self.sp_chars:List[dict] = []

    def desc2charjson(self, desc:str, sys_prompt:str, show_log:bool = False) -> dict:
        """
        Internal function that processes a plant description into a structured dict using the system prompt provided.
        The output is structured as follows:
        {
            'status': (parsing error type returned by LangChain. 'success' if parsing was successful),
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] if parsing_error == None else None
        }

        Parameters:
            desc (str): The species description to parse.
            sys_prompt (str): The system prompt to use.
            show_log (bool): If true, print the run status.

        Returns:
            chardict (dict): The output dictionary.
        """

        # Create prompt template
        prompt_template:ChatPromptTemplate = ChatPromptTemplate.from_messages(
            [
                ('system', sys_prompt),
                MessagesPlaceholder('examples', optional=True),
                ('human', '{description}'),
            ]
        )

        # Create chain
        llm_chain = prompt_template | self.llm.with_structured_output(schema = Species, include_raw = True)

        # Variable for storing output
        chardict = {
            'status': None,
            'data': None
        }

        try: # Check for parsing error
            # Invoke the prompt and get the response
            response = llm_chain.invoke({'description': desc})
        except Exception as err: # If parsing error occurs
            # Print status if show_log is true
            if show_log:
                print('exception thrown! ', end = '', flush = True)
            # Get error string
            err_str:str = err.args[0]
            # Extract dict string from the error string
            err_dict_str = err_str[err_str.find('{') : err_str.rfind('}') + 1]
            # Parse error string
            err_dict = ast.literal_eval(err_dict_str)
            # Set status as error code
            chardict['status'] = err_dict['error']['code'] if 'code' in err_dict['error'] else None
            # Get the output that failed to parse if it exists
            chardict['data'] = err_dict['error']['failed_generation'] if 'failed_generation' in err_dict['error'] else None
        else:
            # Print status if show_log is true
            if show_log:
                print('parse succeeded! ', end = '', flush = True)
            # Set status as success since no exception was thrown at invoke
            chardict['status'] = 'success'
            # Write data in the output dictionary
            chardict['data'] = [
                {
                    'characteristic': trait.characteristic,
                    'value': trait.value
                } for trait in response['parsed'].traits
            ]

        # Return the output dictionary
        return chardict
    
    def get_summary(self) -> dict:
        """
        Function for getting the summary of the LLM run outputs.
        The output dictionary is structured as follows:
        {
            'metadata': {
                'model_name': model name,
                'params': model parameters,
                'mode': run mode name
            },
            'data': sp_chars data
        }
        
        Parameters:
            None
        
        Returns:
            summdict (dict): Dictionary summary of the run
        """

        # Dictionary to store the final output along with metadata
        summdict = copy.deepcopy({
            'metadata': {
                'model_name': self.base_llm,
                'params': self.llm_params,
                'mode': self.RUN_MODE_NAME
            },
            'data': self.sp_chars
        })

        # Return summary dictionary
        return summdict

# ===== Trait accumulator =====

class LCTraitAccumulator(LangChainCharProcessor):
    """
    Class used for trait accumulation.
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_accum_lc'

    def __init__(self,
                 init_prompt:str,
                 accum_prompt:str,
                 base_llm:str,
                 llm_params:dict):
        """
        Initialise trait accumulator.

        Parameters:
            init_prompt (str): The system prompt to use for generating the initial list of traits
            accum_prompt (str): The system prompt to use for subsequent trait accumulation
            base_llm (str): Name of the base LLM to use
            llm_params (dict): Dictionary specifying model parameters as seen here: https://api.python.langchain.com/en/latest/chat_models/langchain_groq.chat_models.ChatGroq.html
        """

        # Run super initialiser
        super().__init__(base_llm, llm_params)

        # Store prompts
        self.init_prompt = init_prompt
        self.accum_prompt = accum_prompt
        
        # Variable to store the characteristic list history
        self.charlist_history:List[List[str]] = []

    def extract_init_chars(self, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for extracting the initial list of characteristics from a single species description.
        The initial list of characteristics is stored in the object if store_results is true.
        The resulting char_json from the processed description is returned, which is formatted as follows:
        {
            'status': (parsing error type returned by LangChain. 'success' if parsing was successful),
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] if parsing_error == None else None
        }
        
        Parameters:
            desc (str): The description to extract the initial characteristics from
            show_log (bool): If this is set to True, show progress logs. Default is False
        
        Returns:
            char_json (dict): The resulting char_json from the processed description
        """

        # Status log
        start = 0
        if show_log:
            print('initial trait list generation: processing... ', end = '', flush = True)
            start = time.time()

        # Generate LLM output
        char_json = self.desc2charjson(desc, self.init_prompt, show_log)

        # If we need to store the resulting list of characteristics
        if store_results:
            # Extract list of characteristics (empty list if the run didn't succeed)
            init_charlist = ([char['characteristic'] for char in char_json['data']]
                            if char_json['status'] == 'success' else [])

            # Store list of characteristics
            self.charlist_history = [init_charlist]

        # Status log
        if show_log:
            elapsed_t = time.time() - start
            print(f'done in {elapsed_t:.2f} s!')
        
        # Return extracted initial list of characteristics
        return char_json

    def accum_step(self, spid:str, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for a step in the accumulation process, where the traits are extracted from an
        additional species and the list of characteristics is updated if
        the new list of characteristics is longer than the most recent list.
        This function returns the char_json from the processed description, which is formatted as follows:
        {
            'status': (parsing error type returned by LangChain. 'success' if parsing was successful),
            'data': [
                {'characteristic': (characteristic), 'value': (value)},
                (...)
            ] if parsing_error == None else None
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
        accum_prompt_wcharlist = self.accum_prompt.replace('[CHARACTER_LIST]', '; '.join(last_charlist)) # Insert characteristics
        
        # Generate char_json output
        char_json = self.desc2charjson(desc, accum_prompt_wcharlist, show_log)

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
                'status': char_json['status'],
                'original_description': desc,
                'char_json': char_json['data'] if char_json['status'] == 'success' else None,
                'failed_str': char_json['data'] if char_json['status'] != 'success' else None
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
                'model_name': model name,
                'params': model parameters,
                'mode': run mode name,
                'init_prompt': initial trait extraction prompt,
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

# ===== Trait extractor =====

class LCTraitExtractor(LangChainCharProcessor):
    """
    Class used for trait extraction given a list of characteristics.
    """

    # Run mode name in the summary output
    RUN_MODE_NAME = 'desc2json_wcharlist_lc'

    def __init__(self,
                 ext_prompt:str,
                 ext_chars:List[str],
                 base_llm:str,
                 llm_params:dict):
        """
        Initialise trait extractor.

        Parameters:
            ext_prompt (str): The system prompt to use for trait extraction given a list of characteristics.
            ext_chars (List[str]): The list of characteristics to extract from the descriptions
            base_llm (str): Name of the base LLM to use
            llm_params (dict): Dictionary specifying model parameters as seen here: https://api.python.langchain.com/en/latest/chat_models/langchain_groq.chat_models.ChatGroq.html
        """

        # Run super initialiser
        super().__init__(base_llm, llm_params)

        # Store parameters
        self.ext_prompt = ext_prompt
        self.ext_chars = ext_chars
    
    def ext_step(self, spid:str, desc:str, show_log:bool = False, store_results:bool = True) -> dict:
        """
        Function for a step in the extraction process, where the traits are extracted from an
        additional species. The traits are stored if store_results is True.
        This function returns the charjson produced by the given description structured as follows:
        {
            'status': (parsing error type returned by LangChain. 'success' if parsing was successful),
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
        prompt_wcontent = self.ext_prompt.replace('[CHARACTER_LIST]', '; '.join(self.ext_chars)) # Insert characteristics
        
        # Generate output
        char_json = self.desc2charjson(desc, prompt_wcontent, show_log)

        # If we need to store the outputs
        if store_results:
            # Update sp_chars
            self.sp_chars.append({
                'coreid': spid,
                'status': char_json['status'], # Status: one of 'success', 'bad_structure', 'invalid_json'
                'original_description': desc,
                'char_json': char_json['data'] if char_json['status'] == 'success' else None,
                'failed_str': char_json['data'] if char_json['status'] != 'success' else None
            })
        
        # Status log
        if show_log:
            elapsed_t = time.time() - start
            print(f'done in {elapsed_t:.2f} s!')

        # Return char_json
        return char_json

    def get_summary(self) -> dict:
        """
        Function for getting the summary of the extraction run.
        The output dictionary is structured as follows:
        {
            'metadata': {
                'model_name': model name,
                'params': model parameters,
                'mode': run mode name,
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