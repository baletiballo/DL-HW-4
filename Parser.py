from Formula import *


# https://en.wikipedia.org/wiki/Shunting_yard_algorithm to turn the input into RPN, for easier parsing
# splitting tokens on spaces seems reasonable
def shunt(formula: str) -> str:
    tokens = formula.split(" ")

    rpn = [token for token in tokens]  # TODO actually do shunting

    return ' '.join(rpn)


def parse_rpn_formula(rpn: str) -> Formula:
    pass


def parse_input(source: str) -> set[Formula]:
    formulae = source.split(",")
    return {parse_rpn_formula(shunt(formula)) for formula in formulae}
