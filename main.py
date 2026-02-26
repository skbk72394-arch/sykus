import sys
import os
import traceback
from lexer import Lexer, Token, TokenTypeList, KEYWORDS
from parser import Parser, ParseError
from evaluator import Evaluator
from environment import Environment
from stdlib import register_stdlib

class SykusAutoHealer:
    def guess_fix(self, code, error):
        lines = code.split('\n')
        error_msg = str(error)
        
        # 1. Unclosed string
        for i, line in enumerate(lines):
            if line.count('"') % 2 != 0:
                lines[i] = line + '"'
                return '\n'.join(lines)
                
        # 2. Missing closing brace
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces > close_braces:
            lines.append('}' * (open_braces - close_braces))
            return '\n'.join(lines)
            
        # 3. Misspelled keywords
        import difflib
        try:
            lexer = Lexer(code)
            tokens = []
            while True:
                tok = lexer.next_token()
                if tok.type == TokenTypeList.EOF:
                    break
                tokens.append(tok)
                
            for tok in tokens:
                if tok.type == TokenTypeList.IDENT:
                    for kw in KEYWORDS.keys():
                        if difflib.SequenceMatcher(None, tok.literal, kw).ratio() > 0.8:
                            if tok.line <= len(lines):
                                line_idx = tok.line - 1
                                lines[line_idx] = lines[line_idx].replace(tok.literal, kw, 1)
                                return '\n'.join(lines)
        except Exception:
            pass

        # 4. Missing semicolon at the end of statements
        if "Expected next token" in error_msg:
            if hasattr(error, 'line') and error.line <= len(lines):
                line_idx = error.line - 1
                if not lines[line_idx].strip().endswith(';'):
                    lines[line_idx] = lines[line_idx] + ';'
                    return '\n'.join(lines)

        return None

def handle_error(e, code, filepath=None):
    is_runtime = isinstance(e, RuntimeError)
    error_type = "Runtime Error" if is_runtime else "Syntax Error"
    
    print(f"\n[{error_type}]: {str(e)}")
    
    line_num = getattr(e, 'line', None)
    col_num = getattr(e, 'column', None)
    
    if not line_num and "line=" in str(e):
        pass # Could be extracted from string representation if needed
        
    lines = code.split('\n')
    if line_num and 1 <= line_num <= len(lines):
        error_line = lines[line_num - 1]
        print(f"  Line {line_num}:")
        print(f"    {error_line}")
        if col_num:
            padding = " " * (col_num - 1)
            print(f"    {padding}^^^^^")
        else:
            print(f"    ^^^^^")
            
    if filepath:
        healer = SykusAutoHealer()
        fixed_code = healer.guess_fix(code, e)
        if fixed_code:
            print(f"\nSuggested Fix:\n{fixed_code}")
            try:
                ans = input("[?] Do you want Sykus to auto-fix this file? (Y/N): ")
                if ans.strip().lower() == 'y':
                    with open(filepath, 'w') as f:
                        f.write(fixed_code)
                    print("File auto-fixed! Re-running...\n")
                    
                    new_evaluator = Evaluator()
                    new_env = new_evaluator.globals
                    register_stdlib(new_env)
                    run_code(fixed_code, new_env, new_evaluator, filepath)
            except EOFError:
                pass

def run_code(code, env, evaluator, filepath=None):
    lexer = Lexer(code)
    parser = Parser(lexer)
    try:
        program = parser.parse_program()
    except ParseError as e:
        handle_error(e, code, filepath)
        return
    except Exception as e:
        handle_error(e, code, filepath)
        return
        
    try:
        evaluator.eval(program, env)
    except Exception as e:
        handle_error(e, code, filepath)

def repl():
    print("Sykus v5.0 (The Auto-Healing Engine)")
    evaluator = Evaluator()
    env = evaluator.globals
    register_stdlib(env)
    
    while True:
        try:
            line = input("syk>>> ")
            if line.strip() == "exit":
                break
            if not line.strip():
                continue
            run_code(line, env, evaluator)
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
        except EOFError:
            print("\nExiting Sykus REPL...")
            break

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "run" and len(sys.argv) > 2:
            filepath = sys.argv[2]
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return
            with open(filepath, 'r') as f:
                code = f.read()
            
            evaluator = Evaluator()
            env = evaluator.globals
            register_stdlib(env)
            run_code(code, env, evaluator, filepath)
        else:
            filepath = sys.argv[1]
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return
            with open(filepath, 'r') as f:
                code = f.read()
            
            evaluator = Evaluator()
            env = evaluator.globals
            register_stdlib(env)
            run_code(code, env, evaluator, filepath)
    else:
        repl()

if __name__ == "__main__":
    main()
