# TODO-finder

It finds TODOs!

## Requirements

Python 3.8

To install, clone the repo and run `pip install -e .`. 

## Usage

Specify a glob pattern with `-g` and use `-o` to specify where to store the CSV report

```
python -m todofinder -g <glob_pattern> ... <glob_pattern> -o FILE 
```

