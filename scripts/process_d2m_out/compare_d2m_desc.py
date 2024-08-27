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
    parser.add_argument('--silent', default=False, action='store_true', help='Script will show progress logs if this option is on')

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
    # Extract and format extracted values only without names of characteristics
    descs_val = ['\n'.join(['{}'.format(char['value']) for char in desc['char_json']]) if desc['status'] == 'success' # Convert JSON into a single string
                       else None # Put None if run failed since we can't distinguish between characteristic names and values
                       for desc in desc_output]

    # Get word sets
    descsets = [desc_nlp.get_word_set(desc) for desc in descs]
    descsets_f = [desc_nlp.get_word_set(desc_f) for desc_f in descs_formatted]
    descsets_val = [desc_nlp.get_word_set(desc_val) if desc_val != None else None for desc_val in descs_val]

    # Dataframe to store the results
    df = pd.DataFrame(columns = [
        'coreid', # WFO taxon ID
        'status', # Status of LLM transcription to JSON: "success", "bad_structure", or "invalid_json"
        'nwords_original', # Number of words in the original text
        'nwords_result', # Number of words in the output
        'nwords_val', # Number of words in the characteristic values in the output; NA if the run did not succeed
        'nwords_recovered', # Number of words in the original text AND the result
        'nwords_omitted', # Number of words in the original text not in the result
        'nwords_created', # Number of words in the result not in the original text
        'nwords_recovered_val', # Number of words in the original text AND the characteristic values in the output
        'nwords_created_val', # Number of words 'created' in the extracted characteristic value; NA if the run did not succeed
        'common_words', # Comma-separated list of words that the original and output text share
        'original_only', # Comma-separated list of words only found in the original text
        'result_only', # Comma-separated list of words only found in the output text
        'common_words_val', # Comma-separated list of words shared between the original description and the output trait values
        'val_only' # Comma-separated list of words found in the output trait values but not in the original description
    ])

    # Go through each description
    for i, descset, descset_f, descset_val, desc_dat in zip(list(range(0, len(descsets))), descsets, descsets_f, descsets_val, desc_output):
        # Print log if not silent
        if not args.silent:
            print('Processing species {} / {}... '.format(i+1, len(descsets)), end='', flush=True)

        # Determine word lists
        common_words = sorted(descset & descset_f)
        original_only = sorted(descset - descset_f)
        result_only = sorted(descset_f - descset)
        common_words_val = sorted(descset & descset_val) if descset_val != None else None
        val_only = sorted(descset_val - descset) if descset_val != None else None

        df_row = {
            'coreid': desc_dat['coreid'],
            'status': desc_dat['status'],
			'nwords_original': len(descset),
			'nwords_result': len(descset_f),
            'nwords_val': len(descset_val) if descset_val != None else 'NA',
            'nwords_recovered': len(common_words),
			'nwords_omitted': len(original_only),
			'nwords_created': len(result_only),
            'nwords_recovered_val': len(common_words_val) if common_words_val != None else 'NA',
            'nwords_created_val': len(val_only) if val_only != None else 'NA',
            'common_words': ','.join(common_words),
			'original_only': ','.join(original_only),
			'result_only': ','.join(result_only),
            'common_words_val': ','.join(common_words_val) if common_words_val != None else 'NA',
            'val_only': ','.join(val_only) if val_only != None else 'NA'
        }

        df_row_conv = pd.DataFrame([df_row])
        df = pd.concat([df, df_row_conv], ignore_index=True)

        # ===== Print log if not silent =====
        if not args.silent:
            print('done!')
    
    # Write df to tsv
    df.to_csv(args.outfile, sep = '\t')


if __name__ == '__main__':
    main()