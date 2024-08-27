"""
This script converts an SDD-formatted XML file from Xper into a JSON file containing the species and their corresponding characteristics & characteristic values.
"""

import argparse
import json
from common_scripts import sdd_functions # Functions for processing SDD-formatted XML files

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description = 'Convert an SDD XML file from Xper into a JSON format')

    # Basic I/O arguments
    parser.add_argument('sddfile', type = str, help = 'SDD XML file from Xper to process')
    parser.add_argument('outfile', type = str, help = 'File to write the processed JSON into')

    # Parse the arguments
    args = parser.parse_args()

    # Variable for storing the final JSON output as dict
    final_dict:dict = {}

    # Read XML file
    xmlstr:str = ''
    with open(args.sddfile, 'r') as fp:
        xmlstr = fp.read()
    
    # Convert string to chardict
    final_dict = sdd_functions.sddxml2dict(xmlstr)

    with open(args.outfile, 'w') as fp:
        json.dump(final_dict, fp)

if __name__ == '__main__':
    main()