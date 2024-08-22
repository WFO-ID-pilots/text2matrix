from typing import List, Optional
from ollama import Client
import time
import json

from common_scripts import regularise, process_words

def desc2charjson(sys_prompt:str,
                  prompt:str,
                  desc:str,
                  client:Client,
                  chars:Optional[List[str]] = None,
                  model:str = 'desc2matrix',
                  silent:bool = False) -> dict:
    """
    Converts a single species description to a structured dict, given the appropriate prompts and the Ollama client.
    Optionally, 'chars' parameter can be used to specify a list of characteristics to extract.
    The resulting dict is structured as follows:
    {
        'status': 'success' | 'bad_structure' | 'invalid_json',
        'data': [{'characteristic': '', 'value': ''}, ...]
    }

    Parameters:
        sys_prompt (str): The system prompt to use for character extraction.
        prompt (str): The prompt to use for character extraction. '[DESCRIPTION]' in the string is replaced by the species description.
        desc (str): The botanical description of the plant species.
        client (Client): The Ollama Client to use for running the LLM.
        model (str): The name of the LLM to use. Default is 'desc2matrix' which is created by desc2matrix_*.py.
        silent (bool): If this is set to False, the function will output a log showing task completion and elapsed time. Default is False.

    Returns:
        char_json (dict): The output containing the status code (['status'] = 'success' | 'bad_structure' | 'invalid_json') and the extracted characteristics(['data'])
    """

    # Pass descriptions to LLM for response
    char_json = {}

    start = 0
    if not silent:
        print('desc2json: processing... ', end = '', flush = True)
        start = time.time()

    # Generate response while specifying system prompt
    prompt_wcontent = prompt.replace('[DESCRIPTION]', desc)
    if chars != None: # Insert characteristics list if specified
        prompt_wcontent = prompt_wcontent.replace('[CHARACTER_LIST]', '; '.join(chars))
    resp = client.generate(model = model,
                                prompt = prompt_wcontent,
                                system = sys_prompt)['response']

    # Attempt to parse prompt as JSON
    try:
        resp_json = json.loads(resp.replace("'", '"')) # Replace ' with "
        # Check validity / regularise output
        reg_resp_json = regularise.regularise_charjson(resp_json)
        if reg_resp_json != None:
            char_json = {'status': 'success', 'data': reg_resp_json} # Save parsed JSON with status
        else:
            if not silent:
                print('ollama output is JSON but is structured badly... ', end = '', flush = True)
            char_json = {'status': 'bad_structure', 'data': str(resp_json)} # Save string with status
    except json.decoder.JSONDecodeError as decode_err: # If LLM returns bad string
        if not silent:
            print('ollama returned bad JSON string... ', end = '', flush = True)
        char_json = {'status': 'invalid_json', 'data': resp} # Save string with status
    
    if not silent:
        elapsed_t = time.time() - start
        print(f'done in {elapsed_t:.2f} s!')
    
    # Return characteristics as array of dict
    return char_json

def desc2charjson_followup(sys_prompt:str,
                           prompt:str,
                           f_prompt:str,
                           desc:str,
                           client:Client,
                           chars:Optional[List[str]] = None,
                           model = 'desc2matrix',
                           silent = False):
    """
    Converts a single species description to a structured dict, given the appropriate prompts, a list of characteristics to extract, and and the Ollama client.
    This function is different from desc2charjson_wchars in that it asks the LLM a 'follow-up' question including the omitted words to recover more characteristics.
    Optionally, 'chars' parameter may be used to provide a list of characteristics to extract.
    The resulting dict is structured as follows:
    {
        'status': 'success' | 'bad_structure' | 'invalid_json' | 'bad_structure_followup' | 'invalid_json_followup',
        'data': [{'characteristic': '', 'value': ''}, ...]
    }

    Parameters:
        sys_prompt (str): The system prompt to use for character extraction.
        prompt (str): The prompt to use for character extraction. '[DESCRIPTION]' in the string is replaced by the species description.
        desc (str): The botanical description of the plant species.
        client (Client): The Ollama Client to use for running the LLM.
        model (str): The name of the LLM to use. Default is 'desc2matrix' which is created by desc2matrix_*.py.
        silent (bool): If this is set to False, the function will output a log showing task completion and elapsed time. Default is False.

    Returns:
        char_json (dict): The output dict
    """

    # Variable to store the final char_json
    char_json = {}

    # Variable to store the initial raw char_json
    init_raw_char_json = None

    # Generate initial response using desc2charjson_single
    init_raw_char_json = desc2charjson(sys_prompt, prompt, desc, client, chars, model, silent)

    # Skip if JSON output was invalid or badly structured
    if(init_raw_char_json['status'] != 'success'):
        # Simply return without follow-up processing
        return init_raw_char_json

    # Extract the char_json itself
    init_char_json = init_raw_char_json['data']

    start = 0
    # Progress log
    if not silent:
        print('desc2json_followup: processing... ', end = '', flush = True)
        start = time.time()
    
    # Retrieve omissions
    omissions = process_words.get_omissions(desc, init_char_json)

    # Build the follow-up prompt
    followup_prompt = f_prompt.replace('[DESCRIPTION]', desc).replace('[MISSING_WORDS]', '; '.join(sorted(omissions))).replace('[CHARACTER_LIST]', '; '.join(chars))

    # Generate response using the follow-up prompt
    followup_resp = client.chat(model = model, stream = False, messages = [
        {'role': 'system', 'content': sys_prompt}, 
        {'role': 'user', 'content': prompt.replace('[DESCRIPTION]', desc)},
        {'role': 'assistant', 'content': json.dumps(init_char_json, indent=4)},
        {'role': 'user', 'content': followup_prompt}
    ])['message']['content']

    # Attempt to parse prompt as JSON
    try:
        resp_json = json.loads(followup_resp.replace("'", '"')) # Replace ' with "
        # Check validity / regularise output
        reg_resp_json = regularise.regularise_charjson(resp_json)
        if reg_resp_json != False:
            char_json = {'status': 'success', 'data': reg_resp_json} # Save parsed JSON with status
        else:
            if not silent:
                print('ollama output is JSON but is structured badly... ', end = '', flush = True)
            char_json = {'status': 'bad_structure_followup', 'data': str(resp_json)} # Save string with status; 'followup' to distinguish it from failure in the first run
    except json.decoder.JSONDecodeError as decode_err: # If LLM returns bad string
        if not silent:
            print('ollama returned bad JSON string... ', end = '', flush = True)
        char_json = {'status': 'invalid_json_followup', 'data': followup_resp} # Save string with status

    # Progress log
    if not silent:
        elapsed_t = time.time() - start
        print(f'done in {elapsed_t:.2f} s!')

    # Return characteristics as an array of dict
    return char_json

def get_char_table(sys_prompt:str,
                   prompt:str,
                   spids:List[str],
                   descs:List[str],
                   client:Client,
                   model:str = 'desc2matrix',
                   silent:str = False) -> dict:
    """
    Generate a structured 'table' of traits from the given spcies descriptions.
    The output dict is structured as follows:
    {
        'status': 'success' | 'bad_structure' | 'invalid_json',
        'data': [
            {'characteristic': '', 'values': ['spid1': '', 'spid2': '', ...]},
            ...
        ]
    }
    
    Parameters:
        sys_prompt (str): The system prompt to use for character extraction.
        prompt (str): The prompt to use for character extraction. '[DESCRIPTION]' in the string is replaced by the species description and '[CHARACTER_LIST]' is replaced by the provided list of characteristics.
        spids (List[str]): List of identifiers for the plant species. In the scripts, this is the WFO taxon ID.
        descs (List[str]): The botanical descriptions of the plant species.
        client (Client): The Ollama Client to use for running the LLM.
        model (str): The name of the LLM to use. Default is 'desc2matrix' which is created by desc2matrix_*.py.
        silent (bool): If this is set to False, the function will output a log showing task completion and elapsed time. Default is False.
    
    Returns:
        char_json (dict): The output dict
    """
    
    # Variable to store the output JSON 'table'
    tab_json = {}

    # Progress log
    start = 0
    if not silent:
        print('get_table: processing... ', end = '', flush = True)
        start = time.time()

    # Build description string
    desc_str = '\n\n'.join(['Species ID: {}\n\nSpecies description:\n{}'.format(spid, desc) for spid, desc in zip(spids, descs)])

    # Generate response while specifying system prompt
    resp = client.generate(model = model,
                                prompt = prompt.replace('[DESCRIPTIONS]', desc_str),
                                system = sys_prompt)['response']
    
    # Attempt to parse to JSON
    try:
        resp_json = json.loads(resp.replace("'", '"')) # Replace ' with "
        # Check validity / regularise output
        reg_resp_json = regularise.regularise_table(resp_json, spids)
        if reg_resp_json != None:
            tab_json = {'status': 'success', 'data': reg_resp_json} # Save parsed JSON with status
        else:
            if not silent:
                print('ollama output is JSON but is structured badly... ', end = '', flush = True)
            tab_json = {'status': 'bad_structure', 'data': str(resp_json)} # Save string with status
    except json.decoder.JSONDecodeError as decode_err: # If LLM returns bad string
        if not silent:
            print('ollama returned bad JSON string... ', end = '', flush = True)
        tab_json = {'status': 'invalid_json', 'data': resp} # Save string with status

    # Elapsed time log
    if not silent:
        elapsed_t = time.time() - start
        print(f'done in {elapsed_t:.2f} s!')

    # Return table of characteristics
    return tab_json