# String Parser

This Python script converts an input string into a list of 2-element tuples based on specified rules.

## Tuple Generation Rules

The input string is parsed character by character, and each character is classified into one of the following categories:

1. **Spaces and Special Characters**: Spaces (' '), tabs ('\t'), and newlines ('\n'), along with various special characters such as arithmetic operators, parentheses, brackets, and curly braces, are each assigned a unique integer value.
   
2. **Digits**: Individual digits are treated as a single category and assigned a unique integer value.

3. **Reserved Words**: Reserved words, such as data types ('void', 'int', 'float', etc.), control flow keywords ('if', 'else', 'for', 'while', etc.), standard I/O functions ('printf', 'include', 'stdio.h'), are each assigned a unique integer value.

4. **General Variables**: Any string that does not fall into the above categories is considered a general variable name and is assigned a unique integer value.

The resulting list consists of tuples where each tuple contains an integer representing the category of the character or string, and the corresponding character or string itself.

## Usage

### Python Version

This script is compatible with Python 3.x.

### File Structure

The file structure is as follows:

.
├── input
│   └── test_case1.txt
└── parser.py

- `parser.py`: Contains the Python script for the string parser.
- `input`: Directory containing test input files.

### How to Run
1. Ensure you have Python 3.x installed on your system.

2. Clone or download the repository to your local machine.

3. Navigate to the directory containing the parser.py file.

4. Run the script using the following command:
```bash
python parser.py
```

## Example
```python
from parser import Parser

# Example input string
input_string = "int main() { return 0; }"

# Initialize parser with input file
parser = Parser(filepath="input/test_case1.txt")

# Parse input string
result = parser.parse()

# Display parsed result
print("Parsed Result:")
for item in result:
    print(item)
```