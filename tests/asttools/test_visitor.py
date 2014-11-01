"""Test suite for asttools.visitor."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ast
import functools
import timeit
import os

import pytest

from pycc.asttools import parse
from pycc.asttools import visitor


@pytest.fixture
def big_ast():
    """Generate a large AST."""
    # Trickery to get the path of a near-by file.
    file_path = os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
        ),
        'test_name.py',
    )

    with open(file_path, 'r') as source_file:

        node = parse.parse(source_file.read())

    # Duplicate the body several times.
    for x in range(5):

        node.body.extend(node.body)

    return node


def test_visitor_out_performs_original(big_ast):
    """Ensure the non-recursive implementation is at least 2x faster."""
    samples = 100

    original_visitor = ast.NodeVisitor()
    original_time = timeit.timeit(
        functools.partial(
            original_visitor.visit,
            big_ast,
        ),
        number=samples,
    )

    custom_visitor = visitor.NodeVisitor(big_ast)
    custom_time = timeit.timeit(
        custom_visitor.visit,
        number=samples,
    )

    avg_time = (original_time + custom_time) / 2
    diff_time = original_time - custom_time
    pct_diff = (diff_time / avg_time) * 100

    assert pct_diff > 100
