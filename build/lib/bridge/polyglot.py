"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus Polyglot Bridge                                                      ║
║                                                                              ║
║   Merge Anything - Embed native code from other languages                    ║
║                                                                              ║
║   [[python]]                                                                 ║
║   import os; os.system('clear')                                              ║
║   [[end]]                                                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PolyglotResult:
    """Result of polyglot execution"""
    success: bool
    output: str
    error: str
    return_code: int


class PolyglotBridge:
    """
    Polyglot Bridge - Execute native code blocks
    
    Supports:
    - Python (direct execution)
    - JavaScript (via Node.js)
    - Bash/Shell (direct execution)
    - Kotlin (compilation + execution)
    """
    
    def __init__(self):
        self.globals: Dict[str, Any] = {}
        self.locals: Dict[str, Any] = {}
    
    def execute(self, lang: str, code: str, share_vars: bool = True) -> PolyglotResult:
        """
        Execute polyglot code block
        
        Args:
            lang: Language identifier (python, javascript, bash, kotlin)
            code: Code to execute
            share_vars: Whether to share variables with main context
        
        Returns:
            PolyglotResult with execution results
        """
        handlers = {
            'python': self._exec_python,
            'py': self._exec_python,
            'javascript': self._exec_javascript,
            'js': self._exec_javascript,
            'bash': self._exec_bash,
            'sh': self._exec_bash,
            'shell': self._exec_bash,
            'kotlin': self._exec_kotlin,
            'kt': self._exec_kotlin,
        }
        
        handler = handlers.get(lang.lower())
        if not handler:
            return PolyglotResult(
                success=False,
                output='',
                error=f'Unsupported language: {lang}. Supported: python, javascript, bash, kotlin',
                return_code=-1
            )
        
        return handler(code, share_vars)
    
    def _exec_python(self, code: str, share_vars: bool) -> PolyglotResult:
        """Execute Python code"""
        try:
            # Capture output
            import io
            import sys
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Execute with shared context
            if share_vars:
                exec(code, self.globals, self.locals)
            else:
                exec(code, {}, {})
            
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            return PolyglotResult(
                success=True,
                output=stdout_capture.getvalue(),
                error=stderr_capture.getvalue(),
                return_code=0
            )
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            return PolyglotResult(
                success=False,
                output='',
                error=str(e),
                return_code=1
            )
    
    def _exec_javascript(self, code: str, share_vars: bool) -> PolyglotResult:
        """Execute JavaScript via Node.js"""
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute with node
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Cleanup
            os.unlink(temp_file)
            
            return PolyglotResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode
            )
            
        except FileNotFoundError:
            return PolyglotResult(
                success=False,
                output='',
                error='Node.js not found. Install Node.js to run JavaScript blocks.',
                return_code=-1
            )
        except subprocess.TimeoutExpired:
            return PolyglotResult(
                success=False,
                output='',
                error='JavaScript execution timed out',
                return_code=-1
            )
        except Exception as e:
            return PolyglotResult(
                success=False,
                output='',
                error=str(e),
                return_code=-1
            )
    
    def _exec_bash(self, code: str, share_vars: bool) -> PolyglotResult:
        """Execute Bash/Shell code"""
        try:
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return PolyglotResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return PolyglotResult(
                success=False,
                output='',
                error='Shell execution timed out',
                return_code=-1
            )
        except Exception as e:
            return PolyglotResult(
                success=False,
                output='',
                error=str(e),
                return_code=-1
            )
    
    def _exec_kotlin(self, code: str, share_vars: bool) -> PolyglotResult:
        """Execute Kotlin code"""
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.kt', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Compile
            compile_result = subprocess.run(
                ['kotlinc', temp_file, '-include-runtime', '-d', temp_file + '.jar'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if compile_result.returncode != 0:
                os.unlink(temp_file)
                return PolyglotResult(
                    success=False,
                    output='',
                    error=f'Kotlin compilation failed: {compile_result.stderr}',
                    return_code=compile_result.returncode
                )
            
            # Execute
            run_result = subprocess.run(
                ['java', '-jar', temp_file + '.jar'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Cleanup
            os.unlink(temp_file)
            os.unlink(temp_file + '.jar')
            
            return PolyglotResult(
                success=run_result.returncode == 0,
                output=run_result.stdout,
                error=run_result.stderr,
                return_code=run_result.returncode
            )
            
        except FileNotFoundError:
            return PolyglotResult(
                success=False,
                output='',
                error='Kotlin not found. Install Kotlin to run Kotlin blocks.',
                return_code=-1
            )
        except Exception as e:
            return PolyglotResult(
                success=False,
                output='',
                error=str(e),
                return_code=-1
            )
    
    def get_shared_vars(self) -> Dict[str, Any]:
        """Get variables shared from polyglot blocks"""
        return {**self.globals, **self.locals}
    
    def set_shared_var(self, name: str, value: Any):
        """Set a shared variable"""
        self.globals[name] = value


# Singleton instance
_polyglot_bridge = None

def get_polyglot_bridge() -> PolyglotBridge:
    """Get singleton PolyglotBridge instance"""
    global _polyglot_bridge
    if _polyglot_bridge is None:
        _polyglot_bridge = PolyglotBridge()
    return _polyglot_bridge


# Convenience function
def polyglot(lang: str, code: str) -> str:
    """Quick polyglot execution"""
    bridge = get_polyglot_bridge()
    result = bridge.execute(lang, code)
    
    if result.success:
        return result.output
    else:
        raise RuntimeError(f'Polyglot error: {result.error}')
