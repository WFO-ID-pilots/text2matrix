# gather_charvalues.py user manual

This document explains how to use `gather_charvalues.py`, which is used for summarising the characteristics and their corresponding values that occur in the output file of a `desc2matrix` script.

## Arguments

| Argument | Description | Required? | Default value |
| --- | --- | --- | --- |
| `charjsonfile` (positional argument) | Path to the `desc2matrix` output JSON file to summarise | Yes | |
| `outputfile` (positional argument) | Path to the output summary file to generate | Yes | |
| `--sortcharbyfreq` | If present, sort the characteristics by frequency | No | `False` |
| `--sortvalbyfreq` | If present, sort the values by frequency | No | `False` |
| `--charsonly` | If present, collapse values to get frequencies of characteristics only | No | `False` |

## Output

The output is a JSON structured as follows with `--charsonly` == `False`:

<pre>
{
    "(name of characteristic)": {
        "(possible value 1)": frequency,
        "(possible value 2)": frequency,
        (...)
    }, (...)
}
</pre>

And as follows with `--charsonly` == `True`:

<pre>
{
    "(name of characteristic)": frequency,
    (...)
}
</pre>