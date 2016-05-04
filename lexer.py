from prettytable import PrettyTable

from tables import *
from utils import get_symbol_attribute, Symbol, Lexeme, EOFException


class LexicalAnalyzer:
    identifiers = {}
    constants = {}
    errors = []
    row = 1
    column = 0

    def add_lexeme(self, lexeme, lexeme_type):
        table = getattr(self, "%ss" % lexeme_type)

        if lexeme.value not in table:
            shift = 501 if lexeme_type == "constant" else 1001
            if lexeme.type:
                table[lexeme.value] = (shift + len(table), lexeme.type)
            else:
                table[lexeme.value] = shift + len(table)

            setattr(self, "%ss" % lexeme_type, table)
        return table[lexeme.value] if not isinstance(table[lexeme.value], tuple)\
                                   else table[lexeme.value][0]

    def read_symbol(self, f):
        # Read file symbol by symbol (and automatically lowercase)
        char = f.read(1).lower()
        if char == '\n':
            self.row += 1
            self.column = 1
        else:
            self.column += 1
        print(char, end="")
        if not char:
            raise EOFException
        return Symbol(char, get_symbol_attribute(char))

    def pretty_print(self):
        print("\nLexical analyzer result:")
        analyzer_result = PrettyTable(["Value", "Code", "Row", "Column"])
        for lexeme in self.result:
            analyzer_result.add_row([lexeme.value, lexeme.code, lexeme.row, lexeme.column])
        print(analyzer_result)

        print("\nConstants table:")
        const = PrettyTable(["Value", "Code"])
        for key, data in self.constants.items():
            const.add_row([key, data[0]])
        const.sort_key("Code")
        print(const.get_string(sortby="Code"))

        print("\nIdentifiers table:")
        ident = PrettyTable(["Name", "Code"])
        for key, data in self.identifiers.items():
            ident.add_row([key, data])
        print(ident.get_string(sortby="Code"))

        for error in self.errors:
            print(error)

    def __init__(self, *args, **kwargs):
        self.result = []
        with open("test.sig") as f:
            try:
                while True:
                    if not hasattr(self, 'cache'):
                        symbol = self.read_symbol(f)
                    else:
                        symbol = self.cache
                        del self.cache
                    lexeme = Lexeme(row=self.row, column=self.column)
                    silent = False  # Flag for suppressing output of current lexeme

                    while symbol.attr == 0:  # Whitespace
                        symbol = self.read_symbol(f)

                    if symbol.attr == 1:  # Constant
                        while symbol.attr == 1:
                            lexeme.value += symbol.value
                            symbol = self.read_symbol(f)
                        self.cache = symbol
                        lexeme.type = "INTEGER"
                        lexeme.code = self.add_lexeme(lexeme, "constant")

                    elif symbol.attr == 2:  # Identifier
                        while symbol.attr == 2 or symbol.attr == 1:
                            lexeme.value += symbol.value
                            symbol = self.read_symbol(f)
                        if lexeme.value not in keywords_table:
                            lexeme.code = self.add_lexeme(lexeme, 'identifier')
                        else:
                            lexeme.code = keywords_table[lexeme.value]
                        self.cache = symbol

                    elif symbol.attr == 3:  # Comment
                        try:
                            second_symbol = self.read_symbol(f)
                            if second_symbol.value != '*':
                                lexeme.value = '('
                                lexeme.code = delimiters['(']
                                self.cache = second_symbol
                            else:
                                silent = True
                                while symbol.value != ')':
                                    while symbol.value != '*':
                                        symbol = self.read_symbol(f)
                                    symbol = self.read_symbol(f)
                        except EOFException:
                            self.errors.append("Expected *) but end of file was found")

                    elif symbol.attr == 4:  # Delimiter
                        # Check for double delimiter
                        second_symbol = self.read_symbol(f)
                        dd = symbol.value + second_symbol.value
                        if dd in double_delimiters:
                            lexeme.code = double_delimiters[dd]
                            lexeme.value = dd
                        else:
                            lexeme.code = single_delimiters[symbol.value]
                            lexeme.value = symbol.value
                            self.cache = second_symbol
                    if symbol.attr == 5:  # Error
                        self.errors.append("Wrong symbol: %s" % symbol.value)
                        silent = True

                    if not silent:
                        self.result.append(lexeme)
            except EOFException:
                pass
