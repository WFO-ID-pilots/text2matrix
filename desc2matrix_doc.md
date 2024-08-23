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
    params # Model params provided as a dict, following this scheme: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
)

# Extract and store the initial list of traits from a plant description
accum.extract_init_chars(desc)
# For TabTraitAccumulator, multiple descriptions must be provided for tabulation:
# accum.extract_init_chras(descs)

# For each species description, grow the list of traits and update the list if needed
# The species id (spid) is provided so that each output is associated with a species id in the final output.
accum.accum_step(spid, desc)

# Get a summary dict including metadata and extracted characteristics
summ_dict = accum.get_summary()
```