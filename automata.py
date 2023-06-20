from collections.abc import Container, Collection
from collections import deque
import abc
import typing
import functools
from dataclasses import dataclass

class Epsilon:
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

# Empty string. Will be used in E_NFA's transitions' key
epsilon = Epsilon()

@dataclass
class AutomatonArgs:
    transitions: typing.Dict[typing.Any, typing.Dict]
    start: typing.Hashable
    finals: Container

class Automaton(abc.ABC):

    @typing.overload
    def __init__(self, transitions: typing.Dict[typing.Hashable, typing.Dict], start: typing.Hashable, finals: Container):
        ...
    @typing.overload
    def __init__(self, args: AutomatonArgs):
        ...

    def __init__(self, *args):
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

    def _all_in(self, container1: Container, container2: Container) -> bool:
        """internal functoin, check if all elements in container1 is in container2

        Args:
            container1 (Container): _description_
            container2 (Container): _description_
        
        Returns:
            bool: all elements in container1 is in container2
        """
        for element in container1:
            if element not in container2:
                return False
        return True

    def _any_in(self, container1: Container, container2: Container) -> bool:
        """internal functoin, check if any element in container1 is in container2

        Args:
            container1 (Container): _description_
            container2 (Container): _description_

        Returns:
            bool: any element in container1 is in container2
        """
        for element in container1:
            if element in container2:
                return True
        return False

    def judge(self, string: Collection) -> bool:
        """judge if the string is accepted

        Args:
            string (Collection): the string to be judged

        Returns:
            bool: is accepted
        """
        return self._any_in(self.trans(string), self._FINALS)

    @abc.abstractmethod
    def trans(self, string: Collection):
        """get the final state of the string

        Args:
            string (Collection): the string to be translated
        """
        pass
    
    __repr__ = __str__ = lambda self: f"Automaton({self.__TRANSITIONS}, {self.__START}, {self.__FINALS})"

class DFA(Automaton):
    def trans(self, string: Collection) -> typing.Any:
        current = self._START
        for alphabet in string:
            current = self._TRANSITIONS[current][alphabet]
        return current

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
            transitions={state: self._TRANSITIONS[state] for state in rechable_states},
            start=self._START,
            finals={state for state in self._FINALS if state in rechable_states}
        )        

class NFA(Automaton):    
    # for cachrise, return tuple
    @functools.lru_cache(maxsize=None)
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
                raise Exception("If you want to show phi, please use {} instead.")
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

    def trans(self, string: Collection) -> typing.Set:
        current = self._START
        for alphabet in string:
            current = self._moveon(alphabet, current)
        return current
    
    def log_trans(self, string: Collection) -> typing.Any:
        """log the process of translation
        Args:
            string (Collection): the string to be translated
        """
        current = self._START
        for alphabet in string:
            print(current, f" --{alphabet}--> ", end="")
            current = self._moveon(alphabet, current)
            print(current)
        return current

    def makeDFAargs(self) -> typing.Tuple[AutomatonArgs, typing.Dict[typing.Hashable, typing.Set]]:
        """make a AutomatonArgs of DFA from this NFA
        DFA is made by subset construction algorithm and contains unreachable states. To remove unreachable states, use DFA.shrinked().
        Returns:
            AutomatonArgs: the args of DFA
            typing.Dict[typing.Hashable, typing.Set]: the map from DFA state to NFA state"""
        ...

class E_NFA(NFA):
    def trans(self, string: Collection) -> typing.Set:
        current = self._moveon(epsilon, self._START) | {self._START}
        for alphabet in string:
            current = self._moveon(alphabet, current)
            current |= self._moveon(epsilon, current)
        return current    
    
    def log_trans(self, string: Collection) -> typing.Any:
        current = self._START
        for alphabet in string:
            print(current, f" --{alphabet}, {epsilon}--> ", end="")
            current = self._moveon(alphabet, current)
            current |= self._moveon(epsilon, current)
            print(current)
        return current


if __name__ == '__main__':
    import random
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

    "if '1' in string[-5:], then string is accepted."
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
    # initialize targets
    targets = []
    formerbinary = ["0", "1"]
    nextbinary = []
    for i in range(1 << 4):
        targets.extend(formerbinary)
        for former in formerbinary:
            for latter in ["0", "1"]:
                nextbinary.append(former + latter)
        formerbinary = nextbinary
        nextbinary = []

    for target in targets:
        assert a.judge(target) == ("1" in target[-5:])

    transitions = {
        "q0": {"0": {"q0"}, "1": {"q3"}, epsilon: {"q1"}},
        "q1": {"0": {"q1"}, "1": {"q2"}},
        "q2": {"0": {"q1"}, "1": {"q2"}},
        "q3": {"0": {"q4"}, "1": {"q0"}},
        "q4": {"0": {"q3"}, "1": {"q4"}}
    }
    start = "q0"
    finals = {"q0", "q1"}
    a = E_NFA(transitions, start, finals)

    for target in targets:
        try:
            assert a.judge(target) == (int(target, 2) % 2 == 0 or int(target, 2) % 3 == 0)
        except AssertionError:
            print(target, a.judge(target), (int(target, 2) % 2 == 0 or int(target, 2) % 3 == 0))
            a.log_trans(target)
            raise AssertionError