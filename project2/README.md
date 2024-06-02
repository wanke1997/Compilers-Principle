# Recursive Descent Parser

## Introduction

A recursive descent parser is a type of top-down parser that uses a set of recursive procedures to process the input. Each non-terminal in the grammar has a corresponding procedure that attempts to match the input string to the production rules of the non-terminal. This parser works for a subset of context-free grammars known as LL(k) grammars, where decisions are made using the next `k` tokens of lookahead.

## Grammar Requirements

To use a recursive descent parser, the grammar must be:

1. **Free from Left Recursion**: Left-recursive rules can cause infinite recursion in a recursive descent parser.
2. **Left Factored**: To ensure that parsing decisions can be made based on a single lookahead token.

### Eliminating Left Recursion

A left-recursive production like:
A -> Aα | β
can be rewritten as:
A -> βA'
A' -> αA' | ε


### Left Factoring

A production with common prefixes like:
A -> αβ | αγ
can be rewritten as:
A -> αA'
A' -> β | γ

## Parsing Process

1. **Lexical Analysis (Tokenization):** The input string is tokenized into individual tokens such as identifiers, operators, and parentheses.
2. **Syntactic Analysis (Parsing):** The tokenized input is parsed according to the grammar rules using recursive descent parsing.
3. **Semantic Analysis:** Once the parsing is complete, additional semantic checks or actions can be performed based on the parsed structure.

## Usage

### Prerequisites
- Python 3.x

### Installation
No installation is required. Simply clone the repository or copy the `recursive_parser.py` file into your project directory.

## File Structure

- `recursive_parser.py`: Contains the implementation of the recursive descent parser.
- `input/`: Directory containing test case files.

## Test Cases

Test cases are provided in the `input/` directory. Each test case file should contain a string representing an expression to be parsed by the parser.

## Bouns
This project we added a cache to store the states visited substrings. When a substring is visited and it is correct, then we added it to cache. Next time when the parser revisits this
string, it will no longer take time to parse it, instead it will return the resule immediately. 
This will save a lot of time. 

### Usage Example

```python
from pathlib import Path
from recursive_parser import RecursiveParser

# Initialize the parser
recursive_parser = RecursiveParser()

# Define the path to the test case file
testcase = "test_case1.txt"
filepath = Path(__file__).parent.resolve().joinpath("input").joinpath(testcase)

# Parse the input file
result = recursive_parser.A(filepath)

# Print the result
print("Result is {}.".format(result))
```