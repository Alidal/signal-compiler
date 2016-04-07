from prettytable import PrettyTable

from tables import *
from utils import get_symbol_attribute, Symbol, Lexeme, EOFException


class LexicalAnalyzer:
    code_arr = []
    identifiers = []
    constants = []

    # def add_to_constants_table(self):

    def read_symbol(self, f):
        # Read file symbol by symbol (and automatically lowercase)
        char = f.read(1).lower()
        if not char:
            raise EOFException
        return Symbol(char, get_symbol_attribute(symbol))

    def __init__(self, *args, **kwargs):
        with open("test.sig") as f:
            try:
                # Read new word
                symbol = self.read_symbol(f)
                lexeme = Lexeme("", 0)
                silent = False

                if symbol.attr == 0:  # Whitespaces
                    while symbol.attr == 0:
                        symbol = self.read_symbol(f)
                    silent = True
                elif symbol.attr == 1:  # Constant
                    while symbol.attr == 1:
                        symbol = self.read_symbol(f)
                        lexeme.value += symbol.value

                if not silent:
                    print(lexeme.code)
            except StopException:
                pass


if __name__ == '__main__':
    la = LexicalAnalyzer()
