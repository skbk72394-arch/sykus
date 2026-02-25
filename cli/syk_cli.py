#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus CLI (syk)                                                            ║
║                                                                              ║
║   Commands:                                                                  ║
║   - syk run <file.syk>          Execute a Sykus file                         ║
║   - syk build <target>          Build for web/apk/desktop                    ║
║   - syk doctor                    Check system health                        ║
║   - syk --version                 Show version                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from colorama import init, Fore, Style
init(autoreset=True)

# Import Sykus engine components
from engine.syk_engine import SykusEngine
from ghost.dependency_manager import get_ghost_manager
from healer.auto_healer import ErrorTranslator


# ASCII Art Banner
BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   {Fore.MAGENTA}███████╗██╗   ██╗██╗  ██╗██╗   ██╗███████╗{Fore.CYAN}                                ║
║   {Fore.MAGENTA}██╔════╝╚██╗ ██╔╝██║ ██╔╝██║   ██║██╔════╝{Fore.CYAN}                                ║
║   {Fore.MAGENTA}███████╗ ╚████╔╝ █████╔╝ ██║   ██║███████╗{Fore.CYAN}                                ║
║   {Fore.MAGENTA}╚════██║  ╚██╔╝  ██╔═██╗ ██║   ██║╚════██║{Fore.CYAN}                                ║
║   {Fore.MAGENTA}███████║   ██║   ██║  ██╗╚██████╔╝███████║{Fore.CYAN}                                ║
║   {Fore.MAGENTA}╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝{Fore.CYAN}                                ║
║                                                                              ║
║                    {Fore.YELLOW}The World's Most Frustration-Free Language{Fore.CYAN}                   ║
║                              {Fore.GREEN}v3.0.0 Auto-Healing Edition{Fore.CYAN}                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""


def print_banner():
    """Print the Sykus banner"""
    print(BANNER)


def print_success(message: str):
    """Print success message"""
    print(f"{Fore.GREEN}✓{Style.RESET_ALL} {message}")


def print_error(message: str):
    """Print error message"""
    print(f"{Fore.RED}✗{Style.RESET_ALL} {message}")


def print_info(message: str):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ{Style.RESET_ALL} {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {message}")


class SykusCLI:
    """Main Sykus CLI class"""
    
    def __init__(self):
        self.engine = SykusEngine()
    
    def run(self, file_path: str, mode: str = 'auto', verbose: bool = False) -> int:
        """Run a Sykus file"""
        if not os.path.exists(file_path):
            print_error(f"File not found: {file_path}")
            return 1
        
        print_info(f"Running {Fore.CYAN}{file_path}{Style.RESET_ALL}...")
        print()
        
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            
            # Execute with auto-healing
            result = self.engine.execute(source, mode=mode, verbose=verbose)
            
            if result['success']:
                print()
                print_success("Execution completed successfully!")
                return 0
            else:
                print()
                print_error("Execution failed")
                return 1
                
        except KeyboardInterrupt:
            print()
            print_warning("Interrupted by user")
            return 130
        except Exception as e:
            print()
            print_error(f"Unexpected error: {e}")
            return 1
    
    def build(self, target: str, file_path: str = None, output_dir: str = None) -> int:
        """Build for a target platform"""
        valid_targets = ['web', 'apk', 'ios', 'desktop', 'python', 'javascript']
        
        if target not in valid_targets:
            print_error(f"Invalid target. Choose from: {', '.join(valid_targets)}")
            return 1
        
        # Find default file if not specified
        if not file_path:
            for candidate in ['main.syk', 'app.syk', 'index.syk']:
                if os.path.exists(candidate):
                    file_path = candidate
                    break
        
        if not file_path or not os.path.exists(file_path):
            print_error("No Sykus file found. Specify a file or create main.syk")
            return 1
        
        print_info(f"Building {Fore.CYAN}{file_path}{Style.RESET_ALL} for {Fore.YELLOW}{target}{Style.RESET_ALL}...")
        
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            
            result = self.engine.build(source, target=target, output_dir=output_dir)
            
            if result['success']:
                print()
                print_success(f"Build completed: {result.get('output_path', 'output/')}")
                
                # Post-build actions
                if target == 'apk':
                    self._post_build_apk(result)
                
                return 0
            else:
                print()
                print_error(f"Build failed: {result.get('error', 'Unknown error')}")
                return 1
                
        except Exception as e:
            print()
            print_error(f"Build error: {e}")
            return 1
    
    def _post_build_apk(self, result: dict):
        """Post-build actions for APK"""
        print()
        print_info("Android build instructions:")
        print(f"  1. cd {result.get('output_path', 'output/')}")
        print(f"  2. buildozer android debug")
        print()
        print_warning("Note: First build may take 10-30 minutes")
    
    def doctor(self) -> int:
        """Check system health"""
        print_info("Checking Sykus system health...\n")
        
        checks = [
            ('Python', self._check_python),
            ('Sykus Engine', self._check_sykus),
            ('Speech Recognition', self._check_speech),
            ('Text-to-Speech', self._check_tts),
            ('Node.js (for JS)', self._check_node),
            ('Buildozer (for APK)', self._check_buildozer),
        ]
        
        all_good = True
        for name, check_fn in checks:
            status, message = check_fn()
            if status:
                print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {name}: {message}")
            else:
                print(f"  {Fore.YELLOW}⚠{Style.RESET_ALL} {name}: {message}")
                all_good = False
        
        print()
        if all_good:
            print_success("All systems operational!")
        else:
            print_warning("Some components need attention")
        
        return 0
    
    def _check_python(self) -> tuple:
        """Check Python version"""
        import sys
        version = sys.version_info
        if version >= (3, 8):
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        return False, "Python 3.8+ required"
    
    def _check_sykus(self) -> tuple:
        """Check Sykus installation"""
        try:
            from engine import syk_engine
            return True, "Engine ready"
        except Exception as e:
            return False, f"Engine issue: {e}"
    
    def _check_speech(self) -> tuple:
        """Check speech recognition"""
        try:
            import speech_recognition
            return True, "Available"
        except ImportError:
            return False, "Run: use speech in your code (auto-installs)"
    
    def _check_tts(self) -> tuple:
        """Check text-to-speech"""
        try:
            import pyttsx3
            return True, "Available"
        except ImportError:
            return False, "Run: use tts in your code (auto-installs)"
    
    def _check_node(self) -> tuple:
        """Check Node.js"""
        try:
            import subprocess
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"Node {result.stdout.strip()}"
            return False, "Node.js not found"
        except:
            return False, "Node.js not installed"
    
    def _check_buildozer(self) -> tuple:
        """Check Buildozer"""
        try:
            import buildozer
            return True, "Available"
        except ImportError:
            return False, "Will auto-install when building APK"


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog='syk',
        description='Sykus - The World\'s Most Frustration-Free Programming Language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
{Fore.CYAN}Examples:{Style.RESET_ALL}
  syk run hello.syk                    Run a Sykus file
  syk run app.syk --mode web           Run in web mode
  syk build apk                        Build Android APK
  syk build web                        Build for web
  syk doctor                           Check system health

{Fore.CYAN}Documentation:{Style.RESET_ALL} https://sykus.dev/docs
        '''
    )
    
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 3.0.0')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a Sykus file')
    run_parser.add_argument('file', help='Sykus file to run')
    run_parser.add_argument('--mode', '-m', choices=['auto', 'ai', 'web', 'desktop'], 
                           default='auto', help='Execution mode')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build for a target')
    build_parser.add_argument('target', choices=['web', 'apk', 'ios', 'desktop', 'python', 'javascript'],
                             help='Build target')
    build_parser.add_argument('--file', '-f', help='Sykus file to build')
    build_parser.add_argument('--output', '-o', help='Output directory')
    
    # Doctor command
    subparsers.add_parser('doctor', help='Check system health')
    
    args = parser.parse_args()
    
    # Print banner for most commands
    if args.command:
        print_banner()
    
    cli = SykusCLI()
    
    if args.command == 'run':
        return cli.run(args.file, mode=args.mode, verbose=args.verbose)
    elif args.command == 'build':
        return cli.build(args.target, args.file, args.output)
    elif args.command == 'doctor':
        return cli.doctor()
    else:
        print_banner()
        parser.print_help()
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
        sys.exit(130)
