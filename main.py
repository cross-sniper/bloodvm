import os
import re, sys
from types import NoneType


def load(file: str) -> tuple[dict[int, dict], int]:
    lines = {}
    with open(file) as f:
        code = f.read().strip().split("\n")
        maxPc = 0
        i = 0

        # Parse each line
        while i < len(code):
            line = code[i].split("#", maxsplit=1)[0]
            parts = line.split()

            if parts:
                command = parts[0]
                if command == "var":
                    # Variable declaration, possibly with an expression
                    name = parts[1]
                    if "{" in line:
                        expression = re.search(r"{(.+?)}", line).group(1)
                        lines[i] = {
                            "type": "var_expr",
                            "name": name,
                            "expression": expression,
                        }
                    else:
                        value = int(parts[2])
                        lines[i] = {"type": "var", "name": name, "value": value}
                elif command == "print":
                    # Print statement with expression
                    expression = re.search(r"{(.+?)}", line).group(1)
                    lines[i] = {"type": "print", "expression": expression}
                elif command == "if":
                    # Conditional statement
                    condition = re.search(r"{(.+?)}", line).group(1)
                    lines[i] = {"type": "if", "condition": condition, "do_line": i + 1}
                elif command == "jmp":
                    # Jump to a specific line
                    target = " ".join(parts[1:])
                    expression = re.search(r"{(.+?)}", target)
                    if expression:
                        expression = expression.group(1)
                    else:
                        expression = target  # fallback
                    lines[i] = {"type": "jmp", "target": expression}
                elif command == "label":
                    # Jump to a specific line
                    target = parts[1]
                    lines[i] = {"type": "label", "name": target, "line": i}
                elif command == "end":
                    # End of a conditional block
                    lines[i] = {"type": "end"}
            else:
                # whitespace is the same as empty, since we needed to enable the ability to jump somewhere
                # even it there is nothing there
                lines[i] = {"type": "whitespace"}
            i += 1
            maxPc = i

    return (lines, maxPc)


def run(program, maxPc):
    variables = {}
    labels = {}
    pc = 0
    # print(program)

    def zeval(expression: str, variables: dict):
        parts = []
        current = ""

        # Step 1: Parse the expression
        for char in expression:
            if char.isspace():  # Skip whitespace
                continue
            if char in "+-*/()><=":  # Operators and parentheses
                if current:
                    parts.append(current)  # Add any accumulated variable/number
                    current = ""
                parts.append(char)  # Add the operator or parenthesis
            else:
                current += char  # Accumulate characters for variable or number

        if current:  # Add the last accumulated variable/number
            parts.append(current)

        # print("Parsed parts:", parts)

        # Step 2: Evaluate the expression
        def eval_parts(parts):
            stack = []
            postfix = []
            precedence = {"+": 1, "-": 1, "*": 2, "/": 2, ">": 0, "<": 0, "=": 0}

            # Convert infix to postfix using the Shunting Yard algorithm
            for part in parts:
                if (
                    part.isidentifier()
                    or part.isnumeric()
                    or part.startswith("$")
                    or part.startswith(":")
                ):  # Check if it's a variable or a number
                    postfix.append(part)
                elif part in precedence:
                    while (
                        stack
                        and stack[-1] in precedence
                        and precedence[stack[-1]] >= precedence[part]
                    ):
                        postfix.append(stack.pop())
                    stack.append(part)
                elif part == "(":
                    stack.append(part)
                elif part == ")":
                    while stack and stack[-1] != "(":
                        postfix.append(stack.pop())
                    stack.pop()  # Remove the '(' from stack

            while stack:
                postfix.append(stack.pop())

            # print(f"Postfix notation: {postfix} {stack}")

            # Evaluate the postfix expression
            eval_stack = []
            try:
                for part in postfix:
                    if part.isnumeric():
                        eval_stack.append(float(part))  # Push number
                    elif part.isidentifier() or part.startswith("$"):
                        eval_stack.append(variables.get(part, 0))  # Push variable value
                    elif part.startswith(":"):
                        eval_stack.append(labels.get(part, 0))  # Push variable value
                    else:
                        if part == "+":
                            b = eval_stack.pop()
                            a = eval_stack.pop()
                            eval_stack.append(a + b)
                        elif part == "-":  # handle "-<number>"
                            b = eval_stack.pop()
                            a = eval_stack.pop()
                            eval_stack.append(a - b)
                        elif part == "*":
                            b = eval_stack.pop()
                            a = eval_stack.pop()
                            eval_stack.append(a * b)
                        elif part == "/":
                            b = eval_stack.pop()
                            a = eval_stack.pop()
                            eval_stack.append(a / b)
                        elif part == ">":
                            b = eval_stack.pop()
                            a = eval_stack.pop()
                            eval_stack.append(int(a > b))
                        elif part == "<":
                            b = eval_stack.pop()
                            a = eval_stack.pop()
                            eval_stack.append(int(a < b))
                        elif part == "=":
                            b = eval_stack.pop()
                            a = eval_stack.pop()
                            eval_stack.append(int(a == b))
            except Exception as e:
                print(
                    f"\n\nerror:{e}\n\nstack: {stack}\n\nvariables: {variables}\n\nlabels: {labels}"
                )
                exit(1)

            return eval_stack[-1] if eval_stack else None

        result = eval_parts(parts)
        # print("Evaluation result:", result)
        return result

    while pc < maxPc:
        variables["$line$"] = pc

        # this allows us to do some math, like "jmp {$line$ - 2}"
        instruction = program[pc]

        if instruction["type"] == "var":
            # Simple variable assignment
            variables[instruction["name"]] = instruction["value"]

        elif instruction["type"] == "var_expr":
            # Evaluate expression for variable assignment
            expression = instruction["expression"]
            variables[instruction["name"]] = zeval(expression, variables)

        elif instruction["type"] == "print":
            # Evaluate and print expression
            expression = instruction["expression"]
            try:
                result = zeval(expression, variables)
                print(result)
            except Exception as e:
                print(f"Error evaluating expression {expression}: {e}")
                exit(1)

        elif instruction["type"] == "if":
            # Evaluate condition
            condition = instruction["condition"]
            if not zeval(condition, variables):
                # Skip to end of the if block
                x = pc
                d = {"type": "whitespace"}

                while pc <= maxPc:
                    d = program[pc]
                    if d["type"] == "end":
                        break
                    pc += 1
                else:
                    print(  # this was a atempt of making it print the error message like gcc, with something that you can follow on a ide(line error leading to where it happened)
                        f'did you add a "end" to complete this "if" {os.path.abspath("main.tt")}:{x}',
                        file=sys.stderr,
                    )
                    exit(1)
        elif instruction["type"] == "label":
            name = instruction["name"]
            line = instruction["line"]
            labels[f":{name}:"] = line
        elif instruction["type"] == "jmp":
            condition = instruction["target"]

            # Jump to a specified line and ensure it's a valid integer
            target_pc = zeval(condition, variables)
            if isinstance(target_pc, float):
                target_pc = int(target_pc)
            if target_pc is None or not isinstance(target_pc, int):
                print(f"Error: Invalid jump target: {condition}", file=sys.stderr)
                exit(1)

            # If the target is valid, update pc
            pc = target_pc
            continue

        # Move to next line unless skipping
        pc += 1


if __name__ == "__main__":
    print("LuminentVortex - v1")
    if len(sys.argv) < 2:
        print("you need to pass a file")
        exit(1)
    else:
        program, maxPc = load(sys.argv[1])
        run(program, maxPc)
