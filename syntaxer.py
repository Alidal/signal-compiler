import uuid
from utils import Error, SyntaxAnalizerError
from treelib import Tree


def syntax_tree_node(func, self):
    def wrapper(*args, **kwargs):
        if 'scan' not in kwargs or kwargs['scan']:
            # Read new lexeme
            self.lexeme = self.lexemas.pop(0)
        else:
            del kwargs['scan']
        # Add node to syntax tree
        node_name = func.__name__
        node_id = str(uuid.uuid1())
        if not self.branch:
            self.tree.create_node(node_name, node_id)
        else:
            self.tree.create_node(node_name, node_id, parent=self.branch[-1])
        self.branch.append(node_id)
        # Call function
        result = func(*args, **kwargs)
        # Gone one level up
        last_id = self.branch.pop()
        # <empty>
        if result == "<empty>":
            self.lexemas.insert(0, self.lexeme)
            self.tree.remove_node(last_id)
        elif result is not None:
            self.tree.create_node(result, result, parent=self.branch[-1])
        return result
    return wrapper


class SyntaxAnalyzer:

    def __init__(self, lexemas, identifiers, constants):
        self.lexemas = lexemas
        self.identifiers = identifiers
        self.constants = constants
        self.tree = Tree()
        self.branch = []
        self.errors = []

    def error(self, text):
        error = Error(text, "Syntax", self.lexeme.row, self.lexeme.column)
        self.errors.append(error)
        raise SyntaxAnalizerError

    def expect(self, keyword):
        if self.lexeme != keyword:
            self.error("Expected %s" % keyword.upper())

    def __getattribute__(self, name):
        # Decorate every class method
        obj = object.__getattribute__(self, name)
        excluded_methods = ['error', 'analyze', 'expect']
        if callable(obj) and obj.__name__ not in excluded_methods:
            return syntax_tree_node(obj, self)
        else:
            return obj

    def analyze(self):
        try:
            self.program()
        except SyntaxAnalizerError:
            pass

    def program(self):
        if self.lexeme == "program":
            self.procedure_identifier()
            self.expect(";")
            self.block()
            self.expect(".")
        elif self.lexeme == "procedure":
            self.procedure_identifier()
            self.parameters_list()
            self.expect(";")
            self.block()
            self.expect(";")
        else:
            self.error("Expected PROGRAM or PROCEDURE keyword")

    def block(self):
        self.declarations(scan=False)
        self.expect("begin")
        self.statements_list()
        self.expect("end")

    def declarations(self):
        self.constant_declarations(scan=False)
        self.variable_declarations()
        self.math_function_declarations()
        self.procedure_declarations()

    def constant_declarations(self):
        if self.lexeme != "const":
            return "<empty>"
        self.constant_declarations_list()

    def constant_declarations_list(self):
        if self.lexemas[0] == "=":
            self.constant_declaration(scan=False)
        else:
            return "<empty>"
        while self.lexemas[0] == "=":
            self.constant_declarations_list()

    def constant_declaration(self):
        self.constant_identifier(scan=False)
        self.expect("=")
        self.constant()
        self.expect(";")

    def constant(self):
        if self.lexeme == '\'':
            self.complex_constant()
        else:
            # Remember about '-'
            self.unsigned_constant()

    def variable_declarations(self):
        if self.lexeme == "var":
            self.declarations_list()
        else:
            return "<empty>"

    def declarations_list(self):
        if self.lexemas[1] == ':':
            self.declaration()
            self.declarations_list()
        else:
            return "<empty>"

    def declaration(self):
        self.variable_identifier(scan=False)
        self.identifiers_list()
        self.expect(":")
        self.attribute()
        self.attributes_list()

    def attribute(self):
        possible_types = ['signal', 'complex', 'integer',
                          'float', 'blockfloat', 'ext']
        # <range>
        if self.lexeme == "[":
            self.range()
            self.ranges_list()
            self.expect("]")
        if self.lexeme.value not in possible_types:
            self.error("Wrong variable type!")

    def ranges_list(self):
        if self.lexeme != ",":
            return "<empty>"
        self.range()
        self.ranges_list()

    def range(self):
        self.unsigned_integer()
        self.expect("..")
        self.unsigned_integer()

    def math_function_declaration(self):
        if self.lexeme == "deffun":
            self.function_list()
        else:
            return "<empty>"

    def function_list(self):
        if self.lexemas[0] == "=":
            self.function(scan=False)
            self.function_list()
        else:
            return "<empty>"

    def function(self):
        self.function_identifier(scan=False)
        self.expect("=")
        self.expression()
        self.function_characteristic()
        self.expect(";")

    def function_characteristic(self):
        self.expect("\\")
        self.unsigned_integer()
        self.expect(",")
        self.unsigned_integer()

    def procedure_declaration(self):
        if self.lexeme == "procedure":
            self.procedure(scan=False)
            self.procedure_declarations()
        else:
            return "<empty>"

    def procedure(self):
        self.expect("procedure")
        self.procedure_identifier()
        self.parameters_list()
        self.expect(";")

    def parameters_list(self):
        if self.lexeme == "(":
            self.declarations_list()
            self.expect(")")
        else:
            return "<empty>"

    def statements_list(self):
        if self.lexeme == "link":
            self.statement(scan=False)
            self.statements_list()
        else:
            return "<empty>"

    def statement(self):
        self.expect("link")
        if self.lexeme == "in" or self.lexeme == "out":
            self.lexeme = self.lexemas.pop(0)
        self.variable_identifier()
        self.expect(";")

    def complex_constant(self):
        self.expect("'")
        self.complex_number()
        self.expect("'")
        self.lexeme = self.lexemas.pop(0)

    def unsigned_constant(self):
        self.unsigned_number()

    def complex_number(self):
        self.left_part()
        self.right_part()

    def left_part(self):
        # No <expression> in grammatic
        return

    def right_part(self):
        # No <expression> in grammatic
        return

    def constant_identifier(self):
        self.identifier(scan=False)

    def variable_identifier(self):
        self.identifier(scan=False)

    def procedure_identifier(self):
        self.identifier(scan=False)

    def function_identifier(self):
        self.identifier(scan=False)

    def identifier(self):
        result = self.lexeme.value
        self.lexeme = self.lexemas.pop(0)
        return result

    def unsigned_number(self):
        self.integer_part(scan=False)
        self.fractional_part()

    def integer_part(self):
        self.unsigned_integer(scan=False)

    def fractional_part(self):
        if self.lexeme == "#":
            self.sign()
            self.unsigned_integer()
        else:
            return "<empty>"

    def unsigned_integer(self):
        result = self.lexeme.value
        self.lexeme = self.lexemas.pop(0)
        return result

    def sign(self):
        if self.lexeme != '-' or self.lexeme != '+':
            self.error("Expected '-' or '+'")
