from tables import *


class Symbol:
    __slots__ = ["value", "attr"]

    def __init__(self, value, attr):
        self.value = value
        self.attr = attr


class Lexeme:
    __slots__ = ["value", "code", "type"]

    def __init__(self, value, code, _type=None):
        self.value = value
        self.code = code
        self.type = _type


class EOFException(Exception):
    pass


def get_symbol_attribute(char):
    if char in whitespaces:
        return 0
    elif char in digits or char in signs:
        return 1
    elif char in letters:
        return 2
    elif char == "(":
        return 3
    elif char in delimiters:
        return 4
    else:
        return 5
