# text2matrix repo content summary

This document summarises the content currently in the repo and provide explanations on how the scripts work together.

## Scripts

Some of these scripts, found in [scripts](scripts/), have corresponding user manuals under [manuals](manuals/). The links to the manuals are provided where relevant.

### desc2matrix

The `desc2matrix` scripts, found under [scripts/desc2matrix](scripts/desc2matrix/), are responsible for extracting structured trait data from unstrutured plant species description text. There are two main types of scripts: (1) **trait accumulation** is the process of accumulating a list of the names of traits mentioned across a set of focal species descriptions, and (2) **trait extraction** is the process of extracting the trait values that correspond to a given list of trait names from individual species descriptions.

| File name | Description | Manual link |
| --- | --- | --- |
| [desc2matrix_accum.py](scripts/desc2matrix/desc2matrix_accum.py) | Script used for trait accumulation | [Manual](manuals/desc2matrix/desc2matrix_accum_manual.md) |
| [desc2matrix_accum_tab.py](scripts/desc2matrix/desc2matrix_accum_tab.py) | Script used for trait accumulation, obtains the initial list of traits by tabulating the traits of a few species | [Manual](manuals/desc2matrix/desc2matrix_accum_tab_manual.md) |
| [desc2matrix_accum_followup.py](scripts/desc2matrix/desc2matrix_accum_followup.py) | Script used for trait accumulation, asks follow-up questions to improve completeness in LLM response | [Manual](manuals/desc2matrix/desc2matrix_accum_followup_manual.md) |