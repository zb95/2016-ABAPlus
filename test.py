import unittest
from aba_plus import *

class TestABAPlus(unittest.TestCase):

    def test_simple_deduction_exists(self):
        a = Predicate("a")
        b = Predicate("b")
        assumptions = set([b])

        rule = Rule(set([b]),a)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set([b])))

    def test_deduction_from_empty_set_exists(self):
        a = Predicate("a")
        b = Predicate("b")
        assumptions = set([b])

        rule = Rule(set(), a)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set()))

    def test_simple_deduction_does_not_exist(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        assumptions = set([a, b])

        rule = Rule(set([b]), c)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertFalse(abap.deduction_exists(to_deduce=a, deduce_from=set([b])))

    def test_transitive_deduction_exists(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        assumptions = set([b])

        rule1 = Rule(set([b]), c)
        rule2 = Rule(set([c]), a)
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set([b])))

    def test_transitive_deduction_from_empty_set_exists(self):
        a = Predicate("a")
        b = Predicate("b")
        assumptions = set()

        rule1 = Rule(set([b]), a)
        rule2 = Rule(set(), b)
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set()))

    def test_complex_deduction_exists(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        d = Predicate("d")
        e = Predicate("e")
        f = Predicate("f")
        g = Predicate("g")
        assumptions = set([a, b, e])

        rule1 = Rule(set([a, b]), c)
        rule2 = Rule(set([e]), f)
        rule3 = Rule(set([c, f]), g)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=g, deduce_from=set([a, b, e])))

    def test_complex_deduction_does_not_exist(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        d = Predicate("d")
        e = Predicate("e")
        f = Predicate("f")
        g = Predicate("g")
        assumptions = set([a, b, e])

        rule1 = Rule(set([a, b]), c)
        rule2 = Rule(set([e]), f)
        rule3 = Rule(set([c, f]), g)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertFalse(abap.deduction_exists(to_deduce=g, deduce_from=set([a, e])))

    def test_simple_WCP_no_violation_check1(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        assumptions = set([a, b])

        rule = Rule(set([b]), c)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_simple_WCP_no_violation_check2(self):
        a = Predicate("a")
        b = Predicate("b")
        assumptions = set([a, b])

        rule1 = Rule(set([b]), a.contrary())
        rule2 = Rule(set([a]), b.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_simple_WCP_no_violation_check3(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        assumptions = set([a, b, c])

        rule1 = Rule(set([b]), a.contrary())
        rule2 = Rule(set([c]), b.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_simple_WCP_violation_check(self):
        a = Predicate("a")
        b = Predicate("b")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule = Rule(set([b]), a.contrary())
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_transitive_WCP_violation_check(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule1 = Rule(set([b]), c)
        rule2 = Rule(set([c]), a.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_transitive_WCP_violation_check(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule1 = Rule(set([b]), c)
        rule2 = Rule(set([c]), a.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_cycle_WCP_violation_check(self):
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule1 = Rule(set([c]), a.contrary())
        rule2 = Rule(set([c]), c)
        rule3 = Rule(set([b]), c)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_complex_WCP_no_violation_check(self):
        alpha = Predicate("alpha")
        beta = Predicate("beta")
        gamma = Predicate("gamma")
        delta = Predicate("delta")
        d = Predicate("d")
        k = Predicate("k")
        m = Predicate("m")
        p = Predicate("p")
        q = Predicate("q")
        r = Predicate("r")
        s = Predicate("s")
        t = Predicate("t")
        u = Predicate("u")
        v = Predicate("v")
        assumptions = set([alpha, beta, gamma, delta])

        rule1 = Rule(set([p, q]), alpha.contrary())
        rule2 = Rule(set([r, beta]), p)
        rule3 = Rule(set([alpha]), r)
        rule4 = Rule(set([]), q)
        rule5 = Rule(set([gamma, d, s]), beta.contrary())
        rule6 = Rule(set([delta]), d)
        rule7 = Rule(set([d,t ]), s)
        rule8 = Rule(set([]), t)
        rule9 = Rule(set([u, v]), gamma.contrary())
        rule10 = Rule(set([delta]), u)
        rule11 = Rule(set([v]), v)
        rule12 = Rule(set([k, m]), delta.contrary())
        rule13 = Rule(set([gamma]), m)
        rules = {rule1, rule2, rule3, rule3, rule4, rule5, rule6,
                 rule7, rule8, rule9, rule10, rule11, rule12, rule13}

        pref1 = Preference(alpha, beta, LESS_THAN)
        pref2 = Preference(delta, gamma, LESS_THAN)
        preferences = {pref1, pref2}

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertTrue(abap.check_WCP())

    '''
    def test_WCP_cannot_be_derived_check(self):
        alpha = Predicate("alpha")
        beta = Predicate("beta")
        gamma = Predicate("gamma")
        a = Predicate("a")
        b = Predicate("b")
        c = Predicate("c")
        k = Predicate("k")
        l = Predicate("l")
        m = Predicate("m")
        n = Predicate("n")
        p = Predicate("p")
        q = Predicate("q")
        s = Predicate("s")
        t = Predicate("t")
        u = Predicate("u")
        v = Predicate("v")
        x = Predicate("x")
        z = Predicate("z")
        assumptions = set([alpha, beta, gamma])
    '''