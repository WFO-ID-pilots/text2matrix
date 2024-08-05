#!/bin/bash
source env/Scripts/activate
python desc2matrix_accum_followup.py data/solanaceae-desc.txt json_outputs/accum_f_out_largerctx_800sp.json --desctype=general --spnum=800 --numpredict=4096 --numctx=32768
python desc2matrix_accum_followup.py data/solanaceae-desc.txt json_outputs/accum_f_out_listinfollowup_800sp.json --desctype=general --spnum=800 --fprompt=alternative_prompts/alt_followup_prompt.txt
python desc2matrix_accum_followup.py data/solanaceae-desc.txt json_outputs/accum_f_out_largerctx_and_listinfollowup_800sp.json --desctype=general --spnum=800 --numpredict=4096 --numctx=32768 --fprompt=alternative_prompts/alt_followup_prompt.txt

deactivate