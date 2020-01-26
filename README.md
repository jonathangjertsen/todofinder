# TODO-finder

[![Build Status](https://travis-ci.com/jonathangjertsen/todofinder.svg?branch=master)](https://travis-ci.com/jonathangjertsen/todofinder)
[![codecov](https://codecov.io/gh/jonathangjertsen/todofinder/branch/master/graph/badge.svg)](https://codecov.io/gh/jonathangjertsen/todofinder)


It finds TODOs!

## Requirements

Python 3.8

To install, run `pip install todofinder`.

## Usage

Specify a glob pattern with `-g` and use `-o` to specify where to store the CSV report.

```
python -m todofinder -g <glob_pattern> ... <glob_pattern> -o FILE
```

The CSV file will have the following fields, and it will have a header with these field names:

* `file`: absolute path to the file
* `line_number`: the TODO's line number
* `text`: The text after "TODO:" (colon optional)
* `token`: The matched token (either TODO or FIXME)
* `full_line`: The complete line (newlines stripped)
* `filetype`: The file's file type (part after the first dot).

### Plugins

You can use `-p` or `--plugins` to enable language-specific parsers that will prevent false
positives and skip over lines without comments. Currently available plugins:

* Python: `-p py`
* C: `-p c`

You can have one or more active plugins (e.g. `-p py c`) or all at once (`-p all`)

### Blame

You can use `-b` or `--blame` to run `git blame` on all files with TODOs and extract info.
This will add the following fields to the CSV report:

* `author`: The name of the person who last touched the line
* `date`: The date at which the last commit touching the line was made
* `commit`: The commit hash
* `message`: The first line of the commit message
