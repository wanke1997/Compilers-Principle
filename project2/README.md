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


## First and Follow Sets

### First Set

The First set of a non-terminal is the set of terminals that begin the strings derivable from the non-terminal. To compute the First set:

1. **Initialization**:
    - For each terminal `t`, `FIRST(t) = { t }`.
    - For each non-terminal `N`, initialize `FIRST(N) = {}`.
2. **Rules Application**:
    - For each production `A -> α`:
        - If `α` is a terminal, add `α` to `FIRST(A)`.
        - If `α` is a non-terminal `B`, add `FIRST(B)` to `FIRST(A)`.
        - If `α` is a sequence of symbols `X1 X2 ... Xn`, add `FIRST(X1)` to `FIRST(A)`.
        - If `ε` (the empty string) can be derived from `X1`, add `FIRST(X2)` to `FIRST(A)`, and so on.
    - Repeat until no more changes occur.

### Follow Set

The Follow set of a non-terminal is the set of terminals that can appear immediately to the right of the non-terminal in some "sentential" form. To compute the Follow set:

1. **Initialization**:
    - For the start symbol `S`, add `$` (end of input marker) to `FOLLOW(S)`.
    - For each non-terminal `N`, initialize `FOLLOW(N) = {}`.
2. **Rules Application**:
    - For each production `A -> αBβ`:
        - Add `FIRST(β) - {ε}` to `FOLLOW(B)`.
        - If `β` is ε or `β` can derive ε, add `FOLLOW(A)` to `FOLLOW(B)`.
    - Repeat until no more changes occur.

## Parsing Functions

Each non-terminal in the grammar has a corresponding parsing function. The function tries to match the input tokens against the grammar rules for that non-terminal.

### Parsing Function Structure

1. **Match Function**:
    - The `match` function checks if the current input token matches the expected token and advances to the next token.
    ```python
    def match(expected_token):
        global current_token
        if current_token == expected_token:
            current_token = next_token()  # Advance to the next token
        else:
            syntax_error()
    ```

2. **Syntax Error Handling**:
    - The `syntax_error` function is called when the input does not match the expected grammar.
    ```python
    def syntax_error():
        raise Exception("Syntax error")
    ```

3. **Non-terminal Functions**:
    - Each non-terminal in the grammar has a corresponding function that implements the production rules for that non-terminal. For example, for a non-terminal `E`:
    ```python
    def parse_E():
        parse_T()
        parse_E_prime()
    ```

## Parsing Process

The overall parsing process involves initializing the input, setting the current token, and calling the parsing function for the start symbol.

1. **Initialization**:
    - Set `current_token` to the first token of input.

2. **Start Parsing**:
    - Call the parsing function for the start symbol (e.g., `parse_E()`).

3. **Completion**:
    - If the parsing function for the start symbol completes and the current token is the end-of-input marker `$`, the input is successfully parsed.
    - Otherwise, report a syntax error.

By following these steps, a recursive descent parser can be implemented to parse a given input string according to a specific grammar.

## Bouns
This project we added a cache to store the states visited substrings. When a substring is visited and it is correct, then we added it to cache. Next time when the parser revisits this
string, it will no longer take time to parse it, instead it will return the resule immediately. 
This will save a lot of time. 