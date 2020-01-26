import csv
from collections import namedtuple
from functools import lru_cache
import glob
import os
import pathlib
import re
import subprocess
import sys
from typing import Dict, Iterable, Optional, List, Tuple

LOWERCASE_CHARS = { chr(x) for x in range(ord('a'), ord('z')) }
UPPERCASE_CHARS = { char.upper() for char in LOWERCASE_CHARS }
DIGITS = { chr(x) for x in range(ord('0'), ord('9')) }
VARNAME_CHARS = LOWERCASE_CHARS | UPPERCASE_CHARS | DIGITS | { '_' }

TOKENS = {
    "todo",
    "fixme",
}

TodoContext = namedtuple("TodoContext", "file line_number full_line filetype")
Todo = namedtuple("Todo", "token text context")
TodoBlame = namedtuple("TodoBlame", "author date commit message")

TODO_FIELDS = (
    "file",
    "line_number",
    "text",
    "token",
    "full_line",
    "filetype"
)

BLAME_FIELDS = (
    "author",
    "date",
    "commit",
    "message"
)

def log_error(message):
    print(message, file=sys.stderr)

def get_files(glob_paths: Iterable[str], recursive: bool=True) -> Iterable[str]:
    for glob_path in glob_paths:
        yield from glob.iglob(glob_path, recursive=recursive)

def get_todo_text(line: str) -> Optional[Tuple[str, str]]:
    # Check for TODO tokens
    lower_line = line.lower()
    for token in TOKENS:
        if token in lower_line:
            break
    else:
        return None

    # Look at what comes before and after
    before, *after = re.split(token, line, flags=re.IGNORECASE)

    # Guard against e.g. "autodoc"
    if before and before[-1] in VARNAME_CHARS:
        return None

    # Guard against e.g. "todofinder"
    if after and after[0] and after[0][0] in VARNAME_CHARS:
        return None

    # Re-assemble the string
    text = ", ".join(after)

    # Remove the colon after the TODO
    text = text.lstrip(":")
    return token, text

def scan_line(line: str, context: TodoContext) -> Optional[Todo]:
    token_and_text = get_todo_text(line)
    if token_and_text is not None:
        token, text = token_and_text
        return Todo(token=token, text=text, context=context)

def scan_file(path: str) -> Iterable[Todo]:
    extension = path.split(".")[-1]
    try:
        with open(path) as file:
            for line_no, line in enumerate(file):
                line = line.strip()
                context = TodoContext(path, line_no, line, extension)
                todo = scan_line(line, context)
                if todo is not None:
                    yield todo
    except Exception as exception:
        log_error("{} while scanning {}: {}".format(type(exception).__name__, path, exception))

def scan_files(paths: Iterable[str], output_file: str) -> Iterable[Todo]:
    for path in paths:
        if path == output_file:
            continue
        yield from scan_file(path)


def to_csv_row(todo: Todo) -> List[str]:
    return [
        todo.context.file,
        todo.context.line_number,
        todo.text,
        todo.token,
        todo.context.full_line,
        todo.context.filetype,
    ]

def to_csv(todos: Iterable[Todo], output_file: str):
    csvfile = sys.stdout
    try:
        if output_file is not None:
            csvfile = open(output_file, "w", newline="")

        writer = csv.writer(csvfile)
        writer.writerow(TODO_FIELDS)
        for todo in todos:
            writer.writerow(to_csv_row(todo))
    finally:
        if csvfile != sys.stdout:
            csvfile.close()

def shell_exec(args: List[str], directory: str) -> Optional[str]:
    orig_dir = os.getcwd()
    try:
        os.chdir(directory)
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.stderr:
            return None
        text = proc.stdout
        text = text.decode("utf-8").strip()
    except Exception:
        return None
    finally:
        os.chdir(orig_dir)
    return text

@lru_cache
def get_git_message(sha: str, directory: str) -> Optional[str]:
    text = shell_exec([
        "git",
        "show",
        sha,
        "-s",
        '--format="%s"',
    ], directory)
    return text.strip('"') if text else None

@lru_cache
def get_blame_for_file(file: str) -> Optional[Dict[int, Dict[str, str]]]:
    file_abs_path = pathlib.Path(file).absolute()
    parent_path = str(file_abs_path.parent)
    text = shell_exec([
        "git",
        "blame",
        str(file_abs_path),
        "--no-show-name",
        "--date=short",
        "-e",
        "-l",
        "-w",
        "-c",
    ], parent_path)

    if not text:
        return None

    lines = text.split("\n")

    blame_per_line = {}
    for line in lines:
        if line:
            sha, mail_ish, date, *line_and_code_parts = line.split("\t")
            mail = mail_ish.lstrip("(<").rstrip(">")
            line_and_code = "\t".join(line_and_code_parts)
            line, *code_parts = line_and_code.split(")")
            code = ")".join(code_parts)
            blame_per_line[int(line)] = {
                "sha": sha,
                "mail": mail,
                "date": date,
                "code": code,
                "message": get_git_message(sha, parent_path)
            }
    return blame_per_line

def get_blame(todo: Todo) -> TodoBlame:
    blame_per_line = get_blame_for_file(todo.context.file)
    if blame_per_line is None:
        return TodoBlame(None, None, None, None)
    else:
        blame = blame_per_line[todo.context.line_number + 1]
        return TodoBlame(author=blame["mail"], commit=blame["sha"], date=blame["date"], message=blame["message"])

def to_csv_with_blame(todos: Iterable[Todo], output_file: str):
    csvfile = sys.stdout
    try:
        if output_file is not None:
            csvfile = open(output_file, "w", newline="")
        writer = csv.writer(csvfile)
        writer.writerow(TODO_FIELDS + BLAME_FIELDS)
        for todo in todos:
            blame = get_blame(todo)
            writer.writerow(to_csv_row(todo) + [
                blame.author,
                blame.date,
                blame.commit,
                blame.message,
            ])
    finally:
        if csvfile != sys.stdout:
            csvfile.close()
