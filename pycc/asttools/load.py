"""Utilities for loading code files into AST objects."""

import ast
import os

from . import references


def load_ast(file_path):
    """Return an AST node for the given file path.

    The AST node is modified to contain parent and sibling references.
    """

    code = ""
    with open(file_path, 'r') as f:

        code = f.read()

    node = ast.parse(code, filename=file_path, mode='exec')
    references.add_parent_references(node)
    references.add_sibling_references(node)

    return node


class AstFile(object):
    """A container of AST nodes that contains useful metadata."""

    def __init__(self, file_path, python_path=None):

        self.file_path = file_path
        self.python_path = python_path
        self.node = load_ast(file_path)

    def __repr__(self):

        return '<AstFile {0} -- {1}>'.format(
            self.file_path,
            self.python_path,
        )


class AstFileCollection(list):
    """A list subclass specialized for AstFile objects."""

    def append(self, *args, **kwargs):
        """Append and item to the list.

        If the kwargs 'file_path' and 'python_path' are the only arguments
        present it will generate a new AstFile object and append it to the
        list. Otherwise it behaves identically to a standard list append.
        """

        if args:

            return super(AstFileCollection, self).append(*args, **kwargs)

        if 'file_path' in kwargs and 'python_path' in kwargs:

            return super(AstFileCollection, self).append(
                AstFile(
                    file_path=kwargs['file_path'],
                    python_path=kwargs['python_path']
                )
            )


def load_file(file_path, python_root=None):
    """Generate an AstFile object based on a given file path.

    If python root is given it will be used to determine the full python path
    for the file.
    """

    python_path = None
    if python_root is not None and python_root in file_path:

        python_path = os.path.join(
            python_root, file_path.split(python_root)[1],
        )

    return AstFile(
        file_path=file_path,
        python_path=python_path,
    )


def load_directory(directory='.'):
    """Generate an AstFileCollection based on directory contents.

    All subdirectories are searched when using this function.
    """

    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):

        raise ValueError('The given path must be a directory.')

    source_name = os.path.split(directory)[1]

    files = AstFileCollection()

    directories = [directory]
    while directories:

        current_directory = directories.pop()
        directories.extend(
            os.path.abspath(os.path.join(current_directory, d))
            for d in os.listdir(current_directory)
            if os.path.isdir(
                os.path.abspath(os.path.join(current_directory, d))
            )
        )

        files.extend(
            load_file(
                file_path=os.path.abspath(os.path.join(current_directory, f)),
                python_root=source_name,
            )
            for f in os.listdir(current_directory)
            if f.endswith('.py') and
            os.path.isfile(os.path.abspath(os.path.join(current_directory, f)))
        )

    return files
