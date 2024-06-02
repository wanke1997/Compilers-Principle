# Compilers Principles Project

## Introduction
Welcome to the Compilers Principles Project! This project is based on the project instruction of Compilers Principle of Beijing Jiaotong University (BJTU) 2019 Spring Semester. I rewrite all five projects in 2024 with better code quality. For more details, please refer to the instruction document (in Chinese) in the repository. At that time I was instructed by Mr. Jin'an Xu, the professor of Computer Science and Technology Department of Beijing Jiaotong University. I deeply appreciate and am grateful for his instructions!

This project is an exploration of fundamental concepts in compilers using Python. Here, we delve into the intricate world of lexing, parsing, semantic analysis, code generation, and optimization.

In this repository, you'll find a series of Python scripts and programs that demonstrate various aspects of compiler design and implementation. Whether you're a student studying compilers or a curious coder looking to understand how programming languages work under the hood, this project aims to provide insight and practical knowledge.

## Project Structure
The project is divided into five sub-projects, each focusing on a specific parsing technique:

1. **String Parser**: This sub-project contains scripts for tokenizing and parsing strings using basic parsing techniques.

2. **Recursive Descent Parser**: Here, you'll find implementations of recursive descent parsers, a top-down parsing technique where each non-terminal in the grammar corresponds to a function.

3. **LL(1) Parser**: This module includes scripts for LL(1) parsing, a predictive parsing technique that parses the input from left to right, constructs a leftmost derivation, and leftmost derivation without backtracking.

4. **Operator-Precedence Parser**: In this section, you'll explore operator-precedence parsing, a method for parsing expressions without using recursive descent or explicit parse tables.

5. **SLR(1) Parser**: Here, you'll find scripts for SLR(1) parsing, a table-driven parsing method that uses a lookahead of one symbol to parse a string.

For more details on each sub-project, please refer to the README.md file in their respective directories.
