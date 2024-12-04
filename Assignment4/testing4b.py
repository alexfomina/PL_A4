import os
import subprocess
import re
import glob

TIMEOUT = 0.2  # Timeout duration in seconds


def load_tests(file_path):
    """Load test cases from the given file."""
    tests = []
    with open(file_path, 'r') as file:
        for line in file:
            name, input, expected_output = line.strip().split(', ')
            tests.append((name, input, expected_output))
    return tests


def run_test(program, input):
    """Run the program with the provided input and capture its output."""
    try:
        result = subprocess.run(
            ['python3', program, input],
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT", ""


def remove_ansi_escape_sequences(text):
    """Remove ANSI escape sequences for clean comparison."""
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def remove_old_py_txt_files():
    """Remove old result files with the .py.txt extension."""
    for file_path in glob.glob("*.py.txt"):
        try:
            os.remove(file_path)
            print(f"Removed old file: {file_path}")
        except OSError as e:
            print(f"Error removing file {file_path}: {e}")


def normalize_expression(expr):
    """Normalize a lambda expression for consistent comparison."""
    # Remove unnecessary spaces and normalize parentheses
    expr = re.sub(r'\s+', ' ', expr.strip())  # Normalize whitespace
    expr = re.sub(r'\(\s+', '(', expr)  # Remove space after '('
    expr = re.sub(r'\s+\)', ')', expr)  # Remove space before ')'
    expr = re.sub(r'\s+->', ' ->', expr)  # Consistent arrow spacing

    # Simplify repeated parentheses: ((\x.x)) -> (\x.x)
    while re.search(r'\(\((.*?)\)\)', expr):
        expr = re.sub(r'\(\((.*?)\)\)', r'(\1)', expr)

    return expr


class FreshNameRenamer:
    """Class for generating consistent fresh variable names."""
    def __init__(self):
        self.name_mapping = {}
        self.counter = 0

    def get_fresh_name(self, old_name):
        """Generate a fresh variable name for the given old name."""
        if old_name not in self.name_mapping:
            self.counter += 1
            self.name_mapping[old_name] = f"Var{self.counter}"
        return self.name_mapping[old_name]


def rename_variables(expr):
    """Rename bound variables consistently in the given expression."""
    renamer = FreshNameRenamer()
    tokens = re.split(r'(\W+)', expr)  # Split on non-word characters
    renamed_tokens = [
        renamer.get_fresh_name(token) if re.match(r'^[a-zA-Z_]\w*$', token) else token
        for token in tokens
    ]
    return ''.join(renamed_tokens)


def alpha_equivalence(expr1, expr2):
    """Check alpha-equivalence between two lambda expressions."""
    renamed_expr1 = rename_variables(expr1)
    renamed_expr2 = rename_variables(expr2)
    return renamed_expr1 == renamed_expr2


def compare_numeric_output(output, expected):
    """Compare numeric outputs with tolerance."""
    try:
        return abs(float(output) - float(expected)) < 1e-9
    except ValueError:
        return False


def main():
    """Main function to process tests and compare results."""
    remove_old_py_txt_files()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tests_path = os.path.join(script_dir, "testing-data.txt")
    tests = load_tests(tests_path)

    for program in os.listdir(script_dir):
        if program.endswith(".py"):  # Only test Python files
            for name, input, expected_output in tests:
                if program.endswith(f"{name}.py"):  # Apply tests matching the program name
                    print(f"Processing \033[95m{program}\033[0m on \033[95m{input}\033[0m")
                    output, error = run_test(program, input)
                    clean_output = remove_ansi_escape_sequences(output)
                    result_file_path = os.path.join(script_dir, f"{program}.txt")

                    with open(result_file_path, 'a') as result_file:
                        # Normalize and rename both the output and expected output
                        normalized_output = normalize_expression(clean_output)
                        normalized_expected = normalize_expression(expected_output)

                        # Compare expressions for alpha-equivalence or numeric equivalence
                        if alpha_equivalence(normalized_output, normalized_expected):
                            result_file.write(f"True | {name} | Input: {input} | Expected: {expected_output} | Output: {clean_output}\n")
                        elif output == "TIMEOUT":
                            result_file.write(f"TIMEOUT | {name} | Input: {input} | Expected: {expected_output} | Output: {output}\n")
                        elif compare_numeric_output(normalized_output, normalized_expected):
                            result_file.write(f"True | {name} | Input: {input} | Expected: {expected_output} | Output: {clean_output}\n")
                        else:
                            result_file.write(f"False | {name} | Input: {input} | Expected: {expected_output} | Output: {clean_output}\n")

                        if error:
                            result_file.write(f"Error: {error}\n")


if __name__ == "__main__":
    main()
