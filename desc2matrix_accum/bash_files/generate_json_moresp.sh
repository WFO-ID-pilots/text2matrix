#!/bin/bash
source env/Scripts/activate
python desc2matrix_accum.py data/solanaceae-desc.txt json_outputs/accum_out_800sp.json --desctype=general --spnum=800
python desc2matrix_accum_tab.py data/solanaceae-desc.txt json_outputs/accum_tab_out_800sp.json --desctype=general --spnum=800
python desc2matrix_accum_followup.py data/solanaceae-desc.txt json_outputs/accum_followup_out_800sp.json --desctype=general --spnum=800
deactivate