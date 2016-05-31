from tables import delimiters


class CodeGenerator:
    stack = []
    program = []

    def __init__(self, identifiers, constants):
        self.identifiers = identifiers
        self.constants = constants

    def walk(self, tree):
        node = tree.get_node(tree.root)
        children = tree.is_branch(tree.root)
        if not children:
            if node.data != ":":  # A little hack
                self.stack.append(node.data)
            return

        # Iterate all successors of current node
        for node_id in children:
            self.walk(tree.subtree(node_id))
