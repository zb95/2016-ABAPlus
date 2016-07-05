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