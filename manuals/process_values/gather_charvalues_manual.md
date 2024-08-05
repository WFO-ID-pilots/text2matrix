# gather_charvalues.py user manual

This document explains how to use `gather_charvalues.py`, which is used for summarising the characteristics and their corresponding values that occur in the output file of a `desc2matrix` script.

## Arguments

| Argument | Description | Required? |
| --- | --- | --- | --- |
| `charjsonfile` (positional argument) | Path to the `desc2matrix` output JSON file to summarise | Yes |
| `outputfile` (positional argument) | Path to the output summary file to generate | Yes |

## Output

The output is a JSON structured as follows:

<pre>
{
    "(name of characteristic)": {
        "(possible value 1)": frequency,
        "(possible value 2)": frequency,
        (...)
    }, (...)
}
</pre>