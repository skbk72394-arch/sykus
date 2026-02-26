import sys
from .tokenizer import Lexer
from .parser import Parser
from .evaluator import Evaluator
from .environment import Environment
from .stdlib import register_stdlib

def run(code, env=None, evaluator=None):
    lexer = Lexer(code)
    parser = Parser(lexer)
    try:
        program = parser.parse_program()
    except Exception as e:
        print(f"Syntax Error: {e}")
        return
        
    if evaluator is None:
        evaluator = Evaluator()
    if env is None:
        env = evaluator.globals
        register_stdlib(env)
        
    try:
        evaluator.eval(program, env)
    except Exception as e:
        print(f"Runtime Error: {e}")

def repl():
    print("Sykus v4.0 REPL")
    evaluator = Evaluator()
    env = evaluator.globals
    register_stdlib(env)
    
    while True:
        try:
            line = input(">> ")
            if line.strip() == "exit":
                break
            run(line, env, evaluator)
        except (KeyboardInterrupt, EOFError):
            print()
            break

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "run" and len(sys.argv) > 2:
            with open(sys.argv[2], 'r') as f:
                code = f.read()
            run(code)
        else:
            print("Usage: syk run <file.syk>")
    else:
        repl()

if __name__ == "__main__":
    main()
