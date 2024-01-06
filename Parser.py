import logging

from Formula import *


test_formula = '◇ ( ◇ p ∧ ◇ ¬ p )'
test_rpn = 'p ◇ p ¬ ◇ ∧ ◇'


# http://www.diag.uniroma1.it/liberato/ar/modal/logic.html
# all unary precedences are the same, then And > Or > -> > <->
def __precedence(operator: str) -> int:
    match operator:
        case "\u00AC" | "~":  # Not
            return 100
        case "\u2227" | "/\\" | "n":  # And
            return 65
        case "\u2228" | "\\/" | "v":  # Or
            return 60
        case "\u25FB" | "[]":  # Box
            return 100
        case "\u2192" | "->":  # Implication
            return 50
        case "\u21D4" | "<->":  # BiImplication
            return 40
        case "\u25C7" | "<>":  # Diamond
            return 100
        case "(":  # "(" doesn't really have a precedence, but this simplifies the shunting
            return 0


# https://en.wikipedia.org/wiki/Shunting_yard_algorithm to turn the input into RPN, for easier parsing
# splitting tokens on spaces seems reasonable
# this could directly generate a Formula, but readability would suffer, and an added linear component on parsing, will
# not hurt PSpace-complete runtime
def __shunt(formula: str) -> str:
    tokens = formula.strip().split()
    rpn: list[str] = []
    stack: list[str] = []  # python lists can be used as a stack

    for token in tokens:  # my proposed set of operator-tokens, first one is Unicode, the others are ASCII imitations
        match token:
            case "\u00AC" | "~":  # Not
                stack.append("\u00AC")  # highest precedence
            case "\u2227" | "/\\" | "n":  # And
                while len(stack) != 0 and __precedence(stack[-1]) >= 65:
                    rpn.append(stack.pop())
                stack.append("\u2227")
            case "\u2228" | "\\/" | "v":  # Or
                while len(stack) != 0 and __precedence(stack[-1]) >= 60:
                    rpn.append(stack.pop())
                stack.append("\u2228")
            case "\u25FB" | "[]":  # Box
                stack.append("\u25FB")  # highest precedence
            case "\u2192" | "->":  # Implication
                while len(stack) != 0 and __precedence(stack[-1]) > 50:  # Implication is right-associative
                    rpn.append(stack.pop())
                stack.append("\u2192")
            case "\u21D4" | "<->":  # BiImplication
                while len(stack) != 0 and __precedence(stack[-1]) >= 40:
                    rpn.append(stack.pop())
                stack.append("\u2228")
            case "\u25C7" | "<>":  # Diamond
                stack.append("\u25C7")  # highest precedence
            case "(":
                stack.append("(")
            case ")":
                try:
                    while stack[-1] != "(":  # push everything inside the brackets to the rpn
                        rpn.append(stack.pop())
                except IndexError:
                    logging.warning("Too many closing brackets. Will ignore this one.")
                else:
                    stack.pop()  # lastly remove "(" from the stack
            case atom:  # Atom
                rpn.append(atom)
    while len(stack) != 0:
        if stack[-1] == "(":
            logging.warning("A opening bracket never got closed. Closing implicitly at end of Formula")
            stack.pop()
        rpn.append(stack.pop())

    return ' '.join(rpn)


def __parse_rpn_formula(rpn: str) -> Formula:
    tokens = rpn.strip().split()
    f_stack: list[Formula] = []
    for token in tokens:  # my proposed set of operator-tokens, first one is Unicode, the others are ASCII imitations
        new: Formula
        match token:
            case "\u00AC" | "~":  # Not
                new = Not(f_stack.pop())
            case "\u2227" | "/\\" | "n":  # And
                right = f_stack.pop()
                left = f_stack.pop()
                new = And(left, right)
            case "\u2228" | "\\/" | "v":  # Or
                new = Or(f_stack.pop(), f_stack.pop())
            case "\u25FB" | "[]":  # Box
                new = Box(f_stack.pop())
            case "\u2192" | "->":  # Implication
                right = f_stack.pop()
                left = f_stack.pop()
                new = Implication(left, right)
            case "\u21D4" | "<->":  # BiImplication
                right = f_stack.pop()
                left = f_stack.pop()
                new = BiImplication(left, right)
            case "\u25C7" | "<>":  # Diamond
                new = Diamond(f_stack.pop())
            case atom_name:  # Atom
                new = Atom(atom_name)
        f_stack.append(new)
    if len(f_stack) > 1:
        logging.error("Input contained a not closed formula")
    return f_stack.pop()


def parse_formula_str(formula: str) -> Formula:
    return __parse_rpn_formula(__shunt(formula))


def parse_label_str(source: str) -> set[Formula]:
    formulae = source.split(",")
    return {parse_formula_str(formula) for formula in formulae}


def parse_file(file_adr: str) -> list[set[Formula]]:
    with open(file_adr, encoding="utf-8") as f:
        file = f.read().splitlines()
    return [parse_label_str(label) for label in file]


if __name__ == '__main__':
    parse_file("Input.txt")

