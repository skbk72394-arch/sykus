import os
import sys
import ctypes

def integrate_sykus_windows():
    """
    Registers the .syk extension in the Windows Registry (HKCU) 
    as a web-standard document, linking it to the Sykus Engine.
    """
    try:
        import winreg
    except ImportError:
        print("[!] 'winreg' module not found. This script is intended for Windows.")
        return

    try:
        print("Registering .syk extension as a Web-Standard document...")
        
        # 1. Register .syk extension under HKCU to avoid needing Admin rights
        key_path = r"Software\Classes\.syk"
        key_ext = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        
        # Set default value to Sykus.Script
        winreg.SetValue(key_ext, "", winreg.REG_SZ, "Sykus.Script")
        
        # Set Content Type (MIME) to text/html to piggyback on web infrastructure
        winreg.SetValueEx(key_ext, "Content Type", 0, winreg.REG_SZ, "text/html")
        winreg.SetValueEx(key_ext, "PerceivedType", 0, winreg.REG_SZ, "text")
        
        # Pre-populate 'Open With' list so the Sykus Engine appears as a recommended app
        open_with_key = winreg.CreateKey(key_ext, "OpenWithProgids")
        winreg.SetValueEx(open_with_key, "Sykus.Script", 0, winreg.REG_NONE, b"")
        winreg.CloseKey(open_with_key)
        
        winreg.CloseKey(key_ext)
        print("[✓] MIME type 'text/html' and OpenWith list configured.")

        # 2. Register the Sykus.Script Class
        class_path = r"Software\Classes\Sykus.Script"
        key_class = winreg.CreateKey(winreg.HKEY_CURRENT_USER, class_path)
        winreg.SetValue(key_class, "", winreg.REG_SZ, "Sykus Source File")

        # 3. Map icon to standard system document/web icon (piggybacking on Windows UI)
        # imageres.dll,-102 is a very clean, modern document icon native to Windows.
        icon_key = winreg.CreateKey(key_class, "DefaultIcon")
        winreg.SetValue(icon_key, "", winreg.REG_SZ, "imageres.dll,-102")
        winreg.CloseKey(icon_key)
        print("[✓] Professional document icon linked natively (no external .ico needed).")

        # 4. Set the shell\open\command to execute the Sykus interpreter
        shell_key = winreg.CreateKey(key_class, r"shell\open\command")
        
        # Build absolute paths for the execution engine
        python_exe = sys.executable
        main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
        
        # The exact command run when a .syk file is double-clicked
        command = f'"{python_exe}" "{main_script}" run "%1"'
        winreg.SetValue(shell_key, "", winreg.REG_SZ, command)
        winreg.CloseKey(shell_key)
        winreg.CloseKey(key_class)
        
        print(f"[✓] Sykus Engine Execution Path bound:
    -> {command}")

        # 5. Broadcast shell refresh (Instant Icon Update)
        print("
Broadcasting system-wide Shell Refresh signal...")
        try:
            # SHCNE_ASSOCCHANGED = 0x08000000, SHCNF_IDLIST = 0x0000
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            print("[✓] Windows Explorer refreshed successfully. Icons are now live!")
        except Exception as e:
            print(f"[!] Failed to refresh shell automatically: {e}")
            print("    (You may need to restart Windows Explorer to see the icon change.)")

        print("
[✓] Setup complete! Your .syk files feel like a native part of the OS.")

    except Exception as e:
        print(f"
[!] An error occurred during registry modification: {e}")

if __name__ == "__main__":
    print("==================================================")
    print("      SYKUS LIGHTWEIGHT WINDOWS INTEGRATION       ")
    print("==================================================")
    
    if os.name != 'nt':
        print("[!] This script is exclusively designed for Windows OS integration.")
        print("    (On Android/Linux/Mac, registry bindings are not applicable.)")
    else:
        integrate_sykus_windows()