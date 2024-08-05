"""
This python script organises the values for each characteristic that have been recovered by the
desc2matrix_wcharlist_*.py scripts, generating a table of the possible values that each
characteristics can take within the dataset and their frequency of occurrence.
"""

from typing import Dict
import json
import argparse

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description = 'Summarise the characteristics and the corresponding values in a desc2matrix output')

    # Basic I/O arguments
    parser.add_argument('charjsonfile', type = str, help = 'File produced by a desc2matrix script to summarise')
    parser.add_argument('outputfile', type = str, help = 'File to write the resulting summary JSON to')

    # Parse the arguments
    args = parser.parse_args()

    # Variable for storing the entire desc2matrix output JSON
    d2m_output = {}

    # Read file into the variable
    with open(args.charjsonfile, 'r') as fp:
        d2m_output = json.load(fp)

    # Dictionary for storing the characteristics and their corresponding possible values
    # Structure is {'characteristic': {'value 1': frequency, 'value 2': frequency, ...}, ...}
    chars_dict:Dict[str, dict] = {}

    # Iterate through species and add charcteristics to chars_dict as appropriate
    for sp in d2m_output['data']:
        if sp['status'] != 'success': # If the species didn't successfully parse
            continue # Skip species

        for char in sp['char_json']: # Iterate through individual characteristics
            # Characteristic name and value
            char_name = char['characteristic']
            char_val = char['value']
            if char_name in chars_dict: # If the characteristic is already in chars_dict
                chars_dict[char_name][char_val] = 1 if not char_val in chars_dict[char_name] else chars_dict[char_name][char_val] + 1 # Increase frequency counter or set frequency as 1
            else: # If the characteristic doesn't exist
                chars_dict[char_name] = {} # Initialise dict
                chars_dict[char_name][char_val] = 1 # Set frequency to 1

    # 'Sort' dictionary
    chars_dict = {char_name: dict(sorted(chars_dict[char_name].items())) for char_name in chars_dict} # Sort values
    chars_dict = dict(sorted(chars_dict.items())) # Sort characteristic names

    with open(args.outputfile, 'w') as fp:
        json.dump(chars_dict, fp)

if __name__ == '__main__':
    main()