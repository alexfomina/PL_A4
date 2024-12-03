from lark import Lark, Transformer, Tree
import os
import math



def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    result_ast = evaluate(ast)
    result = linearize(result_ast)
    return result

parser = Lark(open("grammar.lark").read(), parser='lalr')

class LambdaCalculusTransformer(Transformer):
    def lam(self, args):
        name, body = args
        return ('lam', str(name), body)

    def app(self, args):
        new_args = [(arg.data, arg.children[0]) if isinstance(arg, Tree) and arg.data == 'float' else arg for arg in args]
        return ('app', *new_args)

    def var(self, args):
        token, = args
        return ('var', str(token))

    def NAME(self, token):
        return str(token)
    
    def plus(self, items):
        return ('plus', items[0], items[1])
    
    def minus(self, items):
        return ('minus', items[0], items[1])
    
    def times(self, items):
        return ('times', items[0], items[1])
    
    def power(self, items):
        return ('power', items[0], items[1])
    
    def neg(self, items):
        return ('neg', items[0])
    
    def log(self, items):
        return ('log', items[0], items[1])
    
    def parens(self, items):
        return ('parens', items[0])
    
    def num(self, items):
        return ('num', float(items[0]))
    
    def let(self, items):
        name, value, body = items
        return ('let', str(name), value, body)
    
    def letrec(self, items):
        name, value, body = items
        return ('letrec', str(name), value, body)
    
    def fix(self, items):
        return ('fix', items[0])
    
    def if_expr(self, items):
        cond, then_, else_ = items
        return ('if', cond, then_, else_)
    
    def leq(self, items): 
        return ('leq', items[0], items[1])
    
    def eq(self, items): 
        return ('eq', items[0], items[1])



class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return 'Var' + str(self.counter)

name_generator = NameGenerator()



def evaluate(tree):
    print(f"Evaluating: {linearize(tree)}")  # Log the tree in human-readable format
    
    if isinstance(tree, float):
        return tree

    if tree[0] == 'app':  # Application
        print(" -> Application detected.")
        func = evaluate(tree[1])
        print(f" -> Evaluated function: {linearize(func)}")
        arg = tree[2]  # Do not evaluate the argument yet
        print(f" -> Unevaluated argument: {linearize(arg)}")
        
        if isinstance(func, tuple) and func[0] == 'lam':  # If function is a lambda
            print(" -> Applying lambda.")
            param = func[1]
            body = func[2]
            print(f" -> Substituting {param} with {linearize(arg)} in {linearize(body)}")
            substituted = substitute(body, param, arg)  # Substitute without evaluating the argument
            print(f" -> Result after substitution: {linearize(substituted)}")
            return evaluate(substituted)  # Continue evaluating the resulting expression
        else:
            print(f" -> Resulting application: {linearize(('app', func, arg))}")
            return ('app', func, arg)  # Return partially reduced application

    # Handle other cases as before
    elif tree[0] == 'lam':  # Lambda
        print(" -> Lambda expression.")
        return tree  # Return the lambda as-is for now

    elif tree[0] == 'parens':  # Parentheses
        print(" -> Parenthesized expression.")
        return evaluate(tree[1])
    elif tree[0] == 'plus':  # Addition
        print(" -> Addition.")
        return evaluate(tree[1]) + evaluate(tree[2])
    elif tree[0] == 'minus':  # Subtraction
        print(" -> Subtraction.")
        return evaluate(tree[1]) - evaluate(tree[2])
    elif tree[0] == 'times':  # Multiplication
        print(" -> Multiplication.")
        return evaluate(tree[1]) * evaluate(tree[2])
    elif tree[0] == 'power':  # Exponentiation
        print(" -> Exponentiation.")
        return evaluate(tree[1]) ** evaluate(tree[2])
    elif tree[0] == 'neg':  # Negation
        print(" -> Negation.")
        return -evaluate(tree[1])
    elif tree[0] == 'log':  # Logarithm
        print(" -> Logarithm.")
        return math.log(evaluate(tree[1]), evaluate(tree[2]))
    elif tree[0] == 'num':  # Number
        print(f" -> Number: {tree[1]}")
        return tree[1]
    elif tree[0] == 'var':  # Variable
        print(f" -> Variable: {tree[1]}")
        return tree
    elif tree[0] == 'let':  # Let binding
        print(" -> Let binding.")
        value = evaluate(tree[2])
        print(f" -> Evaluating value: {linearize(value)}")
        body = substitute(tree[3], tree[1], value)
        print(f" -> Substituted body: {linearize(body)}")
        return evaluate(body)
    elif tree[0] == 'letrec':  # Recursive let binding
        print(" -> Recursive let binding.")
        fresh_name = name_generator.generate()
        print(f" -> Generated fresh name: {fresh_name}")
        value = substitute(tree[2], tree[1], ('var', fresh_name))
        print(f" -> Substituted value: {linearize(value)}")
        body = substitute(tree[3], tree[1], ('var', fresh_name))
        print(f" -> Substituted body: {linearize(body)}")
        return evaluate(body)
    elif tree[0] == 'fix':  # Fixed-point combinator
        print(" -> Fixed-point combinator.")
        return tree
    elif tree[0] == 'if':  # Conditional expression
        print(" -> Conditional expression.")
        cond = evaluate(tree[1])
        print(f" -> Evaluating condition: {linearize(cond)}")
        if cond:
            return evaluate(tree[2])
        else:
            return evaluate(tree[3])
    elif tree[0] == 'leq':  # Less than or equal
        print(" -> Less than or equal.")
        return evaluate(tree[1]) <= evaluate(tree[2])
    elif tree[0] == 'eq':  # Equality
        print(" -> Equality.")
        return evaluate(tree[1]) == evaluate(tree[2])
    

    else:
        print(f" -> Returning unprocessed tree: {linearize(tree)}")
        return tree

    
def substitute(tree, name, replacement):
    print(f"Substituting: Replace {name} with {linearize(replacement)} in {linearize(tree)}")
    
    if isinstance(tree, float):
        return tree

    if isinstance(tree, tuple):
        if tree[0] == 'var':
            if tree[1] == name:
                print(f" -> Variable matched: {name} replaced with {linearize(replacement)}")
                return replacement
            else:
                return tree
        elif tree[0] == 'lam':
            if tree[1] == name:
                print(f" -> Skipping substitution inside lambda for {name}.")
                return tree
            else:
                fresh_name = name_generator.generate()
                print(f" -> Renaming variable {tree[1]} to avoid capture: {fresh_name}")
                renamed_body = substitute(tree[2], tree[1], ('var', fresh_name))
                return ('lam', fresh_name, substitute(renamed_body, name, replacement))
        elif tree[0] == 'app':
            print(f" -> Substituting in application: {linearize(tree)}")
            return ('app', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
        # Handle other cases (arithmetic, control flow) as before, logging substitutions
        elif tree[0] in {'+', '-', '*', '/'}:
            left = substitute(tree[1], name, replacement)
            right = substitute(tree[2], name, replacement)
            return (tree[0], left, right)
        elif tree[0] == 'let':
            if tree[1] == name:
                print(f" -> Skipping substitution inside let for {name}.")
                return tree
            else:
                fresh_name = name_generator.generate()
                print(f" -> Renaming variable {tree[1]} to avoid capture: {fresh_name}")
                renamed_value = substitute(tree[2], tree[1], ('var', fresh_name))
                renamed_body = substitute(tree[3], tree[1], ('var', fresh_name))
                return ('let', fresh_name, substitute(renamed_value, name, replacement), substitute(renamed_body, name, replacement))
        elif tree[0] == 'letrec':
            if tree[1] == name:
                print(f" -> Skipping substitution inside letrec for {name}.")
                return tree
            else:
                fresh_name = name_generator.generate()
                print(f" -> Renaming variable {tree[1]} to avoid capture: {fresh_name}")
                renamed_value = substitute(tree[2], tree[1], ('var', fresh_name))
                renamed_body = substitute(tree[3], tree[1], ('var', fresh_name))
                return ('letrec', fresh_name, substitute(renamed_value, name, replacement), substitute(renamed_body, name, replacement))
        elif tree[0] == 'fix':
            print(f" -> Substituting in fix: {linearize(tree)}")
            return ('fix', substitute(tree[1], name, replacement))
        elif tree[0] == 'if':
            cond = substitute(tree[1], name, replacement)
            then_ = substitute(tree[2], name, replacement)
            else_ = substitute(tree[3], name, replacement)
            return ('if', cond, then_, else_)
        elif tree[0] == 'leq':
            left = substitute(tree[1], name, replacement)
            right = substitute(tree[2], name, replacement)
            return ('leq', left, right)
        elif tree[0] == 'eq':
            left = substitute(tree[1], name, replacement)
            right = substitute(tree[2], name, replacement)
            return ('eq', left, right)
        
        
    return tree



def linearize(ast):
    if ast is None:
        return 'error: invalid ast'
    if isinstance(ast, float):
        return str(ast)
        
    if ast[0] == 'var':
        return ast[1]
    elif ast[0] == 'lam':
        return "(" + "\\" + ast[1] + "." + linearize(ast[2]) + ")"
    elif ast[0] == 'app':
        return "(" + linearize(ast[1]) + " " + linearize(ast[2]) + ")"
    elif ast[0] == 'plus':
        return "(" + linearize(ast[1]) + " + " + linearize(ast[2]) + ")"
    elif ast[0] == 'minus':
        return "(" + linearize(ast[1]) + " - " + linearize(ast[2]) + ")"
    elif ast[0] == 'times':
        return "(" + linearize(ast[1]) + " * " + linearize(ast[2]) + ")"
    elif ast[0] == 'power':
        return "(" + linearize(ast[1]) + " ^ " + linearize(ast[2]) + ")"
    elif ast[0] == 'neg':
        return "(-" + linearize(ast[1]) + ")"
    elif ast[0] == 'log':
        return "(log(" + linearize(ast[1]) + ", " + linearize(ast[2]) + "))"
    elif ast[0] == 'parens':
        return linearize(ast[1])
    elif ast[0] == 'num':
        return str(ast[1])
    elif ast[0] == 'let':
        return "(let " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"
    elif ast[0] == 'letrec':
        return "(letrec " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"
    elif ast[0] == 'fix':
        return "(fix " + linearize(ast[1]) + ")"
    elif ast[0] == 'if':
        return "(if " + linearize(ast[1]) + " then " + linearize(ast[2]) + " else " + linearize(ast[3]) + ")"
    elif ast[0] == 'leq':
        return "(" + linearize(ast[1]) + " <= " + linearize(ast[2]) + ")"
    elif ast[0] == 'eq':
        return "(" + linearize(ast[1]) + " == " + linearize(ast[2]) + ")"
    
    else:
        return str(ast)

def main():
    import sys
    if len(sys.argv) != 2:
        sys.exit(1)

    input_arg = sys.argv[1]

    if os.path.isfile(input_arg):
        with open(input_arg, 'r') as file:
            expression = file.read()
    else:
        expression = input_arg

    result = interpret(expression)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()