"""Generate Markdown Documentation from Python Docstring"""

# Inspired by https://niklasrosenstein.github.io/pydoc-markdown/
#
# TODO: Check file exists
# TODO: Add -o --output-file
# TODO: Add -p --output-path
# TODO: Add function filter (regex?)

from __future__ import print_function
import argparse
import ast
import logging


class DocumentationExtractor(object):
    """Extracts Doc String from functions for given python module"""

    def __init__(self, filename=None):
        """Init instance"""
        self.module = None
        self.items = []
        if filename:
            self.run(filename)

    def run(self, filename):
        """Perform all actions:
        - open python file as an AST
        - extract Docstrings for functions and assignments
        - trim them
        - save Docstrings in separate .md files
        """
        self.extract(filename)
        # self.save()

    def extract(self, filename):
        """Read python file and build an AST (Abstract Syntax Tree)
        then extract docstrings for functions (FunctionDef)
        and comments (Expr) which goes after assignments (Assign)"""
        content = open(filename).read()
        tree = ast.parse(content)
        # logging.debug("AST:\n%s", ast.dump(tree))

        assignment = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    self.items.append((node.name, docstring))
                assignment = False
            elif isinstance(node, ast.Assign):
                assignment = node.targets[0].id
            elif isinstance(node, ast.Expr):
                if hasattr(node.value, "s"):
                    docstring = node.value.s
                else:
                    docstring = None
                if assignment and docstring:
                    self.items.append((assignment, docstring))
                assignment = False
            else:
                assignment = False

        for item in self.items:
            logging.debug(":" * 60)
            logging.debug("::: %s", item[0])
            logging.debug(":" * 60 + "\n%s\n", item[1])

    def save(self, extension="md"):
        """Save Docstrings in separate documentation files"""
        for item in self.items:
            # FIXME: use regex instead of replace?
            md_file_name = item[0].replace("_", "-") + "." + extension
            logging.debug("Markdown file: %s", md_file_name)
            with open(md_file_name, "w") as md_file:
                md_file.write(item[1])


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
        DocumentationExtractor(args.file)
        return True
    except Exception as error:
        color_red = "\033[91m"
        color_reset = "\033[0m"
        logging.exception("%s%s%s", color_red, error, color_reset)
        return False


if __name__ == "__main__":
    # NOTE: True(success) -> 0, False(fail) -> 1
    exit(not main())
