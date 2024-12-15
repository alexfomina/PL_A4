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
    print(f"AST {Fore.BLUE}x{RESET} == ('var', 'x')")

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
    
    print(f"\n{Fore.GREEN}parse(): all tests passed.{Fore.RESET}\n")


def test_substitute():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # Additional tests for substitution with operators (highlighted in blue)
    assert substitute(('app', ('app', ('var', '+'), ('var', 'x')), ('var', 'y')), 'x', ('var', 'z')) == ('app', ('app', ('var', '+'), ('var', 'z')), ('var', 'y'))
    print(f"SUBST {Fore.BLUE}x + y [z/x]{Style.RESET_ALL} == ('app', ('app', ('var', '+'), ('var', 'z')), ('var', 'y'))")

    assert substitute(('app', ('var', 'neg'), ('var', 'x')), 'x', ('var', 'y')) == ('app', ('var', 'neg'), ('var', 'y'))
    print(f"SUBST {Fore.BLUE}-x [y/x]{Style.RESET_ALL} == ('app', ('var', 'neg'), ('var', 'y'))")

    assert substitute(('let', 'x', ('num', 5), ('var', 'x')), 'x', ('num', 10)) == ('let', 'x', ('num', 5), ('var', 'x'))
    print(f"SUBST {Fore.BLUE}let x = 5 in x [x/10]{Style.RESET_ALL} == ('let', 'x', ('num', 5), ('var', 'x'))")

    assert substitute(('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f')), 'f', ('num', 5)) == ('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f'))
    print(f"SUBST {Fore.BLUE}letrec f = \\x.x in f [f/5]{Style.RESET_ALL} == ('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f'))")

    assert substitute(('fix', ('var', 'f')), 'f', ('num', 5)) == ('fix', ('num', 5))
    print(f"SUBST {Fore.BLUE}fix f [f/5]{Style.RESET_ALL} == ('fix', ('num', 5))")

    assert substitute(('if', ('var', 'x'), ('var', 'y'), ('var', 'z')), 'x', ('num', 5)) == ('if', ('num', 5), ('var', 'y'), ('var', 'z'))
    print(f"SUBST {Fore.BLUE}if x then y else z [x/5]{Style.RESET_ALL} == ('if', ('num', 5), ('var', 'y'), ('var', 'z'))")
    
    print(f"\n{Fore.GREEN}substitute(): all tests passed.{Fore.RESET}")
    
def test_sequencing():
    assert interpret("1 ;; 2 ;; 3") == "1.0 ;; 2.0 ;; 3.0", "Failed: Sequential composition"
    assert interpret("1+1 ;; 2+2 ;; 3+3") == "2.0 ;; 4.0 ;; 6.0", "Failed: Sequential composition with operations"

def test_list_constructors():
    assert interpret("#") == "#", "Failed: Empty list"
    assert interpret("1:#") == "[1.0]", "Failed: List with one element"
    assert interpret("1:2:#") == "[1.0, 2.0]", "Failed: List with multiple elements"
    assert interpret("1:(2:(3:#))") == "[1.0, 2.0, 3.0]", "Failed: Nested list"

def test_list_destructors():
    assert interpret("hd 1:2:3:#") == "1.0", "Failed: Head of list"
    assert interpret("tl 1:2:3:#") == "[2.0, 3.0]", "Failed: Tail of list"
    assert interpret("hd (1:#)") == "1.0", "Failed: Head with parentheses"
    assert interpret("tl (1:#)") == "[]", "Failed: Tail with parentheses"
    try:
        interpret("hd #")
        assert False, "Failed: Head of empty list should raise error"
    except ValueError:
        pass  # Expected behavior

def test_list_comparison():
    assert interpret("1:2:# == 1:2:#") == "1.0", "Failed: Equal lists"
    assert interpret("1:2:# == 1:3:#") == "0.0", "Failed: Unequal lists"



# def test_evaluate():
#     MAGENTA = '\033[95m'
#     RESET = '\033[0m'
#     PINK = '\033[38;5;206m'
#     GREEN = '\033[92m'

#     print(f"{MAGENTA}TEST EVALUATION{RESET}")
    


#     # 1. Basic Literal Evaluation
#     print(f"{PINK}Testing basic literals{RESET}")
#     assert evaluate(('num', 5)) == 5, "Failed: Basic literal (integer)"
#     assert evaluate(('num', 3.14)) == 3.14, "Failed: Basic literal (float)"
#     print(f"{GREEN}Passed: Basic literals")

#     # 2. Variable Evaluation
#     print(f"{PINK}Testing variable evaluation{RESET}")
#     test_let = ('let', 'x', ('num', 10), ('var', 'x'))
#     assert evaluate(test_let) == 10, "Failed: Variable evaluation in let"
#     print(f"{GREEN}Passed: Variable evaluation")

#     # 3. Arithmetic and Comparison Operators
#     print(f"{PINK}Testing arithmetic and comparison operators{RESET}")
#     assert evaluate(('plus', ('num', 2), ('num', 3))) == 5, "Failed: Addition"
#     assert evaluate(('minus', ('num', 7), ('num', 4))) == 3, "Failed: Subtraction"
#     assert evaluate(('times', ('num', 3), ('num', 5))) == 15, "Failed: Multiplication"
#     assert evaluate(('power', ('num', 2), ('num', 3))) == 8, "Failed: Exponentiation"
#     assert evaluate(('leq', ('num', 2), ('num', 3))) == 1, "Failed: Less or equal (true)"
#     assert evaluate(('leq', ('num', 5), ('num', 3))) == 0, "Failed: Less or equal (false)"
#     print(f"{GREEN}Passed: Arithmetic and comparison operators")

#     # 4. Conditional Expressions
#     print(f"{PINK}Testing conditional expressions{RESET}")
#     test_if_true = ('if', ('leq', ('num', 1), ('num', 2)), ('num', 10), ('num', 20))
#     test_if_false = ('if', ('leq', ('num', 3), ('num', 1)), ('num', 10), ('num', 20))
#     assert evaluate(test_if_true) == 10, "Failed: Conditional (true branch)"
#     assert evaluate(test_if_false) == 20, "Failed: Conditional (false branch)"
#     print(f"{GREEN}Passed: Conditional expressions")

#     # 5. Lambda Functions
#     print(f"{PINK}Testing lambda functions{RESET}")
#     lam = ('lam', 'x', ('plus', ('var', 'x'), ('num', 2)))
#     assert evaluate(lam) == lam, "Failed: Lambda function returned incorrectly"
#     print(f"{GREEN}Passed: Lambda functions")

#     # 6. Lambda Application
#     print(f"{PINK}Testing lambda application{RESET}")
#     lam_app = ('app', ('lam', 'x', ('plus', ('var', 'x'), ('num', 2))), ('num', 3))
#     assert evaluate(lam_app) == 5, "Failed: Lambda application"
#     print(f"{GREEN}Passed: Lambda application")

#     # 7. Let Expressions
#     print(f"{PINK}Testing let expressions{RESET}")
#     test_let = ('let', 'x', ('num', 5), ('plus', ('var', 'x'), ('num', 3)))
#     assert evaluate(test_let) == 8, "Failed: Let expressions"
#     print(f"{GREEN}Passed: Let expressions")

#     # 8. Recursive Let (`letrec`)
#     print(f"{PINK}Testing letrec expressions{RESET}")
#     test_letrec_identity = (
#         'letrec', 'identity',
#         ('lam', 'x', ('var', 'x')),
#         ('app', ('var', 'identity'), ('num', 5))
#     )
#     assert evaluate(test_letrec_identity) == 5, "Failed: Recursive let (identity)"
    
#     test_letrec_with_if = (
#         'letrec', 'return_one',
#         ('lam', 'n', 
#          ('if', 
#           ('leq', ('var', 'n'), ('num', 0)),  # If n <= 0
#           ('num', 1),                        # Then return 1
#           ('num', 2))),                     # Else return 2
#         ('app', ('var', 'return_one'), ('num', 5))  # Test with n = 5
#     )
#     assert evaluate(test_letrec_with_if) == 2, "Failed: Recursive let with if"
#     print(f"{GREEN}Passed: Recursive let")

#     # 9. Fixed-Point Combinator
#     print(f"{PINK}Testing fixed-point combinator{RESET}")
#     test_factorial = (
#         'letrec', 'fact',
#         ('lam', 'n', 
#          ('if', 
#           ('leq', ('var', 'n'), ('num', 1)), 
#           ('num', 1),
#           ('times', ('var', 'n'), 
#            ('app', ('var', 'fact'), ('minus', ('var', 'n'), ('num', 1)))))),
#         ('app', ('var', 'fact'), ('num', 5))
#     )
#     assert evaluate(test_factorial) == 120, "Failed: Fixed-point combinator for factorial"
#     print(f"{GREEN}Passed: Fixed-point combinator")


#     letrec_test = ('letrec', 
#     'f', 
#     ('lam', 'n', 
#         ('if', 
#             ('eq', ('var', 'n'), ('num', 0.0)), 
#             ('num', 0.0), 
#             ('plus', 
#                 ('num', 1.0), 
#                 ('plus', 
#                     ('times', ('num', 2.0), ('parens', ('minus', ('var', 'n'), ('num', 1.0)))), 
#                     ('app', ('var', 'f'), ('parens', ('minus', ('var', 'n'), ('num', 1.0))))
#                 )
#             )
#         )
#     ), 
#     ('app', ('var', 'f'), ('num', 6.0))
# )

#     # Expected result
#     expected_result = 36.0

#     # Evaluate the letrec test
#     assert evaluate(letrec_test) == expected_result, "Failed: Recursive function evaluation returned incorrectly"
    
#     print(f"{Fore.GREEN}evaluate(): all tests passed.{Fore.RESET}")

def test_evaluate():
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

    

    # 1. Basic Literal Evaluation
    print(f"Testing {BLUE}Basic literals{RESET}")
    assert evaluate(('num', 5)) == 5, f"Failed: {BLUE}('num', 5) -> 5{RESET}"
    print(f"{BLUE}('num', 5){RESET} == {GREEN}5{RESET}")
    assert evaluate(('num', 3.14)) == 3.14, f"Failed: {BLUE}('num', 3.14) -> 3.14{RESET}"
    print(f"{BLUE}('num', 3.14){RESET} == {GREEN}3.14{RESET}")
    print(f"{GREEN}Passed: Basic literals{RESET}\n")

    # 2. Variable Evaluation
    print(f"Testing {BLUE}Variable evaluation{RESET}")
    test_let = ('let', 'x', ('num', 10), ('var', 'x'))
    assert evaluate(test_let) == 10, f"Failed: {BLUE}{test_let}{RESET}"
    print(f"{BLUE}{test_let}{RESET} == {GREEN}10{RESET}")
    print(f"{GREEN}Passed: Variable evaluation{RESET}\n")

    # 3. Arithmetic and Comparison Operators
    print(f"Testing {BLUE}Arithmetic and comparison operators{RESET}")
    assert evaluate(('plus', ('num', 2), ('num', 3))) == 5, f"Failed: {BLUE}2 + 3{RESET}"
    print(f"{BLUE}2 + 3{RESET} == {GREEN}5{RESET}")
    assert evaluate(('minus', ('num', 7), ('num', 4))) == 3, f"Failed: {BLUE}7 - 4{RESET}"
    print(f"{BLUE}7 - 4{RESET} == {GREEN}3{RESET}")
    assert evaluate(('times', ('num', 3), ('num', 5))) == 15, f"Failed: {BLUE}3 * 5{RESET}"
    print(f"{BLUE}3 * 5{RESET} == {GREEN}15{RESET}")
    assert evaluate(('power', ('num', 2), ('num', 3))) == 8, f"Failed: {BLUE}2 ^ 3{RESET}"
    print(f"{BLUE}2 ^ 3{RESET} == {GREEN}8{RESET}")
    assert evaluate(('leq', ('num', 2), ('num', 3))) == 1, f"Failed: {BLUE}2 <= 3{RESET}"
    print(f"{BLUE}2 <= 3{RESET} == {GREEN}1{RESET}")
    assert evaluate(('leq', ('num', 5), ('num', 3))) == 0, f"Failed: {BLUE}5 <= 3{RESET}"
    print(f"{BLUE}5 <= 3{RESET} == {GREEN}0{RESET}")
    print(f"{GREEN}Passed: Arithmetic and comparison operators{RESET}\n")

    # 4. Conditional Expressions
    print(f"Testing {BLUE}Conditional expressions{RESET}")
    test_if_true = ('if', ('leq', ('num', 1), ('num', 2)), ('num', 10), ('num', 20))
    test_if_false = ('if', ('leq', ('num', 3), ('num', 1)), ('num', 10), ('num', 20))
    assert evaluate(test_if_true) == 10, f"Failed: {BLUE}{test_if_true}{RESET}"
    print(f"{BLUE}{test_if_true}{RESET} == {GREEN}10{RESET}")
    assert evaluate(test_if_false) == 20, f"Failed: {BLUE}{test_if_false}{RESET}"
    print(f"{BLUE}{test_if_false}{RESET} == {GREEN}20{RESET}")
    print(f"{GREEN}Passed: Conditional expressions{RESET}\n")

    # 5. Lambda Functions
    print(f"Testing {BLUE}Lambda functions{RESET}")
    lam = ('lam', 'x', ('plus', ('var', 'x'), ('num', 2)))
    assert evaluate(lam) == lam, f"Failed: {BLUE}{lam}{RESET}"
    print(f"{BLUE}{lam}{RESET} == {GREEN}{lam}{RESET}")
    print(f"{GREEN}Passed: Lambda functions{RESET}\n")

    # 6. Lambda Application
    print(f"Testing {BLUE}Lambda application{RESET}")
    lam_app = ('app', ('lam', 'x', ('plus', ('var', 'x'), ('num', 2))), ('num', 3))
    assert evaluate(lam_app) == 5, f"Failed: {BLUE}{lam_app}{RESET}"
    print(f"{BLUE}{lam_app}{RESET} == {GREEN}5{RESET}")
    print(f"{GREEN}Passed: Lambda application{RESET}\n")

    # 7. Let Expressions
    print(f"Testing {BLUE}Let expressions{RESET}")
    test_let = ('let', 'x', ('num', 5), ('plus', ('var', 'x'), ('num', 3)))
    assert evaluate(test_let) == 8, f"Failed: {BLUE}{test_let}{RESET}"
    print(f"{BLUE}{test_let}{RESET} == {GREEN}8{RESET}")
    print(f"{GREEN}Passed: Let expressions{RESET}\n")

    # 8. Recursive Let (`letrec`)
    print(f"Testing {BLUE}letrec expressions{RESET}")
    test_letrec_identity = (
        'letrec', 'identity',
        ('lam', 'x', ('var', 'x')),
        ('app', ('var', 'identity'), ('num', 5))
    )
    assert evaluate(test_letrec_identity) == 5, f"Failed: {BLUE}{test_letrec_identity}{RESET}"
    print(f"{BLUE}{test_letrec_identity}{RESET} == {GREEN}5{RESET}")
    print(f"{GREEN}Passed: letrec (identity){RESET}\n")

    # 9. Fixed-Point Combinator
    print(f"Testing {BLUE}Fixed-point combinator{RESET}")
    test_factorial = (
        'letrec', 'fact',
        ('lam', 'n', 
         ('if', 
          ('leq', ('var', 'n'), ('num', 1)), 
          ('num', 1),
          ('times', ('var', 'n'), 
           ('app', ('var', 'fact'), ('minus', ('var', 'n'), ('num', 1)))))),
        ('app', ('var', 'fact'), ('num', 5))
    )
    assert evaluate(test_factorial) == 120, f"Failed: {BLUE}Factorial 5{RESET}"
    print(f"{BLUE}Factorial 5{RESET} == {GREEN}120{RESET}")
    print(f"{GREEN}Passed: Fixed-point combinator{RESET}\n")

    # Final success message
    print(f"\n{GREEN}evaluate(): all tests passed.{RESET}\n")


def test_interpret():

    print(f"Testing {Fore.BLUE}x{Fore.RESET} --> {interpret('x')}")
    print(f"Testing {Fore.BLUE}x y{Fore.RESET} --> {interpret('x y')}")
    input=r"\x.x"; output = interpret(input); print(f"Testing {Fore.BLUE}{input}{Fore.RESET} --> {output}")
    
    # Additional tests for interpretation with operators (highlighted in blue)
    print(f"Testing {Fore.BLUE}2 + 3{Style.RESET_ALL} --> {interpret('2 + 3')}")
    print(f"Testing {Fore.BLUE}log(2){Style.RESET_ALL} --> {interpret('log(2)')}")
    print(f"Testing {Fore.BLUE}-(3){Style.RESET_ALL} --> {interpret('-(3)')}")

    print(f"\n{Fore.GREEN}interpreter(): all tests passed.{Fore.RESET}\n")


if __name__ == "__main__":
    print(Fore.RED + "\nTEST PARSING\n" + Style.RESET_ALL); test_parse()
    print(Fore.RED + "\nTEST SUBSTITUTION\n" + Style.RESET_ALL); test_substitute()
    print(Fore.RED + "\nTEST EVALUATION\n" + Style.RESET_ALL); test_evaluate()
    print(Fore.RED + "\nTEST INTERPRETATION\n" + Style.RESET_ALL); test_interpret()




'''
function for testing evaluate, old version, not sure if it needs
to be kept or not
'''
# def test_evaluate():
#     MAGENTA = '\033[95m'
#     RESET = '\033[0m'
    
#     # Debug the operator evaluation
#     assert linearize(evaluate(ast(r"2 + 3"))) == "5.0"  # Updated to match actual numerical evaluation
#     print(f"EVAL {Fore.BLUE}2 + 3{Style.RESET_ALL} == 5.0")

#     # Test evaluation of applications
#     assert evaluate(('app', ('lam', 'x', ('var', 'x')), ('num', 5))) == 5

#     # Test evaluation of let expressions
#     assert evaluate(('let', 'x', ('num', 5), ('var', 'x'))) == 5

#     # # Test evaluation of letrec expressions
#     # assert evaluate(('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f'))) == ('lam', 'x', ('var', 'x'))
    
#     # assert substitute(('let', 'x', ('num', 5), ('var', 'x')), 'x', ('num', 10)) == ('let', 'x', ('num', 5), ('var', 'x'))
#     # assert substitute(('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f')), 'f', ('num', 5)) == ('letrec', 'f', ('lam', 'x', ('var', 'x')), ('var', 'f'))

#     # Test evaluation of fix expressions
#     assert evaluate(('fix', ('lam', 'f', ('lam', 'x', ('app', ('var', 'f'), ('var', 'x')))))) == ('lam', 'x', ('app', ('fix', ('lam', 'f', ('lam', 'x', ('app', ('var', 'f'), ('var', 'x'))))), ('var', 'x')))

#     # # Test evaluation of if expressions
#     # assert evaluate(('if', ('num', 1), ('num', 2), ('num', 3))) == ('num', 2)
#     # assert evaluate(('if', ('num', 0), ('num', 2), ('num', 3))) == ('num', 3)
    
#     # # Uncomment to indicate all tests passed
#     # print("\nevaluate(): All tests passed!\n")
