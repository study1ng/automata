import sys
sys.path.append("../automata")

from collections.abc import Container
import typing


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




def _any_in(container1: Container, container2: Container) -> bool:
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


def _get_end_of_iterator(g: typing.Iterable):
    """Get g[-1]. Don't use infinite generator as g"""

    former = None
    for element in g:
        former = element
    return former


def _bit_search(container: Container) -> typing.Generator:
    for i in range(1 << (len(container) - 1)):
        yield _get_elements_from_bit(container, i)


def _get_elements_from_bit(container: Container, bit: int) -> typing.Set:
    return {container[i] for i in range(len(bin(bit))) if bit & (1 << i)}
