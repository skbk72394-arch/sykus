#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus Engine - The Auto-Healing Transpiler                                 ║
║                                                                              ║
║   Core Features:                                                             ║
║   - Transpiles Sykus to Python/JavaScript/Kotlin                             ║
║   - Auto-heals errors and continues execution                                ║
║   - Ghost dependency installation                                            ║
║   - Smart database management                                                ║
║   - Polyglot code embedding                                                  ║
║                                                                              ║
║   Philosophy: "Line 4 had a typo. I fixed it and ran it."                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import os
import sys
import json
import traceback
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from colorama import Fore, Style

# Import Sykus components
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.syntax import SykusSyntaxParser, parse_value, value_to_python
from ghost.dependency_manager import get_ghost_manager
from state.smart_memory import get_smart_memory
from healer.auto_healer import get_auto_healer, ErrorTranslator
from bridge.polyglot import get_polyglot_bridge


class SykusEngine:
    """
    Main Sykus Engine - Auto-Healing Transpiler
    
    Transpiles natural English Sykus code to executable Python/JS/Kotlin.
    Automatically fixes errors and installs dependencies.
    """
    
    def __init__(self):
        self.ghost = get_ghost_manager()
        self.memory = get_smart_memory()
        self.healer = get_auto_healer()
        self.polyglot = get_polyglot_bridge()
        
        # Execution context
        self.variables: Dict[str, Any] = {}
        self.agents: Dict[str, Any] = {}
        self.mode = 'ai'
        self.output_lines: List[str] = []
        self.indent_level = 0
        
        # Track auto-heals
        self.heals_made: List[Dict] = []
    
    def execute(self, source: str, mode: str = 'auto', verbose: bool = False) -> Dict[str, Any]:
        """
        Execute Sykus source code with auto-healing
        
        Args:
            source: Sykus source code
            mode: Execution mode (auto, ai, web, desktop)
            verbose: Enable verbose output
        
        Returns:
            Execution result dict
        """
        self.mode = mode if mode != 'auto' else 'ai'
        self.heals_made = []
        
        try:
            # Phase 1: Ghost install dependencies
            if verbose:
                print(f"{Fore.BLUE}[Sykus]{Style.RESET_ALL} Checking dependencies...")
            
            deps = self.ghost.detect_required_modules(source)
            for dep in deps:
                if verbose:
                    print(f"{Fore.BLUE}[Sykus]{Style.RESET_ALL} Auto-installing {dep}...")
                result = self.ghost.ghost_install(dep, silent=not verbose)
                if not result.success and verbose:
                    print(f"{Fore.YELLOW}[Sykus]{Style.RESET_ALL} Could not install {dep}")
            
            # Phase 2: Parse and transpile
            if verbose:
                print(f"{Fore.BLUE}[Sykus]{Style.RESET_ALL} Parsing...")
            
            parser = SykusSyntaxParser(source)
            tokens = parser.parse()
            
            if verbose:
                print(f"{Fore.BLUE}[Sykus]{Style.RESET_ALL} Transpiling to Python...")
            
            python_code = self._transpile(tokens)
            
            # Phase 3: Execute with healing
            if verbose:
                print(f"{Fore.BLUE}[Sykus]{Style.RESET_ALL} Executing...")
                print()
            
            result = self._execute_with_healing(python_code, source)
            
            # Report heals
            if self.heals_made:
                print(self.healer.report_heals())
            
            return result
            
        except Exception as e:
            # Final error handling
            print(ErrorTranslator.format_friendly(e))
            return {'success': False, 'error': str(e)}
    
    def build(self, source: str, target: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Build Sykus source for a target platform
        
        Args:
            source: Sykus source code
            target: Build target (web, apk, python, javascript)
            output_dir: Output directory
        
        Returns:
            Build result dict
        """
        try:
            parser = SykusSyntaxParser(source)
            tokens = parser.parse()
            
            if target == 'python':
                code = self._transpile(tokens)
                output_path = self._save_python(code, output_dir)
                return {'success': True, 'output_path': output_path}
            
            elif target == 'javascript' or target == 'web':
                code = self._transpile_to_js(tokens)
                output_path = self._save_js(code, output_dir)
                return {'success': True, 'output_path': output_path}
            
            elif target == 'apk':
                # Generate Android project
                output_path = self._generate_android_project(tokens, output_dir)
                return {'success': True, 'output_path': output_path}
            
            else:
                return {'success': False, 'error': f'Unknown target: {target}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _transpile(self, tokens: List[Any]) -> str:
        """Transpile tokens to Python code"""
        lines = [
            '#!/usr/bin/env python3',
            '# Auto-generated by Sykus Engine',
            '',
            'import sys',
            'import os',
            '',
        ]
        
        # Track imports needed
        imports = set()
        
        # Process tokens
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Handle block structures
            if token.type in ['if', 'while', 'for', 'async', 'background', 'call_with_block', 'event']:
                block_lines, consumed = self._process_block(tokens, i)
                lines.extend(block_lines)
                i = consumed
                continue
            
            # Handle single-line statements
            line = self._token_to_python(token, imports)
            if line:
                lines.append(line)
            
            i += 1
        
        # Add imports at the top
        import_lines = []
        for imp in sorted(imports):
            import_lines.append(imp)
        
        return '\n'.join(import_lines + [''] + lines)
    
    def _token_to_python(self, token: Any, imports: set) -> Optional[str]:
        """Convert a single token to Python"""
        
        if token.type == 'mode':
            mode, name = token.value
            return f'# Mode: {mode}, App: {name}'
        
        elif token.type == 'use':
            module = token.value[0]
            # Map to Python import
            import_map = {
                'speech': 'import speech_recognition as sr',
                'tts': 'import pyttsx3',
                'voice': 'import speech_recognition as sr\nimport pyttsx3',
                'gemini': 'import google.generativeai as genai',
                'openai': 'import openai',
                'http': 'import requests',
                'json': 'import json',
                'time': 'import time',
                'os': 'import os',
                'sys': 'import sys',
            }
            if module in import_map:
                imports.add(import_map[module])
            return None
        
        elif token.type == 'variable':
            name, value_str = token.value
            value = parse_value(value_str)
            return f'{name} = {value_to_python(value)}'
        
        elif token.type == 'agent':
            name, agent_type, key = token.value
            imports.add('import google.generativeai as genai')
            return f'{name} = genai.configure(api_key="{key}")'
        
        elif token.type == 'say':
            text = token.value[0]
            imports.add('import pyttsx3')
            return f'''
try:
    _tts = pyttsx3.init()
    _tts.say({value_to_python(parse_value(text))})
    _tts.runAndWait()
except:
    print(f"[Say] {{{value_to_python(parse_value(text))}}}")
'''
        
        elif token.type == 'show':
            what = token.value[0]
            return f'print({value_to_python(parse_value(what))})'
        
        elif token.type == 'call':
            obj, method, args = token.value
            if args:
                return f'{obj}.{method}({args})'
            return f'{obj}.{method}()'
        
        elif token.type == 'fetch':
            url, save_to = token.value
            imports.add('import requests')
            return f'''
try:
    _resp = requests.get("{url}")
    {save_to} = _resp.json()
except Exception as e:
    print(f"[Fetch Error] {{e}}")
    {save_to} = {{}}
'''
        
        elif token.type == 'db_save':
            var, db = token.value
            imports.add('from state.smart_memory import save')
            return f'save("{var}", {var}, to="{db}")'
        
        elif token.type == 'db_load':
            var, db = token.value
            imports.add('from state.smart_memory import load')
            return f'{var} = load("{var}", from_="{db}", default={{}})'
        
        elif token.type == 'return':
            value = token.value[0]
            return f'return {value_to_python(parse_value(value))}'
        
        elif token.type == 'stop':
            return 'sys.exit(0)'
        
        elif token.type == 'polyglot':
            lang = token.value['lang']
            code = token.value['code']
            
            if lang == 'python':
                # Execute directly
                return f'# [[python]] block\n{code}'
            else:
                # Use polyglot bridge
                imports.add('from bridge.polyglot import get_polyglot_bridge')
                return f'''
_polyglot = get_polyglot_bridge()
_polyglot_result = _polyglot.execute("{lang}", """{code}""")
if _polyglot_result.success:
    print(_polyglot_result.output)
else:
    print(f"[Polyglot Error] {{{_polyglot_result.error}}}")
'''
        
        elif token.type == 'expression':
            # Raw expression
            return token.value
        
        return None
    
    def _process_block(self, tokens: List[Any], start_idx: int) -> Tuple[List[str], int]:
        """Process a block structure (if, while, for, etc.)"""
        token = tokens[start_idx]
        lines = []
        i = start_idx + 1
        
        # Get base indent level
        base_indent = 0
        
        if token.type == 'if':
            condition = token.value[0]
            lines.append(f'if {self._condition_to_python(condition)}:')
            
            # Collect block body
            body_lines, i = self._collect_block_body(tokens, i)
            for line in body_lines:
                lines.append(f'    {line}')
        
        elif token.type == 'while':
            condition = token.value[0]
            lines.append(f'while {self._condition_to_python(condition)}:')
            
            body_lines, i = self._collect_block_body(tokens, i)
            for line in body_lines:
                lines.append(f'    {line}')
        
        elif token.type == 'for':
            var, iterable = token.value
            lines.append(f'for {var} in {iterable}:')
            
            body_lines, i = self._collect_block_body(tokens, i)
            for line in body_lines:
                lines.append(f'    {line}')
        
        elif token.type == 'async':
            lines.append('async def _async_block():')
            
            body_lines, i = self._collect_block_body(tokens, i)
            for line in body_lines:
                lines.append(f'    {line}')
            lines.append('')
            lines.append('import asyncio')
            lines.append('asyncio.run(_async_block())')
        
        elif token.type == 'background':
            lines.append('def _bg_task():')
            
            body_lines, i = self._collect_block_body(tokens, i)
            for line in body_lines:
                lines.append(f'    {line}')
            lines.append('')
            lines.append('import threading')
            lines.append('threading.Thread(target=_bg_task, daemon=True).start()')
        
        elif token.type == 'call_with_block':
            obj, method = token.value
            lines.append(f'{obj}.{method}()')
            
            body_lines, i = self._collect_block_body(tokens, i)
            # These are typically event handlers
        
        elif token.type == 'event':
            event, target = token.value
            handler_name = f'_handler_{event}_{target}'
            lines.append(f'def {handler_name}():')
            
            body_lines, i = self._collect_block_body(tokens, i)
            for line in body_lines:
                lines.append(f'    {line}')
        
        return lines, i
    
    def _collect_block_body(self, tokens: List[Any], start_idx: int) -> Tuple[List[str], int]:
        """Collect all lines in a block"""
        body = []
        i = start_idx
        
        # Determine base indentation from first non-empty line
        base_indent = None
        
        while i < len(tokens):
            token = tokens[i]
            
            # Check if this is still in the block
            # (In real implementation, check actual indentation)
            # For now, assume all consecutive tokens are in block
            
            if token.type in ['elif', 'else']:
                # End of this block
                break
            
            line = self._token_to_python(token, set())
            if line:
                body.append(line)
            
            i += 1
        
        return body, i
    
    def _condition_to_python(self, condition: str) -> str:
        """Convert Sykus condition to Python"""
        # Replace Sykus operators with Python
        condition = condition.replace(' equals ', ' == ')
        condition = condition.replace(' is ', ' == ')
        condition = condition.replace(' contains ', ' in ')
        condition = condition.replace(' has ', ' in ')
        
        # Handle 'hear' keyword
        if 'hear' in condition:
            match = re.search(r'hear\s+["\']([^"\']+)["\']', condition)
            if match:
                phrase = match.group(1)
                return f'"{phrase}" in command'
        
        return condition
    
    def _execute_with_healing(self, python_code: str, original_source: str) -> Dict[str, Any]:
        """Execute Python code with interactive auto-healing"""
        max_retries = 3 # Prevent infinite loops
        retries = 0

        current_python_code = python_code # Use a mutable variable for the code to be executed

        while retries < max_retries:
            try:
                # Create execution context
                exec_globals = {
                    '__name__': '__main__',
                    '__file__': '<sykus>',
                }

                # Execute
                exec(current_python_code, exec_globals)

                return {'success': True}

            except Exception as e:
                print(f"{Fore.RED}[Sykus Engine]{Style.RESET_ALL} Execution error detected: {type(e).__name__}")
                
                # Attempt interactive healing
                healed_source, heals = self.healer.heal_source(current_python_code, e)

                if heals:
                    # Fix applied, retry execution with healed source
                    current_python_code = healed_source # Update the code to be executed
                    self.heals_made.extend(heals)
                    retries += 1
                    print(f"{Fore.BLUE}[Sykus Engine]{Style.RESET_ALL} Retrying execution after fix (attempt {retries}/{max_retries})...")
                    continue # Try again with the fixed code
                else:
                    # User declined fix or no fix found, report final error
                    print(ErrorTranslator.format_friendly(e))
                    return {'success': False, 'error': str(e)}

        print(f"{Fore.RED}[Sykus Engine]{Style.RESET_ALL} Max auto-fix retries reached. Aborting.")
        # Report the last error if available, otherwise a generic one
        if 'e' in locals():
            print(ErrorTranslator.format_friendly(e))
        else:
            print(f"{Fore.RED}[Sykus Engine]{Style.RESET_ALL} An unknown error occurred and could not be fixed.")
        return {'success': False, 'error': str(e) if 'e' in locals() else "Unknown error"}
    
    def _transpile_to_js(self, tokens: List[Any]) -> str:
        """Transpile tokens to JavaScript"""
        lines = [
            '// Auto-generated by Sykus Engine',
            'class SykusApp {',
            '    constructor() {',
            '        this.variables = {};',
            '        this.elements = {};',
            '    }',
            '',
            '    async init() {',
        ]
        
        for token in tokens:
            if token.type == 'say':
                text = token.value[0]
                lines.append(f'        console.log("{text}");')
            elif token.type == 'show':
                what = token.value[0]
                lines.append(f'        alert("{what}");')
            elif token.type == 'fetch':
                url, save_to = token.value
                lines.append(f'        this.variables["{save_to}"] = await fetch("{url}").then(r => r.json());')
        
        lines.extend([
            '    }',
            '}',
            '',
            'const app = new SykusApp();',
            'app.init();',
        ])
        
        return '\n'.join(lines)
    
    def _save_python(self, code: str, output_dir: Optional[str]) -> str:
        """Save Python code to file"""
        out_dir = Path(output_dir or 'dist')
        out_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = out_dir / 'main.py'
        file_path.write_text(code)
        
        return str(file_path)
    
    def _save_js(self, code: str, output_dir: Optional[str]) -> str:
        """Save JavaScript code to file"""
        out_dir = Path(output_dir or 'dist/web')
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Create HTML wrapper
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Sykus App</title>
</head>
<body>
    <script>
{code}
    </script>
</body>
</html>'''
        
        html_path = out_dir / 'index.html'
        html_path.write_text(html)
        
        return str(out_dir)
    
    def _generate_android_project(self, tokens: List[Any], output_dir: Optional[str]) -> str:
        """Generate Android project structure"""
        out_dir = Path(output_dir or 'dist/android')
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main.py for Kivy
        kivy_code = self._generate_kivy_code(tokens)
        (out_dir / 'main.py').write_text(kivy_code)
        
        # Create buildozer.spec
        spec = '''[app]
title = SykusApp
package.name = sykusapp
package.domain = org.sykus
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
orientation = portrait
android.api = 33
android.minapi = 21
'''
        (out_dir / 'buildozer.spec').write_text(spec)
        
        return str(out_dir)
    
    def _generate_kivy_code(self, tokens: List[Any]) -> str:
        """Generate Kivy Python code"""
        lines = [
            'from kivy.app import App',
            'from kivy.uix.boxlayout import BoxLayout',
            'from kivy.uix.button import Button',
            'from kivy.uix.label import Label',
            'from kivy.uix.textinput import TextInput',
            '',
            'class MainApp(App):',
            '    def build(self):',
            '        layout = BoxLayout(orientation="vertical")',
        ]
        
        for token in tokens:
            if token.type == 'ui_create':
                elem_type, name, text = token.value
                if elem_type == 'button':
                    lines.append(f'        btn = Button(text="{text}")')
                    lines.append(f'        layout.add_widget(btn)')
                elif elem_type == 'text':
                    lines.append(f'        lbl = Label(text="{text}")')
                    lines.append(f'        layout.add_widget(lbl)')
        
        lines.extend([
            '        return layout',
            '',
            'if __name__ == "__main__":',
            '    MainApp().run()',
        ])
        
        return '\n'.join(lines)


# Convenience function
def run_sykus(source: str, mode: str = 'auto') -> Dict[str, Any]:
    """Quick run Sykus source"""
    engine = SykusEngine()
    return engine.execute(source, mode=mode)
