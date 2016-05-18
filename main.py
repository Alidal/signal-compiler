from lexer import LexicalAnalyzer
from syntaxer import SyntaxAnalyzer

if __name__ == "__main__":
    lexer = LexicalAnalyzer()
    lexer.analyze()
    lexer.pretty_print()
    syntaxer = SyntaxAnalyzer(lexer.result, lexer.identifiers, lexer.constants)
    syntaxer.analyze()
