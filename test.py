import unittest
from aba_plus import *

class TestABAPlus(unittest.TestCase):

    def test_simple_transitive_closure(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([a, b, c])

        pref1 = Preference(a, b, LESS_THAN)
        pref2 = Preference(b, c, LESS_THAN)
        preferences = set([pref1, pref2])

        abap = ABA_Plus(assumptions=assumptions, rules=set(), preferences=preferences)
        self.assertEqual(abap.preferences, {pref1, pref2, Preference(a, c, LESS_THAN)})

    def test_simple_deduction_exists(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set([b])

        rule = Rule(set([b]),a)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set([b])))

    def test_deduction_from_empty_set_exists(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set([b])

        rule = Rule(set(), a)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set()))

    def test_simple_deduction_does_not_exist(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([a, b])

        rule = Rule(set([b]), c)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertFalse(abap.deduction_exists(to_deduce=a, deduce_from=set([b])))

    def test_transitive_deduction_exists(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([b])

        rule1 = Rule(set([b]), c)
        rule2 = Rule(set([c]), a)
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set([b])))

    def test_transitive_deduction_from_empty_set_exists(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set()

        rule1 = Rule(set([b]), a)
        rule2 = Rule(set(), b)
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=a, deduce_from=set()))

    def test_complex_deduction_exists(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        d = Sentence("d")
        e = Sentence("e")
        f = Sentence("f")
        g = Sentence("g")
        assumptions = set([a, b, e])

        rule1 = Rule(set([a, b]), c)
        rule2 = Rule(set([e]), f)
        rule3 = Rule(set([c, f]), g)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.deduction_exists(to_deduce=g, deduce_from=set([a, b, e])))

    def test_complex_deduction_does_not_exist(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        d = Sentence("d")
        e = Sentence("e")
        f = Sentence("f")
        g = Sentence("g")
        assumptions = set([a, b, e])

        rule1 = Rule(set([a, b]), c)
        rule2 = Rule(set([e]), f)
        rule3 = Rule(set([c, f]), g)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertFalse(abap.deduction_exists(to_deduce=g, deduce_from=set([a, e])))

    def test_simple_WCP_no_violation_check1(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([a, b])

        rule = Rule(set([b]), c)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_simple_WCP_no_violation_check2(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set([a, b])

        rule1 = Rule(set([b]), a.contrary())
        rule2 = Rule(set([a]), b.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_simple_WCP_no_violation_check3(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([a, b, c])

        rule1 = Rule(set([b]), a.contrary())
        rule2 = Rule(set([c]), b.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_simple_WCP_violation_check(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule = Rule(set([b]), a.contrary())
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_transitive_WCP_violation_check(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule1 = Rule(set([b]), c)
        rule2 = Rule(set([c]), a.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_transitive_WCP_violation_check(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule1 = Rule(set([b]), c)
        rule2 = Rule(set([c]), a.contrary())
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_cycle_WCP_violation_check(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([a, b])

        pref = Preference(b, a, LESS_THAN)
        preferences = set([pref])

        rule1 = Rule(set([c]), a.contrary())
        rule2 = Rule(set([c]), c)
        rule3 = Rule(set([b]), c)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, preferences=preferences, rules=rules)

        self.assertFalse(abap.check_WCP())

    def test_cycle_WCP_no_violation_check(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        d = Sentence("d")
        assumptions = set([a])

        rule1 = Rule(set([b]), a.contrary())
        rule2 = Rule(set([c]), b)
        rule3 = Rule(set([d]), c)
        rule4 = Rule(set([b]), d)
        rules = (set([rule1, rule2, rule3, rule4]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_complex_WCP_no_violation_check1(self):
        alpha = Sentence("alpha")
        beta = Sentence("beta")
        gamma = Sentence("gamma")
        delta = Sentence("delta")
        d = Sentence("d")
        k = Sentence("k")
        m = Sentence("m")
        p = Sentence("p")
        q = Sentence("q")
        r = Sentence("r")
        s = Sentence("s")
        t = Sentence("t")
        u = Sentence("u")
        v = Sentence("v")
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

    def test_complex_WCP_no_violation_check2(self):
        alpha = Sentence("alpha")
        beta = Sentence("beta")
        gamma = Sentence("gamma")
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        k = Sentence("k")
        l = Sentence("l")
        m = Sentence("m")
        n = Sentence("n")
        p = Sentence("p")
        q = Sentence("q")
        s = Sentence("s")
        t = Sentence("t")
        u = Sentence("u")
        v = Sentence("v")
        x = Sentence("x")
        z = Sentence("z")
        assumptions = set([alpha, beta, gamma])

        rule1 = Rule(set([a, b, c]), x)
        rule2 = Rule(set([s, t]), a)
        rule3 = Rule(set([b]), s)
        rule4 = Rule(set([beta, u]), b)
        rule5 = Rule(set([]), u)
        rule6 = Rule(set([v, z]), c)
        rule7 = Rule(set([a]), z)
        rule8 = Rule(set([v]), v)
        rule9 = Rule(set([k, l]), c)
        rule10 = Rule(set([k]), k)
        rule11 = Rule(set([a]), l)
        rule12 = Rule(set([a, m]), k)
        rule13 = Rule(set([beta, n]), m)
        rule14 = Rule(set([p]), n)
        rule15 = Rule(set([b, q]), m)
        rule16 = Rule(set([]), q)
        rules = {rule1, rule2, rule3, rule4, rule5, rule6,
                 rule7, rule8, rule9, rule10, rule11, rule12, rule13,
                 rule14, rule15, rule16}

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertTrue(abap.check_WCP())

    def test_set_combinations(self):
        abap = ABA_Plus()

        set1 = set()
        set1.add(frozenset({"b"}))

        set2 = set()
        set2.add(frozenset({"e"}))
        set2.add(frozenset({"f"}))

        set3 = set()
        set3.add(frozenset({"g"}))

        set4 = set()
        set4.add(frozenset({"i"}))
        set4.add(frozenset({"k"}))

        combs = abap.set_combinations({frozenset(set1), frozenset(set2), frozenset(set3), frozenset(set4)})
        correct_combs = {frozenset({"b", "e", "g", "i"}), frozenset({"b", "e", "g", "k"}),
                         frozenset({"b", "f", "g", "i"}), frozenset({"b", "f", "g", "k"})}
        self.assertEqual(combs, correct_combs)

    def test_simple_generate_argument1(self):
        a = Sentence("a")
        assumptions = set([a])


        abap = ABA_Plus(assumptions=assumptions)

        res = abap.generate_arguments(a)

        self.assertEqual(abap.generate_arguments(a), {frozenset({a})})

    def test_simple_generate_argument2(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = set([b,c])

        rule = Rule(set([b, c]), a)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        res = abap.generate_arguments(a)

        self.assertEqual(abap.generate_arguments(a), {frozenset({b,c})})

    def test_generate_empty_argument(self):
        a = Sentence("a")

        rule = Rule(set(), a)
        rules = (set([rule]))

        abap = ABA_Plus(rules=rules)

        res = abap.generate_arguments(a)

        self.assertEqual(abap.generate_arguments(a), {frozenset()})

    def test_transitive_generate_argument(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        d = Sentence("d")
        e = Sentence("e")
        assumptions = set([b, c, d])

        rule1 = Rule(set([b, e]), a)
        rule2 = Rule(set([c, d]), e)
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(a), {frozenset({b, c, d})})


    def test_generate_multiple_arguments1(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        d = Sentence("d")
        e = Sentence("e")
        assumptions = set([b, d, e])

        rule1 = Rule(set([b, c]), a)
        rule2 = Rule(set([d]), c)
        rule3 = Rule(set([e]), c)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(a), {frozenset({b, d}), frozenset({b, e})})


    def test_generate_multiple_arguments2(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set([b])

        rule1 = Rule(set([b]), a)
        rule2 = Rule(set(), a)
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(a), {frozenset(), frozenset({b})})


    def test_generate_multiple_arguments3(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        d = Sentence("d")
        assumptions = set([b, d])

        rule1 = Rule(set([b, c]), a)
        rule2 = Rule(set(), c)
        rule3 = Rule(set([d]), c)
        rules = (set([rule1, rule2, rule3]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(a), {frozenset({b}), frozenset({b, d})})


    def test_cycle_generate_argument1(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set([b])

        rule1 = Rule(set([a]), a)
        rule2 = Rule(set([b]), a)
        rules = (set([rule1, rule2]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(a), {frozenset({b})})


    def test_cycle_generate_argument2(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        d = Sentence("d")
        e = Sentence("e")
        assumptions = set([e])

        rule1 = Rule(set([b]), a)
        rule2 = Rule(set([c]), b)
        rule3 = Rule(set([d]), c)
        rule4 = Rule(set([b]), d)
        rule5 = Rule(set([e]), a)
        rules = (set([rule1, rule2, rule3, rule4, rule5]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(a), {frozenset({e})})


    def test_generate_no_arguments(self):
        a = Sentence("a")
        b = Sentence("b")
        assumptions = set()

        rule = Rule(set([b]), a)
        rules = (set([rule]))

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(a), set())


    def test_complex_generate_arguments1(self):
        alpha = Sentence("alpha")
        beta = Sentence("beta")
        gamma = Sentence("gamma")
        delta = Sentence("delta")
        d = Sentence("d")
        s1 = Sentence("s1")
        s2 = Sentence("s2")
        s3 = Sentence("s3")
        s4 = Sentence("s4")
        s5 = Sentence("s5")
        s6 = Sentence("s6")
        s7 = Sentence("s7")
        assumptions = set([alpha, beta, gamma, delta])

        rule1 = Rule(set([s3, s4]), d)
        rule2 = Rule(set([s2]), s3)
        rule3 = Rule(set([s1, beta]), s2)
        rule4 = Rule(set([beta]), s1)
        rule5 = Rule(set([s5, s6]), d)
        rule6 = Rule(set([s7]), s5)
        rule7 = Rule(set([alpha, beta, gamma]), s7)
        rule8 = Rule(set([s2]), s6)
        rule9 = Rule(set([s5]), s7)
        rule10 = Rule(set([s2]), s1)
        rules = {rule1, rule2, rule3, rule4, rule5,
                 rule6, rule7, rule8, rule9, rule10, }

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(alpha), {frozenset({alpha})})
        self.assertEqual(abap.generate_arguments(beta), {frozenset({beta})})
        self.assertEqual(abap.generate_arguments(gamma), {frozenset({gamma})})
        self.assertEqual(abap.generate_arguments(delta), {frozenset({delta})})
        self.assertEqual(abap.generate_arguments(d), {frozenset({alpha, beta, gamma})})


    def test_complex_generate_arguments2(self):
        alpha = Sentence("alpha")
        beta = Sentence("beta")
        gamma = Sentence("gamma")
        delta = Sentence("delta")
        epsilon = Sentence("epsilon")
        d = Sentence("d")
        s1 = Sentence("s1")
        s2 = Sentence("s2")
        s3 = Sentence("s3")
        s4 = Sentence("s4")
        s5 = Sentence("s5")
        s6 = Sentence("s6")
        s7 = Sentence("s7")
        s8 = Sentence("s8")
        s9 = Sentence("s9")
        s10 = Sentence("s10")
        assumptions = set([alpha, beta, gamma, delta, epsilon])

        rule1 = Rule(set([alpha, beta]), s1)
        rule2 = Rule(set(), s2)
        rule3 = Rule(set([s1, s2]), s3)
        rule4 = Rule(set([alpha, s3]), s4)
        rule5 = Rule(set([s4, beta]), s5)
        rule6 = Rule(set([s5, gamma]), s4)
        rule7 = Rule(set([s4, s5, s6]), d)
        rule8 = Rule(set([s7]), s6)
        rule9 = Rule(set([gamma, s8]), s7)
        rule10 = Rule(set([s9]), s8)
        rule11 = Rule(set([s2, gamma]), s10)
        rule12 = Rule(set([s10]), d)
        rules = {rule1, rule2, rule3, rule4, rule5, rule6,
                 rule7, rule8, rule9, rule10, rule11, rule12}

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(alpha), {frozenset({alpha})})
        self.assertEqual(abap.generate_arguments(beta), {frozenset({beta})})
        self.assertEqual(abap.generate_arguments(gamma), {frozenset({gamma})})
        self.assertEqual(abap.generate_arguments(delta), {frozenset({delta})})
        self.assertEqual(abap.generate_arguments(epsilon), {frozenset({epsilon})})
        self.assertEqual(abap.generate_arguments(d), {frozenset({gamma})})

    def test_complex_generate_arguments3(self):
        alpha = Sentence("alpha")
        beta = Sentence("beta")
        a = Sentence("a")
        b = Sentence("b")
        s1 = Sentence("s1")
        s2 = Sentence("s2")
        s3 = Sentence("s3")
        s4 = Sentence("s4")
        s5 = Sentence("s5")
        s6 = Sentence("s6")
        s7 = Sentence("s7")
        assumptions = set([alpha, beta])

        rule1 = Rule(set([s1]), a)
        rule2 = Rule(set([s2, s3]), s1)
        rule3 = Rule(set(), s2)
        rule4 = Rule(set([s4]), s3)
        rule5 = Rule(set(), s4)
        rule6 = Rule(set([s5, s6]), b)
        rule7 = Rule(set(), s5)
        rule8 = Rule(set([beta]), s6)
        rule9 = Rule(set([beta]), s7)

        rules = {rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9}

        abap = ABA_Plus(assumptions=assumptions, rules=rules)

        self.assertEqual(abap.generate_arguments(alpha), {frozenset({alpha})})
        self.assertEqual(abap.generate_arguments(beta), {frozenset({beta})})
        self.assertEqual(abap.generate_arguments(a), {frozenset()})
        self.assertEqual(abap.generate_arguments(b), {frozenset({beta})})

    def test_simple_generate_arguments_and_attacks1(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = {a,b,c}

        rule = Rule({a,c}, b.contrary())
        rules = {rule}

        pref1 = Preference(a, b, LESS_THAN)
        pref2 = Preference(c, b, LESS_THAN)
        preferences = {pref1, pref2}

        abap = ABA_Plus(assumptions=assumptions, rules=rules, preferences=preferences)

        res = abap.generate_arguments_and_attacks({a.contrary(), b.contrary(), c.contrary()})
        deductions = res[0]
        attacks = res[1]

        self.assertEqual(deductions[a], {Deduction({a}, {a})})
        self.assertEqual(deductions[b], {Deduction({b}, {b})})
        self.assertEqual(deductions[c], {Deduction({c}, {c})})
        self.assertEqual(deductions[b.contrary()], {Deduction({a,c}, {b.contrary()})})
        self.assertEqual(len(deductions), 4)

        self.assertEqual(attacks, {Attack(Deduction({b}, {b}), Deduction({a,c}, {b.contrary()}), REVERSE_ATK)})

    def test_simple_generate_arguments_and_attacks2(self):
        a = Sentence("a")
        b = Sentence("b")
        c = Sentence("c")
        assumptions = {a, b, c}

        rule1 = Rule({a, c}, b.contrary())
        rule2 = Rule({b, c}, a.contrary())
        rule3 = Rule({a, b}, c.contrary())
        rules = {rule1, rule2, rule3}

        pref1 = Preference(a, b, LESS_THAN)
        pref2 = Preference(c, b, LESS_THAN)
        preferences = {pref1, pref2}

        abap = ABA_Plus(assumptions=assumptions, rules=rules, preferences=preferences)

        res = abap.generate_arguments_and_attacks({a.contrary(), b.contrary(), c.contrary()})
        deductions = res[0]
        attacks = res[1]

        ded_a = Deduction({a}, {a})
        ded_b = Deduction({b}, {b})
        ded_c = Deduction({c}, {c})
        ded_contr_a = Deduction({b, c}, {a.contrary()})
        ded_contr_b = Deduction({a, c}, {b.contrary()})
        ded_contr_c = Deduction({a, b}, {c.contrary()})

        self.assertEqual(deductions[a], {ded_a})
        self.assertEqual(deductions[b], {ded_b})
        self.assertEqual(deductions[c], {ded_c})
        self.assertEqual(deductions[a.contrary()], {ded_contr_a})
        self.assertEqual(deductions[b.contrary()], {ded_contr_b})
        self.assertEqual(deductions[c.contrary()], {ded_contr_c})
        self.assertEqual(len(deductions), 6)

        self.assertEqual(attacks, {Attack(ded_b, ded_contr_b, REVERSE_ATK),
                                   Attack(ded_contr_a, ded_a, NORMAL_ATK),
                                   Attack(ded_contr_c, ded_c, NORMAL_ATK),
                                   Attack(ded_contr_a, ded_contr_c, NORMAL_ATK),
                                   Attack(ded_contr_a, ded_contr_b, NORMAL_ATK),
                                   Attack(ded_contr_a, ded_contr_b, REVERSE_ATK),
                                   Attack(ded_contr_c, ded_contr_a, NORMAL_ATK),
                                   Attack(ded_contr_c, ded_contr_b, REVERSE_ATK),
                                   Attack(ded_contr_c, ded_contr_b, NORMAL_ATK)})

