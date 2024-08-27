"""
This script can be used to merge two JSON output files from a desc2matrix_wcharlist script.
This is useful for when the script was halted and resumed where it stopped, resulting in two separate files.
NB: This DOES NOT support merging two desc2matrix_accum outputs together.
"""

import argparse
import json

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Merge two desc2matrix_wcharlist_*.py outputs together')

    # Add the arguments
    parser.add_argument('part1', type=str, help='The first part of the JSON file')
    parser.add_argument('part2', type=str, help='The second part of the JSON file')
    parser.add_argument('outfile', type=str, help='Output file to write the merged JSON')

    # Parse the arguments
    args = parser.parse_args()

    # Read the JSON files
    part1_dict:dict = {}
    part2_dict:dict = {}
    with open(args.part1, 'r') as fp:
        part1_dict = json.loads(fp.read())
    with open(args.part2, 'r') as fp:
        part2_dict = json.loads(fp.read())

    # ===== Check uniformity between the two output files =====
    
    # Check if the run modes are wcharlist
    if not (part1_dict['mode'].startswith('desc2json_wcharlist') and part2_dict['mode'].startswith('desc2json_wcharlist')):
        raise Exception('One or more output files are not from desc2matrix_wcharlist')
    
    # Check if the run modes are the same
    if part1_dict['mode'] != part2_dict['mode']:
        raise Exception('The run modes do not match between the two files')
    
    # Check if the prompts are the same
    prompt_names = ['sys_prompt', 'prompt', 'tab_prompt', 'f_prompt', 'init_prompt']
    if False in [part1_dict.get(prompt_name) == part2_dict.get(prompt_name) for prompt_name in prompt_names]:
        raise Exception('One or more prompts do not match between the two files')
    
    # Check if the model parameters are the same
    if False in [part1_dict['params'][param_name] == part2_dict['params'][param_name] for param_name in part1_dict['params']]:
        raise Exception('One or more model parameter values do not match between the two files')
    
    # Check if the charlists used for extraction are the same
    if part1_dict['charlist'] != part2_dict['charlist']:
        raise Exception('The lists of characters for extraction do not match between the two files')

    # ===== Merge the two JSON files =====

    # Extract set of WFO IDs from two files
    part1_ids = {sp['coreid'] for sp in part1_dict['data']}
    part2_ids = {sp['coreid'] for sp in part2_dict['data']}
    
    # Find shared WFO IDs
    shared_ids = part1_ids.intersection(part2_ids)

    # Start with all the entries in part 1
    final_data:list = part1_dict['data']

    # Loop through part 2, appending entries that are not shared between the two parts into the final data
    for sp in part2_dict['data']:
        if sp['coreid'] not in shared_ids: # If the coreid is not in the set of shared ids
            final_data.append(sp)
    
    # Build final output from part 1
    final_dict = part1_dict
    # Replace data in final dict
    final_dict['data'] = final_data

    # Write final dict into the output file
    with open(args.outfile, 'w') as fp:
        json.dump(final_dict, fp)

if __name__ == '__main__':
    main()