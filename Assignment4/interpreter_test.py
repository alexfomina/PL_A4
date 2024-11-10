from interpreter import interpret, substitute, evaluate, LambdaCalculusTransformer, parser, linearize
from lark import Lark, Transformer
from colorama import Fore, Style

# For testing the grammar, the parser, and the conversion to ASTs
def print_trees(source_code):
    print("Source code:", source_code); print()
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    print("AST:", ast); print()
    print("===\n")

# Convert concrete syntax to AST
def ast(source_code):
    return LambdaCalculusTransformer().transform(parser.parse(source_code))

def print_ast(source_code):
    print()
    print("AST:", ast(source_code))
    print()

def test_parse():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # Existing tests
    assert ast(r"x") == ('var', 'x')
    print(f"AST {MAGENTA}x{RESET} == ('var', 'x')")

    # Additional tests for operators (highlighted in blue)
    assert ast(r"x + y") == ('app', ('app', ('var', '+'), ('var', 'x')), ('var', 'y'))
    print(f"AST {Fore.BLUE}x + y{Style.RESET_ALL} == ('app', ('app', ('var', '+'), ('var', 'x')), ('var', 'y'))")

    assert ast(r"x - y") == ('app', ('app', ('var', '-'), ('var', 'x')), ('var', 'y'))
    print(f"AST {Fore.BLUE}x - y{Style.RESET_ALL} == ('app', ('app', ('var', '-'), ('var', 'x')), ('var', 'y'))")

    assert ast(r"x * y") == ('app', ('app', ('var', '*'), ('var', 'x')), ('var', 'y'))
    print(f"AST {Fore.BLUE}x * y{Style.RESET_ALL} == ('app', ('app', ('var', '*'), ('var', 'x')), ('var', 'y'))")

    assert ast(r"-x") == ('app', ('var', 'neg'), ('var', 'x'))
    print(f"AST {Fore.BLUE}-x{Style.RESET_ALL} == ('app', ('var', 'neg'), ('var', 'x'))")

    assert ast(r"x ^ y") == ('app', ('app', ('var', 'power'), ('var', 'x')), ('var', 'y'))
    print(f"AST {Fore.BLUE}x ^ y{Style.RESET_ALL} == ('app', ('app', ('var', 'power'), ('var', 'x')), ('var', 'y'))")

    assert ast(r"log(x)") == ('app', ('var', 'log'), ('var', 'x'))
    print(f"AST {Fore.BLUE}log(x){Style.RESET_ALL} == ('app', ('var', 'log'), ('var', 'x'))")

    print("\nParser: All tests passed!\n")

def test_substitute():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # Additional tests for substitution with operators (highlighted in blue)
    assert substitute(('app', ('app', ('var', '+'), ('var', 'x')), ('var', 'y')), 'x', ('var', 'z')) == ('app', ('app', ('var', '+'), ('var', 'z')), ('var', 'y'))
    print(f"SUBST {Fore.BLUE}x + y [z/x]{Style.RESET_ALL} == ('app', ('app', ('var', '+'), ('var', 'z')), ('var', 'y'))")

    assert substitute(('app', ('var', 'neg'), ('var', 'x')), 'x', ('var', 'y')) == ('app', ('var', 'neg'), ('var', 'y'))
    print(f"SUBST {Fore.BLUE}-x [y/x]{Style.RESET_ALL} == ('app', ('var', 'neg'), ('var', 'y'))")

    print("\nsubstitute(): All tests passed!\n")

def test_evaluate():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # Additional tests for evaluation with operators (highlighted in blue)
    assert linearize(evaluate(ast(r"2 + 3"))) == "(2 + 3)"
    print(f"EVAL {Fore.BLUE}2 + 3{Style.RESET_ALL} == (2 + 3)")

    assert linearize(evaluate(ast(r"2 * 3 + 1"))) == "((2 * 3) + 1)"
    print(f"EVAL {Fore.BLUE}2 * 3 + 1{Style.RESET_ALL} == ((2 * 3) + 1)")

    assert linearize(evaluate(ast(r"-4"))) == "(neg 4)"
    print(f"EVAL {Fore.BLUE}-4{Style.RESET_ALL} == (neg 4)")

    print("\nevaluate(): All tests passed!\n")

def test_interpret():
    print(f"Testing x --> {interpret('x')}")
    print(f"Testing x y --> {interpret('x y')}")
    input=r"\x.x"; output = interpret(input); print(f"Testing {input} --> {output}")
    
    # Additional tests for interpretation with operators (highlighted in blue)
    print(f"Testing {Fore.BLUE}2 + 3{Style.RESET_ALL} --> {interpret('2 + 3')}")
    print(f"Testing {Fore.BLUE}log(2){Style.RESET_ALL} --> {interpret('log(2)')}")
    print(f"Testing {Fore.BLUE}-(3){Style.RESET_ALL} --> {interpret('-(3)')}")

    print("\ninterpret(): All tests passed!\n")

if __name__ == "__main__":
    print(Fore.GREEN + "\nTEST PARSING\n" + Style.RESET_ALL); test_parse()
    print(Fore.GREEN + "\nTEST SUBSTITUTION\n" + Style.RESET_ALL); test_substitute()
    print(Fore.GREEN + "\nTEST EVALUATION\n" + Style.RESET_ALL); test_evaluate()
    print(Fore.GREEN + "\nTEST INTERPRETATION\n" + Style.RESET_ALL); test_interpret()



# from interpreter import interpret, substitute, evaluate, LambdaCalculusTransformer, parser, linearize
# from lark import Lark, Transformer
# from colorama import Fore, Style

# # for testing the grammar, the parser and the conversion to ASTs
# def print_trees(source_code):
#     print("Source code:", source_code); print()
#     cst = parser.parse(source_code)
#     #print("CST:", cst); print()
#     ast = LambdaCalculusTransformer().transform(cst)
#     print("AST:", ast); print()
#     print("===\n")

# # convert concrete syntax to AST
# def ast(source_code):
#     return LambdaCalculusTransformer().transform(parser.parse(source_code))

# def print_ast(source_code):
#     print()
#     print("AST:", ast(source_code))
#     print()

# def test_parse():
#     MAGENTA = '\033[95m'
#     RESET = '\033[0m'
    
#     assert ast(r"x") == ('var', 'x')
#     print(f"AST {MAGENTA}x{RESET} == ('var', 'x')")
    
#     assert ast(r"(((x)) ((y)))") == ('app', ('var', 'x'), ('var', 'y'))
#     print(f"AST {MAGENTA}(((x)) ((y))){RESET} == ('app', ('var', 'x'), ('var', 'y'))")
    
#     assert ast(r"x y") == ('app', ('var', 'x'), ('var', 'y'))
#     print(f"AST {MAGENTA}x y{RESET} == ('app', ('var', 'x'), ('var', 'y'))")
    
#     assert ast(r"x y z") == ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z'))
#     print(f"AST {MAGENTA}x y z{RESET} == ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z'))")
    
#     assert ast(r"\x.y") == ('lam', 'x', ('var', 'y'))
#     print(f"AST {MAGENTA}\\x.y{RESET} == ('lam', 'x', ('var', 'y'))")
    
#     assert ast(r"\x.x y") == ('lam', 'x', ('app', ('var', 'x'), ('var', 'y')))
#     print(f"AST {MAGENTA}\\x.x y{RESET} == ('lam', 'x', ('app', ('var', 'x'), ('var', 'y')))")
    
#     assert ast(r"\x.x y z") == ('lam', 'x', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))
#     print(f"AST {MAGENTA}\\x.x y z{RESET} == ('lam', 'x', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))")
    
#     assert ast(r"\x. \y. \z. x y z") == ('lam', 'x', ('lam', 'y', ('lam', 'z', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))))
#     print(f"AST {MAGENTA}\\x. \\y. \\z. x y z{RESET} == ('lam', 'x', ('lam', 'y', ('lam', 'z', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))))")
    
#     assert ast(r"\x. x a") == ('lam', 'x', ('app', ('var', 'x'), ('var', 'a')))
#     print(f"AST {MAGENTA}\\x. x a{RESET} == ('lam', 'x', ('app', ('var', 'x'), ('var', 'a')))")
    
#     assert ast(r"\x. x (\y. y)") == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('var', 'y'))))
#     print(f"AST {MAGENTA}\\x. x (\\y. y){RESET} == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('var', 'y'))))")
    
#     assert ast(r"\x. x (\y. y (\z. z z2))") == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('app', ('var', 'y'), ('lam', 'z', ('app', ('var', 'z'), ('var', 'z2')))))))
#     print(f"AST {MAGENTA}\\x. x (\\y. y (\\z. z z2)){RESET} == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('app', ('var', 'y'), ('lam', 'z', ('app', ('var', 'z'), ('var', 'z2')))))))")
    
#     assert ast(r"\x. y z (\a. b (\c. d e f))") == ('lam', 'x', ('app', ('app', ('var', 'y'), ('var', 'z')), ('lam', 'a', ('app', ('var', 'b'), ('lam', 'c', ('app', ('app', ('var', 'd'), ('var', 'e')), ('var', 'f')))))))
#     print(f"AST {MAGENTA}\\x. y z (\\a. b (\\c. d e f)){RESET} == ('lam', 'x', ('app', ('app', ('var', 'y'), ('var', 'z')), ('lam', 'a', ('app', ('var', 'b'), ('lam', 'c', ('app', ('app', ('var', 'd'), ('var', 'e')), ('var', 'f')))))))")
    
#     print("\nParser: All tests passed!\n")

# def test_substitute():
#     MAGENTA = '\033[95m'
#     RESET = '\033[0m'
    
#     # x [y/x] = y
#     assert substitute(('var', 'x'), 'x', ('var', 'y')) == ('var', 'y')
#     print(f"SUBST {MAGENTA}x [y/x]{RESET} == ('var', 'y')")
    
#     # \x.x [y/x] = (\x.x)
#     assert substitute(('lam', 'x', ('var', 'x')), 'x', ('var', 'y')) == ('lam', 'x', ('var', 'x'))
#     print(f"SUBST {MAGENTA}\\x.x [y/x]{RESET} == ('lam', 'x', ('var', 'x'))")
    
#     # (x x) [y/x] = y y
#     assert substitute(('app', ('var', 'x'), ('var', 'x')), 'x', ('var', 'y')) == ('app', ('var', 'y'), ('var', 'y'))
#     print(f"SUBST {MAGENTA}(x x) [y/x]{RESET} == ('app', ('var', 'y'), ('var', 'y'))")
    
#     # (\y. x ) [y/x] = (\Var1. y)
#     assert substitute(('lam', 'y', ('var', 'x')), 'x', ('var', 'y')) == ('lam', 'Var1', ('var', 'y'))
#     print(f"SUBST {MAGENTA}\\y. x [y/x]{RESET} == ('lam', 'Var1', ('var', 'y'))")

#     print("\nsubstitute(): All tests passed!\n")

# def test_evaluate():
#     MAGENTA = '\033[95m'
#     RESET = '\033[0m'
    
#     # EVAL x == x
#     assert linearize(evaluate(ast(r"x"))) == "x"
#     print(f"EVAL {MAGENTA}x{RESET} == x")
    
#     # EVAL x y == (x y)
#     assert linearize(evaluate(ast(r"x y"))) == "(x y)"
#     print(f"EVAL {MAGENTA}x y{RESET} == (x y)")
    
#     # EVAL x y z == ((x y) z)
#     assert linearize(evaluate(ast(r"x y z"))) == "((x y) z)"
#     print(f"EVAL {MAGENTA}x y z{RESET} == ((x y) z)")
    
#     # EVAL x (y z) == (x (y z))
#     assert linearize(evaluate(ast(r"x (y z)"))) == "(x (y z))"
#     print(f"EVAL {MAGENTA}x (y z){RESET} == (x (y z))")
    
#     # EVAL \x.y == \x.y
#     assert linearize(evaluate(ast(r"\x.y"))) == r"(\x.y)"
#     print(f"EVAL {MAGENTA}\\x.y{RESET} == \\x.y")
    
#     # EVAL (\x.x) y == y
#     assert linearize(evaluate(ast(r"(\x.x) y"))) == "y"
#     print(f"EVAL {MAGENTA}(\\x.x) y{RESET} == y")

#     print("\nevaluate(): All tests passed!\n")

# def test_interpret():
#     print(f"Testing x --> {interpret('x')}")
#     print(f"Testing x y --> {interpret('x y')}")
#     input=r"\x.x"; output = interpret(input); print(f"Testing {input} --> {output}")
#     input=r"(\x.x) y"; output = interpret(input); print(f"Testing {input} --> {output}")
#     input=r"(\x.\y.x y) y"; output = interpret(input); print(f"Testing {input} --> {output}")

#     print("\ninterpret(): All tests passed!\n")

# if __name__ == "__main__":
#     print(Fore.GREEN + "\nTEST PARSING\n" + Style.RESET_ALL); test_parse()
#     print(Fore.GREEN + "\nTEST SUBSTITUTION\n" + Style.RESET_ALL); test_substitute()
#     print(Fore.GREEN + "\nTEST EVALUATION\n" + Style.RESET_ALL); test_evaluate()
#     print(Fore.GREEN + "\nTEST INTERPRETATION\n" + Style.RESET_ALL); test_interpret()
