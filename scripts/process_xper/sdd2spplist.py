"""
This script converts an SDD-formatted XML file into a comma-separated list of species
"""

import argparse
from common_scripts import sdd_functions # Functions for processing SDD-formatted XML files

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description = 'Extract the list of species from and SDD-formatted XML file')

    # Basic I/O arguments
    parser.add_argument('sddfile', type = str, help = 'SDD XML file from Xper to process')
    parser.add_argument('outfile', type = str, help = 'File to write the comma-separated list of species into')
    parser.add_argument('--sortspp', required = False, action = 'store_true', help = 'With this flag, the output species list will be sorted alphabetically')

    # Parse the arguments
    args = parser.parse_args()

    # Variable for storing the species list
    spp_list:list[str] = []

    # Read and parse XML file
    xmlstr:str = ''
    with open(args.sddfile, 'r') as fp:
        xmlstr = fp.read()
    
    # Extract species list
    spp_list = sdd_functions.sddxml2spplist(xmlstr)
        
    # Sort species list if needed
    if args.sortspp == True:
        spp_list.sort()
    
    # Save species list
    with open(args.outfile, 'w') as fp:
        fp.write(','.join(spp_list))

if __name__ == '__main__':
    main()