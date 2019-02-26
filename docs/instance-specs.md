---
title: Specifying benchmark instances
---

Benchmark instances can be specified by one or more of these specification type:

## Folder specification

Given a `path` and git-like `patterns` specification, this specification selects files from the filesystem.

Example:

```yaml
type: folder
path: instances
patterns:
  - '!**/pigeons/*'
  - pigeons/pigeonhole10-unsat.lp
  - pigeons/pigeonhole11-unsat.lp
```

## DOI specification

Given an additional `doi` argument, this specification downloads the dataset linked by the doi to the filesystem before selecting it just as [Folder specification](#folder-specification) does. Additionally, it can extract archives when `extract_archives` argument is set to true.

!!! note

    Currently only datasets from these source is supported: [Zenodo](https://zenodo.org).

!!! note

    Currently only these archive types are supported: `*.zip`.

Example:

```yaml
type: doi
doi: 10.5072/zenodo.261834
path: ./instances
extract_archives: true
patterns:
  - sudoku/*.txt
  - '!**/*.zip'
```
