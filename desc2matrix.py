import argparse
import json
from ollama import Client
import os
import pandas as pd
import time

# ===== Default prompts =====

global_sys_prompt = """
You are a diligent robot assistant made by a botanist. You have expert knowledge of botanical terminology.
Your goal is to transcribe the given list of botanical characteristics into a valid JSON output.
Your answer must be as complete and accurate as possible.
You must answer in valid JSON, with no other text.
"""

# [DESCRIPTION] in the prompt text is replaced by the plant description.
global_prompt = """
You are given a botanical description of a plant species taken from published floras.
You extract the types of characteristics mentioned in the description and their corresponding values, and transcribe them into JSON.
Your answer should be an array of JSON with name of the characteristic and the corresponding value formatted as follows: {"characteristic":(name of characteristic), "value":(value of characteristic)}.
(name of characteristic) should be substituted with the name of the characteristic, and (value of characteristic) should be substituted with the corresponding value.
The name of every characteristic must be written in lowercase.
Make sure that you surround your final answer with square brackets [ and ] so that it is a valid array.
Do not include any text (e.g. introductory text) other than the valid array of JSON.

Follow the instructions below.

1. Transcribe all the mentioned characteristics relating to the whole plant, such as growth form, reproduction, plant height, and branching.

2. Iterate through every mentioned organs (e.g. leaf and other leaf-like organs, stem, flower, inflorescence, fruit, seed and root) and parts of organs (e.g. stipule, anther, ovary) and transcribe their corresponding characteristics.
You must transcribe the length, width, shape, color, surface texture, surface features, and arrangement of each organ or part of an organ.
Each of these characteristics must be separate. The name of every characteristic relating to an organ or a part of an organ must be formatted as follows: "(name of organ or part of organ) (type of characteristic)", where (name of organ or part of organ) should be substituted with the name of the organ or part of the organ, and (type of characteristic) should be substituted with the specific type of characteristic.

In the final output JSON, try to include all words that appear in the given description, as long as they carry information about the plant species.
Do not make up characteristics that are not mentioned in the description.

Here are some examples of descriptions and their correponding transcription in JSON:

Sentence: "Fruit: ovoid berry, 10-12 mm wide, 13-15 mm long, yellow to yellow-green throughout."
JSON: {"characteristic": "fruit shape", "value": "ovoid"}, {"characteristic": "fruit type", "value": "berry"}, {"characteristic": "fruit width", "value": "10-12 mm"}, {"characteristic": "fruit length", "value": "13-15 mm"}, {"characteristic": "fruit color", "value": "yellow to yellow-green"}

Sentence: "Perennial dioecious herbs 60-100cm tall. Leaves alternate, green and glabrous adaxially and hirsute with white to greyish hair abaxially."
JSON: {"characteristic": "life history", "value": "perennial"}, {"characteristic": "reproduction", "value": "dioecious"}, {"characteristic": "growth form", "value": "herb"}, , {"characteristic": "plant height", "value": "60-100 cm"}, {"characteristic": "leaf arrangement", "value": "alternate"}, {"characteristic": "leaf adaxial colour", "value": "green"}, {"characteristic": "leaf adaxial texture", "value": "glabrous"}, {"characteristic": "leaf abaxial texture", "value": "hirsute"}, {"characteristic": "leaf abaxial hair colour", "value": "white to greyish"}

Here is the description that you should transcribe:

[DESCRIPTION]
"""

# ===== Functions =====

# Check JSON output for structural validity and do some cleanup
def regularise_charjson(chars):
    # Return false if the object is not a list; we expect a list of {'characteristic':'', 'value':''}
    if not isinstance(chars, list):
        return False

    new_dict = []

    # Go through elements
    for char in chars:
        # Return false if the keys are different from what we expect
        if set(char.keys()) != {'characteristic', 'value'}:
            return False
        
        # Skip if value is None
        if char['value'] == None:
            continue
        
        # Convert value to string
        char['value'] = str(char['value'])

        # Append characteristic to new dict
        new_dict.append(char)
    
    # Return the new dict
    return new_dict

# Convert a list of descriptions to a list of JSON
def desc2charjson(sys_prompt, prompt, descs, client, model = 'desc2matrix', silent = False):
    # Pass descriptions to LLM for response
    char_jsons = []

    for i, desc in enumerate(descs):
        start = 0
        if not silent:
            print('desc2json: processing {}/{}... '.format(i+1, len(descs)), end = '', flush = True)
            start = time.time()

        # Generate response while specifying system prompt
        resp = client.generate(model = model,
                                   prompt = prompt.replace('[DESCRIPTION]', desc),
                                   system = sys_prompt)['response']

        # Attempt to parse prompt as JSON
        try:
            resp_json = json.loads(resp.replace("'", '"')) # Replace ' with "
            # Check validity / regularise output
            reg_resp_json = regularise_charjson(resp_json)
            if reg_resp_json != False:
                char_jsons.append({'status': 'success', 'data': reg_resp_json}) # Save parsed JSON with status
            else:
                if not silent:
                    print('ollama output is JSON but is structured badly... ', end = '', flush = True)
                char_jsons.append({'status': 'bad_structure', 'data': str(resp_json)}) # Save string with status
        except json.decoder.JSONDecodeError as decode_err: # If LLM returns bad string
            if not silent:
                print('ollama returned bad JSON string... ', end = '', flush = True)
            char_jsons.append({'status': 'invalid_json', 'data': resp}) # Save string with status
        
        if not silent:
            elapsed_t = time.time() - start
            print(f'done in {elapsed_t:.2f} s!')
    
    # Return characteristics as array of dict
    return char_jsons

# Convert a single description to a JSON
def desc2charjson_single(sys_prompt, prompt, desc, client, model = 'desc2matrix', silent = False):
    # Pass descriptions to LLM for response
    char_json = {}

    start = 0
    if not silent:
        print('desc2json: processing... ', end = '', flush = True)
        start = time.time()

    # Generate response while specifying system prompt
    resp = client.generate(model = model,
                                prompt = prompt.replace('[DESCRIPTION]', desc),
                                system = sys_prompt)['response']

    # Attempt to parse prompt as JSON
    try:
        resp_json = json.loads(resp.replace("'", '"')) # Replace ' with "
        # Check validity / regularise output
        reg_resp_json = regularise_charjson(resp_json)
        if reg_resp_json != False:
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

def main(sys_prompt, prompt):
    # Create the parser
    parser = argparse.ArgumentParser(description = 'Extract JSON/dict from description files')

    # Basic I/O arguments
    parser.add_argument('descfile', type = str, help = 'File containing the descriptions produced by dwca2csv.py')
    parser.add_argument('outputfile', type = str, help = 'File to write JSON to')
    parser.add_argument('--desctype', required = True, type = str, help = 'The "type" value used for morphological descriptions in the description file')
    parser.add_argument('--sysprompt', required = False, type = str, help = 'Text file storing the system prompt')
    parser.add_argument('--prompt', required = False, type = str, help = 'Text file storing the prompt')
    parser.add_argument('--silent', required = False, action = 'store_true', help = 'Suppress output showing job progress')

    # Run configs
    parser.add_argument('--start', required = False, type = int, default = 0, help = 'Order ID of the species to start transcribing from')
    parser.add_argument('--spnum', required = False, type = int, help = 'Number of species to process descriptions of. Default behaviour is to process all species present in the file')
    parser.add_argument('--saveeachsp', required = False, action = 'store_true', help = 'If specified, the script writes outputs to the file after running each species description')

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

    # ===== Read descfile =====

    # Read descfile
    descdf = pd.read_csv(args.descfile, sep = '\t')

    # Filter morphological descriptions only
    descdf = descdf.loc[descdf['type'] == args.desctype]

    # Slice according to --start and --spnum options
    if(args.spnum != None):
        descdf = descdf[args.start : args.start + args.spnum]

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
    client = Client(host = 'http://localhost:11434')

    # Create model with the specified params
    client.create(model = 'desc2matrix', modelfile = modelfile)

    # ===== Generate output =====

    # Dictionary to store the final output along with metadata
    outdict = {
        'sys_prompt': sys_prompt,
        'prompt': prompt,
        'params': params,
        'mode': 'desc2json',
        'data': []
    }

    # If running in 'saveeachsp' mode
    if(args.saveeachsp == True):
        # Variable to store extracted characteristic data
        sp_list = []

        # Loop through each species description
        for rowid, desc in enumerate(descs):
            # Log number of species if not silent
            if(args.silent != True):
                print('Processing {}/{}'.format(rowid + 1, len(descs)))

            # Generate output for one species
            char_json = desc2charjson_single(sys_prompt, prompt, desc, client, silent = args.silent == True)

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

            # Write output as JSON
            with open(args.outputfile, 'w') as outfile:
                json.dump(outdict, outfile)

    # If running in bulk mode (default, save to file after all species have been processed)
    else:
        # Generate output
        char_jsons = desc2charjson(sys_prompt, prompt, descs, client, silent = args.silent == True)

        # Compile data
        sp_list = [{
            'coreid': descdf.iloc[rowid]['coreid'],
            'status': cj['status'], # Status: one of 'success', 'bad_structure', 'invalid_json'
            'original_description': descdf.iloc[rowid]['description'],
            'char_json': cj['data'] if cj['status'] == 'success' else None, # Only use this if parsing succeeded
            'failed_str': cj['data'] if cj['status'] != 'success' else None # Only use this if parsing failed
        } for rowid, cj in enumerate(char_jsons)]

        # Store extracted information
        outdict['data'] = sp_list

        # Write output as JSON
        with open(args.outputfile, 'w') as outfile:
            json.dump(outdict, outfile)

if __name__ == '__main__':
    main(global_sys_prompt, global_prompt)