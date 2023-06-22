import unittest
from automata import DFA, AutomatonArgs
import sys
sys.path.append('..')


class TestDFA(unittest.TestCase):
    # DFA accepting string: string.count("1") % 3 == 0
    transitions = {"q0": {"0": "q0", "1": "q1"},
                   "q1": {"0": "q1", "1": "q2"},
                   "q2": {"0": "q2", "1": "q0"}}
    start = "q0"
    accept = {"q0"}
    dfa3args = AutomatonArgs(transitions, start, accept)
    dfa3 = DFA(transitions, start, accept)
    transitions = {"q0": {"0": {"q0"}, "1": {"q1"}},
                     "q1": {"0": {"q1"}, "1": {"q2"}},
                        "q2": {"0": {"q2"}, "1": {"q0"}}}
    dfa3_set = DFA(transitions, start, accept)
    # DFA accepting string: int(string, base=2) % 3 != 0
    transitions = {"modulo0": {"0": "modulo0", "1": "modulo1"},
                   "modulo1": {"0": "modulo-1", "1": "modulo0"},
                   "modulo-1": {"0": "modulo1", "1": "modulo-1"},
                   "modulo-2": {"0": "modulo-2", "1": "modulo-2"}}
    start = "modulo0"
    accept = {"modulo1", "modulo-1"}
    dfa_mod3args = AutomatonArgs(transitions, start, accept)
    dfa_mod3 = DFA(transitions, start, accept)

    def test_shrinked(self):
        shrinked_mod3 = AutomatonArgs({"modulo0": {"0": "modulo0", "1": "modulo1"},
                                       "modulo1": {"0": "modulo-1", "1": "modulo0"},
                                       "modulo-1": {"0": "modulo1", "1": "modulo-1"}},
                                      self.start, self.accept)
        self.assertEqual(self.dfa3.shrinked(), self.dfa3args)
        self.assertEqual(self.dfa_mod3.shrinked(), shrinked_mod3)
    shrinked_dfa_mod3=DFA(dfa_mod3.shrinked())

    def test_get_states(self):
        self.assertEqual(self.dfa3.get_states(), {"q0", "q1", "q2"})
        self.assertEqual(self.dfa_mod3.get_states(), {
                         "modulo0", "modulo1", "modulo-1", "modulo-2"})
        self.assertEqual(self.shrinked_dfa_mod3.get_states(),
                         {"modulo0", "modulo1", "modulo-1"})

    def test_accept(self):
        testcases = [
            "000",
            "111",
            "010101010101010101010101010101010101010101010101010101010101010101010101010101010101010",
        ]
        for case in testcases:
            self.assertEqual(self.dfa3.accept(case), case.count("1") % 3 == 0)
            self.assertEqual(self.dfa_mod3.accept(
                case), int(case, base=2) % 3 != 0)
            self.assertEqual(self.shrinked_dfa_mod3.accept(
                case), int(case, base=2) % 3 != 0)
        testcase = ""

        # epsilon will return the first state
        self.assertTrue(self.dfa3.accept(testcase))
        self.assertFalse(self.dfa_mod3.accept(testcase))
        self.assertFalse(self.shrinked_dfa_mod3.accept(testcase))

    def test_trans(self):
        #part of dfa3
        testcase, translation_expect = "000", ["q0", "q0", "q0", "q0"]
        for i in zip(translation_expect, self.dfa3.trans(testcase)):
            self.assertEqual(i[0], i[1])
        
        testcase, translation_expect = "111", ["q0", "q1", "q2", "q0"]
        for i in zip(translation_expect, self.dfa3.trans(testcase)):
            self.assertEqual(i[0], i[1])

        testcase, translation_expect = "", ["q0"]
        for i in zip(translation_expect, self.dfa3.trans(testcase)):
            self.assertEqual(i[0], i[1])

        #part of dfa_mod3 and shrinked_dfa_mod3
        testcase, translation_expect = "000", ["modulo0", "modulo0", "modulo0", "modulo0"]
        for i in zip(translation_expect, self.dfa_mod3.trans(testcase)):
            self.assertEqual(i[0], i[1])
        for i in zip(translation_expect, self.shrinked_dfa_mod3.trans(testcase)):
            self.assertEqual(i[0], i[1])

        testcase, translation_expect = "1001", ["modulo0", "modulo1", "modulo-1", "modulo1", "modulo0"]
        for i in zip(translation_expect, self.dfa_mod3.trans(testcase)):
            self.assertEqual(i[0], i[1])
        for i in zip(translation_expect, self.shrinked_dfa_mod3.trans(testcase)):
            self.assertEqual(i[0], i[1])

        testcase, translation_expect = "", ["modulo0"]
        for i in zip(translation_expect, self.dfa_mod3.trans(testcase)):
            self.assertEqual(i[0], i[1])
        for i in zip(translation_expect, self.shrinked_dfa_mod3.trans(testcase)):
            self.assertEqual(i[0], i[1])
        