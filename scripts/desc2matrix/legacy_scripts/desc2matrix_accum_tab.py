import argparse
import json
from ollama import Client
import pandas as pd
import copy

from common_scripts import process_descs, default_prompts # Import functions for processing descriptions and the default prompts

def main(sys_prompt, tab_prompt, prompt):
    # Create the parser
    parser = argparse.ArgumentParser(description = 'Extract JSON/dict from description files')

    # Basic I/O arguments
    parser.add_argument('descfile', type = str, help = 'File containing the descriptions produced by dwca2csv.py')
    parser.add_argument('outputfile', type = str, help = 'File to write JSON to')
    parser.add_argument('--desctype', required = True, type = str, help = 'The "type" value used for morphological descriptions in the description file')
    parser.add_argument('--sysprompt', required = False, type = str, help = 'Text file storing the system prompt')
    parser.add_argument('--prompt', required = False, type = str, help = 'Text file storing the prompt')
    parser.add_argument('--tabprompt', required = False, type = str, help = 'Text file storing the prompt to use for tabulating the initial list of characteristics')
    parser.add_argument('--silent', required = False, action = 'store_true', help = 'Suppress output showing job progress')

    # Run configs
    parser.add_argument('--start', required = False, type = int, default = 0, help = 'Order ID of the species to start transcribing from')
    parser.add_argument('--spnum', required = False, type = int, help = 'Number of species to process descriptions of. Default behaviour is to process all species present in the file')
    parser.add_argument('--initspnum', required = False, type = int, default = 3, help = 'Number of species to sample to generate the initial list of characteristics from tabulation')

    # Model properties
    parser.add_argument('--model', required = False, type = str, default = 'llama3', help = 'Name of base LLM to use')
    parser.add_argument('--temperature', required = False, type = float, default = 0.1, help = 'Model temperature between 0 and 1')
    parser.add_argument('--seed', required = False, type = int, default = 1, help = 'Model seed value')
    parser.add_argument('--repeatlastn', required = False, type = int, default = 0, help = 'Number of prompts for the model to look back to prevent repetition')
    parser.add_argument('--numpredict', required = False, type = int, default = 2048, help = 'Maximum number of tokens the model can generate')
    parser.add_argument('--numctx', required = False, type = int, default = 4096, help = 'Size of context window used to generate the token')
    parser.add_argument('--topk', required = False, type = int, help = 'A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative.')
    parser.add_argument('--topp', required = False, type = float, help = 'A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text.')
    # Parse the arguments
    args = parser.parse_args()

    # ===== Prompt setup =====

    # Load prompt files if needed
    if(args.sysprompt != None):
        with open(args.sysprompt, 'r') as fp:
            sys_prompt = fp.read()
    if(args.prompt != None):
        with open(args.prompt, 'r') as fp:
            prompt = fp.read()
    if(args.tabprompt != None):
        with open(args.tabprompt, 'r') as fp:
            tab_prompt = fp.read()

    # ===== Read descfile =====

    # Read descfile
    descdf = pd.read_csv(args.descfile, sep = '\t')

    # Filter morphological descriptions only
    descdf = descdf.loc[descdf['type'] == args.desctype]

    # Slice according to --start and --spnum options
    if(args.spnum != None):
        descdf = descdf[args.start : args.start + args.spnum]
    else:
        descdf = descdf[args.start:]

    # Extract descriptions
    descs = descdf['description'].tolist()

    # ===== Setup Ollama ======

    # Build params
    params = {
        'temperature': args.temperature,
        'seed': args.seed,
        'repeat_last_n': args.repeatlastn,
        'num_predict': args.numpredict,
        'num_ctx': args.numctx,
        'top_k': args.topk,
        'top_p': args.topp
    }

    # Build modelfile
    modelfile = '{}\n{}'.format(
        'FROM {}'.format(args.model),
        '\n'.join(['PARAMETER {} {}'.format(param, value) for param, value in params.items() if value != None])
    )

    # Make connection to client
    client = Client(host = 'http://localhost:11434', timeout = 60 * 5)

    # Create model with the specified params
    client.create(model = 'desc2matrix', modelfile = modelfile)

    # ===== Generate output =====

    # Dictionary to store the final output along with metadata
    outdict = {
        'sys_prompt': sys_prompt,
        'tab_prompt': tab_prompt,
        'prompt': prompt,
        'initspnum': args.initspnum,
        'params': params,
        'mode': 'desc2json_accum_tab',
        'charlist_len_history': [],
        'charlist_history': [],
        'data': []
    }

    # Variable to store extracted characteristic data
    sp_list = []

    # Variable to store the character list history
    charlist_history = []

    # ===== Obtain an initial list of characteristics by tabulation =====

    # Sample a number of species to initially tabulate

    tabdf = descdf.iloc[0:args.initspnum]

    # Extract table of characteristics
    chars_tab = process_descs.get_char_table(sys_prompt, tab_prompt, tabdf['coreid'].tolist(), descs, client, silent = args.silent == True)

    # Terminate the program if parsing has failed
    if(chars_tab['status'] != 'success'):
        raise Exception('Initial tabulation generated bad output with status ' + chars_tab['status'])

    # Extract the initial list of characteristics from the table
    init_char_list = [char['characteristic'] for char in chars_tab['data']]

    # Append the char_list to charlist_history
    charlist_history.append(init_char_list)

    # Loop through each species description
    for rowid, desc in enumerate(descs):
        # Log number of species if not silent
        if(args.silent != True):
            print('Processing {}/{}'.format(rowid + 1, len(descs)))

        # Get the list of characters from the last row
        chars = charlist_history[rowid] # NOT rowid - 1 since there is already one element in the list

        # Generate output with predetermined character list
        char_json = process_descs.desc2charjson(sys_prompt, prompt, desc, client, chars = chars, silent = args.silent == True)

        if(char_json['status'] == 'success'): # If run succeeded
            # Extract character list
            chars = [char['characteristic'] for char in char_json['data']]
        
            # Append only if the new character list is longer or if this is the first entry
            if(len(chars) > len(charlist_history[rowid])):
                charlist_history.append(chars)
            else: # Otherwise copy last entry
                charlist_history.append(copy.deepcopy(charlist_history[rowid]))
        else: # Otherwise
            # Copy the last entry
            charlist_history.append(copy.deepcopy(charlist_history[rowid]))

        # Add entry to sp_list
        sp_list.append({
            'coreid': descdf.iloc[rowid]['coreid'],
            'status': char_json['status'], # Status: one of 'success', 'bad_structure', 'invalid_json'
            'original_description': descdf.iloc[rowid]['description'],
            'char_json': char_json['data'] if char_json['status'] == 'success' else None, # Only use this if parsing succeeded
            'failed_str': char_json['data'] if char_json['status'] != 'success' else None # Only use this if parsing failed
        })
        
        # Store generated outputs
        outdict['data'] = sp_list

        # Store charlist history
        outdict['charlist_history'] = charlist_history

        # Store charlist length history
        outdict['charlist_len_history'] = [len(charlist) for charlist in charlist_history]

        # Write output as JSON
        with open(args.outputfile, 'w') as outfile:
            json.dump(outdict, outfile)

    

if __name__ == '__main__':
    main(default_prompts.global_sys_prompt, default_prompts.global_tablulation_prompt, default_prompts.global_prompt)