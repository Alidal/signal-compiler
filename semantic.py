from tables import keywords_table


class CodeGenerator:
    stack = []
    program = []
    template = ""

    def __init__(self, identifiers, constants):
        self.identifiers = identifiers
        self.constants = constants

    def walk(self, tree):
        node = tree.get_node(tree.root)
        children = tree.is_branch(tree.root)

        # In tree terminals
        if not children:
            if node.data and node.data != ":":  # A little hack
                self.stack.append(node.data.value)
            return

        # Iterate all children of current node
        for node_id in reversed(children):
            self.walk(tree.subtree(node_id))

        if node.tag == "program":
            self.program = self.stack[:-1]
        elif node.tag == "constant_declaration":
            self.stack = ["{:10} equ {}".format(*reversed(self.stack))]
        elif node.tag == "unsigned_number":
            self.stack = [".".join(self.stack)]
        elif node.tag == "constant":
            self.stack = ["".join(self.stack)]
