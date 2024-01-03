from Formula import *
import Parser
"""
Since formulae are objects all splitting and reducing of them is just handling of pointers into the original formula
labels are sets of formulae and python has a built-in set, neat
"""

example_formula = Diamond(And(Diamond(Atom("p")), Diamond(Not(Atom("p"))))).normal_form()
example_label = {example_formula}  # Python built-in set
str(example_formula)


def successful(label):
    negated_formulae = [formula.sub_formulae[0] for formula in label if isinstance(formula, Not)]
    possible_rules = [formula.applicable_tableaux_rule for formula in label
                      if formula.applicable_tableaux_rule is not None]

    # check for clash
    for formula in negated_formulae:
        if formula in label:
            return False

    # check if label is saturated
    if not possible_rules:
        return True

    # recursive case
