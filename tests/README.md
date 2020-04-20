## Test Files

This directory contains test files that you can test against and study to become familiar with filterCSV:

* **test1.csv** is a simple CSV file in a format that can be imported into iThoughts.
* **test2.md** is a simple nested-list Markdown file. Here indentation level is denoted by two spaces for the first level, and so on.
* **mdtest3.csv** is a file with 5 levels of nodes, designed to test Markdown export.
* **badlevels.csv** contains a level error - for use with `check`.

There is also an **expected** that is used by pytest to ensure that our file tests generate the correct output to stdout and stderr.
