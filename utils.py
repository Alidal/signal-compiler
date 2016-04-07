from tables import *
from collections import namedtuple


class Symbol:
    __slots__ = ["value", "attr"]

    def __init__(self, value, attr):
        self.value = value
        self.attr = attr


class Lexeme:
    __slots__ = ["value", "code"]

    def __init__(self, value, code):
        self.value = value
        self.code = code
Symbol = namedtuple("value", "attr")
Lexeme = namedtuple("value", "cpde")


class EOFException(Exception):
    pass


def get_symbol_attribute(char):
    if char in whitespaces:
        return 0
    elif char in numbers:
        return 1
    elif char in letters:
        return 2
    elif char == "(":
        return 3
    elif char in delimiters + signs:
        return 4
    else:
        return 5


# def get_lexeme_code(lexeme, lexeme_type):
#     if lexeme_type == 1:
#         return
