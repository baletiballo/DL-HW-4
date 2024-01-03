import logging
from Formula import *
import Parser

"""
Since formulae are objects all splitting and reducing of them is just handling of pointers into the original formula
labels are sets of formulae and python has a built-in set, neat
"""

example_formula = Diamond(And(Diamond(Atom("p")), Diamond(Not(Atom("p"))))).normal_form()
example_label_1 = {example_formula}  # Python built-in set
example_label_2 = {Box(Implication(Atom("q").normal_form(),
                                   Diamond(Atom("p")))).normal_form(),
                   Diamond(Atom("q")).normal_form(),
                   Box(Box(Not(Atom("p")))).normal_form()
                   }
str(example_formula)


def show(label):
    s = "{  "
    for formula in label:
        s = s + formula.__str__() + ", "
    return s[:-2] + "  }"


def successful(label):
    logging.info(f"Starting with: {show(label)}")

    # check for clashes
    negated_formulae = [formula.sub_formulae[0] for formula in label if isinstance(formula, Not)]
    for formula in negated_formulae:
        if formula in label:
            logging.info(f"Clash on {formula} detected")
            return False

    # we have to check for saturation later, so doing it here would just be boilerplate

    # first apply all non-branching rules
    # we can do this in a loop, to avoid unnecessary recursive calls
    quick_rules = [formula for formula in label if formula.applicable_tableaux_rule == "NotNot" or
                   formula.applicable_tableaux_rule == "And"]
    while quick_rules:
        for formula in quick_rules:
            quick_rules.remove(formula)
            match formula.applicable_tableaux_rule:
                case "NotNot":
                    # accessing formulas two layers deep is not pretty. But I am not sure, if it can be done much better
                    new_formula = formula.sub_formulae[0].sub_formulae[0]
                    label.remove(formula)
                    label.add(new_formula)
                    if new_formula.applicable_tableaux_rule == "NotNot" or \
                            new_formula.applicable_tableaux_rule == "And":  # this may have added a new rule
                        quick_rules.append(new_formula)
                case "And":
                    label.remove(formula)
                    label = label.union(formula.sub_formulae)  # adds both sub formulae
                    # this may have added new rules, add them
                    if formula.sub_formulae[0].applicable_tableaux_rule == "NotNot" or \
                            formula.sub_formulae[0].applicable_tableaux_rule == "And":  # this may have added a new rule
                        quick_rules.append(formula.sub_formulae[0])
                    if formula.sub_formulae[1].applicable_tableaux_rule == "NotNot" or \
                            formula.sub_formulae[1].applicable_tableaux_rule == "And":  # this may have added a new rule
                        quick_rules.append(formula.sub_formulae[1])
    logging.debug(f"After all quick rules: {show(label)}")

    # We have to check for clashes again
    negated_formulae = [formula.sub_formulae[0] for formula in label if isinstance(formula, Not)]
    for formula in negated_formulae:
        if formula in label:
            logging.info(f"Clash on {formula} detected")
            return False

    # Check if label is saturated i.e. no rules are applicable
    possible_rules = [formula for formula in label if formula.applicable_tableaux_rule is not None]
    if not possible_rules:
        logging.info(f"Label is saturated")
        return True

    # we continue with or-branching, as we need to propositionally saturate the label
    or_branches = [formula for formula in label if formula.applicable_tableaux_rule == "NotAnd"]
    if or_branches:
        # as a crude heuristic we branch on the smallest formula first, hoping it succeeds (or clashes) quickly
        branch_formula = min(or_branches, key=lambda f: f.size)
        logging.info(f"Or-Branching on {branch_formula}")
        label.remove(branch_formula)
        branch_1 = label.copy()
        branch_1.add(Not(branch_formula.sub_formulae[0].sub_formulae[0]))
        logging.debug(f"Branch 1: {show(branch_1)}")
        branch_2 = label.copy()
        branch_2.add(Not(branch_formula.sub_formulae[0].sub_formulae[1]))
        logging.debug(f"Branch 2: {show(branch_2)}")
        return successful(branch_1) or successful(branch_2)
    logging.info(f"{show(label)} is propositionally saturated, And-Branching now")

    # finally the and-branching
    # first get all Not-Box formulae
    and_branches = [formula for formula in label if formula.applicable_tableaux_rule == "NotBox"]
    if not and_branches:  #
        logging.info(f"Label is saturated")
        return True
    # as a crude heuristic we branch on the smallest formula first, hoping it clashes (or succeeds) quickly
    and_branches.sort(key=lambda f: f.size)
    logging.debug(f"All branches: {[b.__str__() for b in  and_branches]}")
    # then remove all non-boxed formulae and unbox the boxed ones
    label = {formula.sub_formulae[0] for formula in label if isinstance(formula, Box)}
    logging.debug(f"\"Unboxed\" Label: {show(label)}")
    # now check for all branches, whether they are successful.
    # To try and save space on the heap we use a lazy generator. K being PSpace complete, this will not always work
    branches = (successful(label.copy().union({Not(formula.sub_formulae[0].sub_formulae[0])})) for formula in
                and_branches)
    return all(branches)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="reasoner.log", encoding='utf-8')
    if successful(example_label_2):
        print("Success")
    else:
        print("Fail")
