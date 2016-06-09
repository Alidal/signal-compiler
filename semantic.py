from utils import Error


class CodeGenerator:
    stack = []
    code = []
    data = []
    errors = []
    variables = {}
    proc_names = []

    def __init__(self, identifiers, constants):
        self.identifiers = identifiers
        self.constants = constants

    def pretty_print(self):
        print("DATA SEGMENT")
        print(" ", "\n  ".join(self.data))
        print("DATA ENDS")
        print("\nCODE SEGMENT")
        print("\n".join(self.code))
        print("%s ENDS" % self.prog_name[:-1])
        print("CODE ENDS")
        for error in self.errors:
            print(error)

    def error(self, text, row, column):
        error = Error(text, "Semantic", row, column)
        self.errors.append(error)
        raise Exception

    def walk(self, tree):
        node = tree.get_node(tree.root)
        children = tree.is_branch(tree.root)

        # In tree terminals
        if not children:
            if node.data and node.data != ":":  # A little hack
                try:
                    self.stack.append(node.data.value)
                except:
                    self.stack.append(node.data)
            return

        # Iterate all children of current node
        node_string = ""
        for i, node_id in enumerate(children):
            self.walk(tree.subtree(node_id))

            if node.tag == "program":
                if self.stack:
                    self.code.extend(self.stack)
                    self.prog_name = self.stack[0]
                # Delete prog name from stack
                self.stack = []
            elif node.tag == "constant_declaration":
                if i == 0 and len(children) > 1:
                    node_string = self.stack.pop()
                else:
                    node_string += " equ {}".format(*reversed(self.stack))
                    self.data.append(node_string)
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

        if node.tag == "variable_declarations":
            half = int(len(self.stack) / 2)
            variables = self.stack[:half]
            types = self.stack[half:]
            if len(variables) != len(types):
                self.error("Not enough variables or types", node.data.row, node.data.column)

            for i, var in enumerate(variables):
                is_signal = False
                types_table = {
                    'integer': 'dw',
                    'float': 'dd',
                    'blockfloat': 'dq',
                }
                _type = types[i]
                if _type.startswith("signal"):
                    _type = _type.split()[1]
                    is_signal = True
                # Add to variables table
                if var in self.variables or var in self.proc_names:
                    self.error("Redefinition of variable %s" % var, node.data.row, node.data.column)
                self.variables[var] = {
                    'type': _type,
                    'is_signal': is_signal
                }

                if _type not in types_table:
                    self.data.append("{:5} dw {}".format(var, _type))
                else:
                    self.data.append("{:5} {} ?".format(var, types_table[_type]))
            self.stack = []
        elif node.tag == "function":
            name = self.stack[0]
            operation = self.stack[1]
            start = self.stack[2]
            end = self.stack[3]
            size = int(end) - int(start)
            var = "{:5} db {} dup(?)".format(name, size)
            self.data.append(var)
            var = """; INIT DEFFUNC
mov cx,{0}
mov si,0
@loop_{1}:
    mov bx, si{2}
    mov ARRAY1[si],bx
    inc si
loop @loop_{1}
            """.format(size, name, operation.split('i')[1])
            self.code.append(var)
            self.stack = []
        elif node.tag == "statement":
            operation = self.stack[1]
            var = self.stack[0]
            port = int(self.stack[2])
            self.stack = []
            # Check if variable was declared
            if var not in self.variables:
                self.error("Unknown variable %s" % var, node.data.row, node.data.column)
            # Check if variable is SIGNAL
            if not self.variables[var]['is_signal']:
                self.error("Variable %s should have SIGNAL type modifier" % var, node.data.row, node.data.column)

            if operation == "in":
                self.code.append("{} {},{}".format(operation, var, port))
            else:
                self.code.append("{} {},{}".format(operation, port, var))
        elif node.tag == "procedure":
            procedure_text = self.stack.pop(0)
            half = int(len(self.stack) / 2)
            variables = self.stack[:half][::-1]
            types = self.stack[half:][::-1]
            cur_shift = 8
            if len(variables) != len(types):
                self.error("Not enough variables or types", node.data.row, node.data.column)
            for i, var in enumerate(variables):
                is_signal = False
                types_table = {
                    'integer': 4,
                    'float': 8,
                    'blockfloat': 16,
                }
                _type = types[i]
                if _type.startswith("signal"):
                    _type = _type.split()[1]
                    is_signal = True
                # Add to variables table
                if var in self.variables or var in self.proc_names:
                    self.error("Redefinition of variable %s" % var, node.data.row, node.data.column)

                self.variables[var] = {
                    'type': _type,
                    'is_signal': is_signal
                }
                procedure_text += "\n{:5} equ [EBP+{}]".format(var, cur_shift)
                cur_shift += types_table[_type]
            procedure_text += """
push ebp
mov ebp,esp
sub esp,16

add esp,16
pop ebp
ret"""
            self.code = [procedure_text] + self.code
            self.stack = []

        elif node.tag == "procedure_identifier":
            proc_name = self.stack.pop()
            if proc_name in self.variables or proc_name in self.proc_names:
                self.error("Redefinition of variable %s" % proc_name, node.data.row, node.data.column)
            self.proc_names.append(proc_name)
            self.stack.append("@{}:".format(proc_name.upper()))
