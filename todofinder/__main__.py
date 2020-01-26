import argparse

from todofinder import get_files, scan_files, to_csv, to_csv_with_blame
from todofinder.plugins import plugin_names, swap_scan_line_function, restore_scan_line_function

def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Export a list of TODOs in a repo")
    parser.add_argument("-g", "--glob", nargs="+", help="Glob pattern for source files", required=True)
    parser.add_argument("-o", "--output", metavar="FILE", help="Name of the file in which to store the CSV file.", default="todos.csv")
    parser.add_argument("--print", action="store_true", help="Set flag to print to stdout instead of storing to a file")
    parser.add_argument("-p", "--plugins", metavar="PLUGIN", nargs="*", choices=plugin_names(), help="File-specific TODO behaviours")
    parser.add_argument("-b", "--blame", action="store_true", help="Set this flag to add `git blame` data to the report")
    return parser

def get_args() -> argparse.Namespace:
    parser = get_argparser()
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    files = get_files(args.glob)

    if args.plugins:
        if "all" in args.plugins:
            plugins = plugin_names()
        else:
            plugins = args.plugins
        swap_scan_line_function(plugins)
    output_file = None if args.print else args.output
    result = scan_files(files, output_file=output_file)
    if args.blame:
        to_csv_with_blame(result, output_file=output_file)
    else:
        to_csv(result, output_file=output_file)
    if args.plugins:
        restore_scan_line_function()

def cli():
    if __name__ == "__main__":
        main()

cli()
