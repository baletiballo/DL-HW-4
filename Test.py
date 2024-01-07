from Formula import *
from Reasoner import successful
import Parser
import time


# return a formula of size 2n. Its tableau has n steps
def formula_of_size_2(n: int) -> Formula:
    f = "¬ " * n + "p"
    return Parser.parse_formula_str(f)


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
            big_and = big_and + f" ∧ ( ( q{j} → □ q{j} ) ∧ ( ¬ q{j} → □ ¬ q{j} ) )"
        return f"{phi_n} ∧ { box_n } ( p{n} → ( ♢ ( p{n + 1} ∧ q{n + 1} ) ∧ ♢ ( p{n + 1} ∧ ¬ q{n + 1} ) {big_and} ) )"


if __name__ == '__main__':

    measurements = []
    for n in range(15):
        label = {exp_model_formula(n).normal_form()}
        start = time.time()
        s = successful(label)
        measurements.append(time.time()-start)
    with open("./Measurements.txt", encoding="utf-8", mode="w") as f:
        for n, t in enumerate(measurements):
            f.write(f"{t * 1000:.3f} ms to satisfy ϕ_{n}\n")

    measurements = []
    for n in range(15):
        label = {exp_size_formula(n)}
        start = time.time()
        successful(label)
        measurements.append(time.time()-start)
    with open("./Measurements.txt", encoding="utf-8", mode="a") as f:
        for n, t in enumerate(measurements):
            f.write(f"{t * 1000:.3f} ms to satisfy a (trivial) formula of size 2^{n+1}\n")
