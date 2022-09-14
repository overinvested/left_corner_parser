# Left Corner Parser

## Description

Where a top-down parse wastes time on trees that don't match the input, and a bottom-up parse wastes time on trees that don't have S as a root, left-corner parsing can combine the two techniques to minimize wasted time.

The key idea is that if we have knowledge of the categories our words can belong to and we search only trees with a root of S that place the words in those categories, then we will be able to find the correct structure(s) that will fill in the tree.

The left corner of a production rule is the first symbol of the right-hand side. By requiring that the category we are trying to recognize is a left corner of an upper portion of the tree that we have already observed, we eliminate many subtrees that could not possibly be correct. The goal is to bridge the gap between the symbols we recognize in the bottom-up portion with the symbols we predict in the top-down portion.

The left-corner parse is performed using a classical backtracking search. States are expanded then searched through depth-first, backtracking when necessary.

Based on grammar from Jurafsky and Martin Ch. 13 - recursive rules removed
