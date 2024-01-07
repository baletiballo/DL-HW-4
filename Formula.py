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
        self.sub_formulae = []
        self.applicable_tableaux_rule = None
        self.size = 1
        self.str = ""

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
        return self.str  # computing str bottom up prevents recursion. May take some memory though


class Atom(Formula):
    def __init__(self, name:str):
        super().__init__()
        self.name = name
        self.str = self.name

    # def __str__(self):
    #     return self.name


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
        self.str = f"\u00AC {self.sub_formulae[0]!s}"

    def normal_form(self):  # remove double negation at parse-time
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        # self.str = f"\u00AC {self.sub_formulae[0]!s}"  no need to update str, we return a new object anyway
        if isinstance(self.sub_formulae[0], Not):
            return self.sub_formulae[0].sub_formulae[0]  # this has already been normalized
        else:  # normal form may create instances of "NotAnd" or "NotBox" rules, creating a new object detects that
            return Not(self.sub_formulae[0])

    # def __str__(self):
    #     return f"\u00AC {self.sub_formulae[0]!s}"


class And(Formula):
    def __init__(self, conj_1: Formula, conj_2: Formula):
        super().__init__()
        self.sub_formulae = [conj_1, conj_2]
        self.applicable_tableaux_rule = "And"
        self.str = f"( {self.sub_formulae[0]!s} \u2227 {self.sub_formulae[1]!s} )"

    def normal_form(self):  # remove double negation at parse-time
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        self.sub_formulae[1] = self.sub_formulae[1].normal_form()
        self.str = f"( {self.sub_formulae[0]!s} \u2227 {self.sub_formulae[1]!s} )"  # update str
        return self

    # def __str__(self):
    #     return f"( {self.sub_formulae[0]!s} \u2227 {self.sub_formulae[1]!s} )"


class Box(Formula):
    def __init__(self, boxed: Formula):
        super().__init__()
        self.sub_formulae = [boxed]
        self.applicable_tableaux_rule = None
        self.str = f"\u25FB {self.sub_formulae[0]!s}"

    def normal_form(self):
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        self.str = f"\u25FB {self.sub_formulae[0]!s}"  # update str
        return self

    # def __str__(self):
    #     return f"\u25FB {self.sub_formulae[0]!s}"


class Or(Formula):
    def __init__(self, disj_1: Formula, disj_2: Formula):
        super().__init__()
        self.sub_formulae = [disj_1, disj_2]
        self.applicable_tableaux_rule = None
        self.str = f"{self.sub_formulae[0]!s} \u2228 {self.sub_formulae[1]!s}"

    def normal_form(self):  # A \/ B = ~(~A /\ ~B)
        return Not(And(Not(self.sub_formulae[0]), Not(self.sub_formulae[1]))).normal_form()

    # def __str__(self):
    #     return f"{self.sub_formulae[0]!s} \u2228 {self.sub_formulae[1]!s}"


class Implication(Formula):
    def __init__(self, premise: Formula, conclusion: Formula):
        super().__init__()
        self.sub_formulae = [premise, conclusion]
        self.applicable_tableaux_rule = None
        self.str = f"( {self.sub_formulae[0]!s} \u2192 {self.sub_formulae[1]!s} )"

    def normal_form(self):  # A -> B = ~A \/ B = ~(~(~A) /\ ~B = ~(A /\ ~B)
        return Not(And(self.sub_formulae[0], Not(self.sub_formulae[1]))).normal_form()

    # def __str__(self):
    #     return f"( {self.sub_formulae[0]!s} \u2192 {self.sub_formulae[1]!s} )"


class BiImplication(Formula):
    def __init__(self, eq_1: Formula, eq_2: Formula):
        super().__init__()
        self.sub_formulae = [eq_1, eq_2]
        self.applicable_tableaux_rule = None
        self.str = f"{self.sub_formulae[0]!s} \u21D4 {self.sub_formulae[1]!s}"

    def normal_form(self):  # A <-> B = A -> B /\ B -> A   see above
        return And(Not(And(self.sub_formulae[0], Not(self.sub_formulae[1]))),
                   Not(And(self.sub_formulae[1], Not(self.sub_formulae[0])))).normal_form()

    # def __str__(self):
    #     return f"{self.sub_formulae[0]!s} \u21D4 {self.sub_formulae[1]!s}"


class Diamond(Formula):
    def __init__(self, diamonded: Formula):
        super().__init__()
        self.sub_formulae = [diamonded]
        self.applicable_tableaux_rule = None
        self.str = f"\u25C7 {self.sub_formulae[0]!s}"

    def normal_form(self):  # <> A = ~[]~A
        return Not(Box(Not(self.sub_formulae[0]))).normal_form()

    # def __str__(self):
    #     return f"\u25C7 {self.sub_formulae[0]!s}"


class Top(Formula):
    def __str__(self):
        return "⊤"


class Bot(Formula):

    def normal_form(self):  # <> A = ~[]~A
        return Not(Top())

    def __str__(self):
        return "⊥"
