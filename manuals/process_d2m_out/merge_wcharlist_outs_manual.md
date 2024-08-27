# merge_wcharlist_outs.py user manual

This document explains the usage of `merge_wcharlist_outs.py`, which can be used to merge `desc2matrix_wcharlist` script outputs on the same dataset if the previous run was interrupted. This script does stringent checks on the conformity of run settings betwee the two output files to ensure that the merge is valid. This script accounts for there being duplicate entries between the two files; in this case, the entry in the `part1` file overrides the entry in `part2`.

NB: `merge_wcharlist_outs_legacy.py` should be used to merge `desc2matrix_wcharlist` outputs in the older legacy format, in which the metadata was not packaged within the `metadata` key in the output JSON.

## Arguments

| Argument | Description |
| --- | --- | --- | --- |
| `part1` | The 'first part' of the two `desc2matrix_wcharlist` outputs to merge |
| `part2` | The 'second part' of the two `desc2matrix_wcharlist` outputs to merge |
| `outfile` | Path for the merged `desc2matrix_wcharlist` output |