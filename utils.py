from tables import whitespaces, digits, letters, delimiters


class Symbol:
    __slots__ = ["value", "attr"]

    def __init__(self, value, attr):
        self.value = value
        self.attr = attr


class Lexeme:
    __slots__ = ["value", "code", "type", "column", "row"]

    def __init__(self, value="", code=0, _type=None, row=0, column=0):
        self.value = value
        self.code = code
        self.type = _type
        self.column = column
        self.row = row

    def __eq__(self, lexeme):
        return self.value == lexeme

    def __ne__(self, other):
        return not self.__eq__(other)


class Error:
    __slots__ = ["text", "row", "column", "type"]

    def __init__(self, text="", _type=None, row=0, column=0):
        self.text = text
        self.type = _type
        self.column = column
        self.row = row

    def __str__(self):
        return "({}, {}) {} error: {}".format(self.row,
                                              self.column,
                                              self.type,
                                              self.text)


class EOFException(BaseException):
    pass


class SyntaxAnalizerError(BaseException):
    pass


def get_symbol_attribute(char):
    if char in whitespaces:
        return 0
    elif char in digits:
        return 1
    elif char in letters or char == '$':
        return 2
    elif char == "(":
        return 3
    elif char in delimiters:
        return 4
    else:
        return 5
