# SLR(1) Parser

## Introduction

An SLR(1) parser is a type of bottom-up parser used for a subset of context-free grammars. SLR stands for Simple LR, where "LR" indicates that the parser reads input from Left to right and produces a Rightmost derivation in reverse. The "(1)" signifies that the parser uses one lookahead symbol to make parsing decisions. SLR(1) parsers are more powerful than LL(1) parsers and can handle a larger class of grammars.

## First and Follow Sets

### First Set

The First set of a non-terminal symbol in a grammar is the set of terminals that begin the strings derivable from the non-terminal. To compute the First set, follow these steps:

1. **Initialization**:
    - For each terminal `t`, `FIRST(t) = { t }`.
    - For each non-terminal `N`, initialize `FIRST(N) = {}`.
2. **Rules Application**:
    - For each production `A -> α`:
        - If `α` is a terminal, add `α` to `FIRST(A)`.
        - If `α` is a non-terminal `B`, add `FIRST(B)` to `FIRST(A)`.
        - If `α` is a sequence of symbols `X1 X2 ... Xn`, add `FIRST(X1)` to `FIRST(A)`.
        - If `ε` (the empty string) can be derived from `X1`, then add `FIRST(X2)` to `FIRST(A)`, and so on.
    - Repeat until no more changes occur.

### Follow Set

The Follow set of a non-terminal symbol in a grammar is the set of terminals that can appear immediately to the right of the non-terminal in some "sentential" form. To compute the Follow set, follow these steps:

1. **Initialization**:
    - For the start symbol `S`, add `$` (end of input marker) to `FOLLOW(S)`.
    - For each non-terminal `N`, initialize `FOLLOW(N) = {}`.
2. **Rules Application**:
    - For each production `A -> αBβ`:
        - Add `FIRST(β) - {ε}` to `FOLLOW(B)`.
        - If `β` is ε or `β` can derive ε, add `FOLLOW(A)` to `FOLLOW(B)`.
    - Repeat until no more changes occur.

## Closure and GOTO Functions

### Closure

The closure of a set of items is computed to include all possible items that can be derived from the given items. The steps are:

1. **Initialization**:
    - Start with a set of items `I`.
2. **Rules Application**:
    - For each item `[A -> α.Bβ, a]` in `I` and each production `B -> γ` in the grammar:
        - Add the item `[B -> .γ, b]` to the closure set, where `b` is in `FIRST(βa)`.
    - Repeat until no more items can be added.

### GOTO

The GOTO function transitions from one set of items to another given a grammar symbol. The steps are:

1. **Initialization**:
    - Start with a set of items `I` and a grammar symbol `X`.
2. **Rules Application**:
    - For each item `[A -> α.Xβ, a]` in `I`, add `[A -> αX.β, a]` to the result set.
    - Compute the closure of the result set.

### Discovering New States and Establishing GOTO Relations

To discover new states and establish GOTO relations:

1. **Start State**:
    - Begin with the closure of the initial item `[S' -> .S, $]` where `S'` is the augmented start symbol.
    - This is the initial state, `I0`.
2. **State Construction**:
    - For each state `I` and each grammar symbol `X`, compute the GOTO(I, X):
        - If GOTO(I, X) produces a non-empty set of items, and this set of items is not already a state, it becomes a new state.
        - Record the GOTO transition from state `I` to the new state on symbol `X`.
    - Repeat until no new states are discovered.

## Constructing the DFA

To construct the DFA for the SLR(1) parser:

1. **Initialization**:
    - Start with the closure of the initial item `[S' -> .S, $]`.
2. **State Construction**:
    - Each state corresponds to a set of items.
    - For each state and each grammar symbol, apply the GOTO function to create new states.
    - Record these states and transitions until no new states can be added.

## Constructing the Action and GOTO Tables

1. **Action Table**:
    - For each state and each terminal symbol:
        - If the item is `[A -> α.aβ, b]`, the action is `shift` to the state given by `GOTO(state, a)`.
        - If the item is `[A -> α., a]`, the action is `reduce` by the production `A -> α`.
        - If the item is `[S' -> S., $]`, the action is `accept`.
2. **GOTO Table**:
    - For each state and each non-terminal symbol:
        - The entry is the state given by `GOTO(state, non-terminal)`.

## Parsing Process

The parsing process for an SLR(1) parser involves using the action and goto tables to guide the parsing decisions. Here’s the step-by-step procedure:

1. **Initialization**:
    - Initialize the stack with the start state and the end marker `$`.
    - Read the first input symbol.

2. **Parsing Algorithm**:
    - Repeat until the input is fully consumed or an error is detected:
        - Let `s` be the state on top of the stack and `a` be the current input symbol.
        - Consult the action table for the entry `ACTION[s, a]`:
            - If the action is `shift s'`, push `s'` onto the stack and read the next input symbol.
            - If the action is `reduce A -> β`, pop `|β|` symbols from the stack, and let `t` be the new top state. Push `GOTO[t, A]` onto the stack.
            - If the action is `accept`, the input is successfully parsed.
            - If the action is `error`, report a syntax error.
    - If the stack contains only the start state and the end marker `$`, and the input is fully consumed, the input string is successfully parsed.
    - Otherwise, report an error.

By following these algorithms and procedures, an SLR(1) parser can be constructed to parse a given input string according to a specific grammar.
