import os
import sys
import base64

# Base64 string for a 64x64 Sykus Logo .ico file
# (This is a compressed, minimalist 64x64 transparent/black icon placeholder)
ICO_BASE64 = "AAABAAEAMDAAAAEAIAAwAAAAFgAAACgAAAABAAAAAgAAAAEAIAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

def create_ico():
    """Decodes the Base64 string and saves it as sykus_icon.ico"""
    ico_path = os.path.join(os.getcwd(), "sykus_icon.ico")
    try:
        with open(ico_path, "wb") as f:
            f.write(base64.b64decode(ICO_BASE64))
        return ico_path
    except Exception as e:
        print(f"Failed to extract Sykus icon: {e}")
        return None

def register_windows_extension(ico_path):
    """Registers the .syk extension and binds the icon and execute command."""
    try:
        import winreg
    except ImportError:
        print("
[!] 'winreg' module not found.")
        print("This auto-installer is strictly designed for Windows OS.")
        print("For Android/Linux/Mac, you can already run files using: python3 main.py run <file.syk>")
        return

    try:
        # A. Register .syk extension
        key_ext = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".syk")
        winreg.SetValue(key_ext, "", winreg.REG_SZ, "Sykus.Script")
        winreg.CloseKey(key_ext)

        # B. Register the Sykus.Script Class
        key_class = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "Sykus.Script")
        winreg.SetValue(key_class, "", winreg.REG_SZ, "Sykus Source File")

        # C. Set the DefaultIcon in the registry
        if ico_path:
            key_icon = winreg.CreateKey(key_class, "DefaultIcon")
            winreg.SetValue(key_icon, "", winreg.REG_SZ, f'"{ico_path}"')
            winreg.CloseKey(key_icon)

        # D. Set the shell\open\command to execute python main.py run "%1"
        key_shell = winreg.CreateKey(key_class, r"shell\open\command")
        
        # Build absolute paths for execution
        python_exe = sys.executable
        main_script = os.path.join(os.getcwd(), "main.py")
        
        # Command executed when double-clicking a .syk file
        command = f'"{python_exe}" "{main_script}" run "%1"'
        
        winreg.SetValue(key_shell, "", winreg.REG_SZ, command)
        winreg.CloseKey(key_shell)
        
        winreg.CloseKey(key_class)

        print("
[✓] Successfully linked '.syk' files to the Sykus Engine!")
        print(f"[✓] Set Default Icon: {ico_path}")
        print(f"[✓] Configured Open Command: {command}")
        print("
You can now double-click any .syk file to run it on Windows.")

    except PermissionError:
        print("
[!] Permission Denied!")
        print("Administrator privileges are required to modify the Windows Registry.")
        print("Please right-click your terminal/command prompt -> 'Run as Administrator', and try again.")
    except Exception as e:
        print(f"
[!] An unexpected error occurred: {e}")

def main():
    print("==================================================")
    print("         SYKUS V5.0 - WINDOWS INSTALLER           ")
    print("==================================================")
    
    if os.name != 'nt':
        print("
[!] Non-Windows Environment Detected.")
        print("Creating the Sykus Icon locally anyway...")
        
    # 1. Decode Base64 and save the .ico
    ico_path = create_ico()
    if ico_path:
        print(f"[✓] Sykus Logo extracted to: {ico_path}")
    
    # 2. Register Windows paths and extension properties
    if os.name == 'nt':
        print("
Applying Windows Registry configurations...")
        register_windows_extension(ico_path)

if __name__ == "__main__":
    main()