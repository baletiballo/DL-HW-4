import logging

from Formula import *


test_formula = '◇ (◇ p ∧ ◇ ¬ p)'
test_rpn = 'p ◇ p ¬ ◇ ∧ ◇'


# https://en.wikipedia.org/wiki/Shunting_yard_algorithm to turn the input into RPN, for easier parsing
# splitting tokens on spaces seems reasonable
def shunt(formula: str) -> str:
    tokens = formula.strip().split(" ")

    for token in tokens:  # my proposed set of operator-tokens, first one is Unicode, the others are ASCII imitations
        match token:
            case "\u00AC" | "~":  # Not
                pass
            case "\u2227" | "/\\" | "n":  # And
                pass
            case "\u2228" | "\\/" | "v":  # Or
                pass
            case "\u25FB" | "[]":  # Box
                pass
            case "\u2192" | "->":  # Implication
                pass
            case "\u21D4" | "<->":  # BiImplication
                pass
            case "\u25C7" | "<>":  # Diamond
                pass
            case atom:  # Atom
                pass
    rpn = [token for token in tokens]  # TODO actually do shunting

    return ' '.join(rpn)


def parse_rpn_formula(rpn: str) -> Formula:
    tokens = rpn.strip().split(" ")
    f_stack: list[Formula] = []
    for token in tokens:  # my proposed set of operator-tokens, first one is Unicode, the others are ASCII imitations
        new: Formula
        match token:
            case "\u00AC" | "~":  # Not
                new = Not(f_stack.pop())
            case "\u2227" | "/\\" | "n":  # And
                new = And(f_stack.pop(), f_stack.pop())
            case "\u2228" | "\\/" | "v":  # Or
                new = Or(f_stack.pop(), f_stack.pop())
            case "\u25FB" | "[]":  # Box
                new = Box(f_stack.pop())
            case "\u2192" | "->":  # Implication
                new = Implication(f_stack.pop(), f_stack.pop())
            case "\u21D4" | "<->":  # BiImplication
                new = BiImplication(f_stack.pop(), f_stack.pop())
            case "\u25C7" | "<>":  # Diamond
                new = Diamond(f_stack.pop())
            case atom_name:  # Atom
                new = Atom(atom_name)
        f_stack.append(new)
    if len(f_stack) > 1:
        logging.error("Input contained a not closed formula")
    return f_stack.pop()


def parse_input(source: str) -> set[Formula]:
    formulae = source.split(",")
    return {parse_rpn_formula(shunt(formula)) for formula in formulae}

