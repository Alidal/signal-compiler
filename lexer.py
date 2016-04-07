from prettytable import PrettyTable

from tables import *
from utils import get_symbol_attribute, Symbol, Lexeme, EOFException


class LexicalAnalyzer:
    identifiers = {}
    constants = {}
    errors = []

    def add_lexeme(self, lexeme, lexeme_type):
        table = getattr(self, "%ss" % lexeme_type)

        if lexeme.value not in table:
            shift = 501 if lexeme_type == "constant" else 1001
            if lexeme.type:
                table[lexeme.value] = (shift + len(table), lexeme.type)
            else:
                table[lexeme.value] = shift + len(table)

            setattr(self, "%ss" % lexeme_type, table)
        return table[lexeme.value] if not isinstance(table[lexeme.value], tuple) else table[lexeme.value][0]

    def read_symbol(self, f):
        # Read file symbol by symbol (and automatically lowercase)
        char = f.read(1).lower()
        print(char, end="")
        if not char:
            raise EOFException
        return Symbol(char, get_symbol_attribute(char))

    def prerry_print(self):
        const = PrettyTable(["Value", "Code", "Type"])
        for key, data in self.constants.items():
            const.add_row([key, data[0], data[1]])
        const.sort_key("Code")
        print(const)

        ident = PrettyTable(["Name", "Code"])
        for key, data in self.identifiers.items():
            ident.add_row([key, data])
        ident.sort_key("Code")
        print(ident)

        print(self.errors)

    def __init__(self, *args, **kwargs):
        read_flag = True
        res = []
        with open("test.sig") as f:
            try:
                while True:
                    if read_flag:
                        # Read new word (problem with double delimiter)
                        symbol = self.read_symbol(f)
                    else:
                        symbol = self.cache
                        del self.cache
                    read_flag = True
                    lexeme = Lexeme("", 0)
                    silent = False

                    while symbol.attr == 0:  # Whitespaces
                        symbol = self.read_symbol(f)

                    if symbol.attr == 1:  # Constant
                        while symbol.attr == 1:
                            lexeme.value += symbol.value
                            symbol = self.read_symbol(f)

                        if "#" in lexeme.value:
                            lexeme.type = "FLOAT"
                            lexeme.value = float(lexeme.value.replace("#", "e"))
                        elif "\'" in lexeme.value:
                            lexeme.type = "COMPLEX"
                            lexeme.value = lexeme.value[1:-1]
                        else:
                            lexeme.type = "INTEGER"
                        lexeme.code = self.add_lexeme(lexeme, "constant")

                    elif symbol.attr == 2:  # Identifier
                        while symbol.attr == 2 or symbol.attr == 1:
                            lexeme.value += symbol.value
                            symbol = self.read_symbol(f)
                        if lexeme.value not in keywords_table:
                            lexeme.code = self.add_lexeme(lexeme, 'identifier')
                        else:
                            silent = True

                    elif symbol.attr == 3:  # Comment
                        try:
                            second_symbol = self.read_symbol(f)
                            if second_symbol.value != '*':
                                lexeme.code = ord('(')
                            else:
                                silent = True
                                while symbol.value != ')':
                                    while symbol.value != '*':
                                        symbol = self.read_symbol(f)
                                    symbol = self.read_symbol(f)
                        except EOFException:
                            self.errors.append("Expected *) but end of file was found")
                            pass

                    elif symbol.attr == 4:  # Delimiter (simple)
                        # Check for double delimiter
                        second_symbol = self.read_symbol(f)
                        dd = symbol.value + second_symbol.value
                        if dd in double_delimiters:
                            lexeme.code = double_delimiters[dd]
                            lexeme.value = dd
                        else:
                            read_flag = False
                            lexeme.code = single_delimiters[symbol.value]
                            lexeme.value = symbol.value
                            self.cache = second_symbol
                    if symbol.attr == 5:  # Error
                        self.errors.append("Wrong symbol: %s" % symbol.value)
                        silent = True

                    if not silent:
                        res.append(lexeme.code)
            except EOFException:
                pass
        print(res)


if __name__ == '__main__':
    la = LexicalAnalyzer()
    la.prerry_print()
