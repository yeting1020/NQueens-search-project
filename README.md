# NQueens-search-project
Course project for CMPUT366: N-Queens solver with search heuristics.

A Python implementation of the N-Queens problem as a Constraint Satisfaction Problem (CSP), benchmarking five solver configurations across board sizes from N = 4 to 28.

Usage
pip install matplotlib
pip install numpy
python main.py
Prints solving time, nodes expanded, and backtracks for each configuration, and saves comparison plots (log scale) to the current directory.

Conclusion:
This project demonstrates the significant impact of CSP heuristics on search performance. MRV is the single most effective enhancement, while LCV, backjumping, and forward checking provide improvements on some instances but do not consistently outperform MRV.
