import uuid
import inspect
from utils import Error, SyntaxAnalizerError
from treelib import Node, Tree


class SyntaxAnalyzer:

    def __init__(self, lexemas, identifiers, constants):
        self.lexemas = lexemas
        self.identifiers = identifiers
        self.constants = constants
        self.tree = Tree()
        self.parent = None

    def scan(self):
        self.cur_lexeme = self.lexemas.pop(0)
        node_name = inspect.stack()[1][3]
        node_id = str(uuid.uuid1())
        self.tree.create_node(node_name, node_id, parent=self.parent)
        self.parent = node_id

    def error(self, text):
        error = Error(text, "Syntax", self.cur_lexeme.row, self.cur_lexeme.column)
        self.errors.append(error)
        raise SyntaxAnalizerError

    def analyze(self):
        try:
            self.program()
        except SyntaxAnalizerError():
            pass

    def program(self):
        self.scan()
        if self.cur_lexeme == "program":
            self.procedure_identifier()
            if self.cur_lexeme == ";":
                self.block()
        elif self.cur_lexeme == "procedure":
            self.procedure_identifier()
            self.parameters_list()
            if self.cur_lexeme == ";":
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
            return  # <empty>
        self.scan()
        self.constant_declarations_list()

    def constant_declarations_list(self):
        self.constant_declaration()
        self.scan()
        if self.lexeme.code in self.identifiers:
            self.constant_declarations_list()

    def constant_declaration(self):
        # ToDo: empty
        self.constant_identifier()
        if self.lexeme != "=":
            self.error("Expected '='")
        self.constant()
        if self.lexeme != ";":
            self.error("Expected ';'")

    def constant(self):
        self.scan()
        if self.lexeme == '-':
            
