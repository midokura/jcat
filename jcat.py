#!/usr/bin/env python3
import argparse
import json
import os
import sys

from pprint import pformat

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

pprint_size = 80

def get_term_width():
    """When piping output, stdout is a pipe and not a tty, so we cannot get the
    terminal size from it. This method falls back to getting the tty size from
    stderr"""
    try:
        col, _ = get_tty_size_from_fd(sys.stdout.fileno())
        return col
    except OSError:
        pass
    try:
        col, _ = get_tty_size_from_fd(sys.stderr.fileno())
        return col
    except OSError:
        pass
    return os.getenv('COLUMNS', 80)


def get_tty_size_from_fd(fd):
    from fcntl import ioctl
    from termios import TIOCGWINSZ
    from struct import unpack
    try:
        res = ioctl(fd, TIOCGWINSZ, b"\x00" * 4)
    except IOError as e:
        raise OSError(e)
    lines, columns = unpack("hh", res)
    return (columns, lines)


def pretty_json(json_text: str) -> str:
    global pprint_size
    pfmt = pformat(json_text, compact=True, width=pprint_size)
    if not any((sys.stdout.isatty(), sys.stderr.isatty())):
        print(pfmt)
    highlight(pfmt, PythonLexer(), TerminalFormatter(bg='dark'), outfile=sys.stdout)


def read_stdin():
    # TODO: paginate
    pretty_json(json.loads(sys.stdin.read()))


def main():
    global pprint_size
    pprint_size = get_term_width()

#    sys.stdin.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(
        description='Prints pretty-formatted JSON files'
    )
    parser.add_argument('files',
                        help="JSON file(s) to print, leave empty or use \"-\" to read from stdin",
                        nargs='*')
    args = parser.parse_args()
    for filepath in args.files:
        if filepath == '-':
            continue
        if not os.path.isfile(filepath):
            raise ValueError(f'Not a file: {filepath}')
    if not args.files:
        read_stdin()
    else:
        for filepath in args.files:
            if filepath == '-':
                read_stdin()
            with open(filepath) as f:
                # TODO: paginate
                pretty_json(json.load(f))


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        # TODO: paginate
        # when piping to `less` for example, this error is returned if exiting
        # and closing the output pipe before all text has been output.
        # if we process line by line, we can also avoid processing text that
        # we do not output
        pass