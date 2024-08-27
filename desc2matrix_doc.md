# desc2matrix high-level documentation

This document explains the architecture of the common classes and functions used in the main `desc2matrix` scripts, which are found under [desc2matrix/common_scripts](scripts/desc2matrix/common_scripts/). For detailed documentation on the individual functions, please refer to the docstring in the Python script files.

## Trait accumulator & extractor

Below is a class diagram explaining the architecture of the trait accumulation and extraction logic.

<img src="imgs/text2matrix_classes.svg" alt="desc2matrix class diagram" width="100%"/>

The base `LLMCharProcessor` is in [llmcharprocessor.py](scripts/desc2matrix/common_scripts/llmcharprocessor.py). The `TraitAccumulator` and `TraitExtractor` classes and their children classes are in [accumulator.py](scripts/desc2matrix/common_scripts/accumulator.py) and [extractor.py](scripts/desc2matrix/common_scripts/extractor.py), respectively.

These classes **depend on a running Ollama server**, whose address is specified with the `host_url` parameter during initialisation.

The snippets below show how to use the `TraitAccumulator` and `TraitExtractor` classes.

### TraitAccumulator usage

```python
# Initialise trait accumulator

accumulator = TraitAccumulator(
    sys_prompt, # The system prompt to use
    init_prompt, # The prompt to extract the initial list of characteristics
    # See global_init_prompt and global_tabulation_prompt in default_prompts for examples.
    prompt, # The prompt to run on each species description during accumulation
    # See global_accum_prompt in default_prompts for an example.
    # f_prompt, for FollowupTraitAccumulator
    # See global_followup_prompt in default_prompts for an example.
    model_name, # Name of the base model to use
    # This base model must be installed and available on the Ollama server.
    model_params # Model params provided as a dict, following this scheme: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
)

# Extract and store the initial list of traits from a plant description

accumulator.extract_init_chars(desc)

# For TabTraitAccumulator, multiple descriptions must be provided for tabulation:

# accum.extract_init_chras(descs)

# For each species description, grow the list of traits and update the list if needed
# The species id (spid) is provided so that each output is associated with a species id in the final output.

accumulator.accum_step(spid, desc)

# Get a summary dict including metadata and extracted characteristics

summ_dict = accumulator.get_summary()
```

### TraitExtractor usage

```python
# Initialise trait extractor

extractor = TraitExtractor(
    sys_prompt, # System prompt to use
    prompt, # The extraction prompt to run on each species description
    # See global_ext_prompt in default_prompts for an example.
    # f_prompt, for FollowupTraitExtractor
    # See global_followup_prompt in default_prompts for an example.
    charlist, # The list of the names of characteristics to extract
    model_name, # Name of the base model to use
    # This base model must be installed and available on the Ollama server.
    params # Model params provided as a dict, following this scheme: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
)

# For each species, extract and save traits

extractor.ext_step(spid, desc)

# Generate summary dict

extractor.get_summary()
```

## Trait accumulator & extractor using LangChain

Below is a class diagram explaining the architecture of the trait accumulation and extraction logic using LangChain's [Extraction API](https://python.langchain.com/v0.1/docs/use_cases/extraction/).

<img src="imgs/text2matrix_classes.svg" alt="desc2matrix class diagram" width="100%"/>

Specifically, these classes use Groq which hosts LLMs and handle generation requests.

The usage of these classes are almost identical to the above using Ollama, except only the system prompt is used to communicate instructions to the model. See below for the relevant examples:

### LCTraitAccumulator usage

```python
# Initialise trait accumulator

accumulator = LCTraitAccumulator(
    init_prompt, # See langchain_init_prompt in default_prompts
    prompt, # See langchain_accum_prompt in default_prompts
    args.model,
    params # The parameters are explained here: https://api.python.langchain.com/en/latest/chat_models/langchain_groq.chat_models.ChatGroq.html
)

# Generate & store initial trait list

accumulator.extract_init_chars(desc)
# OR
# accumulator.extract_init_chars(descs)

# Grow trait list on each species

accumulator.accum_step(spid, desc)

# Get summary dict

summ_dict = accumulator.get_summary()
```

### LCTraitExtractor usage

```python
# Initialise trait extractor

extractor = LCTraitExtractor(
    prompt, # See langchain_ext_prompt in default_prompts
    charlist,
    args.model,
    params # The parameters are explained here: https://api.python.langchain.com/en/latest/chat_models/langchain_groq.chat_models.ChatGroq.html
)

# Extract & store traits from a species description

extractor.ext_step(spid, desc)

# Get summary dict

summ_dict = accumulator.get_summary()
```