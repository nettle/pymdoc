"""Generate Markdown Documentation from Python Docstring"""

from __future__ import print_function
import argparse
import ast
import logging
import os

import codegen   # SourceGenerator generates source code from AST


class Error(Exception):
    """Known errors"""
    pass


class SignaturGenerator(codegen.SourceGenerator):
    """Overwrites SourceGenerator to produce Bazel-like function signature"""
    def signature(self, node):
        self.newline()
        self.write(self.indent_with)
        want_comma = []

        def write_comma():
            """Write comma after every argument if needed"""
            if want_comma:
                self.write(",")
                self.newline()
                self.write(self.indent_with)
            else:
                want_comma.append(True)

        padding = [None] * (len(node.args) - len(node.defaults))
        for arg, default in zip(node.args, padding + node.defaults):
            write_comma()
            self.visit(arg)
            if default is not None:
                self.write("=")
                self.visit(default)
        if node.vararg is not None:
            write_comma()
            self.write("*" + node.vararg)
        if node.kwarg is not None:
            write_comma()
            self.write("**" + node.kwarg)

    def visit_FunctionDef(self, node):
        self.newline(extra=1)
        self.decorators(node)
        self.newline(node)
        self.write("%s(" % node.name)
        self.visit(node.args)
        self.newline()
        self.write(")")


class DocstringExtractor(object):
    """
    Extracts docstring from functions and after variables
    for given python file
    """

    def __init__(self, filename=None, output_file=None, output_path=None):
        """Init instance"""
        self.items = []
        self.module_docstring = None
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
        if not os.path.isfile(filename):
            raise Error("File '{}' does not exists".format(filename))
        content = open(filename).read()
        tree = ast.parse(content)
        logging.debug("AST:\n%s\n\n", ast.dump(tree))

        assignment = False
        first = False
        for node in ast.walk(tree):
            logging.debug("AST: node=%s", node)
            if isinstance(node, ast.Module):
                first = True
                continue
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    generator = SignaturGenerator(" " * 4, False)
                    generator.visit(node)
                    code = "".join(generator.result)
                    code = code.replace("'", '"')
                    code = "```python\n" + code + "\n```"
                    logging.debug("CODE:\n%s", code)
                self.items.append((node.name, docstring, code))
                assignment = False
            elif isinstance(node, ast.Assign):
                assignment = node.targets[0].id
            elif isinstance(node, ast.Expr):
                if hasattr(node.value, "s"):
                    docstring = node.value.s
                else:
                    docstring = None
                if first and docstring:
                    self.module_docstring = docstring
                if assignment and docstring:
                    self.items.append((assignment, docstring))
                assignment = False
            else:
                assignment = False
            first = False

    def print(self):
        """Print out result to console"""
        def title(text):
            """"Prints out title"""
            print(":" * 60)
            print(":::", text)
            print(":" * 60)

        def content(text):
            """"Prints out content"""
            if text:
                print(text)
                print()

        if self.module_docstring:
            title("Module DocString")
            content(self.module_docstring)
        for item in self.items:
            title(item[0])
            if len(item) > 2:
                content(item[2])
            content(item[1])

    def save_to_path(self, output_path, extension="md",
                     name_replace={"_": "-"}):
        """Save Docstrings in separate documentation files"""
        if not os.path.isdir(output_path):
            raise Error("Directory '{}' does not exists".format(output_path))
        for item in self.items:
            name = item[0]
            for source in name_replace:
                name = name.replace(source, name_replace[source])
            md_file_name = name + "." + extension
            md_file_path = os.path.join(output_path, md_file_name)
            logging.debug("Markdown file: %s", md_file_path)
            with open(md_file_path, "w") as md_file:
                if len(item) > 2:
                    md_file.write(item[2])
                    md_file.write("\n\n")
                md_file.write(item[1])

    def save_to_file(self, output_file):
        """Save Docstrings in separate documentation files"""
        def write(file_handler, text):
            """Writes text to file with ending linefeeds"""
            if text:
                file_handler.write(text)
                # file_handler.write("\n")
                if not text.count("\n"):
                    file_handler.write("\n")
        with open(output_file, "w") as file_handler:
            if self.module_docstring:
                write(file_handler, self.module_docstring)
            for item in self.items:
                if len(item) > 2:
                    write(file_handler, item[2])
                    file_handler.write("\n\n")
                write(file_handler, item[1])


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
    """Parse args then run DocstringExtractor"""
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
        DocstringExtractor(args.file, args.output_file, args.output_path)
        return True
    except Error as error:
        logging.error("%s%s%s", color_red, error, color_reset)
    except Exception as error:  # pylint: disable=broad-except
        logging.exception("%s%s%s", color_red, error, color_reset)
    return False


if __name__ == "__main__":
    # NOTE: True(success) -> 0, False(fail) -> 1
    exit(not main())
