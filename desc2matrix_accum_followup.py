import argparse
import json
from ollama import Client
import pandas as pd
import copy
import process_descs # Functions for converting species descriptions into standardised output

# ===== Default prompts =====

global_sys_prompt = """
You are a diligent robot assistant made by a botanist. You have expert knowledge of botanical terminology.
Your goal is to transcribe the given botanical description(s) of plant characteristics into a valid JSON output.
Your answer must be as complete and accurate as possible.
You must answer in valid JSON, with no other text.
"""

# [DESCRIPTION] in the prompt text is replaced by the plant description.
# [CHARACTER_LIST] in the prompt text is replaced by the list of characteristics to extract.
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

Include the following list of characteristics in your output. Use the name of the characteristic as given in this list. If you can't find one or more of these characteristics in the given description, put "NA" as the corresponding value. If you find a characteristic in the given description that is not in this list, add that characteristic in your response.

[CHARACTER_LIST]

Here is the description that you should transcribe:

[DESCRIPTION]
"""

# [DESCRIPTIONS] in the prompt text is replaced by a structured list of plant descriptions.
global_tablulation_prompt = """
You are given a botanical description of a few plant species taken from published floras.
You extract the types of characteristics mentioned in the descriptions and their corresponding values, and transcribe them into JSON.
Your answer should be an array of JSON with name of the characteristic, ID of species, and the corresponding values formatted as follows: {"characteristic":(name of characteristic), "values":{(ID of species 1): (value of characteristic for species 1), (ID of species 2): (value of characteristic for species 2), ...}.
(name of characteristic) should be substituted with the name of the characteristic.
(ID of species n) should be substituted with the ID of the nth species.
(value of characteristic for species n) should be substituted with the corresponding characteristic value for the nth species.
The name of every characteristic must be written in lowercase.
Make sure that you surround your final answer with square brackets [ and ] so that it is a valid array.
Do not include any text (e.g. introductory text) other than the valid array of JSON.

Follow the instructions below.

1. Transcribe all the mentioned characteristics relating to the whole plant, such as growth form, reproduction, plant height, and branching.

2. Iterate through every mentioned organs (e.g. leaf and other leaf-like organs, stem, flower, inflorescence, fruit, seed and root) and parts of organs (e.g. stipule, anther, ovary) and transcribe their corresponding characteristics.
You must transcribe the length, width, shape, color, surface texture, surface features, and arrangement of each organ or part of an organ.
Each of these characteristics must be separate. The name of every characteristic relating to an organ or a part of an organ must be formatted as follows: "(name of organ or part of organ) (type of characteristic)", where (name of organ or part of organ) should be substituted with the name of the organ or part of the organ, and (type of characteristic) should be substituted with the specific type of characteristic.

3. If a characteristic is mentioned for one species (e.g. species ID A) but not for another species (e.g. species ID B) you should put "NA" as the corresponding value for species ID B. 

In the final output JSON, try to include all words that appear in the given descriptions, as long as they carry information about the plant species.
Do not make up characteristics that are not mentioned in the descriptions.

Here is an example of how you might transcribe species descriptions:

Description of species ID A: Perennial herb 10-30 cm tall. Fruits ovate, tomentose, yellow when ripe. Leaves alternate, glabrous, deep green.
Description of species ID B: Shrub 1-1.5 m tall. Friuts obovate, red when ripe. Leaves lanceolate, opposite, yellow-green.
Description of species ID C: Annual herb 10-12 cm tall. Fruits flattened, glabrous. Leaves alternate, with serrate margin, mid-green.
JSON output:
[
    {"characteristic": "life history", "values": {"A": "perennial", "B": "perennial", "C": "annual"}},
    {"characteristic": "growth form", "values": {"A": "herb", "B": "shrub", "C": "herb"}},
    {"characteristic": "plant height", "values": {"A": "10-30 cm", "B": "1-1.5 m", "C": "10-12 cm"}},
    {"characteristic": "fruit shape", "values": {"A": "ovate", "B": "obovate", "C": "flattened"}},
    {"characteristic": "fruit color", "values": {"A": "yellow when ripe", "B": "red when ripe", "C": "NA"}},
    {"characteristic": "fruit surface texture", "values": {"A": "tomentose", "B": "NA", "C": "glabrous"}},
    {"characteristic": "leaf arrangement", "values": {"A": "alternate", "B": "opposite", "C": "alternate"}},
    {"characteristic": "leaf surface texture", "values": {"A": "glabrous", "B": "NA", "C": "NA"}},
    {"characteristic": "leaf margin shape", "values": {"A": "NA", "B": "NA", "C": "serrate"}},
    {"characteristic": "leaf shape", "values": {"A": "NA", "B": "lanceolate", "C": "NA"}},
    {"characteristic": "leaf color", "values": {"A": "deep green", "B": "yellow-green", "C": "mid-green"}},
]

Here are the descriptions that you should transcribe:

[DESCRIPTIONS]
"""

# [DESCRIPTION] and [MISSING_WORDS] are each replaced by the plant description and the list of missing words.
global_followup_prompt = """
Please generate a new, more complete JSON response in the same format as before.

Here are the words in the original description that you've omitted in your JSON response:
[MISSING_WORDS]

Some of these are broken parts of words that you have included in your final response. For example, the list might have the word 'seudostipule' when you have 'pseudostipule' in your JSON. Ignore such cases.
Of the words in the above list, try to include all words that contain information about a plant trait that you have genuinely omitted.

Do not include any text (e.g. introductory text) other than the valid array of JSON.

Here is the original description that you should transcribe:
[DESCRIPTION]
"""

def main(sys_prompt, tab_prompt, prompt, f_prompt):
    # Create the parser
    parser = argparse.ArgumentParser(description = 'Extract JSON/dict from description files')

    # Basic I/O arguments
    parser.add_argument('descfile', type = str, help = 'File containing the descriptions produced by dwca2csv.py')
    parser.add_argument('outputfile', type = str, help = 'File to write JSON to')
    parser.add_argument('--desctype', required = True, type = str, help = 'The "type" value used for morphological descriptions in the description file')
    parser.add_argument('--sysprompt', required = False, type = str, help = 'Text file storing the system prompt')
    parser.add_argument('--prompt', required = False, type = str, help = 'Text file storing the prompt')
    parser.add_argument('--tabprompt', required = False, type = str, help = 'Text file storing the prompt to use for tabulating the initial list of characteristics')
    parser.add_argument('--fprompt', required = False, type = str, help = 'Text file storing the follow-up prompt')
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
    parser.add_argument('--numctx', required = False, type = int, default = 16384, help = 'Size of context window used to generate the token')
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
    if(args.fprompt != None):
        with open(args.fprompt, 'r') as fp:
            f_prompt = fp.read()

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
    client = Client(host = 'http://localhost:11434', timeout = 60 * 5)

    # Create model with the specified params
    client.create(model = 'desc2matrix', modelfile = modelfile)

    # ===== Generate output =====

    # Dictionary to store the final output along with metadata
    outdict = {
        'sys_prompt': sys_prompt,
        'tab_prompt': tab_prompt,
        'prompt': prompt,
        'f_prompt': f_prompt,
        'initspnum': args.initspnum,
        'params': params,
        'mode': 'desc2json_accum_followup',
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
        char_json = process_descs.desc2charjson_followup(sys_prompt, prompt, f_prompt, desc, client, chars = chars, silent = args.silent == True)

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
            'status': char_json['status'], # Status: one of 'success', 'bad_structure', 'bad_structure_followup', 'invalid_json', 'invalid_json_followup'
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
    main(global_sys_prompt, global_tablulation_prompt, global_prompt, global_followup_prompt)