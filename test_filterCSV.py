#!/usr/bin/env python3

# To make it easy to import ../filterCSV even though it has no .py extension, we did:
# ln -s ../filterCSV filterCSV.py  # make a symlink from ../filterCSV to ./filterCSV.py

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


def test_calculateMaximumLevel():
    csv_tree = filterCSV.CSVTree(*data_fields)
    csv_tree.data["level"] = 1
    assert csv_tree.calculateMaximumLevel() == 1
    csv_tree.data["level"] = 2
    assert csv_tree.calculateMaximumLevel() == 2
    child = filterCSV.CSVTree(*["child"] * 6)
    child.data["level"] = 4
    csv_tree.addChild(child)
    assert csv_tree.calculateMaximumLevel() == 4
    csv_tree.deleteChild(child)
    assert csv_tree.calculateMaximumLevel() == 2


def test_writeCSVTree():
    outputArray = ["a", "b", "c"]
    csv_tree = filterCSV.CSVTree(*data_fields)
    csv_tree.data["level"] = 1
    assert csv_tree.writeCSVTree(outputArray) == ['a', 'b', 'c',
        ['colour', 'note', 'position', 'shape', 1, '', 'cell']
    ]
    csv_tree.data["level"] = 0
    assert csv_tree.writeCSVTree(outputArray) == ['a', 'b', 'c',
        ['colour', 'note', 'position', 'shape', 1, '', 'cell'],
        ['colour', 'note', 'position', 'shape', 0, 'cell']
    ]
    csv_tree.data["level"] = -1
    assert csv_tree.writeCSVTree(outputArray) == ['a', 'b', 'c',
        ['colour', 'note', 'position', 'shape', 1, '', 'cell'],
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


def test_no_spaces(whitespace=string.ascii_letters+string.digits+string.punctuation):
    s = filterCSV.formatWhitespaceCharacters(whitespace)
    assert "s" not in s
    assert "p" not in s
    # "a" is in both <space> and <tab>
    assert "c" not in s
    assert "e" not in s


expected_err = """
Criterion                                Actions
---------                                -------
^A1$                                     3 note


3 FFFFB2
""".strip()

expected_out = """
"colour","note","position","shape","level","level0","level1","level2","level3","level4","level5","level6","level7","level8","level9","level10","level11","level12","level13","level14","level15","level16","level17","level18","level19","level20"
"","","","","0","A"
"FFFFB2","Matched ^A1$","","","1","","A1"
"","","","","1","","A2"
"","","","","2","","","A2A"
"","","","","3","","","","A2A1"
"","","","square","0","X"
""".strip()


# cat tests/badLevels.csv | ./filterCSV check repairsubtree
# cat tests/test1.csv     | ./filterCSV '^A1$' '3 note'
testdata = {
    "check repairsubtree": "tests/badLevels.csv",
    "^A1$ 3_note": "tests/test1.csv",
    "": "tests/test2.md",
    "markdown 2_3": "tests/mdTest3.csv",
    "xml freemind": "tests/mdTest3.csv",
    "A2A|X keep": "tests/test1.csv",
    "promote 2": "tests/promotion.csv",
}


@pytest.mark.parametrize("args,stdin_file", testdata.items())
def test_file_processing(args, stdin_file):
    dirname, basename = os.path.split(stdin_file)
    file_base = "_".join(args + [basename]).replace("|", "").replace(".", "_")
    expected_err = os.path.join(dirname, "expected", file_base) + "_err.txt"
    expected_out = os.path.join(dirname, "expected", file_base) + "_out.txt"
    assert False, expected_err
    """
    ="tests/test1.csv",
                         args=["./filterCSV", "^A1$", "3 note"],
                         expected_err=expected_err,
                        expected_out=expected_out):
    err_path = f"{stdin_path}
    with open(stdin_path) as in_file:
        # stdin = in_file.read()
        # stdout = None
        cp = subprocess.run(args, capture_output=True, text=True, stdin=in_file)
    assert cp.returncode == 0, cp
    assert cp.stderr, cp.stderr
    assert cp.stdout, cp.stdout
    assert expected_out in cp.stdout, f"{expected_out}\nis not in\n{cp.stdout}"
    """
    
