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

    def prog(self, items):
        return ('prog', items[0], items[1])

    def hd(self, items):
        return ('hd', items[0])

    def tl(self, items):
        return ('tl', items[0])

    def nil(self, items):
        return ('nil',)

    def cons(self, items):
        return ('cons', items[0], items[1])


class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return 'Var' + str(self.counter)

name_generator = NameGenerator()


# helper function to find variables in a tree
def variables_in(tree):
    if isinstance(tree, (float, int)):
        return set()
    if isinstance(tree, tuple):
        if tree[0] == 'var':
            return {tree[1]}
        elif tree[0] == 'lam':
            param, body = tree[1], tree[2]
            return variables_in(body) - {param}  # Exclude bound variable
        elif tree[0] in {'app', 'plus', 'minus', 'times', 'power', 'neg', 'log', 'if', 'leq', 'eq'}:
            return variables_in(tree[1]) | variables_in(tree[2])
    return set()


# helper function to normalize variables
def normalize_variables(tree, original_param=None):
    if isinstance(tree, (float, int)):
        return tree
    if isinstance(tree, tuple):
        if tree[0] == 'lam':
            param, body = tree[1], tree[2]
            if original_param and param == original_param:
                # Skip renaming if it's the same parameter
                return ('lam', param, normalize_variables(body, original_param))
            return ('lam', param, normalize_variables(body, original_param))
        elif tree[0] in {'app', 'plus', 'minus', 'times', 'power', 'neg', 'log', 'if', 'leq', 'eq'}:
            return (tree[0], normalize_variables(tree[1], original_param), normalize_variables(tree[2], original_param))
    return tree


def evaluate(tree):
    
    if isinstance(tree, (float, int)):
        return tree

    # app
    if tree[0] == 'app':  # Application
        func = evaluate(tree[1])
        arg = tree[2]  # Do not evaluate the argument yet
        
        if isinstance(func, tuple) and func[0] == 'lam':  # If function is a lambda
            param = func[1]
            body = func[2]
            substituted = substitute(body, param, arg)  # Substitute without evaluating the argument
            return evaluate(substituted)  # Continue evaluating the resulting expression
        else:
            return ('app', func, arg)  # Return partially reduced application
    
    # lambda 
    elif tree[0] == 'lam':  
        #print(" -> Lambda expression.")
        return tree  # Return the lambda as-is for now

    # parentheses
    elif tree[0] == 'parens':  
        #print(" -> Parenthesized expression.")
        return evaluate(tree[1])
    
    # Addition
    elif tree[0] == 'plus':  
        #print(" -> Addition.")
        return evaluate(tree[1]) + evaluate(tree[2])
    
    # subtraction
    elif tree[0] == 'minus':
        #print(" -> Subtraction.")
        # return evaluate(tree[1]) - evaluate(tree[2])
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise TypeError(f"Cannot subtract non-numeric values: {left} - {right}")
        return left - right
    
    # multiplication
    elif tree[0] == 'times':  
    
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise TypeError(f"Cannot multiply non-numeric values: {left} * {right}")
        return left * right


    # Exponentiation
    elif tree[0] == 'power': 
        #print(" -> Exponentiation.")
        return evaluate(tree[1]) ** evaluate(tree[2])
    
    # negation
    elif tree[0] == 'neg': 
        #print(" -> Negation.")
        return -evaluate(tree[1])
    
    # logarithm
    elif tree[0] == 'log':
        #print(" -> Logarithm.")
        return math.log(evaluate(tree[1]), evaluate(tree[2]))
    
    # number
    elif tree[0] == 'num':
        #print(f" -> Number: {tree[1]}")
        return tree[1]
    
    # variable
    elif tree[0] == 'var': 
        #print(f" -> Variable: {tree[1]}")
        # var_name = tree[1]
        # if var_name == 'log':
        #     return math.log
        return tree
    
    # let
    # DONT CHANGE - works
    elif tree[0] == 'let':  # Let binding
        #print(" -> Let binding.")
        _, name, value, body = tree
        value_eval = evaluate(value)
        # print(f" -> substituting {name} with {linearize(value_eval)} in {linearize(body)}")
        substituted = substitute(body, name, value_eval)
        return evaluate(substituted)
    
    # letrec
    # DON"T CHANGE
        # needs work, deep recursion happens with bigger equations
    elif tree[0] == 'letrec':  # Recursive let binding
       
        # return result
        name, value, body = tree[1], tree[2], tree[3]
        fixed_point = ('fix', ('lam', name, value))
        evaluated_fixed_point = evaluate(fixed_point)
        substituted_body = substitute(body, name, evaluated_fixed_point)
        #print(f"substituted_body: {linearize(substituted_body)}")
        return evaluate(substituted_body)

    # fixed-point combinator aka fix
    # DON'T CHANGE
        # may need modifying for letrec's deep recursion with bigger equations
    elif tree[0] == 'fix':  # Fixed-point combinator
        #print(" -> Fixed-point combinator.")
        _, func = tree
        func_evaluated = evaluate(func)
        if func_evaluated[0] == 'lam':
            param = func_evaluated[1]
            body = func_evaluated[2]
            #print(f" -> Applying fix to: {linearize(func_evaluated)}")
            substituted = substitute(body, param, tree)  # Substitute f with fix (f)
            #print(f" -> Substituted body before normalization: {linearize(substituted)}")
            return evaluate(substituted)  # Directly evaluate the substituted body
        else:
            raise ValueError("fix must be applied to a lambda function.")


    # if 
    elif tree[0] == 'if':  # Conditional expression
        #print(" -> Conditional (if-then-else).")
        _, condition, then_branch, else_branch = tree
        condition_value = evaluate(condition)
        if condition_value != 0:  # Treat non-zero as "true"
            #print(f" -> Condition is true; evaluating then-branch.")
            return evaluate(then_branch)
        else:
            #print(f" -> Condition is false; evaluating else-branch.")
            return evaluate(else_branch)
    
    # leq 
    elif tree[0] == 'leq':
        #print(" -> Less or equal comparison.")
        _, left, right = tree
        return 1 if evaluate(left) <= evaluate(right) else 0
    
    # eq
    # elif tree[0] == 'eq': 
    #     #print(" -> Equality comparison.")
    #     _, left, right = tree
    #     return 1 if evaluate(left) == evaluate(right) else 0
    elif tree[0] == 'eq':  # Equality operator
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        
        # Handle list comparison
        if isinstance(left, tuple) and left[0] == 'cons' and isinstance(right, tuple) and right[0] == 'cons':
            # Compare the head and recursively compare the tail
            return 1.0 if left[1] == right[1] and evaluate(('eq', left[2], right[2])) == 1.0 else 0.0

        # Handle equality for basic types (e.g., numbers)
        return 1.0 if left == right else 0.0

    
    # elif tree[0] == 'prog':
    #     evaluate(tree[1])
    #     return evaluate(tree[2])
    elif tree[0] == 'prog':
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        return ('prog', left, right)


    elif tree[0] == 'hd':
        lst = evaluate(tree[1])
        if not isinstance(lst, tuple) or lst[0] != 'cons':
            raise TypeError(f"Cannot take head of non-list: {lst}")
        return evaluate(lst[1])

    elif tree[0] == 'tl':
        lst = evaluate(tree[1])
        if not isinstance(lst, tuple) or lst[0] != 'cons':
            raise TypeError(f"Cannot take tail of non-list: {lst}")
        return evaluate(lst[2])

    elif tree[0] == 'nil':
        return ('nil',)

    elif tree[0] == 'cons':
        head = evaluate(tree[1])
        tail = evaluate(tree[2])
        return ('cons', head, tail)
    

    else:
        print(f" -> Returning unprocessed tree: {linearize(tree)}")
        return tree




# substitute function
def substitute(tree, name, replacement):
    #print(f"Substituting: Replace {name} with {linearize(replacement)} in {linearize(tree)}")
    
    if isinstance(tree, (float, int)):
        return tree

    if isinstance(tree, tuple):
        # var
        if tree[0] == 'var' and tree[1] == name:
            #print(f" -> Variable matched: {tree[1]} replaced with {linearize(replacement)}")
            return replacement

        # arithmetic operations
        elif tree[0] in {'app', 'plus', 'minus', 'times', 'power', 'leq', 'eq', 'parens'}:
            left = substitute(tree[1], name, replacement) if len(tree) > 1 else None
            right = substitute(tree[2], name, replacement) if len(tree) > 2 else None
            return (tree[0], left, right)
            #return (tree[0], substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

        # lambda
        elif tree[0] == 'lam':
            param, body = tree[1], tree[2]
            if param == name:
                return tree  # Skip substitution for the bound variable
            return ('lam', param, substitute(body, name, replacement))

        # if 
        elif tree[0] == 'if':
            cond = substitute(tree[1], name, replacement)
            then_ = substitute(tree[2], name, replacement)
            else_ = substitute(tree[3], name, replacement)
            return ('if', cond, then_, else_)

        # let 
        elif tree[0] == 'let':
            if tree[1] == name:
                return tree  # Do not substitute into the let binding
            return ('let', tree[1], substitute(tree[2], name, replacement),
                    substitute(tree[3], name, replacement))
            
        # letrec
        # may need to change for letrec's deep recursion with bigger equations
        elif tree[0] == 'letrec':
            if tree[1] == name:
                return tree  # Skip substitution for recursive variable
            return ('letrec', tree[1], substitute(tree[2], name, replacement),
                    substitute(tree[3], name, replacement))
            # _, name, value, body = tree
            # if name in variables_in(replacement):
            #     fresh_name = name_generator.generate()
            #     value = substitute(value, name, ('var', fresh_name))
            #     body = substitute(body, name, ('var', fresh_name))
            #     name = fresh_name
            # value_fixed = ('fix', ('lam', name, value))
            # substituted_body = substitute(body, name, value_fixed)
            # return evaluate(substituted_body)
        elif tree[0] == 'fix':
            return ('fix', substitute(tree[1], name, replacement))
        
        elif tree[0] == 'prog':
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            return ('prog', left, right)
            #return ('prog', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

        elif tree[0] == 'hd':
            return ('hd', substitute(tree[1], name, replacement))
        # elif tree[0] == 'hd':
        #     lst = evaluate(tree[1])
        #     if lst == ('nil',):
        #         raise ValueError("Cannot take head of an empty list")
        #     if lst[0] != 'cons':
        #         raise TypeError(f"Cannot take head of non-list: {lst}")
        #     return lst[1]

        elif tree[0] == 'tl':
            return ('tl', substitute(tree[1], name, replacement))
            # lst = evaluate(tree[1])
            # if lst == ('nil',):
            #     raise ValueError("Cannot take tail of an empty list")
            # if lst[0] != 'cons':
            #     raise TypeError(f"Cannot take tail of non-list: {lst}")
            # return lst[2]

        elif tree[0] == 'nil':
            return tree

        elif tree[0] == 'cons':
            return ('cons', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

    return tree



# linearize function
def linearize(ast):
    if ast is None:
        return 'error: invalid ast'
    if isinstance(ast, (float, int)):
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
    elif ast[0] == 'prog':
        return "(" + linearize(ast[1]) + " ;; " + linearize(ast[2]) + ")"
    # elif ast[0] == 'hd':
    #     return "(hd " + linearize(ast[1]) + ")"
    # elif ast[0] == 'tl':
    #     return "(tl " + linearize(ast[1]) + ")"
    elif ast[0] == 'hd':
        return f"(hd {linearize(ast[1])})"
    elif ast[0] == 'tl':
        return f"(tl {linearize(ast[1])})"
    elif ast[0] == 'nil':
        return "[]"
    elif ast[0] == 'cons':
        head = linearize(ast[1])
        tail = linearize(ast[2])
        if tail == "[]":
            return f"[{head}]"
        elif tail.startswith("[") and tail.endswith("]"):
            return f"[{head}, {tail[1:-1]}]"
        else:
            return f"[{head}] : {tail}"

    # elif ast[0] == 'nil':
    #     return "#"
    # elif ast[0] == 'cons':
    #     return "(" + linearize(ast[1]) + " : " + linearize(ast[2]) + ")"
    
    else:
        return str(ast)


# main function
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