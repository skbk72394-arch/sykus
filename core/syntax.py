"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus Syntax Definitions                                                   ║
║                                                                              ║
║   Ultra-minimal, frustration-free syntax rules                               ║
║   No brackets, no semicolons, just natural English                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union


# ==================== SYKUS SYNTAX PATTERNS ====================

SYKUS_PATTERNS = {
    # Comments
    'comment': r'^\s*#.*$',
    
    # Mode declaration
    'mode': r'^\s*(ai|web|app|desktop)\s+(\w+)\s*$',
    
    # Variable assignment - ultra simple: name = value
    'variable': r'^\s*(\w+)\s*=\s*(.+)$',
    
    # AI Agent creation
    'agent': r'^\s*Agent\s+(\w+)\s*=\s*use\s+(\w+)\s*\(\s*key\s*=\s*"([^"]*)"\s*\)',
    
    # Function call with arrow block
    'call_with_block': r'^\s*(\w+)\.(\w+)\(\)\s*->\s*$',
    
    # Simple function call
    'call': r'^\s*(\w+)\.(\w+)\((.*)\)\s*$',
    
    # Method chain
    'chain': r'^\s*(\w+)\.(\w+)\(\)\s*->\s*(\w+)\.(\w+)\(\)\s*$',
    
    # UI creation
    'ui_create': r'^\s*create\s+(\w+)\s+(\w+)\s+text\s+"([^"]*)"',
    
    # Output commands
    'say': r'^\s*say\s+(.+)$',
    'show': r'^\s*show\s+(.+)$',
    
    # Event handler
    'event': r'^\s*on\s+(\w+)\s+(\w+)\s*->\s*$',
    
    # Database operations
    'db_save': r'^\s*save\s+(\w+)\s+to\s+(\w+)\s*$',
    'db_load': r'^\s*load\s+(\w+)\s+from\s+(\w+)\s*$',
    
    # Conditional
    'if': r'^\s*if\s+(.+?)\s+then\s*$',
    'elif': r'^\s*else\s+if\s+(.+?)\s+then\s*$',
    'else': r'^\s*else\s*$',
    
    # Loops
    'for': r'^\s*for\s+(\w+)\s+in\s+(\w+)\s*->\s*$',
    'while': r'^\s*while\s+(.+?)\s*->\s*$',
    
    # Async
    'async': r'^\s*async\s*->\s*$',
    'await': r'^\s*await\s+(.+)$',
    
    # Background
    'background': r'^\s*background\s*->\s*$',
    
    # Fetch
    'fetch': r'^\s*fetch\s+"([^"]+)"\s+save\s+to\s+(\w+)',
    
    # Use module
    'use': r'^\s*use\s+(\w+)',
    
    # Polyglot blocks
    'polyglot_start': r'^\s*\[\[(\w+)\]\]\s*$',
    'polyglot_end': r'^\s*\[\[end\]\]\s*$',
    
    # Return
    'return': r'^\s*return\s+(.+)$',
    
    # Stop
    'stop': r'^\s*stop\s*$',
}


@dataclass
class SykusToken:
    """A parsed Sykus token"""
    type: str
    value: Any
    line: int
    raw: str


class SykusSyntaxParser:
    """Parse Sykus source code into tokens"""
    
    def __init__(self, source: str):
        self.source = source
        self.lines = source.split('\n')
        self.tokens: List[SykusToken] = []
        self.line_num = 0
        self.in_polyglot = False
        self.polyglot_lang = None
        self.polyglot_code = []
    
    def parse(self) -> List[SykusToken]:
        """Parse entire source into tokens"""
        while self.line_num < len(self.lines):
            line = self.lines[self.line_num]
            token = self._parse_line(line)
            if token:
                self.tokens.append(token)
            self.line_num += 1
        
        return self.tokens
    
    def _parse_line(self, line: str) -> Optional[SykusToken]:
        """Parse a single line"""
        
        # Handle polyglot blocks
        if self.in_polyglot:
            if re.match(SYKUS_PATTERNS['polyglot_end'], line):
                # End polyglot block
                token = SykusToken(
                    type='polyglot',
                    value={'lang': self.polyglot_lang, 'code': '\n'.join(self.polyglot_code)},
                    line=self.line_num,
                    raw=f'[[{self.polyglot_lang}]]...[[end]]'
                )
                self.in_polyglot = False
                self.polyglot_lang = None
                self.polyglot_code = []
                return token
            else:
                # Collect polyglot code
                self.polyglot_code.append(line)
                return None
        
        # Check for polyglot start
        polyglot_match = re.match(SYKUS_PATTERNS['polyglot_start'], line)
        if polyglot_match:
            self.in_polyglot = True
            self.polyglot_lang = polyglot_match.group(1)
            return None
        
        # Skip empty lines and comments
        if not line.strip() or re.match(SYKUS_PATTERNS['comment'], line):
            return None
        
        # Try each pattern
        for pattern_name, pattern in SYKUS_PATTERNS.items():
            if pattern_name in ['polyglot_start', 'polyglot_end', 'comment']:
                continue
            
            match = re.match(pattern, line)
            if match:
                return SykusToken(
                    type=pattern_name,
                    value=match.groups(),
                    line=self.line_num,
                    raw=line.strip()
                )
        
        # Unknown line - could be an expression
        if line.strip():
            return SykusToken(
                type='expression',
                value=line.strip(),
                line=self.line_num,
                raw=line.strip()
            )
        
        return None
    
    def get_indent_level(self, line: str) -> int:
        """Get the indentation level of a line"""
        return len(line) - len(line.lstrip())


# ==================== VALUE PARSERS ====================

def parse_value(value_str: str) -> Any:
    """Parse a Sykus value into Python equivalent"""
    value_str = value_str.strip()
    
    # String
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Number (integer)
    if re.match(r'^-?\d+$', value_str):
        return int(value_str)
    
    # Number (float)
    if re.match(r'^-?\d+\.\d+$', value_str):
        return float(value_str)
    
    # Boolean
    if value_str.lower() in ('true', 'yes'):
        return True
    if value_str.lower() in ('false', 'no'):
        return False
    
    # List
    if value_str.startswith('[') and value_str.endswith(']'):
        items = value_str[1:-1].split(',')
        return [parse_value(item.strip()) for item in items if item.strip()]
    
    # Dictionary
    if value_str.startswith('{') and value_str.endswith('}'):
        # Simple dict parsing
        result = {}
        content = value_str[1:-1]
        pairs = content.split(',')
        for pair in pairs:
            if ':' in pair:
                key, val = pair.split(':', 1)
                result[key.strip().strip('"\'')] = parse_value(val)
        return result
    
    # Variable reference
    return {'_var': value_str}


def value_to_python(value: Any) -> str:
    """Convert a parsed value to Python code"""
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        items = [value_to_python(item) for item in value]
        return f'[{", ".join(items)}]'
    if isinstance(value, dict):
        if '_var' in value:
            return value['_var']
        items = [f'"{k}": {value_to_python(v)}' for k, v in value.items()]
        return f'{{{", ".join(items)}}}'
    return str(value)
