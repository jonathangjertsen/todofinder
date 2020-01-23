import argparse
import csv
from collections import namedtuple
import glob
import re
from typing import Iterable, Optional
import sys

TOKENS = {
    "todo",
    "fixme",
}
CSV_FIELDS = {
    "file": lambda todo: todo.context.file,
    "line_number": lambda todo: todo.context.line_number,
    "text": lambda todo: todo.text,
    "token": lambda todo: todo.token,
    "full_line": lambda todo: todo.context.full_line,
    "filetype": lambda todo: todo.context.filetype
}

TodoContext = namedtuple("TodoContext", "file line_number full_line filetype")
Todo = namedtuple("Todo", "token text context")

def log_error(message):
    print(message, file=sys.stderr)

def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Export a list of TODOs in a repo")
    parser.add_argument("-g", "--glob", nargs="+", help="Glob pattern for source files", required=True)
    parser.add_argument("-o", "--output", metavar="FILE", help="Name of the file in which to store the CSV file.", default="todos.csv")
    return parser

def get_args() -> argparse.Namespace:
    parser = get_argparser()
    args = parser.parse_args()
    return args

def get_files(glob_paths: str, recursive: bool=True) -> Iterable[str]:
    for glob_path in glob_paths:
        yield from glob.iglob(glob_path, recursive=recursive)

def get_todo_text(line: str, matched_token: str) -> str:
    text = re.split(matched_token, line, flags=re.IGNORECASE)[1]
    text = text.lstrip(": ")
    text = text.strip()
    return text

def scan_line(line: str, context: TodoContext) -> Optional[Todo]:
    for token in TOKENS:
        if token in line.lower():
            return Todo(token=token, text=get_todo_text(line, token), context=context)

def scan_file(path: str) -> Iterable[Todo]:
    try:
        with open(path) as file:
            for line_no, line in enumerate(file):
                context = TodoContext(path, line_no, line.strip(), path.split(".")[-1])
                if (todo := scan_line(line, context)) is not None:
                    yield todo
    except Exception as exception:
        log_error("Exception while scanning {}: {}".format(path, exception))

def scan_files(paths: Iterable[str], output_file: str) -> Iterable[Todo]:
    for path in paths:
        if path == output_file:
            continue
        yield from scan_file(path)

def to_csv(todos: Iterable[Todo], output_file: str):
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(CSV_FIELDS.keys())
        for todo in todos:
            writer.writerow([func(todo) for func in CSV_FIELDS.values()])

if __name__ == "__main__":
    args = get_args()
    files = get_files(args.glob)
    result = scan_files(files, output_file=args.output)
    to_csv(result, output_file=args.output)
    