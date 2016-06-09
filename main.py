from lexer import LexicalAnalyzer
from syntaxer import SyntaxAnalyzer
from semantic import CodeGenerator

if __name__ == "__main__":
    lexer = LexicalAnalyzer()
    lexer.analyze()
    lexer.pretty_print()

    syntaxer = SyntaxAnalyzer(lexer.result, lexer.identifiers, lexer.constants)
    syntaxer.analyze()
    syntaxer.pretty_print()

    code_generator = CodeGenerator(lexer.identifiers, lexer.constants)
    try:
        code_generator.walk(syntaxer.tree)
    except:
        pass
    code_generator.pretty_print()
