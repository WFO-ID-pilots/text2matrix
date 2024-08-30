# text2matrix

## Rationale & Overview

This projects explores how we could use a large language model to reformat text species descriptions into species / character matrices, suitable for building multi-entry identification keys.

For a summary of the current results obtained using these scripts, please see here: https://doi.org/10.5281/zenodo.13385757.

The following guide documents may be useful for development:

[Content summary](CONTENT_SUMMARY.md): Summary of the repo content structure & how scripts work together.

[desc2matrix documentation](DESC2MATRIX_DOC.md): High-level documentation for `desc2matrix` scripts responsible for converting unstructured species descriptions into structured output. Includes simple code examples.

## Pre-requisites

An environment capable of running Python, the build tool `make` and the `wget` utility. 
make and wget will be pre-installed on most *nix systems, on Windows they can be installed via [scoop](https://scoop.sh/):

1. Install scoop
     ```
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
    ```
1. Use scoop to install make and wget:
    ```{shell}
    scoop bucket add main
    scoop install main/make
    scoop install main/wget
    ```

## Set-up

1. Create a virtual environment: `python -m venv env`
1. Activate it: `source env/Scripts/activate` 
1. Install required libraries: `pip install -r requirements.txt` 

## Running the software

A complete run will download the specified DWCA files from the World Flora Online data server and process them to extract the taxonomy and descriptions to delimited text files, suitable for further processing using a LLM.

You can see what steps the makefile will execute by typing `make all --dry-run`

You can run the makefile to build all targets by typing: `make all`

## Contributing

Specific issues or enhancements can be added to the [issues tracker](https://github.com/WFO-ID-pilots/text2matrix/issues) for this project. More general discussions are also welcomed on the [discussion board](https://github.com/orgs/WFO-ID-pilots/discussions) for the parent project

## Contacts

- Nicky Nicolson - [@nickynicolson](https://github.com/nickynicolson)
- Young Jun Lee - [@yjkiwilee](https://github.com/yjkiwilee)
