from tables import keywords_table


class CodeGenerator:
    stack = []
    program = []

    def __init__(self, identifiers, constants):
        self.identifiers = identifiers
        self.constants = constants

    def pretty_print(self):
        print("\n".join(self.program))

    def walk(self, tree):
        node = tree.get_node(tree.root)
        children = tree.is_branch(tree.root)

        # In tree terminals
        if not children:
            if node.data and node.data != ":":  # A little hack
                self.stack.append(node.data.value)
            return

        # Iterate all children of current node
        node_string = ""
        for i, node_id in enumerate(children):
            self.walk(tree.subtree(node_id))

            if node.tag == "program":
                self.stack = []
            elif node.tag == "constant_declaration":
                if i == 0 and len(children) > 1:
                    node_string = self.stack.pop()
                else:
                    node_string += " equ {}".format(*reversed(self.stack))
                    self.program.append(node_string)
                    self.stack = []
            elif node.tag == "constant":
                if i == 0 and len(children) > 1:
                    node_string = self.stack.pop()
                else:
                    node_string += "".join(self.stack)
                    self.stack = [node_string]
            elif node.tag == "unsigned_number":
                self.stack = [".".join(self.stack)]
            elif node.tag == "range":
                if i == 0:
                    node_string = self.stack.pop()
                else:
                    start = int(node_string)
                    end = int(self.stack.pop())
                    numbers = [str(i) for i in range(start, end)]
                    node_string = ",".join(numbers)
                    self.stack.append(node_string)

        if node.tag == "declaration":
            half = int(len(self.stack) / 2)
            variables = self.stack[:half]
            types = self.stack[half:]
            if len(variables) != len(types):
                self.error("blah")

            for i, var in enumerate(variables):
                types_table = {
                    'integer': 'dw',
                    'float': 'dd',
                    'signal': 'db',
                    'blockfloat': 'dq',
                }
                type = types[i]
                if type not in types_table:
                    self.program.append("{:5} dw {}".format(var, type))
                else:
                    self.program.append("{:5} {} ?".format(var, types_table[type]))
            self.stack = []
        elif node.tag == "procedure_identifier":
            self.program.append(self.stack.pop().upper() + ":")
