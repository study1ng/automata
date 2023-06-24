import sys

sys.path.append("../automata")
from dataclasses import dataclass
import functools
import typing
import abc
from collections import deque
from collections.abc import Container, Collection
from automata._helper import helper
del sys




class Epsilon:
    """For E_FNA class.

    epsilon := Epsilon which is in this module means empty string, 
    and you can use empty string "" as epsilon in E_FNA, but it is not recommended because of readability."""

    __instance = None

    def __repr__(self):
        return "ε"

    def __str__(self):
        return "ε"

    def __hash__(self):
        return str(self).__hash__()

    def __bool__(self):
        return False

    def __init__(self):
        if Epsilon.__instance == None:
            Epsilon.__instance = self
        else:
            raise Exception("Epsilon is a singleton class.")


epsilon = Epsilon()


@dataclass
class AutomatonArgs:
    transitions: typing.Dict[typing.Any, typing.Dict]
    start: typing.Hashable
    finals: Container

    def __repr__(self):
        return f"AutomatonArgs(transitions = {self.transitions},\nstart = {self.start},\nfinals = {self.finals})"
    __str__ = __repr__


class Automaton(abc.ABC):

    @typing.overload
    def __init__(self, transitions: typing.Dict[typing.Hashable, typing.Dict], start: typing.Hashable, finals: Container):
        ...

    @typing.overload
    def __init__(self, args: AutomatonArgs):
        ...

    def __init__(self, *args: AutomatonArgs | typing.Any):
        if (isinstance(args[0], AutomatonArgs)):
            if (len(args) != 1):
                raise Exception("Automaton must have 1 or 3 arguments.")
            self._TRANSITIONS = args[0].transitions
            self._START = args[0].start
            self._FINALS = args[0].finals
        else:
            if (len(args) != 3):
                raise Exception("Automaton must have 1 or 3 arguments.")
            self._TRANSITIONS = args[0]
            self._START = args[1]
            self._FINALS = args[2]

    def get_states(self) -> typing.Set[typing.Hashable]:
        """get all states in this automaton"""
        return set(self._TRANSITIONS.keys())

    def get_alphabets(self) -> typing.Set[typing.Hashable]:
        return {alphabet for transition in self._TRANSITIONS.values() for alphabet in transition.keys()}

    def accept(self, string: Collection) -> bool:
        """judge if the string is accepted

        Args:
            string (Collection): the string to be judged

        Returns:
            bool: is accepted
        """
        end = helper._get_end_of_iterator(self.trans(string))
        if (isinstance(end, (str, bytes, bytearray))):
            return end in self._FINALS
        elif (isinstance(end, Container)):
            return helper._any_in(end, self._FINALS)
        raise Exception("The final state is not a container or a string.")

    @abc.abstractmethod
    def trans(self, string: Collection) -> typing.Generator:
        """get the final state of the string

        Args:
            string (Collection): the string to be translated
        """
        pass

    __repr__ = __str__ = lambda self: f"Automaton(transitions = {self.__TRANSITIONS},\nstart = {self.__START},\nfinals = {self.__FINALS})"


class DFA(Automaton):
    """ Deterministic Finite Automaton
    you can use this class to create a DFA like below:
    transitions = {"q0": {"0": "q0", "1": "q1"},
                   "q1": {"0": "q1", "1": "q2"},
                   "q2": {"0": "q2", "1": "q0"}}
    start = "q0"
    accept = {"q0"}
    dfa = DFA(transitions, start, accept)
    """

    def trans(self, string: Collection) -> typing.Generator:
        current = self._START
        yield current
        for alphabet in string:
            current = self._TRANSITIONS[current][alphabet]
            yield current

    def shrinked(self) -> AutomatonArgs:
        "remove unreachable states and dead states from transitions"
        queue = deque()
        queue.append(self._START)
        rechable_states = {self._START}
        while len(queue):
            for state in self._TRANSITIONS[queue.popleft()].values():
                if state != None and state not in rechable_states:
                    queue.append(state)
                    rechable_states.add(state)
        return AutomatonArgs(
            transitions={state: self._TRANSITIONS[state]
                         for state in rechable_states},
            start=self._START,
            finals={state for state in self._FINALS if state in rechable_states}
        )


class NFA(Automaton):
    """ Non-deterministic Finite Automaton
    you can use this class to create a NFA like below:
    transitions = {
        "q0": {"0": {"q0"}, "1": {"q0", "q1"}},
        "q1": {"0": {"q2"}, "1": {"q2"}},
        "q2": {"0": {"q3"}, "1": {"q3"}},
        "q3": {"0": {"q4"}, "1": {"q4"}},
        "q4": {"0": {"q5"}, "1": {"q5"}},
        "q5": {"0": {}, "1": {}}
    }
    start = "q0"
    finals = {"q1", "q2", "q3", "q4", "q5"}
    a = NFA(transitions, start, finals)
    """
    # for cachrise, return tuple
    @functools.lru_cache(maxsize=None)
    def trans(self, string: Collection) -> typing.Generator:
        current = self._START
        yield current
        for alphabet in string:
            current = self._moveon(alphabet, current)
            yield current

    def log_trans(self, string: Collection) -> typing.Generator:
        """log the process of translation
        Args:
            string (Collection): the string to be translated
        """
        current = self._START
        yield current
        for alphabet in string:
            print(current, f" --{alphabet}--> ", end="")
            current = self._moveon(alphabet, current)
            print(current)
            yield current

    # Fix: has bug, I think this bug is because of helper._bit_search()
    def makeDFAargs(self) -> AutomatonArgs:
        """ Not Implemented, Don't use it
        make a AutomatonArgs of DFA from this NFA
        DFA is made by subset construction algorithm and contains unreachable states. To remove unreachable states, use DFA.shrinked().
        Returns:
            AutomatonArgs: the args of DFA
            typing.Dict[typing.Hashable, typing.Set]: the map from DFA state to NFA state"""
        transitions = dict()
        for i in (states := helper._bit_search(tuple(self.get_states()))):
            transitions.setdefault(str(i),
                                   dict(
                (alphabet, self._moveon(alphabet, i)) for alphabet in self.get_alphabets()
            ))
        return AutomatonArgs(transitions=transitions,
                             start=self._START,
                             finals={
                                 str(i) for i in states if helper._any_in(states, self._FINALS)})

    def _moveon_wrapper(self, alphabet: typing.Hashable, current: Container | typing.Any, *, check_container: bool = True) -> typing.Tuple:
        """This is just a wrapper, do not use it directly.

        Args:
            alphabet (typing.Any): next alphabet
            current (Container | typing.Any): current state
            check_container (bool, optional): check if current is a container. Defaults to True.

        Returns:
            typing.Tuple: next state
        """
        ans = set()
        if (current == None):
            return tuple(ans)
        # just check once if current is a container
        if (check_container and isinstance(current, Container) and not isinstance(current, (str, bytes, bytearray))):
            for state in current:
                ans |= self._moveon(alphabet, state, check_container=False)
            return tuple(ans)
        try:
            if (self._TRANSITIONS[current][alphabet] == {}):
                return tuple(ans)
            if (self._TRANSITIONS[current][alphabet] == None):
                raise Exception(
                    "If you want to show phi, please use {} instead.")
        except KeyError:
            return tuple(ans)
        ans |= set(self._TRANSITIONS[current][alphabet])
        return tuple(ans)

    def _moveon(self, alphabet: typing.Hashable, current: Container | typing.Any, *, check_container: bool = True) -> typing.Set:
        """internal function, move on to next state and return set of state

        Args:
            alphabet (typing.Any): next alphabet
            current (Container | typing.Any): current state
            check_container (bool, optional): check if current is a container. Defaults to True.

        Returns:
            typing.Set: next state"""
        return set(self._moveon_wrapper(alphabet, (current) if isinstance(current, str) else tuple(current), check_container=check_container))


class E_NFA(NFA):
    """Epsilon Non-deterministic Finite Automaton
    you can use this class to create a ε-NFA like below:    
    transitions = {
        "q0": {"0": {"q0"}, "1": {"q3"}, epsilon: {"q1"}},
        "q1": {"0": {"q1"}, "1": {"q2"}},
        "q2": {"0": {"q1"}, "1": {"q2"}},
        "q3": {"0": {"q4"}, "1": {"q0"}},
        "q4": {"0": {"q3"}, "1": {"q4"}}
    }
    start = "q0"
    finals = {"q0", "q1"}
    a = E_NFA(transitions, start, finals)"""

    def trans(self, string: Collection) -> typing.Generator:
        current = self._moveon("", self._START) | self._moveon(
            epsilon, self._START) | {self._START}
        yield current
        for alphabet in string:
            current = self._moveon(alphabet, current)
            current |= self._moveon(epsilon, current)
            yield current

    def log_trans(self, string: Collection) -> typing.Generator:
        current = self._moveon(epsilon, self._START) | {self._START}
        yield current
        for alphabet in string:
            print(current, f" --{alphabet}, {epsilon}--> ", end="")
            current = self._moveon(alphabet, current)
            current |= self._moveon(epsilon, current)
            print(current)
            yield current

    def makeNFAargs(self) -> AutomatonArgs:
        """make a AutomatonArgs of NFA from this ε-NFA
        Returns:
            AutomatonArgs: the args of NFA"""
        transitions = dict()
        for i in (states := helper._bit_search(tuple(self.get_states()))):
            transitions.setdefault(str(i),
                                   dict(
                (alphabet, self._moveon(alphabet, i)) for alphabet in self.get_alphabets()
            ))
        return AutomatonArgs(transitions=transitions,
                             start=self._START,
                             finals={
                                 str(i) for i in states if helper._any_in(states, self._FINALS)})

    def makeDFAargs(self) -> AutomatonArgs:
        return self.makeNFAargs(super().makeDFAargs())


if __name__ == '__main__':
    import random
    from pprint import pprint
    """
    q0 --0, 1--> q0
    q0 --1--> q1 
    q1 --0--> q2 
    q2 --0--> q3 
    q3 --0--> q4 
    q4 --0--> q5 

    q1 --1--> q2
    q2 --1--> q3
    q3 --1--> q4
    q4 --1--> q5
    """

    # if '1' in string[-5:], then string is accepted.
    transitions = {
        "q0": {"0": {"q0"}, "1": {"q0", "q1"}},
        "q1": {"0": {"q2"}, "1": {"q2"}},
        "q2": {"0": {"q0"}, "1": {"q1", "q2"}},
    }
    start = "q0"
    finals = {"q1", "q2"}
    a = NFA(transitions, start, finals)
    adfa = a.makeDFAargs()
    pprint(adfa.transitions)
    pprint(adfa.start)
    pprint(adfa.finals)

    # transitions = {
    #     "q0": {"0": {"q0"}, "1": {"q0", "q1"}},
    #     "q1": {"0": {"q2"}, "1": {"q2"}},
    #     "q2": {"0": {"q3"}, "1": {"q3"}},
    #     "q3": {"0": {"q4"}, "1": {"q4"}},
    #     "q4": {"0": {"q5"}, "1": {"q5"}},
    #     "q5": {"0": {}, "1": {}}
    # }
    # start = "q0"
    # finals = {"q1", "q2", "q3", "q4", "q5"}
    # a = NFA(transitions, start, finals)
    # adfa = a.makeDFAargs()
    # pprint(adfa.transitions)
    # pprint(adfa.start)
    # pprint(adfa.finals)
    # # initialize targets
    # targets = []
    # formerbinary = ["0", "1"]
    # nextbinary = []

    # test_case = a.log_trans("1000101")
    # try:
    #     while True:
    #         next(test_case)
    # except StopIteration:
    #     pass

    # for i in range(1 << 4):
    #     targets.extend(formerbinary)
    #     for former in formerbinary:
    #         for latter in ["0", "1"]:
    #             nextbinary.append(former + latter)
    #     formerbinary = nextbinary
    #     nextbinary = []

    # for target in targets:
    #     assert a.accept(target) == ("1" in target[-5:])

    # transitions = {
    #     "q0": {"0": {"q0"}, "1": {"q3"}, epsilon: {"q1"}},
    #     "q1": {"0": {"q1"}, "1": {"q2"}},
    #     "q2": {"0": {"q1"}, "1": {"q2"}},
    #     "q3": {"0": {"q4"}, "1": {"q0"}},
    #     "q4": {"0": {"q3"}, "1": {"q4"}}
    # }
    # start = "q0"
    # finals = {"q0", "q1"}
    # a = E_NFA(transitions, start, finals)

    # for target in targets:
    #     try:
    #         assert a.accept(target) == (int(target, 2) %
    #                                     2 == 0 or int(target, 2) % 3 == 0)
    #     except AssertionError:
    #         print(target, a.accept(target), (int(target, 2) %
    #               2 == 0 or int(target, 2) % 3 == 0))
    #         a.log_trans(target)
    #         raise AssertionError
