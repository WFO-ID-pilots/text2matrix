from typing import List, Optional

def regularise_charjson(chars:List[dict]) -> Optional[List[dict]]:
    """
    Validate the structure of a charjson output from functions in process_descs.py,
    and do some reformatting (e.g. converting the values into a string) if required.

    Parameters:
        chars (List[dict]): The charjson output of a process_descs.py function. The expected structure is [{"character": "", "value": ""},...]
    
    Returns:
        new_dict (Optional[List[dict]]): The regularised charjson output. This is set to None if the input is badly structured.
    """

    if not isinstance(chars, list): # If the chars list is not a list; needed as exception will not be thrown if not
        return None

    new_dict = []

    # Go through elements
    for char in chars:
        # Return None if the keys are different from what we expect
        if set(char.keys()) != {'characteristic', 'value'}:
            return None
        
        # Skip if value is None
        if char['value'] == None:
            continue
        
        # Convert value to string
        char['value'] = str(char['value'])

        # Append characteristic to new dict
        new_dict.append(char)
    
    # Return the new dict
    return new_dict

def regularise_table(table:List[dict], spids:List[str]) -> Optional[List[dict]]:
    """
    Check whether the character table dict produced by process_descs.get_char_table has a valid structure,
    and do some cleanup

    Parameters:
        table (List[dict]): A 'table' of characteristics structured as [{'characteristic': '', 'values': ['spid1': '', 'spid2': '', ...]}, ...]
        spids (List[str]): The list of the IDs of the species being tabulated
    
    Returns:
        new_table (Optional[List[dict]]): Cleaned-up and validated table of characteristics. None if the input table was badly structured.
    """

    if not isinstance(table, list): # If table is not a list; needed as no exception will be thrown
        return None

    new_table = []

    # Go through elements
    for char in table:
        # Return false if the keys are different from what we expect
        if set(char.keys()) != {'characteristic', 'values'}:
            return False
        
        # Return false if the values are badly structured
        if set(char['values'].keys()) != set(spids):
            return False
        
        # Convert values to string
        char['values'] = {spid: str(val) for spid, val in char['values'].items()}

        # Append characteristic to new dict
        new_table.append(char)
    
    # Return the new table
    return new_table

