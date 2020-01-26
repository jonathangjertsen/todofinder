import argparse

from todofinder import get_files, scan_files, to_csv

def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Export a list of TODOs in a repo")
    parser.add_argument("-g", "--glob", nargs="+", help="Glob pattern for source files", required=True)
    parser.add_argument("-o", "--output", metavar="FILE", help="Name of the file in which to store the CSV file.", default="todos.csv")
    return parser

def get_args() -> argparse.Namespace:
    parser = get_argparser()
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    files = get_files(args.glob)
    result = scan_files(files, output_file=args.output)
    to_csv(result, output_file=args.output)

def cli():
    if __name__ == "__main__":
        main()

cli()
