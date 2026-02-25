"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus - The World's Most Frustration-Free Programming Language             ║
║                                                                              ║
║   Version: 3.0.0 Auto-Healing Edition                                        ║
║                                                                              ║
║   Core Philosophy:                                                           ║
║   "Line 4 had a typo. I fixed it and ran it."                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

__version__ = "3.0.0"
__author__ = "Sykus Team"
__license__ = "MIT"

from engine.syk_engine import SykusEngine, run_sykus
from ghost.dependency_manager import ghost_install
from state.smart_memory import save, load
from healer.auto_healer import get_auto_healer
from bridge.polyglot import polyglot

__all__ = [
    'SykusEngine',
    'run_sykus',
    'ghost_install',
    'save',
    'load',
    'get_auto_healer',
    'polyglot',
]
