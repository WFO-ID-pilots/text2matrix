# compare_d2m_desc.py user manual

This document is the up-to-date manual for using `compare_d2m_desc.py`, which processes the JSON output of a `desc2matrix` script to compare the extracted characteristics and their corresponding original descriptions and calculate word coverage summary statistics.

## Input

The input file is a JSON file produced by a `desc2matrix` script, with the following minimal format:

<pre>
{
    ..., # Metadata
    'data': [
        {
            'original_description': (Original species description),
            'status': 'success' | 'invalid_json' | 'bad_structure' | ..., # Parsing status
            'char_json': [{'characteristic': '', 'value': ''}, ...], # Structured JSON output upon successful parsing
            'failed_str': '' # The LLM output string that failed to parse; this script will still use this!
        }, ...
    ]
}
</pre>

## Operation

1. Extract the original species description and the LLM output

2. If the LLM output is a JSON, convert it into a single string

The string will be structured as:
<pre>
Name of characteristic 1: Value
Name of characteristic 2: Value
...
</pre>

3. Do pre-processing on the original and output strings

    1. Insert whitespace around punctuation to prevent multiple words being recognised as a single word due to missing whitespace
    2. Collapse numeric ranges including '-' to be expressed without whitespace so that it is recognised as a single 'word'

4. Tokenise strings

5. Remove punctuations & brackets from tokens

6. Singularise nouns

7. With the final word set, populate the output

See below in **Output** for the metrics that this script returns.

## Arguments

| Argument | Description | Required? | Default value |
| --- | --- | --- | --- |
| `inputfile` (positional argument) | The input JSON file to process | Yes | |
| `outfile` (positional argument) | Path to the output tsv file | Yes | |
| `--verbose` (optional flag) | If true, print the list of words as they species are being processed | No | False |

## Output

The output is a tsv file with the following columns:

| Column | Type | Description |
| --- | --- | --- |
| `coreid` | `str` | WFO taxon ID for the species |
| `status` | `str` | Status code for the species returned by `desc2matrix` script |
| `nwords_original` | `int` | Number of words in the original description text |
| `nwords_result` | `int` | Number of words in the JSON output |
| `nwords_val` | `int` | Number of words in the JSON output, NA if the run didn't suceed |
| `nwords_recovered` | `int` | Number of words in the original text AND the output JSON |
| `nwords_omitted` | `int` | Number of omitted words |
| `nwords_created` | `int` | Number of words in the output that was not in the original text description |
| `nwords_recovered_val` | `int` | Number of words in the original text AND the characteristic values in the output |
| `nwords_created_val` | `int` | Number of words 'created' in the extracted characteristic value; NA if the run did not succeed |
| `common_words` | `list`, comma-separated | List of words shared by the original description and the output JSON |
| `original_only` | `list`, comma-separated | List of words that were only in the original description |
| `result_only` | `list`, comma-separated | List of words that were only in the output JSON |
| `common_words_val` | `list`, comma-separated | List of words that were shared between the original description and the extracted trait values |
| `val_only` | `list`, comma-separated | List of words that were found in the output trait values but not in the original description |
