"""
This script contains the default prompts that are used across the desc2matrix scripts.
"""

# System prompt
global_sys_prompt = """
You are a diligent robot assistant made by a botanist. You have expert knowledge of botanical terminology.
Your goal is to transcribe the given botanical description of plant characteristics into a valid JSON output.
Your answer must be as complete and accurate as possible.
You must answer in valid JSON, with no other text.
"""

# Prompt used for extracting a given list of characteristics
# [DESCRIPTION] in the prompt text is replaced by the plant description.
# [CHARACTER_LIST] in the prompt text is replaced by the list of characteristics to extract.
global_prompt = """
You are given a botanical description of a plant species taken from published floras.
You extract the types of characteristics mentioned in the description and their corresponding values, and transcribe them into JSON.
Your answer should be an array of JSON with name of the characteristic and the corresponding value formatted as follows: {"characteristic":(name of characteristic), "value":(value of characteristic)}.
(name of characteristic) should be substituted with the name of the characteristic, and (value of characteristic) should be substituted with the corresponding value.
The name of every characteristic must be written in lowercase.
Make sure that you surround your final answer with square brackets [ and ] so that it is a valid array.
Do not include any text (e.g. introductory text) other than the valid array of JSON.

Follow the instructions below.

1. Transcribe all the mentioned characteristics relating to the whole plant, such as growth form, reproduction, plant height, and branching.

2. Iterate through every mentioned organs (e.g. leaf and other leaf-like organs, stem, flower, inflorescence, fruit, seed and root) and parts of organs (e.g. stipule, anther, ovary) and transcribe their corresponding characteristics.
You must transcribe the length, width, shape, color, surface texture, surface features, and arrangement of each organ or part of an organ.
Each of these characteristics must be separate. The name of every characteristic relating to an organ or a part of an organ must be formatted as follows: "(name of organ or part of organ) (type of characteristic)", where (name of organ or part of organ) should be substituted with the name of the organ or part of the organ, and (type of characteristic) should be substituted with the specific type of characteristic.

In the final output JSON, try to include all words that appear in the given description, as long as they carry information about the plant species.
Do not make up characteristics that are not mentioned in the description.

Here are some examples of descriptions and their correponding transcription in JSON:

Sentence: "Fruit: ovoid berry, 10-12 mm wide, 13-15 mm long, yellow to yellow-green throughout."
JSON: {"characteristic": "fruit shape", "value": "ovoid"}, {"characteristic": "fruit type", "value": "berry"}, {"characteristic": "fruit width", "value": "10-12 mm"}, {"characteristic": "fruit length", "value": "13-15 mm"}, {"characteristic": "fruit color", "value": "yellow to yellow-green"}

Sentence: "Perennial dioecious herbs 60-100cm tall. Leaves alternate, green and glabrous adaxially and hirsute with white to greyish hair abaxially."
JSON: {"characteristic": "life history", "value": "perennial"}, {"characteristic": "reproduction", "value": "dioecious"}, {"characteristic": "growth form", "value": "herb"}, , {"characteristic": "plant height", "value": "60-100 cm"}, {"characteristic": "leaf arrangement", "value": "alternate"}, {"characteristic": "leaf adaxial colour", "value": "green"}, {"characteristic": "leaf adaxial texture", "value": "glabrous"}, {"characteristic": "leaf abaxial texture", "value": "hirsute"}, {"characteristic": "leaf abaxial hair colour", "value": "white to greyish"}

Include the following list of characteristics in your output. Use the name of the characteristic as given in this list. If you can't find one or more of these characteristics in the given description, put "NA" as the corresponding value. If you find a characteristic in the given description that is not in this list, add that characteristic in your response.

[CHARACTER_LIST]

Here is the description that you should transcribe:

[DESCRIPTION]
"""

# Prompt used to populate initial list of characteristics without tabulation
# [DESCRIPTION] in the prompt text is replaced by the plant description.
global_init_prompt = """
You are given a botanical description of a plant species taken from published floras.
You extract the types of characteristics mentioned in the description and their corresponding values, and transcribe them into JSON.
Your answer should be an array of JSON with name of the characteristic and the corresponding value formatted as follows: {"characteristic":(name of characteristic), "value":(value of characteristic)}.
(name of characteristic) should be substituted with the name of the characteristic, and (value of characteristic) should be substituted with the corresponding value.
The name of every characteristic must be written in lowercase.
Make sure that you surround your final answer with square brackets [ and ] so that it is a valid array.
Do not include any text (e.g. introductory text) other than the valid array of JSON.

Follow the instructions below.

1. Transcribe all the mentioned characteristics relating to the whole plant, such as growth form, reproduction, plant height, and branching.

2. Iterate through every mentioned organs (e.g. leaf and other leaf-like organs, stem, flower, inflorescence, fruit, seed and root) and parts of organs (e.g. stipule, anther, ovary) and transcribe their corresponding characteristics.
You must transcribe the length, width, shape, color, surface texture, surface features, and arrangement of each organ or part of an organ.
Each of these characteristics must be separate. The name of every characteristic relating to an organ or a part of an organ must be formatted as follows: "(name of organ or part of organ) (type of characteristic)", where (name of organ or part of organ) should be substituted with the name of the organ or part of the organ, and (type of characteristic) should be substituted with the specific type of characteristic.

In the final output JSON, try to include all words that appear in the given description, as long as they carry information about the plant species.
Do not make up characteristics that are not mentioned in the description.

Here are some examples of descriptions and their correponding transcription in JSON:

Sentence: "Fruit: ovoid berry, 10-12 mm wide, 13-15 mm long, yellow to yellow-green throughout."
JSON: {"characteristic": "fruit shape", "value": "ovoid"}, {"characteristic": "fruit type", "value": "berry"}, {"characteristic": "fruit width", "value": "10-12 mm"}, {"characteristic": "fruit length", "value": "13-15 mm"}, {"characteristic": "fruit color", "value": "yellow to yellow-green"}

Sentence: "Perennial dioecious herbs 60-100cm tall. Leaves alternate, green and glabrous adaxially and hirsute with white to greyish hair abaxially."
JSON: {"characteristic": "life history", "value": "perennial"}, {"characteristic": "reproduction", "value": "dioecious"}, {"characteristic": "growth form", "value": "herb"}, , {"characteristic": "plant height", "value": "60-100 cm"}, {"characteristic": "leaf arrangement", "value": "alternate"}, {"characteristic": "leaf adaxial colour", "value": "green"}, {"characteristic": "leaf adaxial texture", "value": "glabrous"}, {"characteristic": "leaf abaxial texture", "value": "hirsute"}, {"characteristic": "leaf abaxial hair colour", "value": "white to greyish"}

Here is the description that you should transcribe:

[DESCRIPTION]
"""

# Prompt used for initial trait tabulation in desc2matrix_accum_tab.py and desc2matrix_accum_followup.py
# [DESCRIPTIONS] in the prompt text is replaced by a structured list of plant descriptions.
global_tablulation_prompt = """
You are given a botanical description of a few plant species taken from published floras.
You extract the types of characteristics mentioned in the descriptions and their corresponding values, and transcribe them into JSON.
Your answer should be an array of JSON with name of the characteristic, ID of species, and the corresponding values formatted as follows: {"characteristic":(name of characteristic), "values":{(ID of species 1): (value of characteristic for species 1), (ID of species 2): (value of characteristic for species 2), ...}.
(name of characteristic) should be substituted with the name of the characteristic.
(ID of species n) should be substituted with the ID of the nth species.
(value of characteristic for species n) should be substituted with the corresponding characteristic value for the nth species.
The name of every characteristic must be written in lowercase.
Make sure that you surround your final answer with square brackets [ and ] so that it is a valid array.
Do not include any text (e.g. introductory text) other than the valid array of JSON.

Follow the instructions below.

1. Transcribe all the mentioned characteristics relating to the whole plant, such as growth form, reproduction, plant height, and branching.

2. Iterate through every mentioned organs (e.g. leaf and other leaf-like organs, stem, flower, inflorescence, fruit, seed and root) and parts of organs (e.g. stipule, anther, ovary) and transcribe their corresponding characteristics.
You must transcribe the length, width, shape, color, surface texture, surface features, and arrangement of each organ or part of an organ.
Each of these characteristics must be separate. The name of every characteristic relating to an organ or a part of an organ must be formatted as follows: "(name of organ or part of organ) (type of characteristic)", where (name of organ or part of organ) should be substituted with the name of the organ or part of the organ, and (type of characteristic) should be substituted with the specific type of characteristic.

3. If a characteristic is mentioned for one species (e.g. species ID A) but not for another species (e.g. species ID B) you should put "NA" as the corresponding value for species ID B. 

In the final output JSON, try to include all words that appear in the given descriptions, as long as they carry information about the plant species.
Do not make up characteristics that are not mentioned in the descriptions.

Here is an example of how you might transcribe species descriptions:

Description of species ID A: Perennial herb 10-30 cm tall. Fruits ovate, tomentose, yellow when ripe. Leaves alternate, glabrous, deep green.
Description of species ID B: Shrub 1-1.5 m tall. Friuts obovate, red when ripe. Leaves lanceolate, opposite, yellow-green.
Description of species ID C: Annual herb 10-12 cm tall. Fruits flattened, glabrous. Leaves alternate, with serrate margin, mid-green.
JSON output:
[
    {"characteristic": "life history", "values": {"A": "perennial", "B": "perennial", "C": "annual"}},
    {"characteristic": "growth form", "values": {"A": "herb", "B": "shrub", "C": "herb"}},
    {"characteristic": "plant height", "values": {"A": "10-30 cm", "B": "1-1.5 m", "C": "10-12 cm"}},
    {"characteristic": "fruit shape", "values": {"A": "ovate", "B": "obovate", "C": "flattened"}},
    {"characteristic": "fruit color", "values": {"A": "yellow when ripe", "B": "red when ripe", "C": "NA"}},
    {"characteristic": "fruit surface texture", "values": {"A": "tomentose", "B": "NA", "C": "glabrous"}},
    {"characteristic": "leaf arrangement", "values": {"A": "alternate", "B": "opposite", "C": "alternate"}},
    {"characteristic": "leaf surface texture", "values": {"A": "glabrous", "B": "NA", "C": "NA"}},
    {"characteristic": "leaf margin shape", "values": {"A": "NA", "B": "NA", "C": "serrate"}},
    {"characteristic": "leaf shape", "values": {"A": "NA", "B": "lanceolate", "C": "NA"}},
    {"characteristic": "leaf color", "values": {"A": "deep green", "B": "yellow-green", "C": "mid-green"}},
]

Here are the descriptions that you should transcribe:

[DESCRIPTIONS]
"""

# Follow-up prompt used across the scripts
# [DESCRIPTION] and [MISSING_WORDS] are each replaced by the plant description and the list of missing words.
global_followup_prompt = """
Please generate a new, more complete JSON response in the same format as before.

Here are the words in the original description that you've omitted in your JSON response:
[MISSING_WORDS]

Some of these are broken parts of words that you have included in your final response. For example, the list might have the word 'seudostipule' when you have 'pseudostipule' in your JSON. Ignore such cases.
Of the words in the above list, try to include all words that contain information about a plant trait that you have genuinely omitted.

Remember to include the following list of characteristics in your output. Use the name of the characteristic as given in this list. If you can't find one or more of these characteristics in the given description, put "NA" as the corresponding value. If you find a characteristic in the given description that is not in this list, add that characteristic in your response.
[CHARACTER_LIST]

Do not include any text (e.g. introductory text) other than the valid array of JSON.

Here is the original description that you should transcribe:
[DESCRIPTION]
"""