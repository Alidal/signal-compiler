import uuid
import inspect
from utils import Error, SyntaxAnalizerError
from treelib import Tree


class SyntaxAnalyzer:

    def __init__(self, lexemas, identifiers, constants):
        self.lexemas = lexemas
        self.identifiers = identifiers
        self.constants = constants
        self.tree = Tree()
        self.branch = []

    def scan(self):
        self.lexeme = self.lexemas.pop(0)
        node_name = inspect.stack()[1][3]
        node_id = str(uuid.uuid1())
        if not self.branch:
            self.tree.create_node(node_name, node_id)
        else:
            self.tree.create_node(node_name, node_id, parent=self.branch[-1])
        self.branch.append(node_id)

    def empty(self):
        self.lexemas.insert(0, self.lexeme)
        self.tree.remove_node(self.branch.pop())

    def error(self, text):
        error = Error(text, "Syntax", self.lexeme.row, self.lexeme.column)
        self.errors.append(error)
        raise SyntaxAnalizerError

    def __getattribute__(self, name):
        obj = object.__getattribute__(self, name)
        excluded_methods = ['scan', 'empty', 'error']
        if callable(obj) and obj.__name__ not in excluded_methods:
            return syntax_tree_node(obj)
        else:
            return obj

    def analyze(self):
        try:
            self.program()
        except SyntaxAnalizerError():
            pass

    def program(self):
        self.scan()
        if self.lexeme == "program":
            self.procedure_identifier()
            if self.lexeme == ";":
                self.block()
        elif self.lexeme == "procedure":
            self.procedure_identifier()
            self.parameters_list()
            if self.lexeme == ";":
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
            self.empty()
            return
        self.scan()
        self.constant_declarations_list()

    def constant_declarations_list(self):
        self.constant_declaration()
        self.scan()
        if self.lexeme.code in self.identifiers and self.lexemas[0] == '=':
            self.constant_declarations_list()

    def constant_declaration(self):
        self.constant_identifier()
        self.scan()
        if self.lexeme != "=":
            self.error("Expected '='")
        self.constant()
        if self.lexeme != ";":
            self.error("Expected ';'")

    def constant(self):
        self.scan()
        if self.lexeme == '\'':
            self.complex_constant()
        else:
            # Remember about '-'
            self.unsigned_constant()

    def variable_declarations(self):
        self.scan()
        if self.lexeme == "VAR":
            self.declarations_list()
        else:
            self.empty()

    def declarations_list(self):
        self.scan()
        if self.lexemas[1] == ':':
            self.declaration()
            self.declarations_list()
        else:
            self.empty()

    def declaration(self):
        self.variable_identifier()
        self.identifiers_list()
        if self.lexeme != ':':
            self.error("Expected :")
        self.scan()

