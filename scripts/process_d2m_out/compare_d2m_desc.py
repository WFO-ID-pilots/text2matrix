import argparse
import json
import pandas as pd

from common_scripts import desc_nlp

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Get word coverage data from desc2matrix.py output file')

    # Add the arguments
    parser.add_argument('inputfile', type=str, help='JSON output file from desc2matrix.py')
    parser.add_argument('outfile', type=str, help='File to write the tsv output to')
    parser.add_argument('--verbose', action='store_true', help='Script will print the list of words if this option is on')

    # Parse the arguments
    args = parser.parse_args()

    # Read output from desc2matrix.py
    with open(args.inputfile, 'r') as fp:
        raw_output = json.loads(fp.read())
    
    # Extract only the data without the metadata
    desc_output = raw_output['data']

    # Extract original descriptions and their JSON counterparts OR LLM output that failed to parse
    descs = [desc['original_description'] for desc in desc_output]
    descs_formatted = ['\n'.join(['{}: {}'.format(char['characteristic'], char['value']) for char in desc['char_json']]) if desc['status'] == 'success' # Convert JSON into a single string
                       else (desc['failed_str'] if 'failed_str' in desc else '') # failed_str may not exist; put empty string if this is the case
                       for desc in desc_output]

    # Get word sets
    descsets = [desc_nlp.get_word_set(desc) for desc in descs]
    descsets_f = [desc_nlp.get_word_set(desc_f) for desc_f in descs_formatted]

    # Dataframe to store the results
    df = pd.DataFrame(columns = [
        'coreid', # WFO taxon ID
        'status', # Status of LLM transcription to JSON: "success", "bad_structure", or "invalid_json"
        'nwords_original', # Number of words in the original text
        'nwords_result', # Number of words in the result
        'nwords_recovered', # Number of words in the original text AND the result
        'nwords_omitted', # Number of words in the original text not in the result
        'nwords_created', # Number of words in the result not in the original text
        'prop_recovered', # Proportion of words in the original text recovered
        'common_words', # Comma-separated list of words that the original and output text share
        'original_only', # Comma-separated list of words only found in the original text
        'result_only' # Comma-separated list of words only found in the output text
    ])

    # Go through each description
    for i, descset, descset_f, desc_dat in zip(list(range(0, len(descsets))), descsets, descsets_f, desc_output):
        # Calculate word match proportions
        common_words = sorted(descset.intersection(descset_f))
        original_only = sorted(descset.difference(descset_f))
        result_only = sorted(descset_f.difference(descset))
        nwords_recovered = len(common_words)
        nwords_omitted = len(original_only)
        nwords_created = len(result_only)
        nwords_original = len(descset)
        nwords_result = len(descset_f)
        prop_recovered = round(nwords_recovered / len(descset), 3)

        # Store data in dataframe
        df.loc[i] = [
            desc_dat['coreid'],
            desc_dat['status'],
            nwords_original,
            nwords_result,
            nwords_recovered,
            nwords_omitted,
            nwords_created,
            prop_recovered,
            ','.join(common_words),
            ','.join(original_only),
            ','.join(result_only)
        ]

        # Print output if --verbose
        if(args.verbose):
            print('Common words:\n{}\n'.format(', '.join(common_words)))
            print('Words only in the original description:\n{}\n'.format(', '.join(original_only)))
            print('Words only in the script output:\n{}\n'.format(', '.join(result_only)))
    
    # Write df to tsv
    df.to_csv(args.outfile, sep = '\t')


if __name__ == '__main__':
    main()