import argparse
from pathlib import Path
from unittest.mock import patch
import sys
import tempfile
import os

import todofinder
import todofinder.__main__ as cli

TESTVECTOR_DIR: Path = Path(__file__).parent / "testvector"

def test_setup():
    assert TESTVECTOR_DIR.is_dir()
    assert (TESTVECTOR_DIR / "README.md").is_file()


def test_get_files():
    glob_input = str(TESTVECTOR_DIR / "*.md")
    exp_output = str(TESTVECTOR_DIR / "README.md")

    files = todofinder.get_files([glob_input])
    assert list(files) == [exp_output]


def test_scan_line_no_todos():
    context = todofinder.TodoContext(None, None, None, None)
    no_todos = "This is a normal line of text."
    assert todofinder.scan_line(no_todos, context) is None


def test_scan_line_one_todo():
    context = todofinder.TodoContext(None, None, None, None)
    with_todos = "This line of text has a TODO: this one"
    assert todofinder.scan_line(with_todos, context) == todofinder.Todo(
        token="todo",
        text=" this one",
        context=context
    )

def test_scan_line_false_case():
    context = todofinder.TodoContext(None, None, None, None)
    with_todos = "This line has the word autodoc which contains the token"
    assert todofinder.scan_line(with_todos, context) is None


def test_scan_file():
    file = str(TESTVECTOR_DIR / "README.md")
    scan_result = todofinder.scan_file(file)
    todo_list = list(scan_result)
    assert todo_list == [todofinder.Todo(
        token="todo",
        text=" example",
        context=todofinder.TodoContext(
            file=file,
            line_number=0,
            full_line="This is a test-README. TODO: example",
            filetype="md",
        )
    )]


def test_scan_file_nonexistent_file(capsys):
    file = str(TESTVECTOR_DIR / "fakefile.iso")
    scan_result = todofinder.scan_file(file)
    todo_list = list(scan_result)
    assert "while scanning {}".format(str(file)) in capsys.readouterr().err
    assert todo_list == []


def test_integration(capsys):
    real_file = str(TESTVECTOR_DIR / "README.md")
    fake_file = str(TESTVECTOR_DIR / "fakefile.iso")
    outp_file = str(TESTVECTOR_DIR / "todos.csv")
    files = [
        real_file,
        fake_file,
        outp_file,
    ]
    scan_result = todofinder.scan_files(files, output_file=outp_file)
    todofinder.to_csv(scan_result, output_file=outp_file)

    assert "while scanning {}".format(str(fake_file)) in capsys.readouterr().err
    with open(outp_file) as file:
        assert file.read() == """
file,line_number,text,token,full_line,filetype
{real_file},0, example,todo,This is a test-README. TODO: example,md
""".format(real_file=real_file).lstrip()


def test_cli():
    todos_name = "todos_cli.csv"

    globs = [
        str(TESTVECTOR_DIR / "**/*.py"),
        str(TESTVECTOR_DIR / "**/*.md"),
        str(TESTVECTOR_DIR / "**/*.c"),
        str(TESTVECTOR_DIR / "**/*.unknown"),
    ]

    files = {
        "main_py": str(TESTVECTOR_DIR / "main.py"),
        "readme_md": str(TESTVECTOR_DIR / "README.md"),
        "main_c": str(TESTVECTOR_DIR / "main.c"),
        "unknown": str(TESTVECTOR_DIR / "file.unknown"),
    }

    plugins = ["md", "py", "c"]

    try:
        # Touch the todos file
        with open(todos_name, "w"):
            pass

        # CLI arguments
        args = ["todofinder", "-g", *globs, "-o", todos_name, "-p", *plugins]

        # Make the CLI function think it is running from the command line
        with patch.object(sys, "argv", args):
            with patch.object(todofinder.__main__, "__name__", "__main__"):
                cli.cli()

        #
        with open(todos_name, "r") as file:
            csv_data = file.read()
        assert csv_data == """
file,line_number,text,token,full_line,filetype
{main_py},0, add code,todo,#TODO: add code,py
{main_py},2, on indented line,todo,# TODO: on indented line,py
{readme_md},0, example,todo,This is a test-README. TODO: example,md
{main_c},2, something,todo,"printf(""Hello, World!""); // TODO: something",c
{unknown},0, nothing,todo,".unknown is not associated with any plugins, so it should make the main scanline function run. TODO nothing",unknown
""".lstrip().format(**files)
    finally:
        os.remove(todos_name)
