import uuid
from utils import Error, SyntaxAnalizerError
from treelib import Tree


def syntax_tree_node(func, self):
    def wrapper(*args, **kwargs):
        if 'scan' not in kwargs or kwargs['scan']:
            # Read new lexeme
            self.saved_lexeme = getattr(self, 'lexeme', "")
            self.lexeme = self.lexemas.pop(0)
            if self.lexeme == ";":
                self.lexeme = self.lexemas.pop(0)
        else:
            del kwargs['scan']
        # Add node to syntax tree
        node_name = func.__name__
        node_id = str(uuid.uuid1())

        if not self.branch:
            self.tree.create_node(node_name, node_id, data=self.lexeme)
        else:
            self.tree.create_node(node_name, node_id, parent=self.branch[-1], data=self.lexeme)

        self.branch.append(node_id)
        # Call function
        result = func(*args, **kwargs)
        # Go one level up
        self.branch.pop()
        # <empty>
        if result == "<empty>":
            self.lexemas.insert(0, self.lexeme)
            self.lexeme = self.saved_lexeme
            self.tree.remove_node(node_id)
        elif result is not None:
            self.tree.create_node(result, str(uuid.uuid1()), parent=node_id, data=result)
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

    def pretty_print(self):
        print("\nSyntax analyzer result:")
        self.tree.show(reverse=False)
        for error in self.errors:
            print(error)

    def error(self, text):
        error = Error(text, "Syntax", self.lexeme.row, self.lexeme.column)
        self.tree.create_node(str(error), str(uuid.uuid1()), parent=self.branch[-1])
        self.errors.append(error)
        raise SyntaxAnalizerError

    def expect(self, keyword, scan=False):
        if scan:
            self.lexeme = self.lexemas.pop(0)
        if self.lexeme != keyword:
            self.error("Expected %s" % keyword.upper())

    def __getattribute__(self, name):
        # Decorate every class method
        obj = object.__getattribute__(self, name)
        excluded_methods = ['error', 'analyze', 'expect', 'pretty_print']
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
            self.expect(".", scan=True)
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
        self.expect("end", scan=True)

    def declarations(self):
        self.constant_declarations(scan=False)
        self.variable_declarations()
        self.math_function_declarations()
        self.procedure_declaration()
        self.lexeme = self.lexemas.pop(0)

    def constant_declarations(self):
        if self.lexeme != "const":
            return "<empty>"
        self.constant_declarations_list()

    def constant_declarations_list(self):
        if self.lexemas[0] == "=":
            self.constant_declaration(scan=False)
        else:
            return "<empty>"
        while self.lexemas[1] == "=":
            self.constant_declarations_list()

    def constant_declaration(self):
        self.constant_identifier(scan=False)
        self.expect("=")
        self.constant()
        self.expect(";")

    def constant(self):
        if self.lexeme == '\'':
            self.complex_constant(scan=False)
        else:
            self.sign(scan=False)
            self.unsigned_constant()

    def variable_declarations(self):
        if self.lexeme == "var":
            self.declarations_list()
        else:
            return "<empty>"

    def declarations_list(self):
        if self.lexemas[0] == ',':
            self.declaration(scan=False)
            self.declarations_list()
        else:
            return "<empty>"

    def declaration(self):
        self.variable_identifier(scan=False)
        self.identifiers_list(scan=False)
        self.expect(":")
        self.attribute()
        self.attributes_list()

    def identifiers_list(self):
        if self.lexeme == ',':
            self.expect(',')
            self.variable_identifier()
            self.identifiers_list(scan=False)

    def attributes_list(self):
        possible_types = ['signal', 'complex', 'integer',
                          'float', 'blockfloat', 'ext', '[']
        if self.lexemas[0].value not in possible_types:
            return "<empty>"
        self.attribute()
        self.attributes_list()

    def attribute(self):
        possible_types = ['signal', 'complex', 'integer',
                          'float', 'blockfloat', 'ext']
        # <range>
        if self.lexeme == "[":
            self.range()
            self.expect("]")
            self.ranges_list()
        elif self.lexeme.value not in possible_types:
            self.error("Wrong variable type!")
        else:
            return self.lexeme

    def ranges_list(self):
        if self.lexeme != "[":
            return "<empty>"
        self.range()
        self.ranges_list()

    def range(self):
        self.unsigned_integer(scan=False)
        self.expect("..")
        self.unsigned_integer()

    def math_function_declarations(self):
        if self.lexeme == "deffunc":
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
        self.function_characteristic(scan=False)
        self.expect(";")

    def function_characteristic(self):
        self.expect("\\")
        self.unsigned_integer()
        self.expect(",")
        self.unsigned_integer()

    def procedure_declaration(self):
        if self.lexeme == "procedure":
            self.procedure(scan=False)
            self.procedure_declaration()
        else:
            return "<empty>"

    def procedure(self):
        self.expect("procedure")
        self.procedure_identifier()
        self.parameters_list(scan=False)
        self.expect(";")

    def parameters_list(self):
        if self.lexeme == "(":
            self.declarations_list()
            self.expect(")", scan=True)
            self.lexeme = self.lexemas.pop(0)
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
        self.variable_identifier()

        self.unsigned_integer()
        self.expect(";")

    def complex_constant(self):
        self.expect("'")
        self.complex_number()
        self.expect("'")
        self.lexeme = self.lexemas.pop(0)

    def unsigned_constant(self):
        self.unsigned_number(scan=False)

    def complex_number(self):
        self.left_part()
        self.right_part()

    def left_part(self):
        self.expression(scan=False)

    def right_part(self):
        self.expression(scan=False)

    def expression(self):
        result = ""
        while self.lexeme != '\\':
            result += self.lexeme.value
            self.lexeme = self.lexemas.pop(0)
        return result
    def constant_identifier(self):
        self.identifier(scan=False)

    def variable_identifier(self):
        self.identifier(scan=False)

    def procedure_identifier(self):
        self.identifier(scan=False)

    def function_identifier(self):
        self.identifier(scan=False)

    def identifier(self):
        result = self.lexeme
        self.lexeme = self.lexemas.pop(0)
        return result

    def unsigned_number(self):
        self.integer_part(scan=False)
        self.fractional_part()

    def integer_part(self):
        self.unsigned_integer(scan=False)

    def fractional_part(self):
        if self.saved_lexeme == "#":
            self.sign(scan=False)
            self.unsigned_integer()
        else:
            return "<empty>"

    def unsigned_integer(self):
        result = self.lexeme
        self.lexeme = self.lexemas.pop(0)
        return result

    def sign(self):
        if self.lexeme != '-' and self.lexeme != '+':
            return "<empty>"
        return self.lexeme
