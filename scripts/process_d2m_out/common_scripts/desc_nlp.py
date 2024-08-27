"""
Script containing the functions used for various NLP tasks
"""

from typing import Set
import nltk
import inflect
import re

nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords

inf = inflect.engine()
# Turn on 'classical' plurals as they are likely to occur in the dataset
inf.classical()

def get_word_set(descstr:str) -> Set[str]:
    """
    Get the list of non-stop words from a plant description string.
    This function removes punctuations from the tokens, collapses numeric ranges to 'words', and singularises nouns.

    Parameters:
        descstr (str): The plant description string to process.

    Returns:
        descset (Set[str]): The set of non-stop words found in the plant description.
    """

    # Gather stop words
    stop_words = set(stopwords.words('english'))

    # Insert whitespace before/after period, comma, colon, semicolon and brackets
    descstr = re.sub(r'[^0-9] *\. *[^0-9]', '. ', descstr) # Do not substitute periods in floating-point numbers
    descstr = re.sub(r'[^0-9] *\. *[0-9]', '. ', descstr) # Substitute periods next to numbers if either side is not a number
    descstr = re.sub(r'[0-9] *\. *[^0-9]', '. ', descstr)
    descstr = re.sub(r'[,:;\(\)\[\]{}"\'`“”]', ' ', descstr) # Replace brackets, etc. with space

    # Collapse numeric ranges to single 'word' to check for presence
    descstr = re.sub(r'([0-9]) *- *([0-9])', r'\1-\2', descstr)

    # Tokenise words, remove stop words, convert to lowercase
    descset = set([w.lower() for w in nltk.word_tokenize(descstr) if not w.lower() in stop_words])

    # Remove punctuations & brackets
    descset = descset.difference({'.'})

    # Singularise nouns (duplicates will automatically be merged since this is a set)
    descset_n = set([w for w in descset
                     if nltk.pos_tag([w])[0][1] in ['NN', 'NNS', 'NNPS', 'NNP']])
    descset_sing_n = set([w if inf.singular_noun(w) == False else inf.singular_noun(w) # inflection may determine that the word is not a noun, in which case use the original word
                          for w in descset_n])
    descset = descset.difference(descset_n).union(descset_sing_n) # Remove nouns and add back singulars

    # Return word set
    return descset