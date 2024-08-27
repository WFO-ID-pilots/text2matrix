"""
This script converts an SDD-formatted XML file into a list of plant traits.
"""

import argparse
import json
from common_scripts import sdd_functions # Functions for processing SDD-formatted XML string

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description = 'Extract a list of characteristic names from an SDD-formatted XML string')

    # Basic I/O arguments
    parser.add_argument('sddfile', type = str, help = 'SDD XML file from Xper to process')
    parser.add_argument('outfile', type = str, help = 'File to write the character list to')
    parser.add_argument('--sep', type = str, default = '\n', help = 'Separator character for the output file')
    
    # Parse the arguments
    args = parser.parse_args()

    # Read XML file
    xmlstr:str = ''
    with open(args.sddfile, 'r') as fp:
        xmlstr = fp.read()

    # Get coded categorical and quantitative characteristics
    charcodes_cat = sdd_functions.getcharcodes_cat(xmlstr)
    charcodes_quant = sdd_functions.getcharcodes_quant(xmlstr)

    # Extract list of characteristics mentioned in the SDD file
    char_list:list[str] = []
    char_list.extend([
        charinfo['characteristic'] for charid, charinfo in charcodes_cat.items()
    ])
    char_list.extend([
        charinfo['characteristic']for charid, charinfo in charcodes_quant.items()
    ])

    # Sort list of traits
    char_list.sort()

    # Write list to outfile
    with open(args.outfile, 'w') as fp:
        fp.write(args.sep.join(char_list))

if __name__ == '__main__':
    main()