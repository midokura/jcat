#!/usr/bin/env python3
import argparse
import json
import os
import sys

from pprint import pformat

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

pprint_size = 120

def pretty_json(json_text: str) -> str:
    pfmt = pformat(json_text, compact=True, width=pprint_size)
    if not sys.stdout.isatty():
        print(pfmt)
    highlight(pfmt, PythonLexer(), TerminalFormatter(bg='dark'), outfile=sys.stdout)

if __name__ == '__main__':
    if sys.stdout.isatty():
        pprint_size = os.get_terminal_size().columns

    parser = argparse.ArgumentParser(
        description='Prints pretty-formatted JSON files'
    )
    parser.add_argument('files', help="JSON file(s) to print", nargs='+')
    args = parser.parse_args()
    for filepath in args.files:
        if not os.path.isfile(filepath):
            raise ValueError(f'Not a file: {filepath}')
    for filepath in args.files:
        with open(filepath) as f:
            pretty_json(json.load(f))