# text2matrix repo content summary

This document summarises the content currently in the repo and provide explanations on how the scripts work together.

## Scripts

Some of these scripts, found in [scripts](scripts/), have corresponding user manuals under [manuals](manuals/). The links to the manuals are provided where relevant.

### init
test
| File name | Description |
| --- | --- |
| [dwca2csv.py](scripts/init/dwca2csv.py) | Script used by Makefile to get taxa information from WFO |

### desc2matrix

The `desc2matrix` scripts, found under [scripts/desc2matrix](scripts/desc2matrix/), are responsible for extracting structured trait data from unstrutured plant species description text. There are two main types of scripts: (1) **trait accumulation** is the process of accumulating a list of the names of traits mentioned across a set of focal species descriptions, and (2) **trait extraction** is the process of extracting the trait values that correspond to a given list of trait names from individual species descriptions.

#### Main scripts

The legacy counterparts of these scripts that do not use the object-oriented common scripts are stored within legacy_scripts.

| File name | Description | Manual link |
| --- | --- | --- |
| [desc2matrix_accum.py](scripts/desc2matrix/desc2matrix_accum.py) | Trait accumulation | [Manual](manuals/desc2matrix/desc2matrix_accum_manual.md) |
| [desc2matrix_accum_tab.py](scripts/desc2matrix/desc2matrix_accum_tab.py) | Trait accumulation, obtains the initial list of traits by tabulating the traits of a few species | [Manual](manuals/desc2matrix/desc2matrix_accum_tab_manual.md) |
| [desc2matrix_accum_followup.py](scripts/desc2matrix/desc2matrix_accum_followup.py) | Trait accumulation, asks follow-up questions to improve completeness in LLM response | [Manual](manuals/desc2matrix/desc2matrix_accum_followup_manual.md) |
| [desc2matrix_accum_tf.py](scripts/desc2matrix/desc2matrix_accum_tf.py) | Trait accumulation, a combination of `tab` and `followup` | [Manual](manuals/desc2matrix/desc2matrix_accum_tf_manual.md) |
| [desc2matrix_wcharlist.py](scripts/desc2matrix/desc2matrix_wcharlist.py) | Trait extraction | [Manual](manuals/desc2matrix/desc2matrix_wcharlist_manual.md) |
| [desc2matrix_wcharlist_followup.py](scripts/desc2matrix/desc2matrix_wcharlist_followup.py) | Trait extraction, asks follow-up questions to improve completeness in LLM response | [Manual](manuals/desc2matrix/desc2matrix_wcharlist_followup_manual.md) |
| [desc2matrix_langchain_accum.py](scripts/desc2matrix/desc2matrix_langchain_accum.py) | Trait accumulation, uses the LangChain [Extraction API](https://python.langchain.com/v0.2/docs/tutorials/extraction/) | |
| [desc2matrix_langchain_wcharlist.py](scripts/desc2matrix/desc2matrix_langchain_wcharlist.py) | Trait extraction, uses the LangChain Extraction API | |

#### Common scripts

Under [common_scripts](scripts/desc2matrix/common_scripts/). These store classes and functions used in the main scripts.

| File name | Description |
| --- | --- |
| [default_prompts.py](scripts/desc2matrix/common_scripts/default_prompts.py) | Hard-coded default prompts used by main scripts |
| [process_words.py](scripts/desc2matrix/common_scripts/process_words.py) | NLP functions primarily used by follow-up scripts |
| [regularise.py](scripts/desc2matrix/common_scripts/regularise.py) | Functions for validating LLM output against expected structure & clean-up |
| [llmcharprocessor.py](scripts/desc2matrix/common_scripts/llmcharprocessor.py) | `LLMCharProcessor` parent class handling communication with LLM, post-processing and storage of output, and run summary generation |
| [accumulator.py](scripts/desc2matrix/common_scripts/accumulator.py) | `TraitAccumulator` classes inheriting `LLMCharProcessor`, handling trait accumulation |
| [extractor.py](scripts/desc2matrix/common_scripts/extractor.py) | `TraitExtractor` classes inheriting `LLMCharProcessor`, handling trait extraction |
| [langchainprocessor.py](scripts/desc2matrix/common_scripts/langchainprocessor.py) | Analogues of `LLMCharProcessor`, `TraitAccumulator`, and `TraitExtractor` using the LangChain Extraction API |

#### Misc. files

| File/folder name | Description |
| --- | --- |
| [alternative_prompts](scripts/desc2matrix/alternative_prompts) | Alternative prompts for the LLM runs |
| [bash_files/solanum_spp.sh](scripts/desc2matrix/bash_files/solanum_spp.sh) | Shell script used to run the `desc2matrix` scripts on the _Solanum_ species data from the [_Solanum_ key](https://url.uk.m.mimecastprotect.com/s/4XIGCojPZHvPW23izhwuYr7G3) |
| [charlists/solanum_charlist.txt](scripts/desc2matrix/charlists/solanum_charlist.txt) | List of characteristics mentioned in the [_Solanum_ key](https://url.uk.m.mimecastprotect.com/s/4XIGCojPZHvPW23izhwuYr7G3) |
| [charlists/solanum_charlist_gen_shorter.txt](scripts/desc2matrix/charlists/solanum_charlist_gen_shorter.txt) | List of characteristics accumulated by `desc2matrix_accum.py` from the _Solanum_ spp. descriptions |
| [charlists/solanum_charlist_gen_longer.txt](scripts/desc2matrix/charlists/solanum_charlist_gen_longer.txt) | List of characteristics accumulated by `desc2matrix_followup.py` from the _Solanum_ spp. descriptions |

### process_d2m_out

The scripts in the `process_d2m_out` folder are for processing the output from `desc2matrix` scripts.

#### Utility scripts

| File name | Description | Manual link |
| --- | --- | --- |
| [gather_charvalues.py](scripts/process_d2m_out/gather_charvalues.py) | Summarise the characteristic names & values in a `desc2matrix` output | [Manual](manuals/process_d2m_out/gather_charvalues_manual.md) |
| [merge_wcharlist_outs.py](scripts/process_d2m_out/merge_wcharlist_outs.py) / [merge_wcharlist_outs_legacy.py](scripts/process_d2m_out/merge_wcharlist_outs_legacy.py) | Merge two `desc2matrix_wcharlist` output files with the same run parameters | [Manual](manuals/process_d2m_out/merge_wcharlist_outs_manual.md) |

#### Quality control scripts

| File name | Description | Manual link |
| --- | --- | --- |
| [compare_d2m_desc.py](scripts/process_d2m_out/compare_d2m_desc.py) | Compare the structured output from `desc2matrix` against the original descriptions to determine omission, etc. | [Manual](manuals/process_d2m_out/compare_d2m_desc_manual.md) |
| [compare_d2m_key_chars.py](scripts/process_d2m_out/compare_d2m_key_chars.py) | Compare the structured output from `desc2matrix` against the characteristic values extracted by `sdd2json` script | [Manual](manuals/process_d2m_out/compare_d2m_key_chars_manual.md) |

#### Common scripts for QC

These files are found under [common_scripts](scripts/process_d2m_out/common_scripts/).

| File name | Description |
| --- | --- |
| [desc_nlp.py](scripts/process_d2m_out/common_scripts/desc_nlp.py) | Functions for running NLP on plant description data |
| [process_spnames.py](scripts/process_d2m_out/common_scripts/process_spnames.py) | Functions for handling scientific species names |

#### Misc. files

| File name | Description |
| --- | --- |
| [bash_scripts/process_wcharlist.sh](scripts/process_d2m_out/bash_scripts/process_wcharlist.sh) | Shell script for running the quality control scripts on the `desc2matrix` output |

### visualise_d2m_out

This folder contains the R scripts used to generate figures from the script output.

TO BE COMPLETED

### process_xper

This folder contains the scripts used for processing the SDD-formatted XML files downloaded from Xper.

| File name | Description | Manual |
| --- | --- | --- |
| [sdd2charlist.py](scripts/process_xper/sdd2charlist.py) | Convert the XML file into a list of characteristics mentioned | |
| [sdd2json.py](scripts/process_xper/sdd2json.py) | Summarise the characteristics and corresponding values of all species within the structured key | |
| [sdd2spplist.py](scripts/process_xper/sdd2spplist.py) | Gather the list of species in the structured key file into a list in a single file | |
| [subset_descfile.py](scripts/process_xper/subset_descfile.py) | Subset the description file generated by `dwca2csv.py` to include only species found within an SDD-formatted key file | |

## Script output

The output from the scripts described above are stored in [script_output](script_output/). All of these outputs were generated using the species in the [_Solanum_ key](https://url.uk.m.mimecastprotect.com/s/4XIGCojPZHvPW23izhwuYr7G3).

In [desc2matrix](script_output/desc2matrix/), [process_d2m_out](script_output/process_d2m_out/), and [process_xper](script_output/process_xper/), the file names have suffixes specifying the dataset that was used to produce the output as summarised below.

| Suffix | Description |
| --- | --- |
| `f` | Run with follow-up questions |
| `tab` | Run with initial tabulation |
| `langchain` | Run using LangChain scripts |
| no suffix | Run without initial tabulation or follow-up questions |
| `sgenlist` | Run using a shorter accumulated trait list generated by `desc2matrix_accum`; see [here](scripts/desc2matrix/charlists/solanum_charlist_gen_shorter.txt) |
| `lgenlist` | Run using a longer accumulated trait list generated by `desc2matrix_accum_followup`; see [here](scripts/desc2matrix/charlists/solanum_charlist_gen_longer.txt) |
| `subset` | Indicates that these output were generated from species in the _Solanum_ key; may not be present |

Visualisation figures included within the poster are stored in [visualise_d2m_out](script_output/visualise_d2m_out/).