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

def evaluate(tree):
    if isinstance(tree, float):
        return tree
        
    if tree[0] == 'app':
        e1 = evaluate(tree[1])
        if isinstance(e1, tuple) and e1[0] == 'lam':
            body = e1[2]
            name = e1[1]
            arg = tree[2]
            rhs = substitute(body, name, arg)
            return evaluate(rhs)
        else:
            return ('app', e1, evaluate(tree[2]))
    elif tree[0] == 'plus':
        return evaluate(tree[1]) + evaluate(tree[2])
    elif tree[0] == 'minus':
        return evaluate(tree[1]) - evaluate(tree[2])
    elif tree[0] == 'times':
        return evaluate(tree[1]) * evaluate(tree[2])
    elif tree[0] == 'power':
        return evaluate(tree[1]) ** evaluate(tree[2])
    elif tree[0] == 'neg':
        return -1 * evaluate(tree[1])
    elif tree[0] == 'log':
        return float(math.log(evaluate(tree[1]), evaluate(tree[2])))
    elif tree[0] == 'num':
        return tree[1]
    elif tree[0] == 'parens':
        return evaluate(tree[1])
    else:
        return tree

class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

def substitute(tree, name, replacement):
    if isinstance(tree, float):
        return tree
        
    if tree[0] == 'var':
        if tree[1] == name:
            return replacement
        else:
            return tree
    elif tree[0] == 'lam':
        if tree[1] == name:
            return tree
        else:
            fresh_name = name_generator.generate()
            return ('lam', fresh_name, substitute(substitute(tree[2], tree[1], ('var', fresh_name)), name, replacement))
    elif tree[0] == 'app':
        return ('app', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] in ['plus', 'minus', 'times', 'power', 'log']:
        return (tree[0], substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'neg':
        return ('neg', substitute(tree[1], name, replacement))
    elif tree[0] == 'parens':
        return ('parens', substitute(tree[1], name, replacement))
    else:
        return tree

def linearize(ast):
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