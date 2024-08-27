import xmltodict
from typing import Optional
import re

def getcharcodes_cat(sddxml:str, rm_keywords:list[str] = ['clade', 'distribution']) -> dict:
    """
    Extract the categorical character codes from the SDD-formatted XML file.
    The output dict is structured as follows:

    {
        'ID of categorical characteristic': {
            'type': 'categorical',
            'characteristic': (name of characteristic),
            'values': {
                'State ID of a possible value': (possible value),
                (...)
            }
        }, (...)
    }

    Parameters:
        sddxml (str): Raw XML string
        rm_keywords (list[str]): List of keywords to use for removing certain characteristics
    
    Returns:
        cat_char_codes (dict): Output dictionary
    """

    # Parse the raw XML
    sdd_dict:dict = xmltodict.parse(sddxml)

    sdd_dataset:dict = sdd_dict['Datasets']['Dataset'] # Extract the dataset only
    characters:dict = sdd_dataset['Characters'] # Get labelled characteristics

    # ===== Retrieve characteristics, values, and corresponding codes =====

    # Dict for storing characteristic codes
    cat_char_codes:dict = {}

    # Retrieve categorical characteristics
    for cat_char in characters['CategoricalCharacter']: # For each categorical characteristic
        # Characteristic name
        char_name = cat_char['Representation']['Label'].lower().strip()
        # If at least one of the rm_keywords is in the characteristic name
        if True in [rm_keyword in char_name for rm_keyword in rm_keywords]:
            continue # Skip over

        # Add an entry in the dictionary
        cat_char_codes[cat_char['@id']] = {
            'type': 'categorical', # Type of characteristic
            'characteristic': char_name, # Name of characteristic in lowercase
            'values': { # Possible values in key-value pairs
                statedef['@id']: statedef['Representation']['Label'].lower().strip() # Convert to lowercase
                for statedef in cat_char['States']['StateDefinition']
            }
        }
    
    # Return output dictionary
    return cat_char_codes

def getcharcodes_quant(sddxml:str) -> dict:
    """
    Extract the quantitative character codes from the SDD-formatted XML file.
    The output dict is structured as follows:

    {
        'ID of quantitative characteristic': {
            'type': 'quantitative',
            'characteristic': (name of characteristic),
            'units': (units for the quantitative value)
        }, (...)
    }

    Parameters:
        sddxml (str): Raw XML string
    
    Returns:
        cat_char_codes (dict): Output dictionary
    """

    # Parse the raw XML
    sdd_dict:dict = xmltodict.parse(sddxml)

    sdd_dataset:dict = sdd_dict['Datasets']['Dataset'] # Extract the dataset only
    characters:dict = sdd_dataset['Characters'] # Get labelled characteristics

    # ===== Retrieve characteristics, values, and corresponding codes =====

    # Dict for storing characteristic codes
    quant_char_codes:dict = {}

    # Retrieve quantitative characteristics
    for quant_char in characters['QuantitativeCharacter']: # For each quantitative characteristic
        # Add an entry in the dictionary
        quant_char_codes[quant_char['@id']] = {
            'type': 'quantitative', # Type of characteristic
            'characteristic': quant_char['Representation']['Label'].lower().strip(), # Name of characteristic in lowercase
            'units': quant_char['MeasurementUnit']['Label'].lower().strip() # Unit for characteristic value in lowercase
        }
    
    # Return output dictionary
    return quant_char_codes

def sddxml2dict(sddxml:str) -> dict:
    """
    Convert a SDD XML string into a structured dict of species descriptions.
    The output dict is structured as follows:
    {
        "species 1": [
            {"characteristic": (name of characteristic), "value": (corresponding value)},
            (...)
        ], (...)
    }

    Parameters:
        sddxml (str): Raw XML string

    Returns:
        desc_dict (dict): Output dictionary
    """

    # Parse the raw XML
    sdd_dict:dict = xmltodict.parse(sddxml)
    
    sdd_dataset:dict = sdd_dict['Datasets']['Dataset'] # Extract the dataset only
    coded_descs:list = sdd_dataset['CodedDescriptions']['CodedDescription'] # Get coded descriptions of each species

    # ===== Retrieve characteristics, values, and corresponding codes =====
    
    # Retrieve characteristic codes
    cat_char_codes:dict = getcharcodes_cat(sddxml)
    quant_char_codes:dict = getcharcodes_quant(sddxml)
    
    # ===== Retrieve coded descriptions of species =====
    
    # Dict for storing species descriptions
    spp_chars:dict = {}

    # Iterate through each species
    for sp in coded_descs:
        # Species binomial
        sp_fullname:str = sp['Representation']['Label']
        sp_name:str = re.match(r'^([A-Z][^A-Z]*[a-z])', sp_fullname).group(1) # Remove author
        # Species characteristics
        sp_chars:list = []
        # Raw species characteristics
        sp_raw_chars:dict = sp['SummaryData']
        
        # Gather categorical characteristics
        for cat_char_code in cat_char_codes:
            # Find characteristic with cat_char_code for the species
            cat_chars = [cat_char for cat_char in sp_raw_chars['Categorical'] if cat_char['@ref'] == cat_char_code]

            # String representing the characteristic value
            val_str:Optional[str] = ''

            # Put None if character value is not found
            if len(cat_chars) == 0:
                val_str = None

            # Retrieve characteristic
            cat_char = cat_chars[0]
            
            if 'State' not in cat_char: # Put None if character value is not given
                val_str = None
            else:
                # Check if there are multiple categorical values
                if isinstance(cat_char['State'], list): # If there are more than one categorical value
                    val_str = '; '.join([
                        cat_char_codes[cat_char['@ref']]['values'][char_state['@ref']] for char_state in cat_char['State']
                    ]) # Join multiple values together with semicolon
                else: # If there is only one categorical value
                    val_str = cat_char_codes[cat_char['@ref']]['values'][cat_char['State']['@ref']]
            
            # Strip val_str
            val_str = val_str.strip()

            # Append item to sp_chars
            sp_chars.append({
                'characteristic': cat_char_codes[cat_char['@ref']]['characteristic'],
                'value': val_str
            })
        
        # Gether quantitative characteristics
        for quant_char_code in quant_char_codes:
            # Find characteristic with quant_char_code for the species
            quant_chars = [quant_char for quant_char in sp_raw_chars['Quantitative'] if quant_char['@ref'] == quant_char_code]

            # String representing the characteristic value
            val_str:Optional[str] = ''

            # Put None if character value is not found
            if len(quant_chars) == 0:
                val_str = None

            # Retrieve characteristic
            quant_char = quant_chars[0]

            if 'Measure' not in quant_char: # Put None if character value is not given
                val_str = None
            else:
                # Value range (sort so that the minimum value comes first)
                val_range = sorted([float(val['@value']) for val in quant_char['Measure']])

                # Set value string
                val_str = str(
                    val_range[0] if val_range[0] == val_range[1] # Single value if range minimum and maximum are identical
                    else '{}-{}'.format(*val_range) # Range if range minimum and maximum are different
                ) + ' ' + quant_char_codes[quant_char['@ref']]['units'] # Append units to end
                
            # Append characteristic
            sp_chars.append({
                'characteristic': quant_char_codes[quant_char['@ref']]['characteristic'],
                'value': val_str
            })

        # Sort characteristics
        sp_chars = sorted(sp_chars, key = lambda char: char['characteristic'])
        
        # Append species characteristics to spp_chars
        spp_chars[sp_name] = sp_chars

    # Return species characteristics dict
    return spp_chars

def sddxml2spplist(sddxml:str) -> list[str]:
    """
    Extract the list of species from an SDD-formatted XML string

    Parameters:
        sddxml (str): Raw XML string

    Returns:
        spp_list (list[str]): Output list of species
    """

    # Parse the raw XML
    sdd_dict:dict = xmltodict.parse(sddxml)
    
    sdd_dataset:dict = sdd_dict['Datasets']['Dataset'] # Extract the dataset only
    taxa:list = sdd_dataset['TaxonNames']['TaxonName'] # Extract taxa

    # Retrieve list of taxon names
    taxon_names:list[str] = [
        re.match(r'^([A-Z][^A-Z]*[a-z])', taxon['Representation']['Label']).group(1) # Remove the authors
        for taxon in taxa
    ]

    # Return list
    return taxon_names

