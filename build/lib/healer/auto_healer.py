"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus Auto-Healing Interpreter                                             ║
║                                                                              ║
║   The Core Feature: Never show confusing errors                              ║
║   Automatically fixes code and informs the user gently                       ║
║                                                                              ║
║   "Line 4 had a typo. I fixed it and ran it."                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import sys
import os
import json
import traceback
import subprocess
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from colorama import Fore, Style, init

init(autoreset=True)

_ALWAYS_FIX_CONFIG_PATH = os.path.join(os.environ.get('HOME', '/tmp'), '.sykus_always_fix.json')

def _load_always_fix_config() -> Dict[str, bool]:
    if os.path.exists(_ALWAYS_FIX_CONFIG_PATH):
        with open(_ALWAYS_FIX_CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def _save_always_fix_config(config: Dict[str, bool]):
    with open(_ALWAYS_FIX_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

@dataclass
class HealResult:
    """Result of auto-healing"""
    healed: bool
    original_line: str
    fixed_line: str
    explanation: str
    line_num: int


@dataclass
class ErrorFix:
    """A known error pattern and its fix"""
    pattern: str
    fix_func: Callable[[str, Exception], Optional[str]]
    explanation: str


class AutoHealer:
    """
    Auto-Healing Engine for Sykus
    
    Detects common errors and automatically fixes them.
    """
    
    # Known error patterns and their fixes
    ERROR_FIXES = [
        # Import errors
        ErrorFix(
            pattern=r'No module named',
            fix_func=lambda line, err: _fix_module_not_found(line, err),
            explanation='Missing module - will auto-install'
        ),
        
        # Syntax errors
        ErrorFix(
            pattern=r'invalid syntax',
            fix_func=lambda line, err: _fix_syntax(line),
            explanation='Syntax error detected'
        ),
        
        # Name errors
        ErrorFix(
            pattern=r'name.*is not defined',
            fix_func=lambda line, err: _fix_undefined(line, err),
            explanation='Undefined variable'
        ),
        
        # Indentation errors
        ErrorFix(
            pattern=r'unexpected indent',
            fix_func=lambda line, err: _fix_indent(line),
            explanation='Indentation issue'
        ),
        
        # Quote errors
        ErrorFix(
            pattern=r'EOL while scanning string',
            fix_func=lambda line, err: _fix_quotes(line),
            explanation='Unclosed string quote'
        ),
        
        # Parenthesis errors
        ErrorFix(
            pattern=r'unexpected EOF',
            fix_func=lambda line, err: _fix_parens(line),
            explanation='Missing closing parenthesis'
        ),
        
        # Type errors
        ErrorFix(
            pattern=r'can only concatenate',
            fix_func=lambda line, err: _fix_concat(line),
            explanation='Type mismatch in concatenation'
        ),
        
        # Attribute errors
        ErrorFix(
            pattern=r'has no attribute',
            fix_func=lambda line, err: _fix_attribute(line, err),
            explanation='Method or attribute not found'
        ),
    ]
    
    # Sykus-specific fixes
    SYKUS_FIXES = [
        # Missing 'then' in if statement
        {
            'check': lambda line: re.match(r'^\s*if\s+.+$', line) and 'then' not in line and '->' not in line,
            'fix': lambda line: line.rstrip() + ' then',
            'explanation': "Added 'then' to if statement"
        },
        
        # Missing arrow after listen/on/when
        {
            'check': lambda line: any(x in line for x in ['listen ', 'on click', 'when ']) and '->' not in line,
            'fix': lambda line: line.rstrip() + ' ->',
            'explanation': "Added '->' for block start"
        },
        
        # Missing quotes around string
        {
            'check': lambda line: re.search(r'=\s*[^"\'\[\{0-9]', line) and not re.search(r'=\s*[\'"\[\{0-9]', line),
            'fix': lambda line: re.sub(r'=\s*([^"\'\[\{0-9][^#]*)', lambda m: f'= "{m.group(1).strip()}"', line),
            'explanation': 'Added quotes around string value'
        },
        
        # Python-style assignment instead of Sykus
        {
            'check': lambda line: re.match(r'^\s*\w+\s*=\s*.+$', line) and not line.strip().startswith('set '),
            'fix': lambda line: line,  # Keep as-is, will be handled by transpiler
            'explanation': 'Using Sykus variable syntax'
        },
        
        # Missing 'create' before UI element
        {
            'check': lambda line: re.match(r'^\s*(button|text|input|image|list)\s+', line) and 'create ' not in line,
            'fix': lambda line: 'create ' + line.lstrip(),
            'explanation': "Added 'create' before UI element"
        },
        
        # Missing quotes around element name
        {
            'check': lambda line: 'create ' in line and not re.search(r'create\s+\w+\s+"', line),
            'fix': lambda line: re.sub(r'create\s+(\w+)\s+(\w+)', r'create \1 "\2"', line),
            'explanation': 'Added quotes around element name'
        },
        
        # Unclosed quotes
        {
            'check': lambda line: line.count('"') % 2 == 1,
            'fix': lambda line: line.rstrip() + '"',
            'explanation': 'Closed unclosed quote'
        },
    ]
    
    def __init__(self):
        self.heal_count = 0
        self.heals: List[HealResult] = []
        self.always_fix_config = _load_always_fix_config()
    
    def heal_line(self, line: str, line_num: int, error: Optional[Exception] = None) -> HealResult:
        """
        Attempt to heal a single line for Sykus-specific issues (non-interactive).
        """
        original = line
        fixed = line
        explanation = "No fix needed"
        healed = False

        # Try Sykus-specific fixes
        for fix_rule in self.SYKUS_FIXES:
            if fix_rule['check'](line):
                fixed = fix_rule['fix'](line)
                explanation = fix_rule['explanation']
                healed = fixed != line
                break

        result = HealResult(
            healed=healed,
            original_line=original,
            fixed_line=fixed,
            explanation=explanation,
            line_num=line_num
        )

        if healed:
            # These are non-interactive heals, append directly
            self.heals.append(result)
            self.heal_count += 1

        return result
    
    def heal_source(self, source: str, error: Optional[Exception] = None) -> Tuple[str, List[HealResult]]:
        """
        Heal entire source code, potentially interactively
        
        Returns:
            Tuple of (healed_source, list of heal results)
        """
        lines = source.split('\n')
        healed_lines = list(lines)
        self.heals = []
        self.heal_count = 0
        
        if error:
            # For execution errors, try interactive healing on the relevant line
            tb = traceback.extract_tb(error.__traceback__)
            last_frame = tb[-1]
            line_num_in_py = last_frame.lineno # This is the line number in the transpiled Python code

            # Map Python line number back to original Sykus line number if possible
            # For now, we will just use the Python line number for the fix.
            original_line_content = lines[line_num_in_py - 1] if line_num_in_py > 0 and line_num_in_py <= len(lines) else ""
            
            fixed_line_content = self._interactive_heal(error, original_line_content, line_num_in_py)
            
            if fixed_line_content is not None:
                # If the fix was an installation, we don't modify the line content itself.
                # The execution will be retried.
                if not fixed_line_content.startswith("__INSTALL_MODULE__:") and line_num_in_py > 0 and line_num_in_py <= len(healed_lines):
                    healed_lines[line_num_in_py - 1] = fixed_line_content
                    self.heals.append(HealResult(
                        healed=True,
                        original_line=original_line_content,
                        fixed_line=fixed_line_content,
                        explanation="Interactive fix applied", # Explanation from _interactive_heal is better but this is a placeholder
                        line_num=line_num_in_py
                    ))
                    self.heal_count += 1
                return '\n'.join(healed_lines), self.heals
            else:
                # User declined fix or no fix found interactively
                return source, []
        
        # Fallback to non-interactive Sykus-specific healing if no Python error
        # (This path might be less critical or used during initial transpilation)
        for i, line in enumerate(lines):
            result = self.heal_line(line, i + 1, error)
            healed_lines[i] = result.fixed_line
            if result.healed:
                self.heals.append(result)
        
        return '\n'.join(healed_lines), self.heals
    
    def report_heals(self) -> str:
        """Generate a friendly report of all heals"""
        if not self.heals:
            return ""
        
        lines = [
            f"",
            f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}",
            f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.YELLOW}🩹 Sykus Auto-Healer{Style.RESET_ALL}                                          {Fore.CYAN}║{Style.RESET_ALL}",
            f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}",
        ]
        
        for heal in self.heals:
            lines.extend([
                f"{Fore.CYAN}║{Style.RESET_ALL}  Line {heal.line_num}: {heal.explanation}                          ",
                f"{Fore.CYAN}║{Style.RESET_ALL}    {Fore.RED}Before:{Style.RESET_ALL} {heal.original_line[:50]}",
                f"{Fore.CYAN}║{Style.RESET_ALL}    {Fore.GREEN}After:{Style.RESET_ALL}  {heal.fixed_line[:50]}",
                f"{Fore.CYAN}║{Style.RESET_ALL}",
            ])
        
        lines.extend([
            f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}",
            f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}✓ Fixed {self.heal_count} issue(s) and continued execution{Style.RESET_ALL}          {Fore.CYAN}║{Style.RESET_ALL}",
            f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}",
            f"",
        ])
        
        return '\n'.join(lines)

    def _interactive_heal(self, error: Exception, original_line: str, line_num: int) -> Optional[str]:
        """Interactively prompts user to apply a fix for an error."""
        error_str = str(error)
        proposed_fix = None
        explanation = ""
        module_to_install = None

        for error_fix in self.ERROR_FIXES:
            if re.search(error_fix.pattern, error_str, re.IGNORECASE):
                result = error_fix.fix_func(original_line, error)
                if result:
                    if result.startswith("__INSTALL_MODULE__:"):
                        module_to_install = result.split(":")[1]
                        explanation = f"Missing Python module '{module_to_install}'. Proposed fix: Install '{module_to_install}'."
                        proposed_fix = f"Install module '{module_to_install}'"
                    else:
                        proposed_fix = result
                        explanation = error_fix.explanation
                break

        if not proposed_fix and original_line:
            # Try Sykus-specific fixes if no error-based fix found
            for fix_rule in self.SYKUS_FIXES:
                if fix_rule['check'](original_line):
                    proposed_fix = fix_rule['fix'](original_line)
                    explanation = fix_rule['explanation']
                    break

        if not proposed_fix:
            return None # No fix found

        # Check if this error type is always fixed
        error_type_name = type(error).__name__
        if self.always_fix_config.get(error_type_name, False):
            print(f"{Fore.BLUE}[Sykus Auto-Healer]{Style.RESET_ALL} Auto-applying fix for {error_type_name}: {explanation}")
            if module_to_install:
                print(f"{Fore.GREEN}[Sykus Auto-Healer]{Style.RESET_ALL} Installing {module_to_install}...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', module_to_install])
                    print(f"{Fore.GREEN}[Sykus Auto-Healer]{Style.RESET_ALL} Successfully installed {module_to_install}.")
                except subprocess.CalledProcessError as install_err:
                    print(f"{Fore.RED}[Sykus Auto-Healer]{Style.RESET_ALL} Failed to install {module_to_install}: {install_err}")
                    return None # Installation failed, cannot proceed with fix
                return original_line # Module installed, no line change needed, just retry execution
            return proposed_fix

        print(f"{Fore.RED}\n[Sykus Error]{Style.RESET_ALL} Detected an issue at line {line_num}: {explanation}")
        print(f"  {Fore.RED}Original:{Style.RESET_ALL} {original_line.strip()}")
        if proposed_fix and not module_to_install:
            print(f"  {Fore.GREEN}Proposed:{Style.RESET_ALL} {proposed_fix.strip()}")
        elif module_to_install:
            print(f"  {Fore.GREEN}Proposed:{Style.RESET_ALL} Install Python module '{module_to_install}'")

        while True:
            response = input(f"{Fore.CYAN}[?]{Style.RESET_ALL} Do you want to apply this fix? (y/n/a): ").lower().strip()
            if response == 'y':
                if module_to_install:
                    print(f"{Fore.GREEN}[Sykus Auto-Healer]{Style.RESET_ALL} Installing {module_to_install}...")
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module_to_install])
                        print(f"{Fore.GREEN}[Sykus Auto-Healer]{Style.RESET_ALL} Successfully installed {module_to_install}.")
                    except subprocess.CalledProcessError as install_err:
                        print(f"{Fore.RED}[Sykus Auto-Healer]{Style.RESET_ALL} Failed to install {module_to_install}: {install_err}")
                        return None # Installation failed
                    return original_line # Module installed, no line change needed
                return proposed_fix
            elif response == 'n':
                print(f"{Fore.YELLOW}[Sykus Auto-Healer]{Style.RESET_ALL} Fix declined. Aborting execution.")
                return None
            elif response == 'a':
                self.always_fix_config[error_type_name] = True
                _save_always_fix_config(self.always_fix_config)
                print(f"{Fore.BLUE}[Sykus Auto-Healer]{Style.RESET_ALL} Always applying fix for {error_type_name} in the future.")
                if module_to_install:
                    print(f"{Fore.GREEN}[Sykus Auto-Healer]{Style.RESET_ALL} Installing {module_to_install}...")
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module_to_install])
                        print(f"{Fore.GREEN}[Sykus Auto-Healer]{Style.RESET_ALL} Successfully installed {module_to_install}.")
                    except subprocess.CalledProcessError as install_err:
                        print(f"{Fore.RED}[Sykus Auto-Healer]{Style.RESET_ALL} Failed to install {module_to_install}: {install_err}")
                        return None # Installation failed
                    return original_line # Module installed, no line change needed
                return proposed_fix
            else:
                print(f"{Fore.YELLOW}Invalid input. Please enter 'y', 'n', or 'a'.{Style.RESET_ALL}")

# ==================== FIX HELPER FUNCTIONS ====================

def _fix_syntax(line: str) -> Optional[str]:
    """Fix syntax errors"""
    # Try adding missing colon for Python-style
    if line.strip().startswith(('if ', 'for ', 'while ', 'def ', 'class ')):
        if not line.rstrip().endswith(':'):
            return line.rstrip() + ':'
    return None


def _fix_undefined(line: str, error: Exception) -> Optional[str]:
    """Fix undefined variable errors"""
    # Extract variable name from error
    match = re.search(r"name '(\w+)'", str(error))
    if match:
        var_name = match.group(1)
        # Add initialization before use
        return f'{var_name} = None  # Auto-initialized\n{line}'
    return None


def _fix_indent(line: str) -> Optional[str]:
    """Fix indentation errors"""
    # Remove extra indentation
    return line.lstrip()


def _fix_quotes(line: str) -> Optional[str]:
    """Fix unclosed quotes"""
    # Add closing quote
    if line.count('"') % 2 == 1:
        return line.rstrip() + '"'
    if line.count("'") % 2 == 1:
        return line.rstrip() + "'"
    return None


def _fix_parens(line: str) -> Optional[str]:
    """Fix missing parentheses"""
    # Add closing parenthesis
    open_count = line.count('(') + line.count('[') + line.count('{')
    close_count = line.count(')') + line.count(']') + line.count('}')
    
    if open_count > close_count:
        return line.rstrip() + ')' * (open_count - close_count)
    return None


def _fix_concat(line: str) -> Optional[str]:
    """Fix concatenation type errors"""
    # Convert to f-string
    if '+' in line:
        parts = line.split('+')
        if len(parts) == 2:
            return f'f"{{{parts[0].strip()}}}{{{parts[1].strip()}}}"'
    return None


def _fix_attribute(line: str, error: Exception) -> Optional[str]:
    """Fix attribute errors"""
    # Extract attribute name
    match = re.search(r"has no attribute '(\w+)'", str(error))
    if match:
        attr = match.group(1)
        # Common fixes
        if attr == 'lower':
            return line.replace('.lower()', '')
    return None

def _fix_module_not_found(line: str, error: Exception) -> Optional[str]:
    """Extracts module name from ModuleNotFoundError and returns it, signaling to attempt installation"""
    match = re.search(r"No module named '([\w_]+)'", str(error))
    if match:
        module_name = match.group(1)
        print(f"{Fore.YELLOW}[Sykus Auto-Healer]{Style.RESET_ALL} Detected missing module: {module_name}")
        # Return a special string to indicate a module to install
        return f"__INSTALL_MODULE__:{module_name}"
    return None

# ==================== ERROR TRANSLATOR ====================

class ErrorTranslator:
    """Translates Python errors into friendly English"""
    
    TRANSLATIONS = {
        'SyntaxError': {
            'title': 'Syntax Issue',
            'message': 'There\'s a problem with how the code is written.',
            'tips': [
                'Check for missing quotes around text',
                'Make sure parentheses are closed',
                'Verify indentation is consistent'
            ]
        },
        'IndentationError': {
            'title': 'Spacing Problem',
            'message': 'The spacing at the beginning of a line is incorrect.',
            'tips': [
                'Use the same number of spaces for each block',
                'Don\'t mix tabs and spaces'
            ]
        },
        'NameError': {
            'title': 'Unknown Name',
            'message': 'You\'re using something that hasn\'t been defined yet.',
            'tips': [
                'Define variables before using them: name = "value"',
                'Check for typos in variable names'
            ]
        },
        'TypeError': {
            'title': 'Type Mismatch',
            'message': 'You\'re trying to do something with the wrong type of data.',
            'tips': [
                'Make sure you\'re combining compatible types',
                'Convert numbers to strings for display: str(number)'
            ]
        },
        'ValueError': {
            'title': 'Invalid Value',
            'message': 'A value isn\'t what was expected.',
            'tips': [
                'Check that your values are in the correct format',
                'Verify numbers are actually numbers'
            ]
        },
        'KeyError': {
            'title': 'Missing Key',
            'message': 'Trying to access something that doesn\'t exist in a collection.',
            'tips': [
                'Check that the key exists before accessing it',
                'Use .get() with a default value'
            ]
        },
        'IndexError': {
            'title': 'Out of Range',
            'message': 'Trying to access an item that doesn\'t exist.',
            'tips': [
                'Check the length before accessing items',
                'Remember: the first item is at position 0'
            ]
        },
        'AttributeError': {
            'title': 'Missing Feature',
            'message': 'Something doesn\'t have the feature you\'re trying to use.',
            'tips': [
                'Check the documentation for available features',
                'Make sure you\'re using the right type of object'
            ]
        },
        'ModuleNotFoundError': {
            'title': 'Missing Component',
            'message': 'A required component is not installed.',
            'tips': [
                'Use "use module_name" at the top of your file',
                'The system will try to auto-install it'
            ]
        },
        'ImportError': {
            'title': 'Import Problem',
            'message': 'Could not import a required component.',
            'tips': [
                'Check that the module name is spelled correctly',
                'The system will try to auto-install it'
            ]
        },
        'ZeroDivisionError': {
            'title': 'Division by Zero',
            'message': 'You can\'t divide a number by zero.',
            'tips': [
                'Check that your divisor isn\'t zero',
                'Add a condition to handle zero cases'
            ]
        },
        'FileNotFoundError': {
            'title': 'File Not Found',
            'message': 'The file you\'re trying to access doesn\'t exist.',
            'tips': [
                'Check that the file path is correct',
                'Make sure the file exists before reading it'
            ]
        },
    }
    
    @classmethod
    def translate(cls, error: Exception) -> Dict[str, str]:
        """Translate an error into friendly English"""
        error_type = type(error).__name__
        
        if error_type in cls.TRANSLATIONS:
            info = cls.TRANSLATIONS[error_type].copy()
            info['original'] = str(error)
            return info
        
        # Generic error
        return {
            'title': 'Unexpected Error',
            'message': f'Something went wrong: {str(error)}',
            'tips': ['Check your code for issues', 'Refer to the documentation'],
            'original': str(error)
        }
    
    @classmethod
    def format_friendly(cls, error: Exception, line_num: int = 0) -> str:
        """Format error in a friendly way"""
        translation = cls.translate(error)
        
        lines = [
            f"",
            f"{Fore.RED}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}",
            f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⚠ {translation['title']}{Style.RESET_ALL}                                      {Fore.RED}║{Style.RESET_ALL}",
            f"{Fore.RED}╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}",
        ]
        
        if line_num > 0:
            lines.append(f"{Fore.RED}║{Style.RESET_ALL}  Location: Line {line_num}                                        {Fore.RED}║{Style.RESET_ALL}")
            lines.append(f"{Fore.RED}║{Style.RESET_ALL}                                                               {Fore.RED}║{Style.RESET_ALL}")
        
        lines.extend([
            f"{Fore.RED}║{Style.RESET_ALL}  {translation['message']}                        {Fore.RED}║{Style.RESET_ALL}",
            f"{Fore.RED}║{Style.RESET_ALL}                                                               {Fore.RED}║{Style.RESET_ALL}",
            f"{Fore.RED}║{Style.RESET_ALL}  {Fore.CYAN}Tips:{Style.RESET_ALL}                                                      {Fore.RED}║{Style.RESET_ALL}",
        ])
        
        for tip in translation['tips']:
            lines.append(f"{Fore.RED}║{Style.RESET_ALL}    • {tip[:55]:55} {Fore.RED}║{Style.RESET_ALL}")
        
        lines.extend([
            f"{Fore.RED}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}",
            f"",
        ])
        
        return '\n'.join(lines)


# Singleton instance
_auto_healer = None

def get_auto_healer() -> AutoHealer:
    """Get singleton AutoHealer instance"""
    global _auto_healer
    if _auto_healer is None:
        _auto_healer = AutoHealer()
    return _auto_healer
