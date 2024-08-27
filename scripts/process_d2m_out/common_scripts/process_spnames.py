"""
Functions related to processing the SDD-formatted species key file.
"""

from typing import List, Literal
import re
import copy

def get_epithets(sp_name:str) -> List[str]:
    """
    Split a species name into epithets.

    Parameters:
        sp_name (str): Scientific name of species

    Returns:
        epithets (List[str]): Epithets
    """

    return re.findall(r'×?([A-Za-z]+)×?', sp_name)

def spname_identity(binom:str, test:str) -> bool:
    """
    Check whether test is a species/subspecies represented by binom, taking hybrids and variants/subspecies into account
    This function will return True if test is a subspecies within binom.

    Parameters:
        binom (str): Latin binomial or a hybrid species name
        test (str): Loosely-structured test string to determine identity with binom

    Returns:
        is_represented (bool): Whether test is represented by binom
    """

    # Capture epithets from binom string
    binom_parts:List[str] = get_epithets(binom)
    
    # Capture epithets from test string
    test_parts:List[str] = get_epithets(test)

    # Check if the epithets in the binom string match those in the test string
    is_represented:bool = False not in [
        binom_parts[i:i+1] == test_parts[i:i+1]
        for i in range(0, len(binom_parts))
    ]

    return is_represented

def map_spnames(origin_spp:List[str], target_spp:List[str], match_direction:Literal['origin_in_target', 'target_in_origin', 'either', 'both']):
    """
    Return a list of ids equal to the length of origin_spp containing the ids of corresponding species in target_spp.
    
    Parameters:
        origin_spp (List[str]): List of species to map from
        target_spp (List[str]): List of species to map to
        match_direction (Literal['origin_in_target', 'target_in_origin', 'either', 'both']): If 'origin_in_target', a mapping is created if a species in origin is a subtaxon of target. Vice versa for 'target_in_origin'. 'either' creates a mapping if either is true, 'both' creates a mapping only if both is true.
    
    Returns:
        found_ids (List[int]): List of ids equal to the length of origin_spp that maps origin_spp to target_spp
    """

    # Bind spp and ids as a list of tuples
    spp_pairs = list(enumerate(target_spp))

    # List to store the found coreids
    found_ids:List[int] = []

    # Define function for matching
    def match_func(origin_sp, target_sp):
        match match_direction:
            case 'origin_in_target':
                return spname_identity(target_sp, origin_sp)
            case 'target_in_origin':
                return spname_identity(origin_sp, target_sp)
            case 'either':
                return spname_identity(target_sp, origin_sp) or spname_identity(origin_sp, target_sp)
            case 'both':
                return spname_identity(target_sp, origin_sp) and spname_identity(origin_sp, target_sp)

    # Iterate through every species names in spp
    for origin_sp in origin_spp:
        # Get a list of species in spp which are considered to be represented by new_sp
        match_list = list(filter(lambda sp_pair: match_func(origin_sp, sp_pair[1]), spp_pairs))
        # Save the id corresponding to the first item in the list
        # If there are no matches, insert None
        found_ids.append(
            match_list[0][0] if len(match_list) > 0 else None
        )

    # Return id mappings
    return found_ids
