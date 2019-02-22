"""Generate Markdown Documentation from Pyton Docstring

Inspired by https://niklasrosenstein.github.io/pydoc-markdown/

TODO: Add doc strings :)
TODO: Check file exists
TODO: Add -o --output-dir
TODO: Add function filter (regex?)
"""

from __future__ import print_function
import argparse
import imp
import logging


class DocStringExtractor:
    """Extracts Doc String from functions for given python module"""
    def __init__(self, file=None):
        """FIXME"""
        self.module = None
        self.functions = {}
        if file:
            self.open(file)
            self.extract()

    def open(self, file):
        """FIXME"""
        self.module = imp.load_source("module", file)

    def extract(self):
        """FIXME"""
        for func in dir(self.module):
            if not func.startswith("__"):
                logging.debug("Function: %s", func)
                if hasattr(func, "__doc__"):
                    logging.debug("DocString:\n%s",
                                  getattr(self.module, func).__doc__)
                    self.functions[func] = getattr(self.module, func).__doc__

    def trim(self):
        """FIXME"""
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

    def save(self):
        """FIXME"""
        for func in self.functions:
            md_file_name = func.replace("_", "-") + ".md"
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
    """Parse args, get module, go through module, extract doc strings"""
    args = parse_args()

    if args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG, format="DEBUG: %(message)s")

    logging.debug("Args: %s", args)
    logging.debug("Input file: %s", args.file)

    extractor = DocStringExtractor()
    extractor.open(args.file)
    extractor.extract()
    extractor.trim()
    extractor.save()
    # logging.debug("Functions: %s", extractor.functions)
    return True


if __name__ == "__main__":
    # NOTE: True(success) -> 0, False(fail) -> 1
    exit(not main())
