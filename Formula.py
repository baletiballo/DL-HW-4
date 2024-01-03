"""
Formula is essentially an abstract superclass for the recursive syntax-tree (https://en.wikipedia.org/wiki/Parse_tree)
sub-formulae are the sub-formulae (duh) one for Not and Box; two for And
applicable_tableaux_rule gives easier access and will allow a match-case construct
size is the number of logical connectives in the formula. A crude heuristic which branch to choose first
normal_form takes care of Diamond, or, -> and alike. Please use it after parsing formulae.

Formula implements __eq__ thus comparisons with == (or "in") are possible
"""
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
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name


class Not(Formula):
    def __init__(self, neg):
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
    def __init__(self, conj_1, conj_2):
        super().__init__()
        self.sub_formulae = [conj_1, conj_2]
        self.applicable_tableaux_rule = "And"

    def normal_form(self):  # remove double negation at parse-time
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        self.sub_formulae[1] = self.sub_formulae[1].normal_form()
        return self

    def __str__(self):
        return f"({self.sub_formulae[0]!s} \u2227 {self.sub_formulae[1]!s})"


class Box(Formula):
    def __init__(self, boxed):
        super().__init__()
        self.sub_formulae = [boxed]
        self.applicable_tableaux_rule = None

    def normal_form(self):
        self.sub_formulae[0] = self.sub_formulae[0].normal_form()
        return self

    def __str__(self):
        return f"\u25FB {self.sub_formulae[0]!s}"


class Or(Formula):
    def __init__(self, disj_1, disj_2):
        super().__init__()
        self.sub_formulae = [disj_1, disj_2]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A \/ B = ~(~A /\ ~B)
        return Not(And(Not(self.sub_formulae[0]), Not(self.sub_formulae[1]))).normal_form()

    def __str__(self):
        return f"{self.sub_formulae[0]!s} \u2228 {self.sub_formulae[1]!s}"


class Implication(Formula):
    def __init__(self, premise, conclusion):
        super().__init__()
        self.sub_formulae = [premise, conclusion]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A -> B = ~A \/ B = ~(~(~A) /\ ~B = ~(A /\ ~B)
        return Not(And(self.sub_formulae[0], Not(self.sub_formulae[1]))).normal_form()

    def __str__(self):
        return f"{self.sub_formulae[0]!s} \u2192 {self.sub_formulae[1]!s}"


class BiImplication(Formula):
    def __init__(self, eq_1, eq_2):
        super().__init__()
        self.sub_formulae = [eq_1, eq_2]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A <-> B = A -> B /\ B -> A   see above
        return And(Not(And(self.sub_formulae[0], Not(self.sub_formulae[1]))),
                   Not(And(self.sub_formulae[1], Not(self.sub_formulae[0])))).normal_form()

    def __str__(self):
        return f"{self.sub_formulae[0]!s} \u21D4 {self.sub_formulae[1]!s}"


class Diamond(Formula):
    def __init__(self, diamonded):
        super().__init__()
        self.sub_formulae = [diamonded]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # <> A = ~[]~A
        return Not(Box(Not(self.sub_formulae[0]))).normal_form()

    def __str__(self):
        return f"\u25C7 {self.sub_formulae[0]!s}"
