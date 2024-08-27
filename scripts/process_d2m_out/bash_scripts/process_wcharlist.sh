#!/bin/bash

# This script is for running the quality control scripts on the wcharlist output files.
cd ../../..

# compare_d2m_key_chars.py

python scripts/process_d2m_out/compare_d2m_key_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/compare_d2m_key_chars/wcharlist_comp.tsv

python scripts/process_d2m_out/compare_d2m_key_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_sgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/compare_d2m_key_chars/wcharlist_sgenlist_comp.tsv

python scripts/process_d2m_out/compare_d2m_key_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_lgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/compare_d2m_key_chars/wcharlist_lgenlist_comp.tsv

python scripts/process_d2m_out/compare_d2m_key_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_f_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/compare_d2m_key_chars/wcharlist_f_comp.tsv

python scripts/process_d2m_out/compare_d2m_key_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_f_sgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/compare_d2m_key_chars/wcharlist_f_sgenlist_comp.tsv

python scripts/process_d2m_out/compare_d2m_key_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_f_lgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/compare_d2m_key_chars/wcharlist_f_lgenlist_comp.tsv

# compare_d2m_desc.py

