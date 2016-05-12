from utils import Lexeme, Error, SyntaxAnalizerError


class SyntaxAnalyzer:

    def __init__(self, lexemas, identifiers, constants):
        self.lexemas = lexemas
        self.identifiers = identifiers
        self.constants = constants

    def scan(self):
        self.cur_lexeme = self.lexemas.pop(0)

    def error(self, text):
        error = Error(text, "Syntax", self.cur_lexeme.row, self.cur_lexeme.column)
        self.errors.append(error)
        raise SyntaxAnalizerError

    def analyze(self):
        self.scan()
        try:
            self.program()
        except SyntaxAnalizerError():
            pass

    def program(self):
        if self.cur_lexeme == "program":
            self.scan()
            self.procedure_identifier()
            if self.cur_lexeme == ";":
                self.scan()
                self.block()
        elif self.cur_lexeme == "procedure":
            self.scan()
            self.procedure_identifier()
            self.parameters_list()
            if self.cur_lexeme == ";":
                self.scan()
                self.block()
        else:
            self.error("Expected PROGRAM or PROCEDURE keyword")

    def block(self):
        self.scan()
        self.declarations()
        if self.lexeme != "begin":
            self.error("Expected BEGIN keyword")
        self.statements_list()
        if self.lexeme != "end":
            self.error("Expected END keyword")

    def declarations(self):
        self.scan()
        self.constants_declarations()
        self.variable_declarations()
        self.math_function_declarations()
        self.procedure_declarations()

    def constant_declarations(self):
        if self.lexeme != "const":
            self.scan()
            return
        self.scan()
        self.constant_declarations_list()

    def constant_declarations_list(self):
        self.constant_declaration()
        self.constant_declarations_list()

    def constant_declaration(self):
        self.constant_identifier()
        if self.lexeme != "=":
            self.error("Expected '='")
        self.constant()
        if self.lexeme != ";":
            self.error("Expected ';'")

