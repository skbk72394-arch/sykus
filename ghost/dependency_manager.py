"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus Ghost Dependency Manager                                             ║
║                                                                              ║
║   Automatically installs dependencies in the background                      ║
║   No user intervention required - truly frustration-free                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import subprocess
import sys
import threading
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class GhostInstallResult:
    """Result of ghost installation"""
    success: bool
    package: str
    pip_package: str
    error: Optional[str] = None


class GhostDependencyManager:
    """
    Ghost Dependency Manager
    
    Automatically detects and installs required dependencies
    without bothering the user.
    """
    
    # Map Sykus module names to pip packages
    MODULE_MAP = {
        # AI & Speech
        'gemini': {'pip': ['google-generativeai'], 'env': ['GOOGLE_API_KEY']},
        'openai': {'pip': ['openai'], 'env': ['OPENAI_API_KEY']},
        'anthropic': {'pip': ['anthropic'], 'env': ['ANTHROPIC_API_KEY']},
        'speech': {'pip': ['SpeechRecognition', 'pyaudio']},
        'tts': {'pip': ['pyttsx3']},
        'voice': {'pip': ['SpeechRecognition', 'pyaudio', 'pyttsx3']},
        
        # Computer Vision
        'face_recognition': {'pip': ['face-recognition', 'opencv-python', 'Pillow']},
        'cv2': {'pip': ['opencv-python']},
        'opencv': {'pip': ['opencv-python']},
        'vision': {'pip': ['opencv-python', 'Pillow']},
        
        # Web & HTTP
        'requests': {'pip': ['requests']},
        'http': {'pip': ['requests', 'aiohttp']},
        'flask': {'pip': ['flask']},
        'fastapi': {'pip': ['fastapi', 'uvicorn']},
        
        # Database
        'sqlite': {'pip': []},  # Built-in
        'sqlite3': {'pip': []},  # Built-in
        'postgres': {'pip': ['psycopg2-binary']},
        'mongodb': {'pip': ['pymongo']},
        'redis': {'pip': ['redis']},
        
        # ML/Data
        'numpy': {'pip': ['numpy']},
        'pandas': {'pip': ['pandas']},
        'sklearn': {'pip': ['scikit-learn']},
        'torch': {'pip': ['torch']},
        'tensorflow': {'pip': ['tensorflow']},
        'transformers': {'pip': ['transformers']},
        
        # Media
        'pillow': {'pip': ['Pillow']},
        'image': {'pip': ['Pillow']},
        'audio': {'pip': ['pydub']},
        'video': {'pip': ['opencv-python', 'moviepy']},
        
        # Utilities
        'rich': {'pip': ['rich']},
        'colorama': {'pip': ['colorama']},
        'click': {'pip': ['click']},
        'yaml': {'pip': ['PyYAML']},
        'toml': {'pip': ['toml']},
        
        # Android
        'buildozer': {'pip': ['buildozer', 'cython']},
        'kivy': {'pip': ['kivy']},
    }
    
    def __init__(self):
        self.installed: Set[str] = set()
        self.installing: Set[str] = set()
        self.lock = threading.Lock()
        self.cache_file = Path.home() / '.sykus' / 'ghost_cache.json'
        self._load_cache()
    
    def _load_cache(self):
        """Load cache of installed packages"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.installed = set(data.get('installed', []))
            except:
                pass
    
    def _save_cache(self):
        """Save cache of installed packages"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump({'installed': list(self.installed)}, f)
    
    def is_installed(self, module: str) -> bool:
        """Check if a module is installed"""
        # Check cache first
        if module in self.installed:
            return True
        
        # Try importing
        try:
            __import__(module)
            with self.lock:
                self.installed.add(module)
                self._save_cache()
            return True
        except ImportError:
            return False
    
    def ghost_install(self, module: str, silent: bool = True) -> GhostInstallResult:
        """
        Ghost install a module - installs in background without user knowing
        
        Args:
            module: Sykus module name
            silent: If True, suppresses output
        
        Returns:
            GhostInstallResult with success status
        """
        # Already installed
        if self.is_installed(module):
            return GhostInstallResult(success=True, package=module, pip_package='')
        
        # Already installing
        if module in self.installing:
            # Wait for installation to complete
            while module in self.installing:
                import time
                time.sleep(0.1)
            return GhostInstallResult(success=True, package=module, pip_package='')
        
        with self.lock:
            self.installing.add(module)
        
        try:
            # Get pip packages for this module
            if module not in self.MODULE_MAP:
                # Try direct pip install
                result = self._pip_install(module, silent)
                with self.lock:
                    self.installing.discard(module)
                return result
            
            pip_packages = self.MODULE_MAP[module]['pip']
            
            if not pip_packages:
                # Built-in module
                with self.lock:
                    self.installed.add(module)
                    self.installing.discard(module)
                    self._save_cache()
                return GhostInstallResult(success=True, package=module, pip_package='built-in')
            
            # Install each pip package
            for pip_pkg in pip_packages:
                result = self._pip_install(pip_pkg, silent)
                if not result.success:
                    with self.lock:
                        self.installing.discard(module)
                    return GhostInstallResult(
                        success=False,
                        package=module,
                        pip_package=pip_pkg,
                        error=result.error
                    )
            
            with self.lock:
                self.installed.add(module)
                self.installing.discard(module)
                self._save_cache()
            
            return GhostInstallResult(
                success=True,
                package=module,
                pip_package=', '.join(pip_packages)
            )
            
        except Exception as e:
            with self.lock:
                self.installing.discard(module)
            return GhostInstallResult(
                success=False,
                package=module,
                pip_package='',
                error=str(e)
            )
    
    def _pip_install(self, package: str, silent: bool = True) -> GhostInstallResult:
        """Install a package using pip"""
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', package]
            
            if silent:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
            else:
                result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                return GhostInstallResult(success=True, package=package, pip_package=package)
            else:
                return GhostInstallResult(
                    success=False,
                    package=package,
                    pip_package=package,
                    error=result.stderr or 'Installation failed'
                )
                
        except Exception as e:
            return GhostInstallResult(
                success=False,
                package=package,
                pip_package=package,
                error=str(e)
            )
    
    def auto_install_async(self, modules: List[str], callback=None):
        """Install multiple modules asynchronously"""
        def install_all():
            results = []
            for module in modules:
                result = self.ghost_install(module, silent=True)
                results.append(result)
            if callback:
                callback(results)
        
        thread = threading.Thread(target=install_all, daemon=True)
        thread.start()
        return thread
    
    def detect_required_modules(self, source: str) -> List[str]:
        """Detect modules required by source code"""
        required = []
        
        # Pattern: use module_name
        import re
        use_pattern = r'^\s*use\s+(\w+)'
        for match in re.finditer(use_pattern, source, re.MULTILINE):
            module = match.group(1)
            if not self.is_installed(module):
                required.append(module)
        
        # Pattern: Agent name = use Module(key="...")
        agent_pattern = r'Agent\s+\w+\s*=\s*use\s+(\w+)'
        for match in re.finditer(agent_pattern, source, re.MULTILINE):
            module = match.group(1).lower()
            if module not in required and not self.is_installed(module):
                required.append(module)
        
        return required
    
    def install_all_required(self, source: str, silent: bool = True) -> List[GhostInstallResult]:
        """Install all required modules for source code"""
        modules = self.detect_required_modules(source)
        results = []
        
        for module in modules:
            result = self.ghost_install(module, silent=silent)
            results.append(result)
        
        return results


# Singleton instance
_ghost_manager = None

def get_ghost_manager() -> GhostDependencyManager:
    """Get the singleton GhostDependencyManager"""
    global _ghost_manager
    if _ghost_manager is None:
        _ghost_manager = GhostDependencyManager()
    return _ghost_manager


# Convenience function
def ghost_install(module: str, silent: bool = True) -> bool:
    """Quick ghost install a module"""
    manager = get_ghost_manager()
    result = manager.ghost_install(module, silent=silent)
    return result.success
