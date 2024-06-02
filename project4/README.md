# Operator-Precedence Parser

## Introduction

An operator-precedence parser is a type of bottom-up parser for a subset of context-free grammars. It is particularly useful for parsing expressions involving binary operators, where the operators have precedence and associativity rules that govern the order of operations. This parser uses a precedence relation table to decide when to shift (read the next input symbol) or reduce (apply a production rule).

## Precedence Relations

The operator-precedence parser uses three types of precedence relations between grammar symbols (terminals and non-terminals):

1. **Less than ( < )**: Indicates that the symbol on the left has lower precedence than the symbol on the right.
2. **Equal to ( = )**: Indicates that the symbols have the same precedence, often used for operators of the same precedence level.
3. **Greater than ( > )**: Indicates that the symbol on the left has higher precedence than the symbol on the right.

### Constructing the Precedence Relation Table

1. **Identify all terminals and non-terminals** in the grammar.
2. **Define precedence and associativity** rules for each operator. Common rules include:
    - Multiplication (*) and division (/) have higher precedence than addition (+) and subtraction (-).
    - Operators of the same precedence level (e.g., + and -) are left-associative.
3. **Fill the precedence relation table** based on these rules:
    - Use the less-than (<), equal-to (=), and greater-than (>) relations to compare pairs of symbols.

## FirstVT and LastVT Sets

To construct the precedence relation table, we need to compute the FirstVT and LastVT sets for each non-terminal. These sets help in determining the precedence relations.

### FirstVT Set

The FirstVT set of a non-terminal symbol `A` is the set of terminals that appear first in any string derived from `A`.

1. **Initialization**:
    - For each non-terminal `A`, initialize `FirstVT(A) = {}`.
2. **Rules Application**:
    - For each production `A -> aα`, where `a` is a terminal:
        - Add `a` to `FirstVT(A)`.
    - For each production `A -> Bα`, where `B` is a non-terminal:
        - Add `FirstVT(B)` to `FirstVT(A)`.
    - For each production `A -> Ba`, where `B` is a non-terminal and `a` is a terminal:
        - Add `a` to `FirstVT(A)`.
    - Repeat until no more changes occur.

### LastVT Set

The LastVT set of a non-terminal symbol `A` is the set of terminals that appear last in any string derived from `A`.

1. **Initialization**:
    - For each non-terminal `A`, initialize `LastVT(A) = {}`.
2. **Rules Application**:
    - For each production `A -> αa`, where `a` is a terminal:
        - Add `a` to `LastVT(A)`.
    - For each production `A -> αB`, where `B` is a non-terminal:
        - Add `LastVT(B)` to `LastVT(A)`.
    - For each production `A -> aB`, where `a` is a terminal and `B` is a non-terminal:
        - Add `a` to `LastVT(A)`.
    - Repeat until no more changes occur.

## Parsing Process

The parsing process for an operator-precedence parser involves using a stack to hold symbols and a precedence relation table to guide parsing decisions. Here’s the step-by-step procedure:

1. **Initialization**:
    - Initialize the stack with the start symbol and the end marker `$`.
    - Read the first input symbol.

2. **Shift and Reduce Operations**:
    - **Shift**: Push the input symbol onto the stack and read the next input symbol.
    - **Reduce**: Apply a production rule to reduce a sequence of symbols on the stack to a non-terminal.

3. **Parsing Algorithm**:
    - Repeat until the stack contains only the start symbol and the end marker `$`, and the input is fully consumed:
        - Let `a` be the top symbol of the stack and `b` be the current input symbol.
        - Consult the precedence relation table for the relation between `a` and `b`.
        - If the relation is `<` or `=`, perform a shift operation.
        - If the relation is `>`, perform a reduce operation:
            - Find the rightmost handle (a sequence of symbols that matches the right-hand side of a production rule).
            - Replace the handle with the corresponding non-terminal.
        - If no valid relation exists, report an error.

4. **End of Input**:
    - If the stack is reduced to the start symbol and the input is fully consumed, the input string is successfully parsed.
    - Otherwise, report an error.

By following these algorithms and procedures, an operator-precedence parser can be constructed to parse expressions with defined precedence and associativity rules.
