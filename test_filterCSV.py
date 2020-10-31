#!/usr/bin/env python3

# To make it easy to import ../filterCSV even though it has no .py extension, we did:
# ln -s ./filterCSV filterCSV.py  # make a symlink from ./filterCSV to ./filterCSV.py

import os
import string
import subprocess

import pytest

from . import filterCSV

data_fields = ("shape", "colour", "note", "level", "position", "cell")


def test_CSVTree():
    csv_tree = filterCSV.CSVTree(*data_fields)
    assert csv_tree.childNodes == []
    for field in data_fields:
        assert csv_tree.data[field] == field
    assert csv_tree.parent is None
    assert csv_tree.matched is False


def test_CSVTree_add_get_delete():
    csv_tree = filterCSV.CSVTree(*data_fields)
    child = filterCSV.CSVTree(*["child"] * 6)
    csv_tree.addChild(child)
    assert len(csv_tree.childNodes) == 1
    assert child in csv_tree.getChildren()
    csv_tree.deleteChild(child)
    assert csv_tree.childNodes == []
    assert child not in csv_tree.getChildren()


def test_CSVTree_isMatch():
    csv_tree = filterCSV.CSVTree(*data_fields)
    for criterion in "shape ape colour col r note no cell ell".split():
        assert csv_tree.isMatch(criterion), criterion
    for criterion in "level position x X y Y z Z 1 2 3 4 5 6 7 8 9 0".split():
        assert not csv_tree.isMatch(criterion), criterion


expected = (
    "shape      colour     note       0          position   cell",
    "  child      child      child      1          child      child",
    "      grandchild grandchild grandchild 3          grandchild grandchild",
)


def test_CSVTree_dump():
    csv_tree = filterCSV.CSVTree(*data_fields)
    csv_tree.data["level"] = 0
    actual = csv_tree.dump()
    assert expected[0] in actual, (expected[0] in actual)
    child = filterCSV.CSVTree(*["child"] * 6)
    child.data["level"] = 1
    csv_tree.addChild(child)
    actual = csv_tree.dump()
    assert "\n".join(expected[0:1]) in actual, ("\n".join(expected[0:1]) in actual)
    child.addChild(filterCSV.CSVTree(*["grandchild"] * 6)).data["level"] = 3
    actual = csv_tree.dump()
    assert "\n".join(expected) in actual, ("\n".join(expected) in actual)


def test_calculateMaximumLevel():
    csv_tree = filterCSV.CSVTree(*data_fields)
    csv_tree.data["level"] = 1  # test as int
    assert csv_tree.calculateMaximumLevel() == 1
    csv_tree.data["level"] = "0"  # test as str
    assert csv_tree.calculateMaximumLevel() == 0
    # make a child
    child = filterCSV.CSVTree(*["child"] * 6)
    child.data["level"] = "2"
    csv_tree.addChild(child)
    assert csv_tree.calculateMaximumLevel() == 2
    # make a grandchild
    grandchild = filterCSV.CSVTree(*["grandchild"] * 6)
    grandchild.data["level"] = "4"  # test as str
    child.addChild(grandchild)
    assert csv_tree.calculateMaximumLevel() == 4
    assert child.calculateMaximumLevel() == 4
    assert grandchild.calculateMaximumLevel() == 4
    grandchild.data["level"] = 5  # test as int
    assert csv_tree.calculateMaximumLevel() == 5
    csv_tree.deleteChild(child)
    assert csv_tree.calculateMaximumLevel() == 0


def test_writeCSVTree():
    outputArray = ["a", "b", "c"]
    csv_tree = filterCSV.CSVTree(*data_fields)
    csv_tree.data["level"] = 1
    assert csv_tree.writeCSVTree(outputArray) == ['a', 'b', 'c',
        ['colour', 'note', 'position', 'shape', 1, '', 'cell']  # noqa: E128
    ]
    csv_tree.data["level"] = 0
    assert csv_tree.writeCSVTree(outputArray) == ['a', 'b', 'c',
        ['colour', 'note', 'position', 'shape', 1, '', 'cell'],  # noqa: E128
        ['colour', 'note', 'position', 'shape', 0, 'cell']
    ]
    csv_tree.data["level"] = -1
    assert csv_tree.writeCSVTree(outputArray) == ['a', 'b', 'c',
        ['colour', 'note', 'position', 'shape', 1, '', 'cell'],  # noqa: E128
        ['colour', 'note', 'position', 'shape', 0, 'cell']
    ]


testdata = {
    " \t \t \t": "<space><tab><space><tab><space><tab>",
    "a  b \tc\t\td": "<tab><space><space><tab><space><tab><tab><tab><tab><tab>",
    " filterCSV ": "<space><tab><tab><tab><tab><tab><tab><tab><tab><tab><space>",
}


@pytest.mark.parametrize("whitespace,expected", testdata.items())
def test_formatWhitespaceCharacters(whitespace, expected):
    assert filterCSV.formatWhitespaceCharacters(whitespace) == expected


def test_no_spaces(
    whitespace=string.ascii_letters + string.digits + string.punctuation
):
    s = filterCSV.formatWhitespaceCharacters(whitespace)
    assert "s" not in s
    assert "p" not in s
    # "a" is in both <space> and <tab>
    assert "c" not in s
    assert "e" not in s


# cat tests/badLevels.csv | ./filterCSV check repairsubtree
# cat tests/test1.csv     | ./filterCSV '^A1$' '3 note'
testdata = {
    "check repairsubtree": "tests/badLevels.csv",
    "^A1$ 3_note": "tests/test1.csv",
    "": "tests/test2.md",
    "markdown 2_3": "tests/mdTest3.csv",
    "xml freemind": "tests/mdTest3.csv",
    "A2A|X keep": "tests/test1.csv",
    # "promote 2": "tests/promotion.csv",
}


@pytest.mark.parametrize("args,stdin_file", testdata.items())
def test_file_processing(args, stdin_file):
    args = args.split()
    dirname, basename = os.path.split(stdin_file)
    file_base = os.path.join(dirname, "expected", "_".join(args + [basename.replace(".", "_")]).replace("^", "").replace("$", "").replace("|", ""))
    # tests/expected/check_repairsubtree_badLevels_csv
    # tests/expected/A2AX_keep_test1_csv

    args = [arg.replace("_", " ") for arg in ["./filterCSV"] + args]
    with open(stdin_file) as in_file:
        cp = subprocess.run(args, capture_output=True, text=True, stdin=in_file)
    assert cp.returncode == 0, cp

    with open(f"{file_base}_err.txt") as in_file:
        expected_err = in_file.read().strip()
    for line in expected_err.splitlines():
        assert line in cp.stderr, f"\n{line}\n***is not in***\n{cp.stderr}"
    assert expected_err in cp.stderr, f"{expected_err}\n***is not in***\n{cp.stderr}"

    with open(f"{file_base}_out.txt") as in_file:
        expected_out = in_file.read().strip()
    for line in expected_out.splitlines():
        assert line in cp.stdout, f"\n{line}\n***is not in***\n{cp.stdout}"
    assert expected_out in cp.stdout, f"{expected_out}\n***is not in***\n{cp.stdout}"


if __name__ == "__main__":
    import doctest

    doctest.testmod()
