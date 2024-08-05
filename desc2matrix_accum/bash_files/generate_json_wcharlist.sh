#!/bin/bash
source env/Scripts/activate
# python desc2matrix_wcharlist.py data/solanaceae-desc.txt charlists/charlist_solanaceae.txt outputs/wcharlist_out_800sp.json --desctype=general --spnum=800
# python desc2matrix_wcharlist_followup.py data/solanaceae-desc.txt charlists/charlist_solanaceae.txt outputs/wcharlist_followup_out_800sp.json --desctype=general --spnum=800
# python desc2matrix_wcharlist.py data/solanaceae-desc.txt charlists/charlist_solanaceae_shorter.txt outputs/wcharlist_shortlist_out_800sp.json --desctype=general --spnum=800
python desc2matrix_wcharlist_followup.py data/solanaceae-desc.txt charlists/charlist_solanaceae_shorter.txt outputs/wcharlist_shortlist_followup_out_800sp.json --desctype=general --spnum=800
deactivate