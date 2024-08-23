#!/bin/bash

# This script is for running the compare_chars.py script on the wcharlist output files.
cd ../../../..

source env/Scripts/activate

python scripts/process_d2m_out/quality_control/compare_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/quality_control/compare_chars/wcharlist_comp.tsv

python scripts/process_d2m_out/quality_control/compare_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_sgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/quality_control/compare_chars/wcharlist_sgenlist_comp.tsv

python scripts/process_d2m_out/quality_control/compare_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_lgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/quality_control/compare_chars/wcharlist_lgenlist_comp.tsv

python scripts/process_d2m_out/quality_control/compare_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_f_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/quality_control/compare_chars/wcharlist_f_comp.tsv

python scripts/process_d2m_out/quality_control/compare_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_f_sgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/quality_control/compare_chars/wcharlist_f_sgenlist_comp.tsv

python scripts/process_d2m_out/quality_control/compare_chars.py script_output/desc2matrix/wcharlist/subset/wcharlist_f_lgenlist_subset.json script_output/process_xper/sdd2json/solanum_spp.json data/solanaceae-taxa-subset.txt script_output/process_d2m_out/quality_control/compare_chars/wcharlist_f_lgenlist_comp.tsv