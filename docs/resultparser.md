---
title: Parsing Benchmark Results
---

# Result Parser

A result parser is a function that receives the parameters:

- **root**
  The root path of the run
- **runspec**
  An instance of `Runspec`, containing various information about the run as defined in the runscript.
- **instance**
  An instance of `Instance`, containing the information regarding the benchmark instance used for this run, such as location and instance name.

and returns a list of triples `(key, type, value)` for later use by the summarizer.

## Example

A full example can be seen in `benchmarks/examples/**/resultparser.py`.

```python
def myresultparser(root, runspec, instance):
    # ...
    return [
        ('wall', 'float', 1.0242),
        ('mem', 'float', 82519554),
    ]
```
