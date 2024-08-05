#!/bin/bash
# Go to main branch directory
cd ..
# Activate venv
source ../env/Scripts/activate
# Run desc2matrix_accum_followup.py with alternative prompts over 800 species
# python desc2matrix_accum_followup.py ../data/solanaceae-desc.txt outputs/accum_output/accum_followup_altprompt_out_800sp.json --desctype=general --prompt=alternative_prompts/prompt_fix.txt --spnum=800
# Run desc2matrix_wcharlist.py with alternative prompts and the shorter trait list over 800 species
# python desc2matrix_wcharlist.py ../data/solanaceae-desc.txt charlists/charlist_solanaceae_shorter.txt outputs/wcharlist_output/wcharlist_altprompt_out_800sp.json --desctype=general --prompt=alternative_prompts/prompt_fix.txt --spnum=800
# Run desc2matrix_wcharlist_followup.py with alternative prompts and the shorter trait list over 800 species
# python desc2matrix_wcharlist_followup.py ../data/solanaceae-desc.txt charlists/charlist_solanaceae_shorter.txt outputs/wcharlist_output/wcharlist_followup_altprompt_out_800sp.json --desctype=general --prompt=alternative_prompts/prompt_fix.txt --spnum=800
# python desc2matrix_wcharlist_followup.py ../data/solanaceae-desc.txt charlists/charlist_solanaceae_shorter.txt outputs/wcharlist_output/wcharlist_followup_altprompt_out_800sp.json --desctype=general --prompt=alternative_prompts/prompt_fix.txt --spnum=800
python desc2matrix_wcharlist_followup.py ../data/solanaceae-desc.txt charlists/charlist_solanaceae_shorter.txt outputs/wcharlist_output/wcharlist_followup_altprompt_pt2_out_800sp.json --desctype=general --prompt=alternative_prompts/prompt_fix.txt --start=101 --spnum=800
# Exit venv
deactivate