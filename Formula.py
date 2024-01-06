import Parser
"""
Formula is essentially an abstract superclass for the recursive syntax-tree (https://en.wikipedia.org/wiki/Parse_tree)
sub-formulae are the sub-formulae (duh) one for Not and Box; two for And
applicable_tableaux_rule gives easier access and will allow a match-case construct
size is the number of logical connectives in the formula. A crude heuristic which branch to choose first
normal_form removes double negations, as well as Diamond, or, -> and alike. Please use it before reasoning.

Formula implements:
__eq__   so comparisons with == (or "in") are possible
__str__  to print a canonical form (using unicode for the logical symbols)
__hash__ to allow sets of formulae

The available subclasses are:
Atom, Not, And, Box, Or, Implication, BiImplication, Diamond
They all take one or two Formulas as argument, depending on whether they are unary or binary.
Except for Atom, which takes a string as its name
"""


# The abstract superclass. Don't make an object of this type, use its subclasses
class Formula:
    def __init__(self):
        self.sub_formulae = None
        self.applicable_tableaux_rule = None
        self.size = 1

    def normal_form(self):
        return self

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return ""


class Atom(Formula):
    def __init__(self, name:str):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name


class Not(Formula):
    def __init__(self, neg: Formula):
        super().__init__()
        self.sub_formulae = [neg]
        if isinstance(neg, Not):
            self.applicable_tableaux_rule = "NotNot"
        elif isinstance(neg, And):
            self.applicable_tableaux_rule = "NotAnd"
        elif isinstance(neg, Box):
            self.applicable_tableaux_rule = "NotBox"
        else:
            self.applicable_tableaux_rule = None

    def normal_form(self):  # remove double negation at parse-time
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        if isinstance(self.sub_formulae[0], Not):
            return self.sub_formulae[0].sub_formulae[0]  # this has already been normalized
        else:  # normal form may create instances of "NotAnd" or "NotBox" rules, creating a new object detects that
            return Not(self.sub_formulae[0])

    def __str__(self):
        return f"\u00AC {self.sub_formulae[0]!s}"


class And(Formula):
    def __init__(self, conj_1: Formula, conj_2: Formula):
        super().__init__()
        self.sub_formulae = [conj_1, conj_2]
        self.applicable_tableaux_rule = "And"

    def normal_form(self):  # remove double negation at parse-time
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        self.sub_formulae[1] = self.sub_formulae[1].normal_form()
        return self

    def __str__(self):
        return f"( {self.sub_formulae[0]!s} \u2227 {self.sub_formulae[1]!s} )"


class Box(Formula):
    def __init__(self, boxed: Formula):
        super().__init__()
        self.sub_formulae = [boxed]
        self.applicable_tableaux_rule = None

    def normal_form(self):
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        return self

    def __str__(self):
        return f"\u25FB {self.sub_formulae[0]!s}"


class Or(Formula):
    def __init__(self, disj_1: Formula, disj_2: Formula):
        super().__init__()
        self.sub_formulae = [disj_1, disj_2]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A \/ B = ~(~A /\ ~B)
        return Not(And(Not(self.sub_formulae[0]), Not(self.sub_formulae[1]))).normal_form()

    def __str__(self):
        return f"{self.sub_formulae[0]!s} \u2228 {self.sub_formulae[1]!s}"


class Implication(Formula):
    def __init__(self, premise: Formula, conclusion: Formula):
        super().__init__()
        self.sub_formulae = [premise, conclusion]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A -> B = ~A \/ B = ~(~(~A) /\ ~B = ~(A /\ ~B)
        return Not(And(self.sub_formulae[0], Not(self.sub_formulae[1]))).normal_form()

    def __str__(self):
        return f"( {self.sub_formulae[0]!s} \u2192 {self.sub_formulae[1]!s} )"


class BiImplication(Formula):
    def __init__(self, eq_1: Formula, eq_2: Formula):
        super().__init__()
        self.sub_formulae = [eq_1, eq_2]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A <-> B = A -> B /\ B -> A   see above
        return And(Not(And(self.sub_formulae[0], Not(self.sub_formulae[1]))),
                   Not(And(self.sub_formulae[1], Not(self.sub_formulae[0])))).normal_form()

    def __str__(self):
        return f"{self.sub_formulae[0]!s} \u21D4 {self.sub_formulae[1]!s}"


class Diamond(Formula):
    def __init__(self, diamonded: Formula):
        super().__init__()
        self.sub_formulae = [diamonded]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # <> A = ~[]~A
        return Not(Box(Not(self.sub_formulae[0]))).normal_form()

    def __str__(self):
        return f"\u25C7 {self.sub_formulae[0]!s}"


# return a formula of size 2n. Its tableau has n steps
def formula_of_size_2(n: int) -> Formula:
    f = "♢ " * n + "p"
    return Parser.parse_formula_str(f).normal_form()


# returns a formula with 2^(n+1)-1 symbols.
def exp_size_formula(n: int) -> Formula:
    if n == 0:
        return Atom("p")
    else:
        return And(exp_size_formula(n - 1), exp_size_formula(n - 1))


# returns the series of formulae, that don't have the polynomial model property
def exp_model_formula(n: int) -> Formula:
    return Parser.parse_formula_str(__em_formula_str(n))


# It is a lot easier to write the formula in string-format, then let the parser deal with it
def __em_formula_str(n: int) -> str:
    if n == 0:
        return "p0"
    else:
        n = n-1  # we return phi_{n+1}, reducing n now keeps the indices from the Ex. sheet
        phi_n = __em_formula_str(n)
        box_n = "□ " * n
        big_and = ""
        for j in range(1, n+1):
            big_and = big_and + f" ∧ ( ( q{j} → □ q{j} ) ∧ ( ¬ q{j} → □ ¬ q{j} ) ) ) ) "
        return f"{phi_n} ∧ { box_n } ( p{n} → ( ♢ ( p{n + 1} ∧ q{n + 1} ) ∧ ♢ ( p{n + 1} ∧ ¬ q{n + 1} ) {big_and}"
