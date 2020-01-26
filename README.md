# TODO-finder

[![Build Status](https://travis-ci.com/jonathangjertsen/todofinder.svg?branch=master)](https://travis-ci.com/jonathangjertsen/todofinder)

It finds TODOs!

## Requirements

Python 3.8

To install, run `pip install todofinder`.

## Usage

Specify a glob pattern with `-g` and use `-o` to specify where to store the CSV report

```
python -m todofinder -g <glob_pattern> ... <glob_pattern> -o FILE 
```

