# Overview

This repository contains a implementation of a toy programming language based on the specifications outlined in the book "Compiling to Assembly from Scratch" by Aleksey Keleshev. The language is designed to generate assembly code targeting the arm32 architecture.
# Features
- LL(1) Parsing: The implementation employs a variant of LL(1) parsing, enhancing the efficiency and reliability of the parsing process.
- Regular Expression-based Lexer: A makeshift Lexer is utilized, driven by Regular Expressions, to tokenize the input source code effectively.
- Assembly Code Generation: The generated code is targeted for the arm32 architecture, providing a practical demonstration of the compilation process.
- Support for Recursion and Loops: The toy language supports fundamental programming constructs such as recursion and loops, allowing for the creation of more complex algorithms.

# Usage
  `python main.py <file_path_to_generate_asm>` for example `python main.py sample.txt`

# To-Do List
Implementation of greater than and less than operators, array support and Basic Code Optimization.