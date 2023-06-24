import sys
sys.path.append("../automata")

import unittest
from automata import NFA, AutomatonArgs

class TestNFA(unittest.TestCase):
    # this NFA will accept strings which "1" in string[:-1]
    transitions = {
        "q0": {"0": {"q0"}, "1": {"q0", "q1"}},
        "q1": {"0": {"q2"}, "1": {"q2"}},
        "q2": {"0": {"q3"}, "1": {"q3"}},
        "q3": {"0": {"q4"}, "1": {"q4"}},
        "q4": {"0": {"q5"}, "1": {"q5"}},
        "q5": {"0": {}, "1": {}} # {} is the empty set and will never go to anywhere
    }
    start = "q0"
    finals = {"q1", "q2", "q3", "q4", "q5"}
    nfa_1_in_last5chars = NFA(transitions, start, finals)
    
    # this NFA will accept string which match  ("0b")? + binary string which is multiple of 3 or multiple of 2
    
    transitions = {
        "start": {"0": {"0", "binary%2=0", "binary%3=0"}, "1": {"binary%2=1", "binary%3=1"}},
        "0": {"0": {"0", "binary%2=0", "binary%3=0"}, "1": {"binary%2=1", "binary%3=1"}, "b": {"b"}},
        "b": {"0": {"binary%2=0", "binary%3=0"}, "1": {"binary%2=1", "binary%3=1"}},
        "binary%2=0": {"0": {"binary%2=0"}, "1": {"binary%2=1"}, "b": {}},
        "binary%2=1": {"0": {"binary%2=0"}, "1": {"binary%2=1"}, "b": {}},
        "binary%3=0": {"0": {"binary%3=0"}, "1": {"binary%3=1"}},
        "binary%3=1": {"0": {"binary%3=2"}, "1": {"binary%3=0"}},
        "binary%3=2": {"0": {"binary%3=1"}, "1": {"binary%3=2"}}
    }
    start = "start"
    finals = {"0", "binary%2=0", "binary%3=0"}
    nfa_mod2or3 = NFA(transitions, start, finals)

    def test_get_states(self):
        self.assertEqual(self.nfa_1_in_last5chars.get_states(), {"q0", "q1", "q2", "q3", "q4", "q5"})
        self.assertEqual(self.nfa_mod2or3.get_states(), {"start", "0", "b", "binary%2=0", "binary%2=1", "binary%3=0", "binary%3=1", "binary%3=2"})
    def test_accept(self):
        testcase = ""
        self.assertFalse(self.nfa_1_in_last5chars.accept(""))
        self.assertFalse(self.nfa_mod2or3.accept(""))
        testcases = [
            "0",
            "1",
            "00",
            "01",
            "010100011"
            "0100100000"
        ]
        for testcase in testcases:
            self.assertEqual(self.nfa_1_in_last5chars.accept(testcase), "1" in testcase[-5:])
            self.assertEqual(self.nfa_mod2or3.accept(testcase), (int(testcase, 2) % 2 == 0) or (int(testcase, 2) % 3 == 0))
        testcases = ["0b" + testcase for testcase in testcases]
        for testcase in testcases:
            self.assertEqual(self.nfa_mod2or3.accept(testcase), (int(testcase[2:], 2) % 2 == 0) or (int(testcase[2:], 2) % 3 == 0))
        testcases = "b0110001"
        self.assertFalse(self.nfa_mod2or3.accept(testcases))

    def test_trans(self):
        testcase = "101001"
        expected_result_1_in_last5chars = [
            "q0", # 1
            {"q0", "q1"}, # 0
            {"q0", "q2"}, # 1
            {"q0", "q1", "q3"}, # 0
            {"q0", "q2", "q4"}, # 0
            {"q0", "q3", "q5"}, # 1
            {"q0", "q1", "q4"}  # END
            ]
        actual_result_1_in_last5chars = self.nfa_1_in_last5chars.trans(testcase)
        expected_result_mod2or3 = [
            "start", # 1
            {"binary%2=1", "binary%3=1"}, # 0
            {"binary%2=0", "binary%3=2"}, # 1
            {"binary%2=1", "binary%3=2"}, # 0
            {"binary%2=0", "binary%3=1"}, # 0
            {"binary%2=0", "binary%3=2"}, # 1
            {"binary%2=1", "binary%3=2"}  # END
            ]
        actual_result_mod2or3 = self.nfa_mod2or3.trans(testcase)

        for i in zip(expected_result_1_in_last5chars, actual_result_1_in_last5chars):
            self.assertEqual(i[0], i[1])
        for i in zip(expected_result_mod2or3, actual_result_mod2or3):
            self.assertEqual(i[0], i[1])

        testcase = "0b01001"
        expected_result_mod2or3 = [
            "start", # 0
            {"0", "binary%2=0", "binary%3=0"}, # b
            {"b"}, # 0
            {"binary%2=0", "binary%3=0"}, # 1
            {"binary%2=1", "binary%3=1"}, # 0
            {"binary%2=0", "binary%3=2"}, # 0
            {"binary%2=0", "binary%3=1"},  # 1
            {"binary%2=1", "binary%3=0"}  # END
            ]
        actual_result_mod2or3 = self.nfa_mod2or3.trans(testcase)

        for i in zip(expected_result_mod2or3, actual_result_mod2or3):
            self.assertEqual(i[0], i[1])