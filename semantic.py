class CodeGenerator:
    stack = []
    program = []
    template = ""

    def __init__(self, identifiers, constants):
        self.identifiers = identifiers
        self.constants = constants

    def get_current_template(self, node):
        if node.tag == "program":
            pass

    def walk(self, tree):
        node = tree.get_node(tree.root)
        children = tree.is_branch(tree.root)
        # In tree terminals
        if not children:
            if node.data != ":":  # A little hack
                self.stack.append(node.data)
            return

        # Iterate all children of current node
        for node_id in children:
            self.walk(tree.subtree(node_id))

        self.get_current_template(node)