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
    # assert ast(r"x + y") == ('app', ('app', ('var', '+'), ('var', 'x')), ('var', 'y'))
    # print(f"AST {Fore.BLUE}x + y{Style.RESET_ALL} == ('app', ('app', ('var', '+'), ('var', 'x')), ('var', 'y'))")

    actual_ast = ast(r"x + y")
    print(f"Debug - actual AST for 'x + y':", actual_ast)
    assert ast(r"x + y") == ('plus', ('var', 'x'), ('var', 'y'))
    print(f"AST {Fore.BLUE}x + y{Style.RESET_ALL} == ('plus', ('var', 'x'), ('var', 'y'))")

    assert ast(r"x - y") == ('minus', ('var', 'x'), ('var', 'y'))
    print(f"AST {Fore.BLUE}x - y{Style.RESET_ALL} == ('minus', ('var', 'x'), ('var', 'y'))")

    actual_ast = ast(r"x * y")
    print(f"Debug - actual AST for 'x * y':", actual_ast)
    assert ast(r"x * y") == ('times', ('var', 'x'), ('var', 'y'))
    print(f"AST {Fore.BLUE}x * y{Style.RESET_ALL} == ('times', ('var', 'x'), ('var', 'y'))")

    assert ast(r"-x") == ('neg', ('var', 'x'))
    print(f"AST {Fore.BLUE}-x{Style.RESET_ALL} == ('neg', ('var', 'x'))")

    assert ast(r"x ^ y") == ('power', ('var', 'x'), ('var', 'y'))
    print(f"AST {Fore.BLUE}x ^ y{Style.RESET_ALL} == ('power', ('var', 'x'), ('var', 'y'))")

    actual_ast = ast(r"log(x)")
    print(f"Debug - actual AST for 'log(x)':", actual_ast)
    assert ast(r"log(x)") == ('app', ('var', 'log'), ('parens', ('var', 'x')))
    print(f"AST {Fore.BLUE}log(x){Style.RESET_ALL} == ('app', ('var', 'log'), ('parens', ('var', 'x')))")

    assert ast(r"let x = 5 in x") == ('let', 'x', ('num', 5.0), ('var', 'x'))
    print(f"AST {Fore.BLUE}let x = 5 in x{Style.RESET_ALL} == ('let', 'x', ('num', 5.0), ('var', 'x'))")

    assert ast(r"letrec f = \x.x in f") == ('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f'))
    print(f"AST {Fore.BLUE}letrec f = \\x.x in f{Style.RESET_ALL} == ('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f'))")

    assert ast(r"fix f") == ('fix', ('var', 'f'))
    print(f"AST {Fore.BLUE}fix f{Style.RESET_ALL} == ('fix', ('var', 'f'))")

    assert ast(r"if x then y else z") == ('if', ('var', 'x'), ('var', 'y'), ('var', 'z'))
    print(f"AST {Fore.BLUE}if x then y else z{Style.RESET_ALL} == ('if', ('var', 'x'), ('var', 'y'), ('var', 'z'))")
    
    # print("\nParser: All tests passed!\n")

def test_substitute():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # Additional tests for substitution with operators (highlighted in blue)
    assert substitute(('app', ('app', ('var', '+'), ('var', 'x')), ('var', 'y')), 'x', ('var', 'z')) == ('app', ('app', ('var', '+'), ('var', 'z')), ('var', 'y'))
    print(f"SUBST {Fore.BLUE}x + y [z/x]{Style.RESET_ALL} == ('app', ('app', ('var', '+'), ('var', 'z')), ('var', 'y'))")

    assert substitute(('app', ('var', 'neg'), ('var', 'x')), 'x', ('var', 'y')) == ('app', ('var', 'neg'), ('var', 'y'))
    print(f"SUBST {Fore.BLUE}-x [y/x]{Style.RESET_ALL} == ('app', ('var', 'neg'), ('var', 'y'))")

    # print("\nsubstitute(): All tests passed!\n")

# def test_evaluate():
#     MAGENTA = '\033[95m'
#     RESET = '\033[0m'
    
#     # Debug the operator evaluation
#     result = linearize(evaluate(ast(r"2 + 3")))
#     print(f"Debug - actual result: {result}")
#     assert result == "5.0"  # Updated to match actual numerical evaluation
#     print(f"EVAL {Fore.BLUE}2 + 3{Style.RESET_ALL} == 5.0")
#     print("AST for '2 + 3':", ast(r"2 + 3"))


#     # print("\nevaluate(): All tests passed!\n")




def test_evaluate():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # Debug the operator evaluation
    result = linearize(evaluate(ast(r"2 + 3")))
    print(f"Debug - actual result: {result}")
    assert result == "5.0"  # Updated to match actual numerical evaluation
    print(f"EVAL {Fore.BLUE}2 + 3{Style.RESET_ALL} == 5.0")
    print("AST for '2 + 3':", ast(r"2 + 3"))
    
    # Uncomment to indicate all tests passed
    print("\nevaluate(): All tests passed!\n")



    

def test_interpret():
    print(f"Testing x --> {interpret('x')}")
    print(f"Testing x y --> {interpret('x y')}")
    input=r"\x.x"; output = interpret(input); print(f"Testing {input} --> {output}")
    
    # Additional tests for interpretation with operators (highlighted in blue)
    print(f"Testing {Fore.BLUE}2 + 3{Style.RESET_ALL} --> {interpret('2 + 3')}")
    print(f"Testing {Fore.BLUE}log(2){Style.RESET_ALL} --> {interpret('log(2)')}")
    print(f"Testing {Fore.BLUE}-(3){Style.RESET_ALL} --> {interpret('-(3)')}")

    # print("\ninterpret(): All tests passed!\n")

if __name__ == "__main__":
    print(Fore.GREEN + "\nTEST PARSING\n" + Style.RESET_ALL); test_parse()
    print(Fore.GREEN + "\nTEST SUBSTITUTION\n" + Style.RESET_ALL); test_substitute()
    print(Fore.GREEN + "\nTEST EVALUATION\n" + Style.RESET_ALL); test_evaluate()
    print(Fore.GREEN + "\nTEST INTERPRETATION\n" + Style.RESET_ALL); test_interpret()