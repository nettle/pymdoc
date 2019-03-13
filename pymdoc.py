"""Generate Markdown Documentation from Python Docstring"""

# Inspired by https://niklasrosenstein.github.io/pydoc-markdown/
#
# TODO: Check input file exists?
# TODO: Add function filter (regex?)

from __future__ import print_function
import argparse
import ast
import logging
import os


class DocumentationExtractor(object):
    """Extracts Doc String from functions for given python file"""

    def __init__(self, filename=None, output_file=None, output_path=None):
        """Init instance"""
        self.items = []
        if filename:
            self.run(filename, output_file, output_path)

    def run(self, filename, output_file=None, output_path=None):
        """Perform all actions:
        - open python file as an AST
        - extract Docstrings for functions and assignments
        - trim them
        - save Docstrings in separate .md files
        """
        self.extract(filename)
        if output_file:
            self.save_to_file(output_file)
        elif output_path:
            self.save_to_path(output_path)
        else:
            self.print()

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

    def print(self):
        """Print out result to console"""
        for item in self.items:
            print(":" * 60)
            print(":::", item[0])
            print(":" * 60)
            print(item[1])

    def save_to_path(self, output_path, extension="md"):
        """Save Docstrings in separate documentation files"""
        # FIXME: check if output_path exists
        for item in self.items:
            # FIXME: use regex instead of replace?
            md_file_name = item[0].replace("_", "-") + "." + extension
            # FIXME: get absolute path?
            md_file_path = os.path.join(output_path, md_file_name)
            logging.debug("Markdown file: %s", md_file_path)
            with open(md_file_path, "w") as md_file:
                md_file.write(item[1])

    def save_to_file(self, output_file):
        """Save Docstrings in separate documentation files"""
        with open(output_file, "w") as file_handler:
            for item in self.items:
                file_handler.write(item[1])
                file_handler.write("\n")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="verbosity level, use: [-v | -vv | -vvv]")
    parser.add_argument("-p", "--output-path",
                        help="save generated files in specified folder")
    parser.add_argument("-o", "--output-file",
                        help="save everything to specified file")
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
    else:
        logging.basicConfig(format="%(levelname)s:   %(message)s")

    logging.debug("Args: %s", args)
    logging.debug("Input file: %s", args.file)
    logging.debug("Output file: %s", args.output_file)
    logging.debug("Output path: %s", args.output_path)

    color_red = "\033[91m"
    color_reset = "\033[0m"
    try:
        DocumentationExtractor(args.file, args.output_file, args.output_path)
        return True
    except IOError as error:
        logging.error("%s%s%s", color_red, error, color_reset)
    except Exception as error:  # pylint: disable=broad-except
        logging.exception("%s%s%s", color_red, error, color_reset)
    return False


if __name__ == "__main__":
    # NOTE: True(success) -> 0, False(fail) -> 1
    exit(not main())
