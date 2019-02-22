"""Generate Markdown Documentation from Pyton Docstring"""

# Inspired by https://niklasrosenstein.github.io/pydoc-markdown/
#
# TODO: Check file exists
# TODO: Add -o --output-dir
# TODO: Add function filter (regex?)

from __future__ import print_function
import argparse
import imp
import logging


class DocStringExtractor:
    """Extracts Doc String from functions for given python module"""

    def __init__(self, file=None):
        """Init DocStringExtractor"""
        self.module = None
        self.functions = {}
        if file:
            self.run(file)

    def run(self, file):
        """Perform all actions:
        - open python file as a module
        - extract Docstrings for functions
        - trim them
        - save Docstrings in separate .md files
        """
        self.open(file)
        self.extract()
        self.trim()
        self.save()

    def open(self, file):
        """Open python file as a module"""
        self.module = imp.load_source("module", file)

    def extract(self):
        """Extract Docstrings for functions"""
        for func in dir(self.module):
            if not func.startswith("__"):
                logging.debug("Function: %s", func)
                if hasattr(func, "__doc__"):
                    logging.debug("DocString:\n%s",
                                  getattr(self.module, func).__doc__)
                    self.functions[func] = getattr(self.module, func).__doc__

    def trim(self):
        """Trim Docstrings"""
        for func in self.functions:
            # Get lines as a list
            lines = self.functions[func].splitlines()
            # If there is more than 1 line and first line is empty
            if len(lines) > 1 and not lines[0]:
                # Remove first empty line
                lines.pop(0)
                # Get number of leading spaces
                spaces = len(lines[0]) - len(lines[0].lstrip(" "))
                # logging.debug("First line (%d): %s", spaces, lines[0])
                # Trim lines
                lines = [line[spaces:] for line in lines]
                # logging.debug("Trimmed:\n%s", lines)
                # Combine trimmed lines and put them back to dict
                self.functions[func] = "\n".join(lines)
        logging.debug("Result:\n%s", self.functions)

    def save(self, extension="md"):
        """Save Docstrings in separate documentation files"""
        for func in self.functions:
            # FIXME: use regex instead of replace?
            md_file_name = func.replace("_", "-") + "." + extension
            logging.debug("Markdown file: %s", md_file_name)
            with open(md_file_name, "w") as md_file:
                md_file.write(self.functions[func])


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="verbosity level, use: [-v | -vv | -vvv]")
    parser.add_argument("file",
                        help="input file name, must be python module")
    args = parser.parse_args()
    return args


def main():
    """Parse args then run DocStringExtractor"""
    args = parse_args()

    if args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG,
                            format="[%(levelname)s]: %(message)s")

    logging.debug("Args: %s", args)
    logging.debug("Input file: %s", args.file)

    try:
        DocStringExtractor(args.file)
        return True
    except Exception as error:
        color_red = "\033[91m"
        color_reset = "\033[0m"
        logging.exception("%s%s%s", color_red, error, color_reset)
        return False


if __name__ == "__main__":
    # NOTE: True(success) -> 0, False(fail) -> 1
    exit(not main())
