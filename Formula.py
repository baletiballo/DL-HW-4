"""
Formula is essentially an abstract superclass for the recursive syntax-tree (https://en.wikipedia.org/wiki/Parse_tree)
sub-formulae are the sub-formulae (duh) one for Not and Box; two for And
applicable_tableaux_rule gives easier access and will allow a match-case construct
"""
class Formula:
    def __init__(self):
        self.sub_formulae = None
        self.applicable_tableaux_rule = None

    def normal_form(self):
        return self


class Not(Formula):
    def __init__(self, neg):
        super().__init__()
        self.sub_formulae = [neg]
        if isinstance(self.sub_formulae, Not):
            self.applicable_tableaux_rule = "NotNot"
        elif isinstance(self.sub_formulae, And):
            self.applicable_tableaux_rule = "NotAnd"
        elif isinstance(self.sub_formulae, Box):
            self.applicable_tableaux_rule = "NotBox"
        else:
            self.applicable_tableaux_rule = None


class And(Formula):
    def __init__(self, conj_1, conj_2):
        super().__init__()
        self.sub_formulae = [conj_1, conj_2]
        self.applicable_tableaux_rule = "And"


class Box(Formula):
    def __init__(self, boxed):
        super().__init__()
        self.sub_formulae = [boxed]
        self.applicable_tableaux_rule = None


class Or(Formula):
    def __init__(self, disj_1, disj_2):
        super().__init__()
        self.sub_formulae = [disj_1, disj_2]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A \/ B = ~(~A /\ ~B)
        return Not(And(Not(self.sub_formulae[0]), Not(self.sub_formulae[1])))


class Implication(Formula):
    def __init__(self, premise, conclusion):
        super().__init__()
        self.sub_formulae = [premise, conclusion]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A -> B = ~A \/ B = ~(~(~A) /\ ~B = ~(A /\ ~B)
        return Not(And(self.sub_formulae[0], Not(self.sub_formulae[1])))


class BiImplication(Formula):
    def __init__(self, eq_1, eq_2):
        super().__init__()
        self.sub_formulae = [eq_1, eq_2]
        self.applicable_tableaux_rule = None

    def normal_form(self):  # A <-> B = A -> B /\ B -> A   see above
        return And(Not(And(self.sub_formulae[0], Not(self.sub_formulae[1]))),
                   Not(And(self.sub_formulae[1], Not(self.sub_formulae[0]))))


class Atom(Formula):
    def __init__(self, name):
        super().__init__()
        self.name = name
