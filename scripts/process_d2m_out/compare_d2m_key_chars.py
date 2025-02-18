"""
Script for comparing the model outputs and the actual characteristic values in an SDD-formatted key extracted by sdd2json.py.

The desc2matrix.py output is expected to have the following structure:
{
    (...),
    'data': [
        {
            'coreid': WFO coreid,
            'status': 'success' | '...',
            'original_description': Original plant description,
            'char_json': [
                {
                    'characteristic': Name of characteristic,
                    'value': Corresponding value
                }, (...)
            ] if status == 'success' else None,
            'failed_str': String that failed to parse if status != 'success' else None
        }
    ]
}

The sdd2json.py output is expected to have the following structure:
{
    Species binomial: [
        {
            'characteristic': Name of characteristic,
            'value': Corresponding value
        }, (...)
    ]
}
"""

import argparse
import pandas as pd
import json

from common_scripts import process_spnames, desc_nlp

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Compare desc2matrix output against characteristic values from an SDD-formatted taxon key')

    # Add the arguments
    parser.add_argument('charjson', type=str, help='JSON output file from desc2matrix.py')
    parser.add_argument('originalchars', type=str, help='JSON output from sdd2json.py')
    parser.add_argument('taxafile', type=str, help='Taxa tsv generated by dwca2csv.py')
    parser.add_argument('outfile', type=str, help='File to write the tsv output to')
    parser.add_argument('--silent', default=False, action='store_true', help='If true, suppress progress log')

    # Parse the arguments
    args = parser.parse_args()

    # ===== Read files specified by parameter =====

    # desc2matrix output dictionary
    d2m_output:dict = {}
    with open(args.charjson, 'r') as fp:
        d2m_output = json.loads(fp.read())
    # sdd2json output dictionary
    keysp_chars:dict = {}
    with open(args.originalchars, 'r') as fp:
        keysp_chars = json.loads(fp.read())
    # Taxa tsv file
    taxa_df:pd.DataFrame = pd.read_csv(args.taxafile, sep='\t')

    # ===== Map species in the d2m output to those in the key =====
    
    # Set the coreid as the index in taxa_df
    taxa_df = taxa_df.set_index('coreid')

    # Get the list of coreids of the species included within charjson
    d2m_coreids = [
        sp['coreid'] for sp in d2m_output['data']
    ]

    # Get the corresponding list of species names from the taxa file
    d2m_spnames = taxa_df.loc[d2m_coreids, 'scientificName'].tolist()
    
    # Get the list of species included within the key
    key_spnames = list(keysp_chars.keys())

    # Map the list of species in the desc2matrix output to those in the key
    # 'target_in_origin' means that we consider there to be a match if the species in the key output is, or is a subtaxon of, the species in the d2m output.
    d2m_key_map = process_spnames.map_spnames(d2m_spnames, key_spnames, 'target_in_origin')

    # ===== Calculate comparison metrics =====

    # Dataframe to store the results
    df = pd.DataFrame(columns = [
        'coreid', # WFO taxon ID
        'status', # Status of LLM transcription to JSON in the desc2matrix output
        'nchars_d2m', # Number of characteristics with 'non-nully' values in the d2m output
        'nchars_key', # Number of characteristics with non-null values in the key
        'nchars_common', # Number of characteristic names that are exactly the same between the d2m output and the key
        'nwords_d2m_only', # Number of non-stop words in the d2m output only
        'nwords_key_only', # Number of non-stop words in the key description only
        'nwords_common', # Number of non-stop words that are shared between the d2m output and the structured description in the key
        'words_d2m_only', # Comma-separated list of non-stop words that are only in the d2m output
        'words_key_only', # Comma-separated list of non-stop words that are only in the structured key
        'words_common', # Comma-separated list of non-stop words that the d2m output and the key output share
        'nwords_d2m_only_vals', # With characteristic values only
        'nwords_key_only_vals', # With characteristic values only
        'nwords_common_vals', # Same as nwords_common, but with characteristic values only
        'words_d2m_only_vals', # With characteristic values only
        'words_key_only_vals', # With characteristic values only
        'words_common_vals' # With characteristic values only
    ])

    # Iterate through the species in the d2m output
    for i, d2m_sp in enumerate(d2m_output['data']):
        # Print log if not silent
        if not args.silent:
            print('Processing species {} / {}... '.format(i+1, len(d2m_output['data'])), end='', flush=True)

        # Get characteristics and values from the mapped key species
        key_sp_chars = keysp_chars[key_spnames[d2m_key_map[i]]]
        # Get characteristic names WITH NON-NULL VALUES from the key species
        key_charnames = [ key_sp_char['characteristic'] for key_sp_char in key_sp_chars if key_sp_char['value'] != None ]

        # Dict representing row to insert into df
        df_row = {
            colname: '' for colname in df.columns.values
        }

        # Put coreid & status
        df_row.update({
            'coreid': d2m_sp['coreid'],
            'status': d2m_sp['status']
        })

        # ===== Retrieve and compare list of characteristic names =====

        # If the run didn't successfully parse, put in NAs for the nchars_* columns except for nchars_key
        if d2m_sp['status'] != 'success':
            df_row.update({
                'nchars_d2m': 'NA',
                'nchars_key': len(key_charnames),
                'nchars_common': 'NA'
            })
        else: # Otherwise,
            # Get characteristics and values from the d2m output
            d2m_sp_chars = d2m_sp['char_json']

            # Get characteristic names WITH NON-NULLY VALUES from d2m output
            d2m_charnames = [
                d2m_sp_char['characteristic'] for d2m_sp_char in d2m_sp_chars
                if d2m_sp_char['value'] not in ['NA', None, 'null']
            ]

            # ===== Calculate sets of shared characteristics =====

            # Characteristics that are strictly shared
            chars_common = set(key_charnames).intersection(set(d2m_charnames))

            # Put values into row
            df_row.update({
                'nchars_d2m': len(d2m_charnames),
                'nchars_key': len(key_charnames),
                'nchars_common': len(chars_common)
            })

        # ===== Generate strings from the d2m output and structured description from key =====

        # Convert d2m output into a single string
        d2m_str = ('\n'.join(['{}: {}'.format(char['characteristic'], char['value']) for char in d2m_sp['char_json']])
                    if d2m_sp['status'] == 'success' # Convert JSON into a single string if run succeeded
                    else (d2m_sp['failed_str'] if 'failed_str' in d2m_sp else '')) # Otherwise use failed_str, although failed_str may not exist; put empty string if this is the case

        # Convert structured description in key into a single string
        key_str = '\n'.join(['{}: {}'.format(char['characteristic'], char['value']) for char in key_sp_chars])

        # Get word sets from strings
        d2m_wset = desc_nlp.get_word_set(d2m_str)
        key_wset = desc_nlp.get_word_set(key_str)
        
        # Calculate intersections and differences
        w_common = d2m_wset & key_wset
        w_d2m_only = d2m_wset - key_wset
        w_key_only = key_wset - d2m_wset

        # Calculate word count metrics & put into row
        df_row.update({
            'nwords_common': len(w_common),
            'nwords_d2m_only': len(w_d2m_only),
            'nwords_key_only': len(w_key_only),
            'words_common': ','.join(sorted(w_common)),
            'words_d2m_only': ','.join(sorted(w_d2m_only)),
            'words_key_only': ','.join(sorted(w_key_only))
        })

        # ===== Do the same but with values only =====

        # Convert d2m output into a single string
        d2m_str_val = ('\n'.join([char['value'] for char in d2m_sp['char_json']])
                    if d2m_sp['status'] == 'success' # Convert JSON into a single string if run succeeded
                    else (d2m_sp['failed_str'] if 'failed_str' in d2m_sp else '')) # Otherwise use failed_str, although failed_str may not exist; put empty string if this is the case
        
        # Convert structured description in key into a single string
        key_str_val = '\n'.join(['{}: {}'.format(char['characteristic'], char['value']) for char in key_sp_chars])

        # Get word sets from strings
        d2m_wset_val = desc_nlp.get_word_set(d2m_str_val)
        key_wset_val = desc_nlp.get_word_set(key_str_val)
        
        # Calculate intersections and differences
        w_common_val = d2m_wset_val & key_wset_val
        w_d2m_only_val = d2m_wset_val - key_wset_val
        w_key_only_val = key_wset_val - d2m_wset_val

        # Calculate word count metrics & put into row
        df_row.update({
            'nwords_common_vals': len(w_common_val),
            'nwords_d2m_only_vals': len(w_d2m_only_val),
            'nwords_key_only_vals': len(w_key_only_val),
            'words_common_vals': ','.join(sorted(w_common_val)),
            'words_d2m_only_vals': ','.join(sorted(w_d2m_only_val)),
            'words_key_only_vals': ','.join(sorted(w_key_only_val))
        })

        # ===== Insert row into df =====
        
        # Convert row to df
        df_row_conv = pd.DataFrame([df_row])
        df = pd.concat([df, df_row_conv], ignore_index=True)

        # ===== Print log if not silent =====
        if not args.silent:
            print('done!')

    # Write df to tsv
    df.to_csv(args.outfile, sep = '\t')

if __name__ == '__main__':
    main()