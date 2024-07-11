import argparse
from dwca.read import DwCAReader
from dwca.darwincore.utils import qualname as qn
from dwca.read import DwCAReader
import pandas as pd
import re
        
def dwca2df(dwcafile):
    with DwCAReader(dwcafile) as dwca:
        # We need to map the headers from their long qualified name to a more usable short name
        header_mapper = {header:short_header for header, short_header in zip(dwca.descriptor.core.headers, dwca.descriptor.core.short_headers)}        
        # Add an extra mapping for the coreid
        header_mapper['http://rs.tdwg.org/dwc/terms/taxonID'] = 'coreid'

        # Now we collate the dict format core rows
        rows = []
        # Iterate over all core rows
        for row in dwca.rows:
            row_renamed = {header_mapper.get(key, key): value for key, value in row.data.items()}
            rows.append(row_renamed)

        # Convert our list of dictionaries to a pandas dataframe
        df = pd.DataFrame(rows)

        # Convert unmapped long header names to shorter names by truncating the URL
        unmapped_headers = [h for h in df.columns if '/' in h] # Unmapped header names with '/'
        unmapped_short = [re.sub('^.*\/', '', h) for h in unmapped_headers] # Extract short header names
        df = df.rename(columns = dict(zip(unmapped_headers, unmapped_short)))

        return df

def dwcaext2df(dwcafile, extensiontype="http://rs.gbif.org/terms/1.0/Description"):
    with DwCAReader(dwcafile) as dwca:
        # We need to map the headers from their long qualified name to a more usable short name
        header_mapper = dict()
        for ext in dwca.descriptor.extensions:
            # We're only interested in the specified extension type
            if ext.type == extensiontype:
                header_mapper = {header:short_header for header, short_header in zip(ext.headers, ext.short_headers)}
        # Add an extra mapping for the coreid
        header_mapper['http://rs.tdwg.org/dwc/terms/taxonID'] = 'coreid'

        # Now we collate the dict format rows for the selected extension type
        ext_rows = []
        # Iterate over all core rows
        for row in dwca.rows:
            # Iterate over all the extensions for this core row
            for extension_line in row.extensions:
                if extension_line.rowtype == extensiontype:
                    # We use the header mapper to shorten the key names
                    extension_line_renamed = {header_mapper.get(key, key): value for key, value in extension_line.data.items()}
                    # Add a coreid if its not there already
                    if not 'coreid' in extension_line_renamed.keys():
                        extension_line_renamed['coreid'] = row.id
                    ext_rows.append(extension_line_renamed)

        # Convert our list of dictionaries to a pandas dataframe
        df = pd.DataFrame(ext_rows)


        # Convert unmapped long header names to shorter names by truncating the URL
        unmapped_headers = [h for h in df.columns if '/' in h] # Unmapped header names with '/'
        unmapped_short = [re.sub('^.*\/', '', h) for h in unmapped_headers] # Extract short header names
        df = df.rename(columns = dict(zip(unmapped_headers, unmapped_short)))

        return df

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Explore DWCA format description files')
    
    # Add the arguments
    parser.add_argument('inputfile', type=str, help='DWCA file')
    parser.add_argument('--output_type', required=False, choices={"core", "desc"}, default='core')
    parser.add_argument('outputfile', type=str)
    
    # Parse the arguments
    args = parser.parse_args()

    # DWCA datafile is arranged as a core and a number of optional extensions.
    if args.output_type == 'core':
        df_core = dwca2df(args.inputfile)
        fields = ['coreid'] + [col for col in df_core.columns if col != 'coreid']
        df_core[fields].to_csv(args.outputfile, sep='\t', index=False)
    elif args.output_type == 'desc':
        df_desc = dwcaext2df(args.inputfile)
        fields = ['coreid'] + [col for col in df_desc.columns if col != 'coreid']
        df_desc[fields].to_csv(args.outputfile, sep='\t', index=False)

if __name__ == '__main__':
    main()